import pandas as pd

from src.etl.normaliser import (
    normalize_ticker,
    normalize_year
)


# ---------------------------
# normalize_ticker tests
# ---------------------------

def test_ticker_uppercase():
    df = pd.DataFrame({"id": ["tcs"]})
    result = normalize_ticker(df)
    assert result["id"][0] == "TCS"


def test_ticker_strip_spaces():
    df = pd.DataFrame({"id": ["  tcs  "]})
    result = normalize_ticker(df)
    assert result["id"][0] == "TCS"


def test_ticker_already_upper():
    df = pd.DataFrame({"id": ["INFY"]})
    result = normalize_ticker(df)
    assert result["id"][0] == "INFY"


def test_ticker_mixed_case():
    df = pd.DataFrame({"id": ["InFy"]})
    result = normalize_ticker(df)
    assert result["id"][0] == "INFY"


def test_ticker_numeric_string():
    df = pd.DataFrame({"id": ["123"]})
    result = normalize_ticker(df)
    assert result["id"][0] == "123"


def test_ticker_single_letter():
    df = pd.DataFrame({"id": ["a"]})
    result = normalize_ticker(df)
    assert result["id"][0] == "A"


def test_ticker_empty_string():
    df = pd.DataFrame({"id": [""]})
    result = normalize_ticker(df)
    assert result["id"][0] == ""


def test_ticker_special_characters():
    df = pd.DataFrame({"id": ["abc-1"]})
    result = normalize_ticker(df)
    assert result["id"][0] == "ABC-1"


def test_ticker_multiple_rows():
    df = pd.DataFrame({"id": ["tcs", "infy"]})
    result = normalize_ticker(df)
    assert list(result["id"]) == ["TCS", "INFY"]


def test_ticker_nan_string():
    df = pd.DataFrame({"id": [None]})
    result = normalize_ticker(df)
    assert pd.isna(result["id"][0])


def test_ticker_custom_column():
    df = pd.DataFrame({"company_id": ["tcs"]})
    result = normalize_ticker(df, column="company_id")
    assert result["company_id"][0] == "TCS"


def test_ticker_missing_column():
    df = pd.DataFrame({"x": ["tcs"]})
    result = normalize_ticker(df)
    assert "x" in result.columns


def test_ticker_whitespace_only():
    df = pd.DataFrame({"id": ["   "]})
    result = normalize_ticker(df)
    assert result["id"][0] == ""


def test_ticker_long_value():
    df = pd.DataFrame({"id": ["adanienterprises"]})
    result = normalize_ticker(df)
    assert result["id"][0] == "ADANIENTERPRISES"


def test_ticker_duplicate_values():
    df = pd.DataFrame({"id": ["tcs", "tcs"]})
    result = normalize_ticker(df)
    assert result["id"].nunique() == 1


# ---------------------------
# normalize_year tests
# ---------------------------

def test_year_string():
    df = pd.DataFrame({"year": ["2023"]})
    result = normalize_year(df)
    assert result["year"][0] == "2023"


def test_year_integer():
    df = pd.DataFrame({"year": [2023]})
    result = normalize_year(df)
    assert result["year"][0] == "2023"


def test_year_strip_spaces():
    df = pd.DataFrame({"year": [" 2023 "]})
    result = normalize_year(df)
    assert result["year"][0] == "2023"


def test_year_multiple_rows():
    df = pd.DataFrame({"year": [2022, 2023]})
    result = normalize_year(df)
    assert list(result["year"]) == ["2022", "2023"]


def test_year_empty():
    df = pd.DataFrame({"year": [""]})
    result = normalize_year(df)
    assert result["year"][0] == ""


def test_year_none():
    df = pd.DataFrame({"year": [None]})
    result = normalize_year(df)
    assert pd.isna(result["year"][0])


def test_year_custom_column():
    df = pd.DataFrame({"fiscal_year": [2024]})
    result = normalize_year(df, column="fiscal_year")
    assert result["fiscal_year"][0] == "2024"


def test_year_missing_column():
    df = pd.DataFrame({"x": [2024]})
    result = normalize_year(df)
    assert "x" in result.columns


def test_year_float():
    df = pd.DataFrame({"year": [2024.0]})
    result = normalize_year(df)
    assert result["year"][0] == "2024.0"


def test_year_long_string():
    df = pd.DataFrame({"year": ["FY2024"]})
    result = normalize_year(df)
    assert result["year"][0] == "FY2024"


def test_year_zero():
    df = pd.DataFrame({"year": [0]})
    result = normalize_year(df)
    assert result["year"][0] == "0"


def test_year_negative():
    df = pd.DataFrame({"year": [-1]})
    result = normalize_year(df)
    assert result["year"][0] == "-1"


def test_year_duplicate():
    df = pd.DataFrame({"year": [2023, 2023]})
    result = normalize_year(df)
    assert len(result) == 2


def test_year_already_clean():
    df = pd.DataFrame({"year": ["2022"]})
    result = normalize_year(df)
    assert result["year"][0] == "2022"


def test_year_with_tabs():
    df = pd.DataFrame({"year": ["\t2022\t"]})
    result = normalize_year(df)
    assert result["year"][0] == "2022"


def test_year_with_newline():
    df = pd.DataFrame({"year": ["\n2022\n"]})
    result = normalize_year(df)
    assert result["year"][0] == "2022"


def test_year_text():
    df = pd.DataFrame({"year": ["current"]})
    result = normalize_year(df)
    assert result["year"][0] == "current"


def test_year_dataframe_shape():
    df = pd.DataFrame({"year": [2020, 2021, 2022]})
    result = normalize_year(df)
    assert result.shape[0] == 3


def test_year_preserves_column():
    df = pd.DataFrame({"year": [2020]})
    result = normalize_year(df)
    assert "year" in result.columns


def test_year_returns_dataframe():
    df = pd.DataFrame({"year": [2020]})
    result = normalize_year(df)
    assert isinstance(result, pd.DataFrame)