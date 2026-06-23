import sqlite3

DB_PATH = "db/nifty100.db"


def get_connection():
    return sqlite3.connect(DB_PATH)

# Why?

# Later every ETL file becomes:

# from db_utils import get_connection

# conn = get_connection()

# instead of repeating:

# sqlite3.connect(
#     "db/nifty100.db"
# )

# everywhere.

# This is closer to how production ETL projects are structured.