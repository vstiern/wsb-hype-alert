"""All database quires."""

from src.database.models import get_db_connection


def count_current_tickers():
    """Count number of ticker in table."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT count(ticker_id) from ticker;
    """
    cur.execute(sql)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def get_all_control_tickers():
    """Get list of all valid tickers."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT ticker_id from ticker;
    """
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return [t[0] for t in result]


def check_for_existing_mentioned(ticker, comment_id):
    """Check if ticker mentioned is already recorded in db."""


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
        strftime('%Y-%m-%d %H',
                    datetime(ticker_mentions.timestamp,  'unixepoch'))
    FROM
        ticker_mentions
    INNER JOIN
        ticker_control on ticker_control.ticker = ticker_mentions.ticker
    GROUP BY
        ticker_mentions.ticker,
        strftime('%Y-%m-%d %H',
                    datetime(ticker_mentions.timestamp,  'unixepoch'))
    ORDER BY
        count(ticker_mentions.mention_id) DESC,
        ticker_mentions.ticker;
    """
    cur.execute(sql)
    return cur.fetchall()


def get_all_submission_ids():
    """Get all unique submission ids."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT submission_id from submission;
    """
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return [id[0] for id in result]


def get_most_recent_submission():
    """Get most recent submission id."""
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT submission_id
    FROM submission
    WHERE timestamp = (SELECT max(timestamp) FROM submission);
    """
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return [id[0] for id in result]
