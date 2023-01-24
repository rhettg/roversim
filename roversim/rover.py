import math


class Motor:
    def __init__(self, world, id, recorder=None):
        self.id = id
        self.world = world
        self.world.entities.append(self)
        self.recorder = recorder
        self.speed = 0

    def set_power(self, power):
        self.speed = power
        if self.recorder:
            self.recorder.set("{}:speed".format(self.id), self.speed)

    def tick(self, ts):
        pass


class Rover:
    # At full power, how fast should the motors push the rover?
    # In meters per second.
    MAX_MOTOR_VELOCITY = 0.001
    WHEELBASE_LENGTH = 0.005

    def __init__(self, world, id, recorder=None):
        self.id = id
        self.world = world
        self.world.entities.append(self)

        self.recorder = recorder

        self.motor_a = Motor(self.world, "motor_a", self.recorder)
        self.motor_b = Motor(self.world, "motor_b", self.recorder)

        self.last_tick = 0

    def size(self):
        return (0.01, 0.01)

    def calculate_movement(self, ts):
        dt = ts - self.last_tick

        s1 = self.MAX_MOTOR_VELOCITY * self.motor_a.speed
        s2 = self.MAX_MOTOR_VELOCITY * self.motor_b.speed

        # TODO: What I'd like to do is take into account the speed of two
        # motors, the wheelbase length and how the arc of the movemeent changes
        # based on those factors. But I'm not sure how to do that yet, and it's
        # probably not strictly necessary at this point. The physical model
        # doesn't need to be accurate yet.
        # As the motor speeds are the same, the rover will move in a straight line, or an infite radius circle.
        # copilot gave me this formula, but does it work?
        # r = self.WHEELBASE_LENGTH / 2 * (s1 + s2) / (s2 - s1)
        # r = self.WHEELBASE_LENGTH / (2 + (s2 + s1))

        if s1 == s2:
            s = s1
            rotation = 0
        else:
            if s1 > s2:
                s = (s1 - s2) / 2
                sign = 1.0
            elif s2 > s1:
                s = (s2 - s1) / 2
                sign = -1.0

            circ = 2 * math.pi * self.WHEELBASE_LENGTH / 2
            arcLength = s / circ

            # Now we have two sides of a triangle, we estimate the rotation angle
            rotation = sign * math.atan(arcLength / s)

        return (rotation * dt, 0, s * dt)

    def tick(self, ts):
        if self.last_tick == 0:
            self.last_tick = ts

        rotate, direction, amount = self.calculate_movement(ts)
        # print("rotation after {:.4f}: {:.2f}°, direction: {}°, amount: {:.3f}m".format(ts - self.lastTick, math.degrees(rotate), math.degrees(direction), amount))

        self.world.translate(self, direction, amount)
        self.world.rotate(self, rotate)

        p = self.world.entity_positions[self]

        print("[+{:.2f}] Rover: {:.1f}° ({:.3f}m, {:.3f}m)".format(
            ts, math.degrees(p.angle), p.point.x, p.point.y))

        self.last_tick = ts


class Recorder:
    def __init__(self, name, redis_client):
        self.name = name
        self.redis_client = redis_client
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def save(self):
        self.redis_client.xadd(self.name, self.data)
