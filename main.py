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

    streams = {
        "yakapi:prime:motor_a": "$",
        "yakapi:prime:motor_b": "$",
    }

    while True:
        start_time = time.time()
        try:
            for stream, evts in rds.xread(streams, block=int(TIME_STEP * 1000)):
                for evt in evts:
                    if stream == b"yakapi:prime:motor_a":
                        r.motor_a.set_power(float(evt[1][b"power"]))
                    if stream == b"yakapi:prime:motor_b":
                        r.motor_b.set_power(float(evt[1][b"power"]))

                    streams[stream] = evt[0]

            ts += time.time() - start_time
            w.tick(ts)
        except KeyboardInterrupt:
            print("Bye!")
            break


if __name__ == "__main__":
    main()
