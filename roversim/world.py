import math


class World:
    def __init__(self, redis_client=None):
        self.entities = []
        self.entityPositions = {}
        self.redis_client = redis_client

    def tick(self, ts):
        for entity in self.entities:
            entity.tick(ts)

        if self.redis_client:
            self.redis_client.set("roversim:ts", ts)

    def restore_entity(self, entity):
        self.entityPositions[entity] = self._load_entity(entity)

    def setEntityPosition(self, entity, position):
        self.entityPositions[entity] = position
        self._save_entity(entity)

    def translate(self, entity, direction, amount):
        self.entityPositions[entity] = self.entityPositions[entity].translate(
            direction, amount)
        self._save_entity(entity)

    def rotate(self, entity, angle):
        self.entityPositions[entity] = self.entityPositions[entity].rotate(
            angle)
        self._save_entity(entity)

    def _save_entity(self, entity):
        if not self.redis_client:
            return

        position = self.entityPositions[entity]
        self.redis_client.xadd("roversim:entity:{}".format(entity.id), {
                               "x": position.point.x, "y": position.point.y, "direction": position.angle})

    def _load_entity(self, entity):
        if not self.redis_client:
            return

        parts = self.redis_client.xrevrange(
            "roversim:entity:{}".format(entity.id), count=1)
        if len(parts) == 0:
            return EntityPosition(Point(0, 0), 0)

        return EntityPosition(Point(float(parts[0][1][b"x"]), float(
            parts[0][1][b"y"])), float(parts[0][1][b"direction"]))


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def translate(self, direction, amount):
        newx = self.x + amount * math.cos(direction)
        newy = self.y + amount * math.sin(direction)
        return Point(newx, newy)

    def rotate(self, angle, center):
        newx = center.x + (self.x - center.x) * math.cos(angle) - \
            (self.y - center.y) * math.sin(angle)
        newy = center.y + (self.x - center.x) * math.sin(angle) + \
            (self.y - center.y) * math.cos(angle)
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
        center = Point((self.p1.x + self.p2.x) / 2,
                       (self.p1.y + self.p2.y) / 2)
        newP1 = self.p1.rotate(angle, center)
        newP2 = self.p2.rotate(angle, center)
        return EntityBounds(newP1, newP2)
