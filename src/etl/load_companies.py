import sqlite3

from loader import load_excel
from normaliser import (
    normalize_column_names,
    normalize_text_columns
)


DB_PATH = "db/nifty100.db"


def load_companies():

    df = load_excel(
        "data/raw/companies.xlsx"
    )

    df = normalize_column_names(df)
    df = normalize_text_columns(df)

    columns_to_keep = [
        "id",
        "company_name",
        "website",
        "face_value",
        "book_value",
        "roce_percentage",
        "roe_percentage"
    ]

    df = df[columns_to_keep]

    conn = sqlite3.connect(DB_PATH)

    df.to_sql(
        "companies",
        conn,
        if_exists="append",
        index=False
    )

    conn.commit()
    conn.close()

    print(
        f"{len(df)} companies loaded."
    )


if __name__ == "__main__":
    load_companies()