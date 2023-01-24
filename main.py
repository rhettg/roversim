import os
import sys
import time

import redis

import roversim

TIME_STEP = 0.1


def apply_command(rover, cmd):
    cmd = cmd.strip().lower()

    if cmd == "quit":
        return None
    elif cmd == "noop":
        return TIME_STEP
    elif cmd.startswith("lt "):
        _, angle = cmd.split(" ")
        rover.motor_a.set_power(-0.8)
        rover.motor_b.set_power(0.8)

        return 1.32 * abs(float(angle) / 100)
    elif cmd.startswith("rt "):
        _, angle = cmd.split(" ")
        rover.motor_a.set_power(0.8)
        rover.motor_b.set_power(-0.8)

        return 1.32 * abs(float(angle)) / 100
    elif cmd.startswith("fwd "):
        _, duration = cmd.split(" ")
        rover.motor_a.set_power(0.8)
        rover.motor_b.set_power(0.8)
        return float(duration) / 100
    elif cmd.startswith("ffwd "):
        _, duration = cmd.split(" ")
        rover.motor_a.set_power(1.0)
        rover.motor_b.set_power(1.0)
        return float(duration) / 100
    elif cmd.startswith("bck "):
        _, duration = cmd.split(" ")
        rover.motor_a.set_power(-0.8)
        rover.motor_b.set_power(-0.8)
        return float(duration) / 100
    else:
        print("Unknown command: {}".format(cmd))
        return TIME_STEP


def main():
    rds = redis.from_url(os.environ.get(
        "REDIS_URL", "redis://localhost:6379/0"))
    if not rds.ping():
        print("Redis is not available", file=sys.stderr)
        sys.exit(1)

    w = roversim.World(rds)

    recorder = roversim.Recorder("yakapi:prime", rds)
    r = roversim.Rover(w, "prime", recorder=recorder)
    w.restore_entity(r)

    ts = float(rds.get("roversim:ts")) or 0.0
    print("starting at +{:.2f}s".format(ts))

    try:
        for cmd in sys.stdin:
            print("processing {}".format(cmd))
            next_delay = apply_command(r, cmd)
            while next_delay > 0:
                w.tick(ts)
                recorder.save()
                time.sleep(TIME_STEP)
                ts += TIME_STEP
                next_delay -= TIME_STEP

            r.motor_a.set_power(0)
            r.motor_b.set_power(0)
            w.tick(ts)
            recorder.save()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
