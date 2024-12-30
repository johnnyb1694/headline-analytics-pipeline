"""Prefect tasks which form part of the overall pipeline `flow`.

Tasks:

- Task 1: Open connection to Postgres database (context-managed) (Y)
- Task 2: Extract data 'as at' the given year and month
- Task 3: Load extracted data into staging area of Postgres database
- Task 4: Transform loaded data via `dbt` framework
- Task 5: If applicable, download logit inputs
- Task 6: If applicable, administer logistic growth model fit
- Task 6: If applicable, upload logistic growth fit to Postgres database

"""
from prefect import task
from src.db.utils import open_connection
from src.data_loader import (
    nytas_extract_archive, 
    nytas_filter_archive, 
    stage,
    ingest
)


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


@task(name="stage_nytas_archive_to_csv")
def stage_nytas_archive_to_csv(
    nytas_api_key: str,
    year: int, 
    month: int,
    staging_path: str
) -> None:
    """Stages headlines for a given 'as at' date to disk (in `.csv` format)
    """
    nyt_archive = nytas_extract_archive(
        nytas_api_key,
        year,
        month
    )
    filtered_archive = nytas_filter_archive(
        nyt_archive
    )
    stage(
        records=filtered_archive,
        field_names=["headline", "publication_date", "author", "news_desk", "url"],
        path=staging_path
    )
    

@task(name="ingest_nytas_archive", cache_policy=None)
def ingest_nytas_archive(
    conn,
    source_path: str
) -> None:
    """Ingests NYT Archive Search response into Postgres instance
    """
    ingest(
        conn=conn,
        schema="raw",
        table="nytas",
        columns=["headline", "publication_date", "author", "news_desk", "url"],
        source_path=source_path
    )
    

if __name__ == "__main__":
    pass