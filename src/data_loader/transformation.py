"""Transformations executed prior to batch upload.

Note that whilst the 'transformation' piece of the ELT pipeline is primarily delegated to `dbt`,
some minor transformations take place prior to the initial load.
"""
from datetime import datetime


def nytas_transform_date(raw_date: str) -> datetime:
    """Parses and converts the raw publication date into an ISO format (suitable for Postgres)

    :param raw_date: raw (publication) date as a string e.g. "2022-09-01T00:25:54+0000"
    :return: valid ISO-formatted date for ingestion
    """
    parsed = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S%z") 
    return parsed.isoformat()


def nytas_transform_author(raw_author: str) -> str:
    """Removes the prefix 'By ' from the author tag in the NYTAS API response.

    :param raw_author: original author tag, normally written as e.g. "By Johnny Breen"
    :return: the name of the author e.g. "Johnny Breen"
    """
    return raw_author.replace("By ", "")