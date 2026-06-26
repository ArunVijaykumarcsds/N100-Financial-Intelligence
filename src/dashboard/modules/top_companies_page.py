import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"


def get_top_roe():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        company_name,
        roe_percentage
    FROM companies
    ORDER BY roe_percentage DESC
    LIMIT 10
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df