import sqlite3
import pandas as pd


def load_financial_ratios():

    df = pd.read_csv(
        "data/processed/financial_ratios.csv"
    )

    conn = sqlite3.connect(
        "db/nifty100.db"
    )

    df.to_sql(
        "financial_ratios",
        conn,
        if_exists="replace",
        index=False
    )

    conn.commit()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM financial_ratios
        """
    )

    print(
        "Rows:",
        cursor.fetchone()[0]
    )

    conn.close()


if __name__ == "__main__":
    load_financial_ratios()