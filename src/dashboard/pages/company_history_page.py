import sqlite3
import pandas as pd
import plotly.express as px

DB_PATH = "db/nifty100.db"


def get_companies():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT DISTINCT id
    FROM companies
    ORDER BY id
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df["id"].tolist()


def get_company_history(company_id):

    conn = sqlite3.connect(DB_PATH)

    query = f"""
    SELECT
        year,
        sales,
        net_profit,
        eps
    FROM profit_loss
    WHERE company_id = '{company_id}'
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df

