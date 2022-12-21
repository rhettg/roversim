import sys
import time

import roversim

TIME_STEP = 0.1


def applyCommand(rover, cmd):
    cmd = cmd.strip().lower()

    if cmd == "quit":
        return None
    elif cmd == "noop":
        return TIME_STEP
    elif cmd.startswith("lt "):
        _, angle = cmd.split(" ")
        rover.motorA.setPower(-0.8)
        rover.motorB.setPower(0.8)

        return 1.32 * abs(float(angle) / 100)
    elif cmd.startswith("rt "):
        _, angle = cmd.split(" ")
        rover.motorA.setPower(0.8)
        rover.motorB.setPower(-0.8)

        return 1.32 * abs(float(angle)) / 100
    elif cmd.startswith("fwd "):
        _, duration = cmd.split(" ")
        rover.motorA.setPower(0.8)
        rover.motorB.setPower(0.8)
        return float(duration) / 100
    elif cmd.startswith("ffwd "):
        _, duration = cmd.split(" ")
        rover.motorA.setPower(1.0)
        rover.motorB.setPower(1.0)
        return float(duration) / 100
    elif cmd.startswith("bck "):
        _, duration = cmd.split(" ")
        rover.motorA.setPower(-0.8)
        rover.motorB.setPower(-0.8)
        return float(duration) / 100
    else:
        print("Unknown command: {}".format(cmd))
        return TIME_STEP


def main():
    w = roversim.World()

    r = roversim.Rover(w)
    w.setEntityPosition(r, roversim.EntityPosition(roversim.Point(0, 0), 0))

    ts = 0.0

    try:
        for cmd in sys.stdin:
            print("processing {}".format(cmd))
            nextDelay = applyCommand(r, cmd)
            while nextDelay > 0:
                w.tick(ts)
                time.sleep(TIME_STEP)
                ts += TIME_STEP
                nextDelay -= TIME_STEP

            r.motorA.setPower(0)
            r.motorB.setPower(0)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
