import sqlite3

from loader import load_excel
from normaliser import normalize_column_names

DB_PATH = "db/nifty100.db"


def load_balance_sheet():

    df = load_excel(
        "data/raw/balancesheet.xlsx"
    )

    df = normalize_column_names(df)

    conn = sqlite3.connect(DB_PATH)

    df.to_sql(
        "balance_sheet",
        conn,
        if_exists="append",
        index=False
    )

    conn.commit()
    conn.close()

    print(
        f"{len(df)} balance-sheet records loaded."
    )


if __name__ == "__main__":
    load_balance_sheet()