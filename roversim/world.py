import math
import sqlite3
import json


class World:
    def __init__(self, db_path='roversim.db'):
        self.entities = []
        self.entity_positions = {}
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                position TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS world_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.conn.commit()

    def tick(self, ts):
        self._save_world_state('ts', ts)
        for entity in self.entities:
            entity.tick(ts)
    def restore_entity(self, entity):
        self.entity_positions[entity] = self._load_entity(entity)

    def set_entity_position(self, entity, position):
        self.entity_positions[entity] = position
        self._save_entity(entity)

    def translate(self, entity, direction, amount):
        self.entity_positions[entity] = self.entity_positions[entity].translate(direction, amount)
        self._save_entity(entity)

    def rotate(self, entity, angle):
        self.entity_positions[entity] = self.entity_positions[entity].rotate(angle)
        self._save_entity(entity)

    def _save_entity(self, entity):
        position = self.entity_positions[entity]
        position_data = json.dumps({
            'x': position.point.x,
            'y': position.point.y,
            'direction': position.angle
        })
        self.cursor.execute('''
            INSERT OR REPLACE INTO entities (id, position)
            VALUES (?, ?)
        ''', (entity.id, position_data))
        self.conn.commit()

    def _load_entity(self, entity):
        self.cursor.execute('SELECT position FROM entities WHERE id = ?', (entity.id,))
        result = self.cursor.fetchone()
        if result:
            position_data = json.loads(result[0])
            return Position(Point(position_data['x'], position_data['y']), position_data['direction'])
        return Position(Point(0, 0), 0)

    def _save_world_state(self, key, value):
        self.cursor.execute('''
            INSERT OR REPLACE INTO world_state (key, value)
            VALUES (?, ?)
        ''', (key, json.dumps(value)))
        self.conn.commit()

    def _load_world_state(self, key, default=None):
        self.cursor.execute('SELECT value FROM world_state WHERE key = ?', (key,))
        result = self.cursor.fetchone()
        if result:
            return json.loads(result[0])
        return default

    def get_current_time(self):
        return self._load_world_state("ts", 0.0)


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
        new_angle = (self.angle + angle) % (2 * math.pi)
        return Position(self.point, new_angle)
