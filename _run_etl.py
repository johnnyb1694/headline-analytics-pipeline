"""Extracts a batch of NYTAS extracts and uploads them into Postgres.
"""
import click
import logging
import os
from dotenv import load_dotenv
from src.data_loader import extract_nytas, load, DBC
from pathlib import Path


# ---- Configuration ----
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
STAGING_ROOT = Path(__file__).parent / "staging" 

# ---- Command line tool ----
@click.command()
@click.option("--year", help="Year of interest (expressed as integer)")
@click.option("--month", help="Month of interest (expressed as integer)")
def main(
    year: int,
    month: int
):
    """Extracts from relevant news publication archives.
    """
    logging.info("Configuring staging area parameters")
    staging_path_nytas = STAGING_ROOT / f"{year}_{month}_nytas.csv"
    dbc = DBC(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PWD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

    logging.info(f"Staging NYT archive as at {year}-{int(month):02d} @ '{staging_path_nytas}'")
    extract_nytas(
        nytas_api_key=os.getenv("NYTAS_API_KEY"),
        year=year,
        month=month,
        staging_path=staging_path_nytas
    )

    logging.info(f"Uploading NYT archive to Postgres database @ '{str(dbc)}'")
    load(
        staging_path=staging_path_nytas,
        dbc=dbc
    )


if __name__ == "__main__":
    main()