from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parents[2] / "src"
    )
)

from analytics.cashflow_kpis import CashFlowKPIs


def test_fcf():

    assert (
        CashFlowKPIs.free_cash_flow(
            100,
            -40
        )
        == 60
    )


def test_cfo_quality_high():

    assert (
        CashFlowKPIs.cfo_quality_score(
            200,
            100
        )
        == "High Quality"
    )


def test_cfo_quality_moderate():

    assert (
        CashFlowKPIs.cfo_quality_score(
            70,
            100
        )
        == "Moderate"
    )


def test_cfo_quality_risk():

    assert (
        CashFlowKPIs.cfo_quality_score(
            20,
            100
        )
        == "Accrual Risk"
    )


def test_capex_asset_light():

    assert (
        CashFlowKPIs.capex_intensity(
            -10,
            1000
        )
        == "Asset Light"
    )


def test_fcf_conversion():

    assert (
        round(
            CashFlowKPIs.fcf_conversion(
                100,
                200
            ),
            2
        )
        == 50.00
    )