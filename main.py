import os
import sys
import time

import redis

import roversim

TIME_STEP = 0.1


def main():
    rds = redis.from_url(os.environ.get(
        "REDIS_URL", "redis://localhost:6379/0"))
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
    for stream in ("yakapi:prime:motor_a", "yakapi:prime:motor_b"):
        last = rds.xrevrange(stream, count=1)
        # Create a reasonable default if the stream is empty.
        streams[stream] = b'0-0'
        if last:
            streams[stream] = last[0][0]

    while True:
        start_time = time.time()
        try:
            for result in rds.xread(streams, block=int(TIME_STEP * 1000)):
                stream, evts = result
                for evt in evts:
                    if stream == b"yakapi:prime:motor_a":
                        r.motor_a.set_power(float(evt[1][b"power"]))
                    if stream == b"yakapi:prime:motor_b":
                        r.motor_b.set_power(float(evt[1][b"power"]))

                    streams[stream.decode()] = evt[0]

            ts += time.time() - start_time
            w.tick(ts)

            # At the end of the cycle we update our telemetry values. This can
            # be consumed by yakapi.  This is done outside the simulation
            # entities themselves so as to not confuse what is part of the We
            # would expect a real rover to send all these same values, just
            # finding the value by reading it's own sensors.
            telemetry = {
                "motor_a_power": r.motor_a.power,
                "motor_b_power": r.motor_b.power,
            }
            rds.hset("yakapi:prime", mapping=telemetry)
        except KeyboardInterrupt:
            print("Bye!")
            break


if __name__ == "__main__":
    main()
