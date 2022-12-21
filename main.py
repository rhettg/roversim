import time
import math


class World:
    def __init__(self):
        self.entities = []
        self.entityPositions = {}
    
    def tick(self, ts):
        for entity in self.entities:
            entity.tick(ts)

    def setEntityPosition(self, entity, position):
        self.entityPositions[entity] = position

    def translate(self, entity, direction, amount):
        self.entityPositions[entity] = self.entityPositions[entity].translate(direction, amount)

    def rotate(self, entity, angle):
        self.entityPositions[entity] = self.entityPositions[entity].rotate(angle)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def translate(self, direction, amount):
        newx = self.x + amount * math.cos(direction)
        newy = self.y + amount * math.sin(direction)
        return Point(newx, newy)
    
    def rotate(self, angle, center):
        newx = center.x + (self.x - center.x) * math.cos(angle) - (self.y - center.y) * math.sin(angle)
        newy = center.y + (self.x - center.x) * math.sin(angle) + (self.y - center.y) * math.cos(angle)
        return Point(newx, newy)


class EntityPosition:
    def __init__(self, point, angle):
        self.point = point
        self.angle = angle
    
    def translate(self, direction, amount):
        absDirection = self.angle + direction
        if absDirection > 2 * math.pi:
            absDirection -= 2 * math.pi
        if absDirection < 0:
            absDirection += 2 * math.pi

        newpoint = self.point.translate(absDirection, amount)
        return EntityPosition(newpoint, self.angle)
    
    def rotate(self, angle):
        newAngle = self.angle + angle
        if newAngle > 2 * math.pi:
            newAngle -= 2 * math.pi
        if newAngle < 0:
            newAngle += 2 * math.pi

        return EntityPosition(self.point, newAngle)


class EntityBounds:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    
    def center(self):
        return Point((self.p1.x + self.p2.x) / 2, (self.p1.y + self.p2.y) / 2)

    def translate(self, direction, amount):
        newP1 = self.p1.translate(direction, amount)
        newP2 = self.p2.translate(direction, amount)
        return EntityBounds(newP1, newP2)

    def rotate(self, angle):
        center = Point((self.p1.x + self.p2.x) / 2, (self.p1.y + self.p2.y) / 2)
        newP1 = self.p1.rotate(angle, center)
        newP2 = self.p2.rotate(angle, center)
        return EntityBounds(newP1, newP2)


class Motor:
    def __init__(self, world):
        self.world = world
        self.world.entities.append(self)
        self.speed = 0
    
    def setPower(self, power):
        # TODO: model in acceleration, stall, etc.
        self.speed = power

    def tick(self, ts):
        pass


class Rover:
    # At full power, how fast should the motors push the rover?
    # In meters per second.
    MAX_MOTOR_VELOCITY = 0.001
    WHEELBASE_LENGTH = 0.005

    def __init__(self, world):
        self.world = world
        self.world.entities.append(self)

        self.motorA = Motor(self.world)
        self.motorB = Motor(self.world)

        self.lastTick = 0
    
    def size(self):
        return (0.01, 0.01)

    def calculateMovement(self, ts):
        dt = ts - self.lastTick

        s1 = self.MAX_MOTOR_VELOCITY * self.motorA.speed
        s2 = self.MAX_MOTOR_VELOCITY * self.motorB.speed

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
            elif s2 > s1:
                s = (s2 - s1) / 2

            circ = 2 * math.pi * self.WHEELBASE_LENGTH / 2
            arcLength = s / circ

            # Now we have two sides of a triangle, we estimate the rotation angle
            rotation = math.atan(arcLength / s)

        return (rotation * dt, 0, s * dt)

    def tick(self, ts):
        if self.lastTick == 0:
            self.lastTick = ts

        rotate, direction, amount = self.calculateMovement(ts)
        #print("rotation after {:.4f}: {:.2f}°, direction: {}°, amount: {:.3f}m".format(ts - self.lastTick, math.degrees(rotate), math.degrees(direction), amount))

        self.world.translate(self, direction, amount)
        self.world.rotate(self, rotate)

        p = self.world.entityPositions[self]
        print("Rover: {}° ({:.3f}m, {:.3f}m)".format(math.degrees(p.angle), p.point.x, p.point.y))
        self.lastTick = ts


def main():
    w = World()

    r = Rover(w)
    w.setEntityPosition(r, EntityPosition(Point(0, 0), 0))
    #w.rotate(r, math.radians(45))
    r.motorA.setPower(1.0)
    r.motorB.setPower(-1.0)


    ts = 0.0
    try:
        while True:
            time.sleep(0.1)
            ts += 0.1
            w.tick(ts)
    except KeyboardInterrupt:
        pass



if __name__ == "__main__":
    main()