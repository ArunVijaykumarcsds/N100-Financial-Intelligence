import pandas as pd

from loader import load_excel
from normaliser import normalize_column_names


def check_nulls(df):
    return df.isnull().sum()


def check_duplicates(df):
    return df.duplicated().sum()


def check_primary_key(df, column):
    return df[column].duplicated().sum()


def check_composite_key(df, columns):
    return df.duplicated(subset=columns).sum()

def show_composite_duplicates(df, columns):
    duplicates = df[df.duplicated(subset=columns, keep=False)]
    return duplicates.sort_values(columns)


if __name__ == "__main__":

    balance_df = load_excel(
        "data/raw/balancesheet.xlsx"
    )

    balance_df = normalize_column_names(
        balance_df
    )

    print("SHAPE")
    print(balance_df.shape)

    print("\nCOLUMNS")
    print(balance_df.columns.tolist())

    print("\nNULL CHECK")
    print(check_nulls(balance_df))

    print("\nDUPLICATE CHECK")
    print(check_duplicates(balance_df))

    print("\nPRIMARY KEY CHECK")
    print(
        check_primary_key(
            balance_df,
            "id"
        )
    )

    print("\nCOMPOSITE KEY CHECK")
    print(
        check_composite_key(
            balance_df,
            ["company_id", "year"]
        )
    )

    print("\nDUPLICATE COMPOSITE RECORDS")

duplicates = show_composite_duplicates(
    balance_df,
    ["company_id", "year"]
)

print(
    duplicates[
        ["id", "company_id", "year"]
    ]
)

print("\nDUPLICATES BY COMPANY")

print(
    duplicates["company_id"]
    .value_counts()
)

clean_balance_df = balance_df.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
)

print("\nORIGINAL SHAPE")
print(balance_df.shape)

print("\nCLEAN SHAPE")
print(clean_balance_df.shape)

print("\nREMAINING DUPLICATES")
print(
    clean_balance_df.duplicated(
        subset=["company_id", "year"]
    ).sum()
)