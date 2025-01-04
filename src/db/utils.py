"""Dedicated module which contains connectivity logic for the remote Postgres database.
"""
import psycopg2
import tempfile
import pandas as pd
import logging

from psycopg2 import sql
from psycopg2.errors import OperationalError


logger = logging.getLogger(__name__)


def open_connection(
    dbname: str,
    user: str,
    password: str,
    host: str = "publications-db",
    port: int = 5432
):
    """Open connection to Postgres database.

    :param dbname: name of database (see `container_name` property)
    :param user: username of service account (typically 'postgres')
    :param password: password of service account (see `POSTGRES_PASSWORD_FILE` property)
    :param host: address of database instance, defaults to "localhost"
    :param port: port on which the database listens for incoming connections, defaults to 5432
    :return: a connection object
    """
    conn = None
    try:
        conn_params = { 
            "dbname": dbname, 
            "user": user, 
            "password": password, 
            "host": host, 
            "port": str(port)
        }
        conn = psycopg2.connect(**conn_params)
    except OperationalError as e:
        logging.error(f"Connectivity could not be established to DWH: '{str(e)}'")
    return conn


def read_sql(
    conn, 
    query: str | sql.SQL
) -> pd.DataFrame:
    """Efficiently download the results of a 'SELECT' `query` into a `pd.DataFrame`
    object located in working memory. 

    :param conn: a connection object (inherited from `psycopg2`)
    :param query: `SELECT` query on Postgres instance
    :return: a dataframe object mirroring the result of the `SELECT` query
    """
    with tempfile.TemporaryFile() as tmpfile, conn.cursor() as cursor:
        bulk_download = sql.SQL("COPY ({}) TO STDOUT WITH CSV HEADER").format(query)
        cursor.copy_expert(bulk_download, tmpfile)
        tmpfile.seek(0) # NB: 'rewinds' the file handle to point '0' post Postgres 'COPY'
        df = pd.read_csv(tmpfile)
        return df


if __name__ == "__main__":
    
    open_connection(
        'publications',
        'adopajwd',
        'adkaworkwa',
        'localhost'
    )