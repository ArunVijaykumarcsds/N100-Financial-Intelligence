import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"

company1 = "ABB"
company2 = "TCS"

conn = sqlite3.connect(DB_PATH)

query = f"""
SELECT
    id,
    company_name,
    roe_percentage,
    roce_percentage,
    book_value,
    face_value
FROM companies
WHERE id IN ('{company1}', '{company2}')
"""

df = pd.read_sql_query(
    query,
    conn
)

print(df)

conn.close()