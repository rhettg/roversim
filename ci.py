import os
import time

from yakapi import Client


def motor_a(yakapi_client, power):
    yakapi_client.publish("motor_a", {"power": power})


def motor_b(yakapi_client, power):
    yakapi_client.publish("motor_b", {"power": power})


def apply_command(rds, cmd, args):
    cmd = cmd.strip().lower()
    args = args.split(" ")

    if cmd == "noop":
        return 0.0
    elif cmd.startswith("lt"):
        angle = args[0]
        motor_a(rds, -0.8)
        motor_b(rds, 0.8)

        return 1.32 * abs(float(angle) / 100)
    elif cmd.startswith("rt"):
        angle = args[0]
        motor_a(rds, 0.8)
        motor_b(rds, -0.8)

        return 1.32 * abs(float(angle)) / 100
    elif cmd.startswith("fwd"):
        duration = args[0]
        motor_a(rds, 0.8)
        motor_b(rds, 0.8)
        return float(duration) / 100
    elif cmd.startswith("ffwd"):
        duration = args[0]
        motor_a(rds, 1.0)
        motor_b(rds, 1.0)
        return float(duration) / 100
    elif cmd.startswith("bck"):
        duration = args[0]
        motor_a(rds, -0.8)
        motor_b(rds, -0.8)
        return float(duration) / 100
    else:
        raise Exception("Unknown command: {}".format(cmd))


def send_result(yakapi_client, id, result, error=None):
    response = {"id": id}

    if error:
        response["error"] = error
    else:
        response["result"] = result

    yakapi_client.publish("ci:result", response)
    print(f"sent response: {response}")


def main():
    yc = Client(os.environ.get("YAKAPI_URL", "http://localhost:8080"))

    while True:
        try:
            for _, evt in yc.subscribe(["ci"]):
                print(f"processing {evt}")

                if 'id' not in evt:
                    print("skipping because missing id")
                    continue

                try:
                    next_delay = apply_command(yc, evt["cmd"], evt.get("args", ""))
                except Exception as e:
                    send_result(yc, evt['id'], None, error=str(e))
                    continue

                print(f"sleeping")
                time.sleep(next_delay)
                motor_a(yc, 0)
                motor_b(yc, 0)
                print("done")

                send_result(yc, evt['id'], "ok")
        except KeyboardInterrupt:
            print("Bye!")
            break


if __name__ == "__main__":
    print("starting ci")
    main()
