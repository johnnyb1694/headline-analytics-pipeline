"""Loads data from a CSV file into a remote Postgres database instance efficiently with `COPY`
"""
import psycopg2
import os
from pathlib import Path
from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)


def construct_copy_statement(
    schema: str,
    table: str,
    columns: list
) -> sql.SQL:
    """Constructs the copy statement for efficient loading of CSV into Postgres using
    safe query interpolation.
    """
    # Construct the columns part of the SQL query safely
    columns_sql = sql.SQL(', ').join(map(sql.Identifier, columns))
    bulk_insert = sql.SQL(
        """
            COPY {}.{} ({})
            FROM STDIN WITH (FORMAT csv, DELIMITER '|', HEADER true);
        """).format(
        sql.Identifier(schema),
        sql.Identifier(table),
        columns_sql
    )
    return bulk_insert


def ingest(
    conn,
    schema: str,
    table: str,
    columns: list,
    source_path: Path
) -> None:
    """Loads data extracted in a CSV format into Postgres.

    :param conn: connection object (inherited from `psycopg2`)
    :param schema: schema of the target table
    :param table: name of the target table
    :param source_path: path to CSV file for upload
    :param columns: list of columns to be included in the COPY command
    :return: null
    """
    try:
        with conn.cursor() as cursor, open(source_path, "r") as staged_csv:
            bulk_insert = construct_copy_statement(
                schema,
                table,
                columns
            )
            cursor.copy_expert(bulk_insert, staged_csv)
    except psycopg2.errors.DatabaseError as err:
        logger.error(f"Failed to upload staged file to Postgres: '{err}'")
    else:  
        conn.commit()
        os.remove(source_path)


if __name__ == "__main__":
    pass
    
