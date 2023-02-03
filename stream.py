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
            for evts in rds.xread(streams, block=100):
                stream = evts[0]
                for evt in evts[1]:
                    print("{} {} {}".format(
                        stream.decode(), evt[0].decode(), evt[1]))
                    streams[stream] = evt[0]
        except KeyboardInterrupt:
            print("Bye!")
            break


if __name__ == "__main__":
    main()
