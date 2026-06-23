import pandas as pd


def normalize_column_names(df):
    """
    Standardize column names
    """

    df.columns = [
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("%", "percentage")
        for col in df.columns
    ]

    return df


def normalize_ticker(df, column="id"):
    """
    Standardize company ticker names
    """

    if column in df.columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    return df


def normalize_year(df, column="year"):
    """
    Standardize year format
    """

    if column in df.columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

    return df

def normalize_text_columns(df):

    for col in df.columns:

        if df[col].dtype == "object":

            df[col] = (
                df[col]
                .astype(str)
                .str.replace("\n", " ", regex=False)
                .str.strip()
            )

    return df

if __name__ == "__main__":

    from loader import load_excel

    df = load_excel(
        "data/raw/profitandloss.xlsx"
    )

    df = normalize_column_names(df)

    df = normalize_ticker(
        df,
        column="company_id"
    )

    print(df.head())

    print(df.columns.tolist())

