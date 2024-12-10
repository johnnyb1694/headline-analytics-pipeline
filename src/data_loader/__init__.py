"""Responsible for ingesting data from publication outlets into the Postgres `db` service.
"""
import logging
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


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def ingest_headlines(
    nytas_api_key: str,
    year: int, 
    month: int,
    dbc: DBC,
    staging_path: str
) -> int:

    logging.info(f"Extracting archives (as at: {year}-{month:02d})")
    nyt_archive = nytas_extract_archive(
        nytas_api_key,
        year,
        month
    )

    logging.info("Filtering extracted archive on relevant fields")
    filtered_archive = nytas_filter_archive(
        nyt_archive
    )

    logging.info(f"Staging archive @ '{staging_path}'")
    stage(
        records=filtered_archive,
        field_names=["headline", "publication_date", "author", "news_desk", "url"],
        path=staging_path
    )

    logging.info(f"Copying archive into Postgres database @ '{str(conn)}'")
    with open_connection(dbc) as conn:
        nytas_load(conn, source_path=staging_path)


if __name__ == "__main__":
    pass