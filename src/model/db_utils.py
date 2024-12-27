import pandas as pd
import psycopg2
import logging
import os
from datetime import date
from pydantic import BaseModel
from pathlib import Path


logger = logging.getLogger(__name__)


class DBC(BaseModel):
    """Database Configuration ('DBC')
    """
    dbname: str
    user: str
    password: str
    host: str = "localhost"
    port: int = 5432

    def __str__(self):
        return f"Postgres (db: '{self.dbname}', host: '{self.host}', port: '{self.port}')"


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


def get_logit_inputs(
    conn,
    min_publication_date: date,
    max_publication_date: date,
    min_term_frequency: int = 50
) -> pd.DataFrame:
    logit_inputs = pd.read_sql(
        """
            select 
                publication,
                headline_term,
                (publication_date - %s) as cum_time_elapsed,
                successes,
                failures
            from dwh.fct_logit_inputs 
            where headline_term_frequency >= %s
            and publication_date between %s and %s
            and headline_term != '';
        """,
        con=conn,
        params=(
            min_publication_date,
            min_term_frequency,
            min_publication_date,
            max_publication_date,
        )
    )
    for col in ['cum_time_elapsed', 'successes', 'failures']:
        logit_inputs[col] = logit_inputs[col].astype('int')
    return logit_inputs


def load_logit_outputs(
    cursor,
    source_path: Path
) -> None:
    """Loads logistic growth outputs into a given database (via `conn`)

    :param cursor: connection.cursor() object inherited from `psycopg2`
    :param source_path: path to CSV file for upload
    :return: null
    """
    try:
        with cursor, open(source_path, "r") as staged_csv:
            bulk_insert = """
                            copy model.output (
                                headline_term, 
                                coef_intercept, 
                                coef_time,
                                rse_time,
                                p_value_time,
                                model_run_id
                            ) from stdin with (format csv, delimiter '|', header true);
                          """
            cursor.copy_expert(bulk_insert, staged_csv)
    except psycopg2.errors.DatabaseError as err:
        logger.error(f"Failed to upload results to Postgres: '{err}'")
    else:  
        os.remove(source_path)


if __name__ == "__main__":
    pass