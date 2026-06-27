class CashFlowKPIs:

    @staticmethod
    def free_cash_flow(
        operating_activity,
        investing_activity
    ):

        return (
            operating_activity +
            investing_activity
        )

    @staticmethod
    def cfo_quality_score(
        operating_activity,
        net_profit
    ):

        if net_profit == 0:
            return None

        ratio = (
            operating_activity /
            net_profit
        )

        if ratio > 1:

            return "High Quality"

        elif ratio >= 0.5:

            return "Moderate"

        else:

            return "Accrual Risk"

    @staticmethod
    def capex_intensity(
        investing_activity,
        sales
    ):

        if sales == 0:
            return None

        ratio = (
            abs(investing_activity)
            / sales
        ) * 100

        if ratio < 3:

            return "Asset Light"

        elif ratio <= 8:

            return "Moderate"

        else:

            return (
                "Capital Intensive"
            )

    @staticmethod
    def fcf_conversion(
        free_cash_flow,
        operating_profit
    ):

        if operating_profit == 0:
            return None

        return (
            free_cash_flow /
            operating_profit
        ) * 100

    @staticmethod
    def capital_allocation_pattern(
        cfo,
        cfi,
        cff
    ):

        signs = (
            "+" if cfo > 0 else "-",
            "+" if cfi > 0 else "-",
            "+" if cff > 0 else "-"
        )

        patterns = {

            ("+", "-", "-"):
                "Reinvestor",

            ("+", "+", "-"):
                "Liquidating Assets",

            ("-", "+", "+"):
                "Distress Signal",

            ("-", "-", "+"):
                "Growth Funded By Debt",

            ("+", "+", "+"):
                "Cash Accumulator",

            ("-", "-", "-"):
                "Pre-Revenue",

            ("+", "-", "+"):
                "Mixed"
        }

        return patterns.get(
            signs,
            "Unknown"
        )