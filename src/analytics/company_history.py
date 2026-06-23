import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "db/nifty100.db"
)

ticker = "ABB"

query = f"""
SELECT
    year,
    sales,
    net_profit,
    eps
FROM profit_loss
WHERE company_id = '{ticker}'
"""

df = pd.read_sql_query(
    query,
    conn
)

print(df)

conn.close()