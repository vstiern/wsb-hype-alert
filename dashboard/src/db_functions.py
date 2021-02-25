"""All database quires."""

import psycopg2
from configparser import ConfigParser
from pathlib import Path


# read file
def get_config_section(section, file_name="config.ini"):
    """
    Parse config file.

    :param section_name: Section header name as string.
    :param file_name: File name of config file. Defualt name provided.
    :return: Dictionary with config name as keys and config value as value.
    """
    # create parser
    parser = ConfigParser()
    file_path = Path(__file__).parent.parent
    parser.read(file_path / file_name)
    config_dict = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config_dict[param[0]] = param[1]
    else:
        raise Exception(f'Section: {section} not found in the {file_name}')
    return config_dict


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


def get_tickers_per_date_hour():
    """
    Get main data for dashboard. 
    Groupby by ticker_id, date and hour.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    SELECT
        t.ticker_id,
        t.company_name,
        COUNT(tm.ticker_id) as total_count,
        SUM(c.score) as total_score,
        (c.timestamp AT TIME ZONE 'Europe/Stockholm')::date as comment_date,
        EXTRACT(hour FROM c.timestamp AT TIME ZONE 'Europe/Stockholm') as comment_hour
    FROM 
        ticker_mention tm
    INNER JOIN 
        comment c USING(comment_id)
    INNER JOIN 
        ticker t USING(ticker_id)
    GROUP BY
        t.ticker_id,
        (c.timestamp AT TIME ZONE 'Europe/Stockholm')::date,
        EXTRACT(hour FROM c.timestamp AT TIME ZONE 'Europe/Stockholm')
    ORDER BY
        COUNT(tm.ticker_id),
        t.ticker_id
    ;
    """
    cur.execute(sql)
    return cur.fetchall()