import sqlite3

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

with open("db/schema.sql", "r") as f:
    schema = f.read()

conn.executescript(schema)

conn.commit()

conn.close()

print("Database created successfully.")