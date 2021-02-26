"""Main data collector and db updater for project."""

import time

from src.database.models import create_db
from src.aux_functions import get_config_section
from src.iex_collector import IEXCollector
from src.reddit_collector import RedditCollector


def get_ticker_data():
    """Collect tickers from IEX Cloud """
    # call iex api and get valid list of tickers
    config = get_config_section("iexfinance")
    iex = IEXCollector(**config)
    iex.update_database()

    # call iex api to get prices
    # iex.update_prices()
    # TODO!


def main():
    """Main data collection function."""
    # create database
    create_db()

    # ticker data
    get_ticker_data()

    # create reddit object
    config = get_config_section("reddit")
    reddit = RedditCollector(**config)

    # update data every with 5min sleep
    while True:
        reddit.get_new_data(subreddit_name="wallstreetbets",
                            subreddit_params={
                                "subreddit_sorting": "hot",
                                "limit": 1
                                },
                            comment_params={
                                "limit": 1
                                }
                            )
        timer_min = 1
        print(f"Waiting for next call: {timer_min} min.")
        time.sleep(60*timer_min)


if __name__ == "__main__":
    print("Running data-collector...")
    main()


# def get_app_data():
#     """Get data from db for visualizations."""
#     data = get_dash_data()
#     columns = ["name", "ticker", "count", "score", "datetime", "date_hour"]
#     df = pd.DataFrame(data, columns=columns)
#     top_10_tickers = df.groupby(["ticker"])["name"].count().nlargest(10).reset_index()
#     tickers = top_10_tickers.ticker.unique()
#     return df, tickers
