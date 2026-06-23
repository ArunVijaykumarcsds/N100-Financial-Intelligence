import pandas as pd


def load_excel(filepath):
    """
    Generic loader for Bluestock N100 Excel files
    """

    df = pd.read_excel(filepath)

    # First row contains actual column names
    df.columns = df.iloc[0]

    # Remove header row
    df = df.iloc[1:].reset_index(drop=True)

    return df


def show_summary(df, name):
    print(f"\n{name}")
    print("-" * 50)
    print("Shape:", df.shape)
    print(df.head(3))


if __name__ == "__main__":

    companies = load_excel(
        "data/raw/companies.xlsx"
    )

    profitandloss = load_excel(
        "data/raw/profitandloss.xlsx"
    )

    show_summary(companies, "COMPANIES")

    show_summary(
        profitandloss,
        "PROFIT & LOSS"
    )