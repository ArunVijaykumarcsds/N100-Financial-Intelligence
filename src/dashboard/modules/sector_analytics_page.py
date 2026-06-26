from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from analytics.sector_analytics import (
    sector_summary,
    sector_leaderboard,
    top_sector,
    bottom_sector,
    market_cap_distribution
)


def get_sector_dashboard():

    return {
        "summary": sector_summary(),
        "leaderboard": sector_leaderboard(),
        "top_sector": top_sector(),
        "bottom_sector": bottom_sector(),
        "market_cap_distribution":
            market_cap_distribution()
    }