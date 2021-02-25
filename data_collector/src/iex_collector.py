"""IEX Cloud api data collector using IEXFinance SDK"""

from iexfinance.refdata import get_symbols
# from iexfinance.stocks import get_historical_intraday

from src.database.queries import count_current_tickers
from src.database.inserts import insert_tickers


class IEXCollector:
    """Class to handle all api calls from IEX Fianance."""
    def __init__(self, token):
        print("Connecting to IEX Cloud...")
        self.token = token

    def check_database(self):
        """Check ticker control table if already populated."""
        if count_current_tickers() < 1:
            return False
        else:
            return True

    def get_all_tickers(self):
        """Get all tickers from IEX."""
        print("Calling ticker data from IEX Cloud...")
        all_symbols = get_symbols(token=self.token)
        return all_symbols[["symbol", "name"]]

    def convert_df_to_tuples(self, df):
        """Convert df to list of tuples for postgres executemany."""
        return [tuple(x) for x in df.to_numpy()]

    def update_database(self):
        """Call api if databse is empty and insert values."""
        if self.check_database() is False:
            ticker_data = self.get_all_tickers()
            ticker_db_format = self.convert_df_to_tuples(ticker_data)
            insert_tickers(ticker_db_format)
            print(f"Ticker table updated. Available tickers: {len(ticker_data)}")
        else:
            print("Ticker table already populated.")
