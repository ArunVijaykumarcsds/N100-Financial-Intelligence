from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

import pandas as pd

from analytics.quality import (
    quality_summary,
    top_quality_companies,
    bottom_quality_companies
)


def get_quality_dashboard():

    df = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    return {
        "summary": quality_summary(df),
        "top_quality": top_quality_companies(df),
        "bottom_quality": bottom_quality_companies(df)
    }