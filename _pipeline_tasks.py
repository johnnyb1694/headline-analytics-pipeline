"""Prefect tasks which form part of the pipeline `flow` object.
"""
from prefect import task
from prefect_dbt.cli.commands import DbtCoreOperation
from pathlib import Path
from src.db.utils import open_connection
from src.data_loader import (
    nytas_extract_archive, 
    nytas_filter_archive, 
    stage,
    ingest
)


PROJECT_DIR = Path(__file__).parent
PATH_DBT_PROFILES = PROJECT_DIR / "config"
PATH_DBT_PROJECT = PROJECT_DIR / "src" / "data_transformer"


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


@task
def trigger_dbt_flow() -> str:
    """Run all dbt models in succession
    """
    return DbtCoreOperation(
        commands=["dbt seed", "dbt run"],
        project_dir=PATH_DBT_PROJECT,
        profiles_dir=PATH_DBT_PROFILES
    ).run()


if __name__ == "__main__":
    pass