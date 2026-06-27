import pandas as pd

df = pd.read_csv(
    "data/processed/financial_ratios.csv"
)

issues = []

for _, row in df.iterrows():

    company = row["company_id"]
    year = row["year"]

    roe = row.get(
        "return_on_equity_pct"
    )

    roa = row.get(
        "return_on_assets_pct"
    )

    de = row.get(
        "debt_to_equity"
    )

    icr = row.get(
        "interest_coverage"
    )

    if pd.isna(roe):
        issues.append(
            f"{company} | {year} | Missing ROE"
        )

    if pd.isna(roa):
        issues.append(
            f"{company} | {year} | Missing ROA"
        )

    if pd.isna(icr):
        issues.append(
            f"{company} | {year} | Interest Coverage N/A"
        )

    if (
        pd.notna(de)
        and de > 5
    ):
        issues.append(
            f"{company} | {year} | High Debt Equity ({de:.2f})"
        )

with open(
    "logs/ratio_edge_cases.log",
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "RATIO EDGE CASE REPORT\n"
    )

    f.write(
        "=" * 50 + "\n\n"
    )

    for item in issues:
        f.write(item + "\n")

print(
    f"Logged {len(issues)} edge cases"
)