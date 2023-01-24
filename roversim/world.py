import math


class World:
    def __init__(self, redis_client=None):
        self.entities = []
        self.entity_positions = {}
        self.redis_client = redis_client

    def tick(self, ts):
        for entity in self.entities:
            entity.tick(ts)

        if self.redis_client:
            self.redis_client.set("roversim:ts", ts)

    def restore_entity(self, entity):
        self.entity_positions[entity] = self._load_entity(entity)

    def set_entity_position(self, entity, position):
        self.entity_positions[entity] = position
        self._save_entity(entity)

    def translate(self, entity, direction, amount):
        self.entity_positions[entity] = self.entity_positions[entity].translate(
            direction, amount)
        self._save_entity(entity)

    def rotate(self, entity, angle):
        self.entity_positions[entity] = self.entity_positions[entity].rotate(
            angle)
        self._save_entity(entity)

    def _save_entity(self, entity):
        if not self.redis_client:
            return

        position = self.entity_positions[entity]
        self.redis_client.xadd("roversim:entity:{}".format(entity.id), {
                               "x": position.point.x, "y": position.point.y, "direction": position.angle})

    def _load_entity(self, entity):
        if not self.redis_client:
            return

        parts = self.redis_client.xrevrange(
            "roversim:entity:{}".format(entity.id), count=1)
        if len(parts) == 0:
            return Position(Point(0, 0), 0)

        return Position(Point(float(parts[0][1][b"x"]), float(
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


class Position:
    def __init__(self, point, angle):
        self.point = point
        self.angle = angle

    def translate(self, direction, amount):
        abs_direction = self.angle + direction
        if abs_direction > 2 * math.pi:
            abs_direction -= 2 * math.pi
        if abs_direction < 0:
            abs_direction += 2 * math.pi

        newpoint = self.point.translate(abs_direction, amount)
        return Position(newpoint, self.angle)

    def rotate(self, angle):
        new_angle = self.angle + angle
        if new_angle > 2 * math.pi:
            new_angle -= 2 * math.pi
        if new_angle < 0:
            new_angle += 2 * math.pi

        return Position(self.point, new_angle)
