import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "db/nifty100.db"
)

# =====================
# TOP 10 BY ROE
# =====================

roe_query = """
SELECT
    company_name,
    roe_percentage
FROM companies
ORDER BY roe_percentage DESC
LIMIT 10
"""

roe_df = pd.read_sql_query(
    roe_query,
    conn
)

print("\nTOP 10 BY ROE")
print(roe_df)

# =====================
# TOP 10 BY ROCE
# =====================

roce_query = """
SELECT
    company_name,
    roce_percentage
FROM companies
ORDER BY roce_percentage DESC
LIMIT 10
"""

roce_df = pd.read_sql_query(
    roce_query,
    conn
)

print("\nTOP 10 BY ROCE")
print(roce_df)

# =====================
# TOP 10 BY BOOK VALUE
# =====================

book_query = """
SELECT
    company_name,
    book_value
FROM companies
ORDER BY book_value DESC
LIMIT 10
"""

book_df = pd.read_sql_query(
    book_query,
    conn
)

print("\nTOP 10 BY BOOK VALUE")
print(book_df)

conn.close()