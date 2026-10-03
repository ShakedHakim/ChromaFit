import sqlite3
import urllib.request

# Replaces the colors table with the xkcd color survey (CC0, https://xkcd.com/color/rgb.txt).
# db_playground.py is kept as the record of the original CSS4 seeding.

XKCD_URL = "https://xkcd.com/color/rgb.txt"
DB_PATH = "chromafit.db"


def hex_to_rgb(hex_value: str) -> tuple[int, int, int]:
    """Convert "#af884a" to (175, 136, 74)."""
    hex_value = hex_value.lstrip("#")
    return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))


def parse_xkcd(text: str) -> list[tuple[str, int, int, int]]:
    """Parse "name<TAB>#hex" lines into (name, r, g, b) rows, skipping the license header."""
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, hex_value = line.split("\t")[:2]
        rows.append((name.strip(), *hex_to_rgb(hex_value.strip())))
    return rows


def main() -> None:
    """Download the xkcd colors and replace the contents of the colors table with them."""
    # Part 1: build the data

    with urllib.request.urlopen(XKCD_URL) as response:
        rows = parse_xkcd(response.read().decode("utf-8"))

    # Part 2: store data

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS colors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            r INTEGER,
            g INTEGER,
            b INTEGER
        )
    """)

    cursor.execute("DELETE FROM colors")

    cursor.executemany(
        "INSERT INTO colors (name, r, g, b) VALUES (?, ?, ?, ?)",
        rows
    )
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM colors")
    print(f"Seeded {cursor.fetchone()[0]} xkcd colors into {DB_PATH}")

    conn.close()


if __name__ == "__main__":
    main()
