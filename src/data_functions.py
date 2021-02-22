"""All functions collecting and updating data for project."""

import pandas as pd

from src.aux_functions import get_config_section
from src.db_functions import create_db, get_dash_data
from src.iex_api import IEXFinance
from src.reddit_api import RedditCollector


def cold_start_initization():
    """Main function for ticker mentions analysis."""
    # get config file
    config = get_config_section()

    # create tables
    create_db()

    # call iex api and get valid list of tickers
    iex = IEXFinance(config["iexfinance"]["token"])
    iex.update_database()

    # call reddit api and get ticker mention data
    reddit = RedditCollector(**config["reddit"])
    reddit.update_data(subreddit="wallstreetbets", page_sorting="hot", 
                       submission_limit=int(config["reddit-limits"]["cold_start_submission_limit"]), 
                       comment_limit=int(config["reddit-limits"]["cold_start_comment_limit"]))

    # call iex api to get prices for top 10 mention tickers for each available date
    # api not responding ...
    # iex.update_prices()
    return True

def get_new_reddit_data():
    """Get new reddit data."""
    # get config file
    config = get_config_section()

    # call reddit api and get ticker mention data
    reddit = RedditCollector(**config["reddit"])
    reddit.update_new_data(subreddit="wallstreetbets",
                           submission_limit=int(config["reddit-limits"]["new_data_submission_limit"]), 
                           comment_limit=int(config["reddit-limits"]["new_data_submission_limit"]))
    return True


def get_app_data():
    """Get data from db for visualizations."""
    data = get_dash_data()
    columns = ["name", "ticker", "count", "score", "datetime", "date_hour"]
    df = pd.DataFrame(data, columns=columns)
    top_10_tickers = df.groupby(["ticker"])["name"].count().nlargest(10).reset_index()      # get top 10 mentioned tickers
    tickers = top_10_tickers.ticker.unique()
    return df, tickers