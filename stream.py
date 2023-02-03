import os
import sys
import time

import redis


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 stream.py <stream name>...", file=sys.stderr)
        sys.exit(1)

    rds = redis.from_url(os.environ.get(
        "REDIS_URL", "redis://localhost:6379/0"))
    if not rds.ping():
        print("Redis is not available", file=sys.stderr)
        sys.exit(1)

    streams = {}
    for s in sys.argv[1:]:
        streams[s] = "$"

    while True:
        try:
            for stream, evts in rds.xread(streams, block=100):
                for evt in evts:
                    fields = ""
                    for k, v in evt[1].items():
                        fields += "{}={} ".format(k.decode(), v.decode())
                    print("{} {} {}".format(
                        stream.decode(), evt[0].decode(), fields))
                    streams[stream] = evt[0]
        except KeyboardInterrupt:
            print("Bye!")
            break


if __name__ == "__main__":
    main()
