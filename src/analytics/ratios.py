import pandas as pd


class RatioEngine:

    @staticmethod
    def net_profit_margin(
        net_profit,
        sales
    ):

        if sales == 0:
            return None

        return (
            net_profit / sales
        ) * 100

    @staticmethod
    def operating_profit_margin(
        operating_profit,
        sales
    ):

        if sales == 0:
            return None

        return (
            operating_profit / sales
        ) * 100

    @staticmethod
    def roe(
        net_profit,
        equity_capital,
        reserves
    ):

        equity = (
            equity_capital +
            reserves
        )

        if equity <= 0:
            return None

        return (
            net_profit / equity
        ) * 100

    @staticmethod
    def roce(
        ebit,
        equity_capital,
        reserves,
        borrowings
    ):

        capital = (
            equity_capital +
            reserves +
            borrowings
        )

        if capital <= 0:
            return None

        return (
            ebit / capital
        ) * 100

    @staticmethod
    def roa(
        net_profit,
        total_assets
    ):

        if total_assets == 0:
            return None

        return (
            net_profit /
            total_assets
        ) * 100

    @staticmethod
    def debt_to_equity(
        borrowings,
        equity_capital,
        reserves
    ):

        if borrowings == 0:
            return 0

        equity = (
            equity_capital +
            reserves
        )

        if equity <= 0:
            return None

        return (
            borrowings /
            equity
        )

    @staticmethod
    def interest_coverage(
        operating_profit,
        other_income,
        interest
    ):

        if interest == 0:
            return None

        return (
            operating_profit +
            other_income
        ) / interest

    @staticmethod
    def asset_turnover(
        sales,
        total_assets
    ):

        if total_assets == 0:
            return None

        return (
            sales /
            total_assets
        )