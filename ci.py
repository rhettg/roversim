import os
import sys
import time

import redis


def motor_a(rds, power):
    rds.xadd("yakapi:prime:motor_a", {"power": power})


def motor_b(rds, power):
    rds.xadd("yakapi:prime:motor_b", {"power": power})


def apply_command(rds, cmd):
    cmd = cmd.strip().lower()

    if cmd == "quit":
        return None
    elif cmd == "noop":
        return 0.0
    elif cmd.startswith("lt "):
        _, angle = cmd.split(" ")
        motor_a(rds, -0.8)
        motor_b(rds, 0.8)

        return 1.32 * abs(float(angle) / 100)
    elif cmd.startswith("rt "):
        _, angle = cmd.split(" ")
        motor_a(rds, 0.8)
        motor_b(rds, -0.8)

        return 1.32 * abs(float(angle)) / 100
    elif cmd.startswith("fwd "):
        _, duration = cmd.split(" ")
        motor_a(rds, 0.8)
        motor_b(rds, 0.8)
        return float(duration) / 100
    elif cmd.startswith("ffwd "):
        _, duration = cmd.split(" ")
        motor_a(rds, 1.0)
        motor_b(rds, 1.0)
        return float(duration) / 100
    elif cmd.startswith("bck "):
        _, duration = cmd.split(" ")
        motor_a(rds, -0.8)
        motor_b(rds, -0.8)
        return float(duration) / 100
    else:
        print("Unknown command: {}".format(cmd))
        return 0.0


def main():
    rds = redis.from_url(os.environ.get(
        "REDIS_URL", "redis://localhost:6379/0"))
    if not rds.ping():
        print("Redis is not available", file=sys.stderr)
        sys.exit(1)

    try:
        for cmd in sys.stdin:
            cmd = cmd.strip()
            print("processing {}... ".format(cmd), end="", flush=True)
            next_delay = apply_command(rds, cmd)
            time.sleep(next_delay)

            motor_a(rds, 0)
            motor_b(rds, 0)
            print("done")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
