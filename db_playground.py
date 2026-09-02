import sqlite3
import matplotlib.colors as mcolors

# Part 1: build the data

rows = []
for name, hex_val in mcolors.CSS4_COLORS.items():
    r, g, b = [int(c * 255) for c in mcolors.to_rgb(hex_val)]
    rows.append((name, r, g, b))

# Part 2: store data

conn = sqlite3.connect("chromafit.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS items")

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

cursor.execute("SELECT * FROM colors LIMIT 10")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT COUNT(*) FROM colors")
print(cursor.fetchone())

conn.close()