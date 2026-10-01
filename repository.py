from abc import ABC, abstractmethod
from models import NamedColor
import sqlite3


class ColorRepository(ABC):

    @abstractmethod
    def get_all(self) -> list[NamedColor]:
        """Return every named color in the repository."""
        pass



class MockColorRepository(ColorRepository):

    def __init__(self):
        self._colors = [
            NamedColor("navy", (0, 0, 128)),
            NamedColor("white", (255, 255, 255)),
            NamedColor("black", (0, 0, 0)),
            NamedColor("crimson", (220, 20, 60)),
            NamedColor("olive", (128, 128, 0)),
            NamedColor("tan", (210, 180, 140)),
        ]

    def get_all(self) -> list[NamedColor]:
        """Return a copy of the hardcoded color list."""
        return list(self._colors)


class SqliteColorRepository(ColorRepository):
    """Loads named colors from a SQLite database."""

    def __init__(self, db_path: str = "chromafit.db",
                 connection: sqlite3.Connection | None = None):
        """Use db_path for per-query connections, or an injected connection if given."""
        self.db_path = db_path
        self._connection = connection

    def _to_color(self, row) -> NamedColor:
        """Convert a database row into a NamedColor."""
        name = row[1]
        rgb = (row[2], row[3], row[4])
        return NamedColor(name, rgb)

    def get_all(self) -> list[NamedColor]:
        """Load every row of the colors table as a NamedColor."""
        if self._connection is not None:
            rows = self._connection.execute("SELECT * FROM colors").fetchall()
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM colors")
                rows = cursor.fetchall()

        colors = []
        for row in rows:
            colors.append(self._to_color(row))
        return colors