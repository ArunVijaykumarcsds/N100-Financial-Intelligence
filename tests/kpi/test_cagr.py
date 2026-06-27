from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parents[2] / "src"
    )
)

from analytics.cagr import CAGRCalculator


def test_normal_cagr():

    value, flag = (
        CAGRCalculator.calculate(
            100,
            200,
            5
        )
    )

    assert flag == "OK"


def test_zero_base():

    value, flag = (
        CAGRCalculator.calculate(
            0,
            100,
            5
        )
    )

    assert flag == "ZERO_BASE"


def test_turnaround():

    value, flag = (
        CAGRCalculator.calculate(
            -100,
            100,
            5
        )
    )

    assert flag == "TURNAROUND"


def test_decline_to_loss():

    value, flag = (
        CAGRCalculator.calculate(
            100,
            -100,
            5
        )
    )

    assert flag == "DECLINE_TO_LOSS"


def test_both_negative():

    value, flag = (
        CAGRCalculator.calculate(
            -100,
            -50,
            5
        )
    )

    assert flag == "BOTH_NEGATIVE"