import pandas as pd


class CAGRCalculator:

    @staticmethod
    def calculate(
        start_value,
        end_value,
        years
    ):

        if years <= 0:
            return None, "INVALID"

        if start_value == 0:
            return None, "ZERO_BASE"

        if start_value > 0 and end_value < 0:
            return None, "DECLINE_TO_LOSS"

        if start_value < 0 and end_value > 0:
            return None, "TURNAROUND"

        if start_value < 0 and end_value < 0:
            return None, "BOTH_NEGATIVE"

        cagr = (
            (
                end_value /
                start_value
            )
            ** (1 / years)
            - 1
        ) * 100

        return cagr, "OK"