from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parents[2] / "src"
    )
)

from analytics.ratios import RatioEngine

def test_net_profit_margin():

    assert (
        round(
            RatioEngine.net_profit_margin(
                100,
                1000
            ),
            2
        )
        == 10.00
    )


def test_zero_sales():

    assert (
        RatioEngine.net_profit_margin(
            100,
            0
        )
        is None
    )


def test_roe():

    assert (
        round(
            RatioEngine.roe(
                100,
                100,
                400
            ),
            2
        )
        == 20.00
    )


def test_negative_equity():

    assert (
        RatioEngine.roe(
            100,
            -100,
            50
        )
        is None
    )


def test_debt_free():

    assert (
        RatioEngine.debt_to_equity(
            0,
            100,
            500
        )
        == 0
    )


def test_interest_coverage():

    assert (
        round(
            RatioEngine.interest_coverage(
                100,
                20,
                10
            ),
            2
        )
        == 12.00
    )


def test_asset_turnover():

    assert (
        round(
            RatioEngine.asset_turnover(
                1000,
                500
            ),
            2
        )
        == 2.00
    )

def test_interest_coverage_zero_interest():

    assert (
        RatioEngine.interest_coverage(
            100,
            20,
            0
        )
        is None
    )