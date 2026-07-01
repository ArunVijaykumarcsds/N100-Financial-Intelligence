from analytics.cagr import CAGRCalculator


def get_5yr_cagr(series):

    series = series.dropna()

    if len(series) < 6:
        return None

    start_value = series.iloc[0]
    end_value = series.iloc[-1]

    cagr, flag = CAGRCalculator.calculate(
        start_value,
        end_value,
        5
    )

    return cagr