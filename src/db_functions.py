"""All db related functions."""
import sqlite3

from src.aux_functions import get_config_section


def get_db_connection():
    """
    Connecto to database connection to a SQLite database.     
    :return: Connection object or None
    """
    # open config file
    config = get_config_section()

    conn = None
    try:
        conn = sqlite3.connect(config["sqlite"]["db_file"])
        return conn
    except Exception as e:
        print(f"Couldn't connect to database. Error: {e}")
    return conn


def create_ticker_control_table():
    """Create ticker control table."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS ticker_control (
        id integer PRIMARY KEY,
        ticker text NOT NULL,
        name text NOT NULL
        );
    """
    cur.execute(sql)


def create_ticker_mentions_table():
    """Create ticker control table."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS ticker_mentions (
        mention_id text PRIMARY KEY,
        submission_id text NOT NULL,
        submission_timestamp text NOT NULL,
        comment_id text NOT NULL,
        author_id text NOT NULL,
        timestamp text NOT NULL,
        score integer NOT NULL,
        source text NOT NULL,
        ticker text NOT NULL,
        FOREIGN KEY (ticker) REFERENCES ticker_control (ticker)
        );
    """
    cur.execute(sql)


def create_ticker_price_table():
    """Create ticker price table."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS ticker_prices (
        id integer PRIMARY KEY,
        ticker text NOT NULL,
        date text NOT NULL,
        close_price real NOT NULL,
        FOREIGN KEY (ticker) REFERENCES ticker_control (ticker)
        );
    """
    cur.execute(sql)


def create_db():
    """Create all tables if not already exists."""
    create_ticker_control_table()
    create_ticker_mentions_table()
    create_ticker_price_table()


def count_current_tickers():
    """Count number of ticker in table."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT count(ticker) from ticker_control;
    """
    cur.execute(sql)
    return cur.fetchone()[0]


def get_all_control_tickers():
    """Get ticker control table and get all valid tickers."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT ticker from ticker_control;
    """
    cur.execute(sql)
    result = cur.fetchall()
    return [t[0] for t in result]


def get_all_mention_ids():
    """Get all unique submission ids from ticker mentions."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT mention_id from ticker_mentions;
    """
    cur.execute(sql)
    result = cur.fetchall()
    return [id[0] for id in result]


def get_most_recent_submission():
    """Get most recent submission id."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT submission_id 
    FROM ticker_mentions
    WHERE submission_timestamp = (SELECT max(submission_timestamp) FROM ticker_mentions);
    """
    cur.execute(sql)
    result = cur.fetchall()
    return [id[0] for id in result]


def insert_control_tickers(ticker, name):
    """Insert new control tickers."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO ticker_control (ticker, name)
        VALUES (?, ?);
    """
    cur.execute(sql, (ticker, name))
    try:
        conn.commit()
        return 1
    except Exception as e:
        print(f"Couldn't insert control tickers. Error: {e}")
        conn.rollback()
        return 0


def insert_ticker_mentions(mention_id, submission_id, submission_timestamp, comment_id, 
                           author_id, timestamp, score, source, ticker):
    """Insert new ticker mentions."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO ticker_mentions (mention_id, submission_id, submission_timestamp, comment_id, 
                                     author_id, timestamp, score, source, ticker)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    try:
        cur.execute(sql, (mention_id, submission_id, submission_timestamp, comment_id, 
                          author_id, timestamp, score, source, ticker))
        conn.commit()
        return 1
    except Exception as e:
        print(f"Couldn't insert new ticker mentions. Error: {e}")
        conn.rollback()
        return 0


def insert_ticker_prices(ticker, date, price):
    """Insert new ticker price."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO ticker_prices (ticker, date, price)
        VALUES (?, ?, ?);
    """
    try:
        cur.execute(sql, (ticker, date, price))
        conn.commit()
        return 1
    except Exception as e:
        print(f"Couldn't insert new ticker price. Error: {e}")
        conn.rollback()
        return 0


def get_dates_for_top10_mentioned_tickers():
    """Get 10top mentioned tickers for each available date."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT 
        ticker_mentions.ticker, 
        date(ticker_mentions.timestamp,  'unixepoch')
    FROM 
        ticker_mentions
    GROUP BY
        ticker_mentions.ticker
    ORDER BY 
        count(ticker_mentions.mention_id) DESC
    LIMIT 10;
    """
    cur.execute(sql)
    return cur.fetchall()


def get_dash_data():
    """Get all data for dash app."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT 
        ticker_control.name, 
        ticker_mentions.ticker, 
        count(ticker_mentions.mention_id) as count,
        sum(ticker_mentions.score) as score,
        datetime(ticker_mentions.timestamp, 'unixepoch'),
        strftime('%Y-%m-%d %H', datetime(ticker_mentions.timestamp,  'unixepoch'))
    FROM 
        ticker_mentions
    INNER JOIN 
        ticker_control on ticker_control.ticker = ticker_mentions.ticker 
    GROUP BY
        ticker_mentions.ticker, 
        strftime('%Y-%m-%d %H', datetime(ticker_mentions.timestamp,  'unixepoch'))
    ORDER BY 
        count(ticker_mentions.mention_id) DESC,
        ticker_mentions.ticker;
    """
    cur.execute(sql)
    return cur.fetchall()


def drop_table():
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """DROP TABLE ticker_mentions;"""
    cur.execute(sql)