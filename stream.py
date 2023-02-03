import os
import sys
import redis


def main():
    # Parse arguments
    if len(sys.argv) != 2:
        print("Usage: python3 stream.py <stream name>", file=sys.stderr)
        sys.exit(1)

    stream_name = sys.argv[1]

    rds = redis.from_url(os.environ.get(
        "REDIS_URL", "redis://localhost:6379/0"))
    if not rds.ping():
        print("Redis is not available", file=sys.stderr)
        sys.exit(1)

    # find the last event in the stream
    tail = rds.xrevrange(stream_name, "+", "-", count=1)
    if len(tail) == 0:
        print("Stream not found", file=sys.stderr)
        sys.exit(1)

    last_message_id = tail[0][0]

    while True:
        try:
            for evt in rds.xrange(stream_name, "({}".format(last_message_id.decode()), "+"):
                last_message_id = evt[0]
                print(evt)
        except KeyboardInterrupt:
            print("Bye!")
            break


if __name__ == "__main__":
    main()
