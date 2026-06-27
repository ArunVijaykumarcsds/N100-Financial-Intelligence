from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

import pandas as pd

from analytics.cashflow_kpis import (
    CashFlowKPIs
)

import pandas as pd

from analytics.cashflow_kpis import (
    CashFlowKPIs
)


def build_capital_allocation():

    cf = pd.read_excel(
        "data/raw/cashflow.xlsx",
        header=1
    )

    cf["pattern_label"] = cf.apply(
        lambda x:
        CashFlowKPIs.capital_allocation_pattern(
            x["operating_activity"],
            x["investing_activity"],
            x["financing_activity"]
        ),
        axis=1
    )

    cf["cfo_sign"] = cf[
        "operating_activity"
    ].apply(
        lambda x:
        "+" if x > 0 else "-"
    )

    cf["cfi_sign"] = cf[
        "investing_activity"
    ].apply(
        lambda x:
        "+" if x > 0 else "-"
    )

    cf["cff_sign"] = cf[
        "financing_activity"
    ].apply(
        lambda x:
        "+" if x > 0 else "-"
    )

    result = cf[
        [
            "company_id",
            "year",
            "cfo_sign",
            "cfi_sign",
            "cff_sign",
            "pattern_label"
        ]
    ]

    result.to_csv(
        "output/capital_allocation.csv",
        index=False
    )

    return result


if __name__ == "__main__":

    result = build_capital_allocation()

    print(result.head())

    print(
        "\nRows:",
        len(result)
    )