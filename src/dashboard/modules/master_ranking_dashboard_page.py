from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from analytics.master_ranking import (
    get_master_ranking
)


def get_master_dashboard():

    df = get_master_ranking()

    return {
        "leaderboard": df.head(20),
        "summary": {
            "total_companies": len(df),
            "highest_score": round(
                df["master_score"].max(),
                2
            ),
            "average_score": round(
                df["master_score"].mean(),
                2
            )
        }
    }