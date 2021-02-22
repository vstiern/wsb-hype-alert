"""IEX Finance API"""
import pandas as pd
from iexfinance.refdata import get_symbols
from iexfinance.stocks import get_historical_intraday

from src.db_functions import (count_current_tickers, insert_control_tickers, 
                              insert_ticker_prices, get_dates_for_top10_mentioned_tickers)


class IEXFinance:
    """Class to handle all api calls from IEX Fianance."""
    def __init__(self, token):
        self.token = token
        
    def check_database(self):
        """Check ticker control table if already populated."""
        if count_current_tickers() < 1:
            return False
        else:
            return True
    
    def get_all_tickers(self):
        """Get all tickers from IEX."""
        all_symbols = get_symbols(token=self.token)
        return all_symbols[["symbol", "name"]]

    def update_database(self):
        """Call api if databse is empty and insert values."""
        updates = 0
        if self.check_database() is False:
            ticker_data = self.get_all_tickers()
            for _, row in ticker_data.iterrows():
                updates += insert_control_tickers(ticker=row["symbol"], name=row["name"])
                if updates % 100 == 0:
                    print(f"Updating control tickers. Updates: {updates}")
            print(f"Ticker table updated. Available tickers: {updates}")
        else:
            print("Ticker table already populated.")

    def update_prices(self):
        """Call api to get closing prices for top10 mentioned tickers."""
        data = get_dates_for_top10_mentioned_tickers()
        tickers = pd.DataFrame(data, columns=["ticker", "date"])
        for _, t_row in tickers.iterrows():
            try:
                prices = self.get_historical_intraday(**t_row)
                for p_ts, p_row in prices.iterrows():
                    insert_ticker_prices(t_row["ticker"], p_ts, p_row["close"])
            except Exception as e:
                print(f"Couldn't get intraday prices for ticker: {t_row['ticker']}. Error: {e}")
                continue

    def get_historical_data(self, ticker, date):
        """Get historical price data for ticker for date range."""
        return get_historical_data(ticker, date, output_format='pandas', token=self.token)


    