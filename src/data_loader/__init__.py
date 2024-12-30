"""Responsible for ingesting data from publication outlets into the Postgres `db` service.
"""
from .extract import (
    nytas_extract_archive,
    nytas_filter_archive,
    stage
)
from .load import (
    ingest
)


if __name__ == "__main__":
    pass