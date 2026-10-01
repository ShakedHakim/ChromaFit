import sqlite3
import unittest

from models import NamedColor
from repository import MockColorRepository, SqliteColorRepository


class TestSqliteColorRepository(unittest.TestCase):

    ROWS = [
        ("navy", 0, 0, 128),
        ("white", 255, 255, 255),
        ("black", 0, 0, 0),
        ("crimson", 220, 20, 60),
        ("olive", 128, 128, 0),
    ]

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("""
            CREATE TABLE colors (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                r INTEGER,
                g INTEGER,
                b INTEGER
            )
        """)
        self.conn.executemany(
            "INSERT INTO colors (name, r, g, b) VALUES (?, ?, ?, ?)", self.ROWS
        )
        self.colors = SqliteColorRepository(connection=self.conn).get_all()

    def tearDown(self):
        self.conn.close()

    def test_get_all_returns_one_color_per_row(self):
        self.assertEqual(len(self.colors), len(self.ROWS))

    def test_get_all_returns_named_color_instances(self):
        for color in self.colors:
            self.assertIsInstance(color, NamedColor)

    def test_get_all_maps_names_and_rgb_from_rows(self):
        expected = [(name, (r, g, b)) for name, r, g, b in self.ROWS]
        actual = [(color.name, color.rgb) for color in self.colors]
        self.assertEqual(actual, expected)


class TestMockColorRepository(unittest.TestCase):

    def test_get_all_returns_hardcoded_colors(self):
        expected = [
            NamedColor("navy", (0, 0, 128)),
            NamedColor("white", (255, 255, 255)),
            NamedColor("black", (0, 0, 0)),
            NamedColor("crimson", (220, 20, 60)),
            NamedColor("olive", (128, 128, 0)),
            NamedColor("tan", (210, 180, 140)),
        ]
        self.assertEqual(MockColorRepository().get_all(), expected)


if __name__ == "__main__":
    unittest.main()
