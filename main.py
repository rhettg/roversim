import os
import sys
import time
import sqlite3
from yakapi import Client

import roversim

TIME_STEP = 0.1

def send_telemetry(yak_client, key, value):
    response = {key: str(value)}

    yak_client.publish("telemetry", response)
    print(f"sent telemetry: {response}")


def main():
    yak_client = Client(os.environ.get("YAKAPI_URL", "http://localhost:8080"))

    print("Connecting to SQLite database...")
    db_path = os.environ.get("SQLITE_DB_PATH", "roversim.db")

    w = roversim.World(db_path)

    r = roversim.Rover(w, "prime")
    w.restore_entity(r)

    ts = w.get_current_time()
    print("starting at +{:.2f}s".format(ts))

    while True:
        start_time = time.time()
        change = False

        for stream, event in yak_client.subscribe(["motor_a", "motor_b"], timeout_event=60.0):
            # We may have been blocked for some time. Before mutating the world, let's catch up.
            ts += time.time() - start_time
            w.tick(ts)
            start_time = time.time()

            change = True
            if stream == "motor_a":
                r.motor_a.set_power(float(event["power"]))
            if stream == "motor_b":
                r.motor_b.set_power(float(event["power"]))

            yak_client.publish("telemetry", {
                "motor_a_power": r.motor_a.power,
                "motor_b_power": r.motor_b.power,
                "heading": r.compass.heading,
            })

        # TODO: Make this timeout driven
        # At the end of the cycle we update our telemetry values. This can
        # be consumed by yakapi.  This is done outside the simulation
        # entities themselves so as to not confuse what is part of the We
        # would expect a real rover to send all these same values, just
        # finding the value by reading it's own sensors.
        if change:
            pass


if __name__ == "__main__":
    print("booting roversim ...")
    try:
        main()
    except KeyboardInterrupt:
        print("Bye!")
