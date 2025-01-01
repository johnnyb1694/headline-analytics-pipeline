"""Prefect tasks which form part of the logit growth model 'fitting' `flow`.
"""
import pandas as pd
from prefect import task
from psycopg2 import sql
from src.db.utils import open_connection, read_sql
from src.data_loader import ingest
from src.model import compute_batch_trend


@task(name="establish_dwh_connection", retries=3, retry_delay_seconds=5)
def establish_dwh_connection(
    dbname: str,
    user: str,
    password: str,
    host: str = "publications-db",
    port: int = 5432
):
    """Establishes connection to data warehouse
    """
    return open_connection(
        dbname,
        user,
        password,
        host,
        port
    )


@task(name="get_logit_inputs", retries=3, retry_delay_seconds=5, cache_policy=None)
def get_logit_inputs(
    conn,
    start_date: str,
    end_date: str
):
    """Download the inputs to administer logistic growth on each term / topic
    """
    bulk_download = sql.SQL(
        """
            select 
                publication,
                headline_term,
                (publication_date - {}) as cum_time_elapsed,
                successes,
                failures
            from dwh.fct_logit_inputs 
            where headline_term_frequency >= 50
            and publication_date between {} and {}
            and headline_term != ''
        """
    ).format(
        sql.Literal(start_date),
        sql.Literal(start_date),
        sql.Literal(end_date)
    )
    logit_inputs = read_sql(
        conn,
        bulk_download
    )
    for col in ['cum_time_elapsed', 'successes', 'failures']:
        logit_inputs[col] = logit_inputs[col].astype('int')
    return logit_inputs


@task(name="get_model_run_id", cache_policy=None)
def get_model_run_id(
    conn,
    start_date: str,
    end_date: str
) -> int:
    """Retrieves the model run ID associated with the given start date and end date combo
    """
    with conn.cursor() as cursor:
        cursor.execute(
            """
                select 
                    model_run_id
                from model.run 
                where min_publication_date = %s 
                and max_publication_date = %s
            """,
            (start_date, end_date,)
        )
        result = cursor.fetchone() 
        if result: 
            return result[0] 
        return 0


@task(name="assign_model_run_id", cache_policy=None)
def assign_model_run_id(
    conn,
    start_date: str,
    end_date: str
) -> int:
    """Assigns model run ID for the given start date and end date combo
    """
    with conn.cursor() as cursor:
        cursor.execute(
            """
                insert into model.run (
                    publication,
                    min_publication_date,
                    max_publication_date
                ) values (
                    'New York Times',
                    %s,
                    %s
                )
                returning model_run_id;
            """,
            (start_date, end_date,)
        )
        return cursor.fetchone()[0]


@task(name="fit_logit_batch")
def fit_logit_batch(
    logit_inputs: pd.DataFrame
) -> pd.DataFrame:
    """Fits logistic growth model to each headline topic and returns the results in a `pd.DataFrame`
    """
    return compute_batch_trend(
        logit_inputs
    )


@task(name="ingest_logit_outputs", cache_policy=None)
def ingest_logit_outputs(
    conn,
    source_path: str
) -> None:
    """Ingests logistic growth model outputs into Postgres instance
    """
    ingest(
        conn=conn,
        schema="model",
        table="output",
        columns=[
            "headline_term", 
            "coef_intercept", 
            "coef_time", 
            "rse_time", 
            "p_value_time", 
            "model_run_id"
        ],
        source_path=source_path
    )


if __name__ == "__main__":
    pass