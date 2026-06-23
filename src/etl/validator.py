import pandas as pd


def check_nulls(df):
    """
    Count null values per column
    """
    return df.isnull().sum()


def check_duplicates(df):
    """
    Count duplicate rows
    """
    return df.duplicated().sum()


def check_primary_key(df, column):
    """
    Check uniqueness of primary key
    """
    return df[column].duplicated().sum()

def check_composite_key(df, columns):
    """
    Check uniqueness of composite key
    """

    return df.duplicated(subset=columns).sum()

def show_composite_duplicates(df, columns):
    duplicates = df[df.duplicated(subset=columns, keep=False)]
    return duplicates.sort_values(columns)


if __name__ == "__main__":

    from loader import load_excel
    from normaliser import normalize_column_names

    df = load_excel(
        "data/raw/companies.xlsx"
    )

    df = normalize_column_names(df)

    print("\nNULL CHECK")
    print(check_nulls(df))

    print("\nDUPLICATE CHECK")
    print(check_duplicates(df))

    print("\nPRIMARY KEY CHECK")
    print(check_primary_key(df, "id"))

profit_df = load_excel(
    "data/raw/profitandloss.xlsx"
)

print("\nDUPLICATE COMPOSITE RECORDS")

duplicates = show_composite_duplicates(
    profit_df,
    ["company_id", "year"]
)

print(
    duplicates[
        ["company_id", "year"]
    ]
)

profit_df = normalize_column_names(
    profit_df
)

print("\nCOMPOSITE KEY CHECK")
print(
    check_composite_key(
        profit_df,
        ["company_id", "year"]
    )
)

print("\nFULL DUPLICATE ROWS")

print(
    profit_df[
        profit_df["company_id"] == "ADANIPORTS"
    ][
        ["id", "company_id", "year"]
    ]
)

duplicate_records = profit_df[
    profit_df.duplicated(
        subset=["company_id", "year"],
        keep=False
    )
]

duplicate_records.to_csv(
    "output/validation_failures.csv",
    index=False
)

print(
    "\nSaved validation failures to "
    "output/validation_failures.csv"
)