"""Loads data from a CSV file into a remote Postgres database instance efficiently with `COPY`
"""
import psycopg2
from pydantic import BaseModel
from pathlib import Path


class DBC(BaseModel):
    """ Database Configuration ('DBC')
    """
    dbname: str
    user: str
    password: str
    host: str = "localhost"
    port: int = 5432


def open_connection(
    dbc: DBC
):
    """Open connection to Postgres database.

    :param dbname: name of database (see `container_name` property)
    :param user: username of service account (typically 'postgres')
    :param password: password of service account (see `POSTGRES_PASSWORD_FILE` property)
    :param host: address of database instance, defaults to "localhost"
    :param port: port on which the database listens for incoming connections, defaults to 5432
    :return: a connection object
    """
    conn_params = { 
        "dbname": dbc.dbname, 
        "user": dbc.user, 
        "password": dbc.password, 
        "host": dbc.host, 
        "port": str(dbc.port)
    }
    return psycopg2.connect(**conn_params)


def nytas_load(
    conn,
    source_path: Path
) -> None:
    """Loads data extracted from the New York Times Archive into Postgres.

    :param conn: connection inherited from `psycopg2`
    :param source_path: path to CSV file for upload
    :return: null
    """
    with conn.cursor() as cursor, open(source_path, "r") as staged_csv:
        bulk_insert = """
                        COPY raw.nyt (
                            headline, 
                            publication_date, 
                            author,
                            news_desk,
                            url
                        ) FROM STDIN WITH (FORMAT csv, DELIMITER '|', HEADER true);
                      """
        cursor.copy_expert(bulk_insert, staged_csv)


if __name__ == "__main__":
    pass
    
