"""Responsible for ingesting data from publication outlets into the Postgres `db` service.
"""
from .extract import (
    nytas_extract_archive,
    nytas_filter_archive,
    stage
)
from .load import (
    open_connection,
    nytas_load,
    DBC
)


def extract_nytas(
    nytas_api_key: str,
    year: int, 
    month: int,
    staging_path: str
) -> None:
    """Ingests headlines for a given 'as at' date into our local Postgres instance.

    :param nytas_api_key: access key for NYTAS
    :param year: year of interest
    :param month: month of interest

    :param staging_path: local path (on disk) to staging area prior to Postgres upload
    :return: null return type
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


def load(
    staging_path: str,
    dbc: DBC
):
    """Loads data into remote RDBMS (e.g. Postgres).

    :param dbc: database configuration class for access to Postgres
    """
    with open_connection(dbc) as conn:
        nytas_load(conn, source_path=staging_path)


if __name__ == "__main__":
    pass