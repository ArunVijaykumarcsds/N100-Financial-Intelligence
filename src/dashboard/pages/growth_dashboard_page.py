from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from analytics.growth import (
    growth_summary,
    top_growth_companies,
    bottom_growth_companies,
    growth_leaderboard
)


def get_growth_dashboard():

    return {
        "summary": growth_summary(),
        "top_growth": top_growth_companies(),
        "bottom_growth": bottom_growth_companies(),
        "leaderboard": growth_leaderboard()
    }