import pandas as pd
import psycopg2
from datetime import date
from pydantic import BaseModel


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
    return pd.read_sql(
        """
            select 
                publication,
                headline_term,
                (publication_date - %s) as cum_time_elapsed,
                successes,
                failures
            from dwh.fct_logit_inputs 
            where headline_term_frequency >= %s
            and publication_date between %s and %s;
        """,
        con=conn,
        params=(
            min_publication_date,
            min_term_frequency,
            min_publication_date,
            max_publication_date,
        )
    )


if __name__ == "__main__":
    pass