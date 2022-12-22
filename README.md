# Rover Sim

A prototype of a python-based rover simulation.

See also [Yak API](https://github.com/The-Yak-Collective/yakapi)

## Usage

Running the CLI is simple enough:

    python3 main.py

The "Rover" responds to commands over stdin. For example:

```ShellSession
$ python3 main.py
fwd 100
rt 90
^D
$
```

## Redis

The simulator uses Redis for peristence. To get started you can run redis in a
docker container. This can be done easily in the docker ui or via the command
line:

    docker run --rm -p 55000:6379 redis:latest

Read more [here](https://hub.docker.com/_/redis/)

Then specify the connect string when running the simulator:

    export REDIS_URL=redis://localhost:55000 python3 main.py

### Streams

#### roversim:entity:<id>

This stream tracks the absolute position data for the Rover. When restarting,
the most recent position is used to reset the Rover.