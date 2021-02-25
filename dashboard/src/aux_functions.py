"""Supporting functions for dash app."""

import pandas as pd

from src.db_functions import get_tickers_per_date_hour


def get_dash_dataframe():
    """Get data from database and convert to pandas dataframe."""
    data = get_tickers_per_date_hour()
    columns = ["ticker", "company_name", "total_count", 
               "total_score", "date", "hour"]
    df = pd.DataFrame(data, columns=columns)
    df["date_hour"] = pd.to_datetime(df["date"]) + pd.to_timedelta(df["hour"], unit='h')
    return df


def get_dropdown_tickers(dash_df):
    """Get top 10 most mentioned tickers."""
    top_10_tickers = dash_df.groupby(["ticker"])["total_count"].sum().nlargest(10).reset_index()      
    return top_10_tickers.ticker.unique()


def get_dash_data():
    """Get dash data."""
    df = get_dash_dataframe()
    tickers = get_dropdown_tickers(df)
    return df, tickers