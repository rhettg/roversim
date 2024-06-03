import os
import sys
import time

import redis

import roversim

TIME_STEP = 0.1

def send_telemetry(rds, key, value):
    response = {key: str(value)}

    rds.xadd("yakapi:telemetry", response, maxlen=1000)
    print(f"sent response: {response}")


def main():
    redis_url = os.environ.get("YAKAPI_REDIS_URL", "localhost:6379")
    rds = redis.from_url(os.environ.get(
        "REDIS_URL", f"redis://{redis_url}/0"))
    if not rds.ping():
        print("Redis is not available", file=sys.stderr)
        sys.exit(1)

    w = roversim.World(rds)

    r = roversim.Rover(w, "prime")
    w.restore_entity(r)

    ts = float(rds.get("roversim:ts") or "0")
    print("starting at +{:.2f}s".format(ts))

    # We can't rely on "$" when using multiple streams because the first stream
    # will end up racing with the others. Let's explicilty find the last message
    # in each stream and initialize our loop that way.
    streams = {}
    for stream in (b"yakapi:prime:motor_a", b"yakapi:prime:motor_b"):
        last = rds.xrevrange(stream, count=1)
        # Create a reasonable default if the stream is empty.
        streams[stream] = b'0-0'
        if last:
            streams[stream] = last[0][0]

    while True:
        start_time = time.time()
        change = False
        try:
            events = []
            for result in rds.xread(streams, block=int(TIME_STEP * 1000)):
                stream, evts = result
                for evt in evts:
                    events.append((stream, evt))
                    streams[stream] = evt[0]

            # We may have been blocked for some time. Before mutating the world, let's catch up.
            ts += time.time() - start_time
            w.tick(ts)

            for stream, evt in events:
                change = True
                if stream == b"yakapi:prime:motor_a":
                    r.motor_a.set_power(float(evt[1][b"power"]))
                if stream == b"yakapi:prime:motor_b":
                    r.motor_b.set_power(float(evt[1][b"power"]))

            # At the end of the cycle we update our telemetry values. This can
            # be consumed by yakapi.  This is done outside the simulation
            # entities themselves so as to not confuse what is part of the We
            # would expect a real rover to send all these same values, just
            # finding the value by reading it's own sensors.
            if change:
                send_telemetry(rds, "motor_a_power", r.motor_a.power)
                send_telemetry(rds, "motor_b_power", r.motor_b.power)
                send_telemetry(rds, "heading", r.compass.heading)
        except KeyboardInterrupt:
            print("Bye!")
            break


if __name__ == "__main__":
    main()
