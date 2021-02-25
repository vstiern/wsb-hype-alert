"""All inserts to db."""

import psycopg2

from src.database.models import get_db_connection


def insert_tickers(ticker_list):
    """
    Insert multiple new tickers to table.

    Args:
    :ticker_list: [(ticker_id, company_name, )]
    """
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO ticker (ticker_id, company_name)
        VALUES(%s, %s);
    """
    try:
        cur.executemany(sql, ticker_list)
        conn.commit()
    except Exception as e:
        print(f"Couldn't insert control tickers. Error: {e}")
        conn.rollback()
    cur.close()
    conn.close()


def insert_closing_price(price_list):
    """
    Insert multiple new prices to table.

    Args:
    :price_list: [(close_price, timestamp, )]
    """
    # TODO


def insert_source(source):
    """
    Insert single new source to table.

    Args:
    :source: string with name of source
    """
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO source (source)
        VALUES(%s);
    """
    try:
        try:
            cur.execute(sql, (source, ))
            conn.commit()
        # Exception for duplicate record
        except psycopg2.IntegrityError:
            conn.rollback()
    except Exception as e:
        print(f"Couldn't insert new source. Error: {e}")
        conn.rollback()
    cur.close()
    conn.close()


def insert_author(author_id):
    """
    Insert single new author to table.

    Args:
    :author_id: string with id of author
    """
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO author (author_id)
        VALUES(%s);
    """
    try:
        try:
            cur.execute(sql, (author_id, ))
            conn.commit()
        # Exception for duplicate record
        except psycopg2.IntegrityError:
            conn.rollback()
    except Exception as e:
        print(f"Couldn't insert new author. Error: {e}")
        conn.rollback()
    cur.close()
    conn.close()


def insert_submission(submission_id, timestamp, score,
                      nr_comments, author_id, source):
    """
    Insert single new submission to table.
    Provide following datapoints of submission:

    Args:
    :submission_id: string with id
    :timestamp: timestamp UTC
    :score: int with score
    :nr_comments: int with nr_comments
    :author_id: string with author_id
    :source: string with source
    """
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO submission (submission_id, timestamp, score,
                                nr_comments, author_id, source_id)
        VALUES(%s, %s, %s, %s, %s,
            (SELECT source_id from source where source = %s));
    """
    try:
        try:
            cur.execute(sql, (submission_id, timestamp, score,
                              nr_comments, author_id, source, ))
            conn.commit()
        # Exception for duplicate record
        except psycopg2.IntegrityError:
            conn.rollback()
    except Exception as e:
        print(f"Couldn't insert new submission. Error: {e}")
        conn.rollback()
    cur.close()
    conn.close()


def insert_comment(comment_id, timestamp, score, submission_id, author_id):
    """
    Insert single new comment to table.
    Provide following datapoints of comment:

    Args:
    :comment_id: string with comment_id
    :timestamp: timestamp UTC
    :score: int with score
    :submission_id: string with submission_id
    :author_id: string with author_id
    """
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO comment (comment_id, timestamp, score, submission_id, author_id)
        VALUES(%s, %s, %s, %s, %s);
    """
    try:
        try:
            cur.execute(sql, (comment_id, timestamp, score, submission_id, author_id, ))
            conn.commit()
        # Exception for duplicate record
        except psycopg2.IntegrityError:
            conn.rollback()
    except Exception as e:
        print(f"Couldn't insert new comment. Error: {e}")
        conn.rollback()
    cur.close()
    conn.close()


def insert_ticker_mention(ticker, comment_id):
    """
    Insert single new comment to table.
    Provide following datapoints of comment:

    Args:
    :ticker: string with ticker
    :comment_id: string with comment_id
    """
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO ticker_mention (ticker_id, comment_id)
        VALUES(%s, %s);
    """
    try:
        try:
            cur.execute(sql, (ticker, comment_id, ))
            conn.commit()
        # Exception for duplicate record
        except psycopg2.IntegrityError:
            conn.rollback()
    except Exception as e:
        print(f"Couldn't insert new comment. Error: {e}")
        conn.rollback()
    cur.close()
    conn.close()
