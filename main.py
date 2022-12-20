import time
import math


class World:
    def __init__(self):
        self.entities = []
        self.entityBounds = {}
    
    def tick(self, ts):
        for entity in self.entities:
            entity.tick(ts)

    def setEntityPosition(self, entity, position):
        height, width = entity.size()
        bounds = EntityBounds(
            Point(position.x - width / 2, position.y - height / 2), 
            Point(position.x + width / 2, position.y + height / 2))

        self.entityBounds[entity] = bounds

    def translate(self, entity, direction, amount):
        b = self.entityBounds[entity]
        self.entityBounds[entity] = b.translate(direction, amount)

    def rotate(self, entity, angle):
        b = self.entityBounds[entity]
        self.entityBounds[entity] = b.rotate(angle)


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
    
    def setVelocity(self, velocity):
        # TODO: model in acceleration, stall, etc.
        self.speed = velocity

    def tick(self, ts):
        print("I'm a motor!")


class Rover:
    def __init__(self, world):
        self.world = world
        self.world.entities.append(self)

        self.motorA = Motor(self.world)
        self.motorB = Motor(self.world)
    
    def size(self):
        return (0.01, 0.01)

    def tick(self, ts):
        s = self.motorA.speed
        self.world.translate(self, 0, s)

        b = self.world.entityBounds[self]
        print("Rover: ({}, {})".format(b.center().x, b.center().y))


def main():
    w = World()

    r = Rover(w)
    w.setEntityPosition(r, Point(0, 0))
    w.rotate(r, 90 * math.pi / 180)
    r.motorA.setVelocity(0.001)
    r.motorB.setVelocity(0.001)


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