"""All db models for the project."""

import psycopg2

from src.aux_functions import get_config_section


def get_db_connection():
    """
    Connecto to database connection to a PostgreSQL database.
    :return: Connection object or None
    """
    # open config file
    config = get_config_section("postgres")
    conn = None
    try:
        conn = psycopg2.connect(**config)       # connect to server
    except (psycopg2.DatabaseError) as error:
        print(f"Couldn't connect to database. Error: {error}")
    return conn


def create_table(sql):
    """Create a postgres table."""
    conn = get_db_connection()      # connection
    cur = conn.cursor()             # get cursor
    cur.execute(sql)                # execution
    cur.close()                     # close communication
    conn.commit()                   # commit the changes


def set_timezone():
    """Set UTC timezone for database."""
    conn = get_db_connection()              # connection
    cur = conn.cursor()                     # get cursor
    cur.execute("SET timezone = 'UTC';")   # execution
    cur.close()                             # close communication
    conn.commit()                           # commit the changes


def create_ticker_table():
    """
    Create ticker control table.
    """
    sql = """
    CREATE TABLE IF NOT EXISTS ticker (
        ticker_id VARCHAR(10) PRIMARY KEY,
        company_name VARCHAR(200) NOT NULL
    );
    """
    return create_table(sql)


def create_price_table():
    """Create ticker price table. Unique price per ticker and timestamp."""
    sql = """
    CREATE TABLE IF NOT EXISTS price (
        price_id INT PRIMARY KEY,
        ticker_id VARCHAR(10),
        close_price NUMERIC(4) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        CONSTRAINT fk_ticker_id
            FOREIGN KEY(ticker_id)
                REFERENCES ticker(ticker_id)
    );
    """
    return create_table(sql)


def create_source_table():
    """
    Create source table i.e. r/wallstreetbets, twitter.
    """
    sql = """
    CREATE TABLE IF NOT EXISTS source (
        source_id SERIAL PRIMARY KEY,
        source VARCHAR(200) NOT NULL,
        UNIQUE (source)
    );
    """
    return create_table(sql)


def create_author_table():
    """Create author/user name table. Can be"""
    sql = """
    CREATE TABLE IF NOT EXISTS author (
        author_id VARCHAR(20) PRIMARY KEY
    );
    """
    return create_table(sql)


def create_submission_table():
    """Create submission table i.e. original reddit submission/post."""
    sql = """
    CREATE TABLE IF NOT EXISTS submission (
        submission_id VARCHAR(20) PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL,
        score INT NOT NULL,
        nr_comments INT NOT NULL,
        author_id VARCHAR(20),
        source_id SERIAL,
        CONSTRAINT fk_submission_author_id
            FOREIGN KEY(author_id)
                REFERENCES author(author_id),
        CONSTRAINT fk_source
            FOREIGN KEY(source_id)
                REFERENCES source(source_id)
    );
    """
    return create_table(sql)


def create_comment_table():
    """Create reddit comment table i.e. comment to a reddit submission."""
    sql = """
    CREATE TABLE IF NOT EXISTS comment (
        comment_id VARCHAR(20) PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL,
        score INT NOT NULL,
        author_id VARCHAR(20),
        submission_id VARCHAR(20),
        CONSTRAINT fk_comment_author_id
            FOREIGN KEY(author_id)
                REFERENCES author(author_id),
        CONSTRAINT fk_submission_id
            FOREIGN KEY(submission_id)
                REFERENCES submission(submission_id)
    );
    """
    return create_table(sql)


def create_ticker_mention_table():
    """
    Create table that track all ticker mentions from comments.
    Only allow one record per combination of ticker and comment_id.
    """
    sql = """
    CREATE TABLE IF NOT EXISTS ticker_mention (
        mention_id SERIAL PRIMARY KEY,
        ticker_id VARCHAR(10),
        comment_id VARCHAR(20),
        CONSTRAINT fk_ticker_id
            FOREIGN KEY(ticker_id)
                REFERENCES ticker(ticker_id),
        CONSTRAINT fk_comment_id
            FOREIGN KEY(comment_id)
                REFERENCES comment(comment_id),
        UNIQUE (ticker_id, comment_id)
    );
    """
    return create_table(sql)


def create_db():
    """Create all tables if not already exists."""
    set_timezone()
    create_ticker_table()
    create_price_table()
    create_source_table()
    create_author_table()
    create_submission_table()
    create_comment_table()
    create_ticker_mention_table()


def drop_table():
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """DROP TABLE ticker_mentions;"""
    cur.execute(sql)
