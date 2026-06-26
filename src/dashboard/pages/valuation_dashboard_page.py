from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from analytics.valuation import (
    ValuationAnalyzer
)


def get_valuation_dashboard():

    analyzer = ValuationAnalyzer()

    return {
        "summary":
            analyzer.valuation_summary(),

        "undervalued":
            analyzer.top_undervalued(),

        "overvalued":
            analyzer.top_overvalued()
    }