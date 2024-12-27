"""Fits logistic growth model to each relevant term in the input data and logs the results to a database.
"""
import click
import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from psycopg2 import sql
from src.model import (
    open_connection,
    DBC,
    get_logit_inputs,
    compute_batch_trend,
    load_logit_outputs
)


# ---- Configuration ----
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
STAGING_ROOT = Path(__file__).parent / "staging" 

# TODO: abstract certain database operations presented below into 'src/models/db_utils.py'
def run_model(
    min_publication_date: datetime,
    max_publication_date: datetime
):
    """Fits logistic regression model to each and every term found in headlines
    that were published between `min` and `max` publication dates.
    """
    logging.info("Configuring connection to remote database")
    dbc = DBC(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PWD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    staging_path = STAGING_ROOT / f"{str(min_publication_date)}_{str(max_publication_date)}_nytas.csv"

    logging.info("Commencing model fitting exercise")
    with open_connection(dbc) as conn:
        conn.autocommit = False
        with conn.cursor() as cursor:
            
            logging.info(f"Checking for pre-existing output for time horizon: '{str(min_publication_date)}' - '{str(max_publication_date)}'")
            cursor.execute(
                """
                    SELECT 
                        COUNT(*) 
                    FROM model.run 
                    WHERE min_publication_date = %s 
                    AND max_publication_date = %s
                """,
                (str(min_publication_date), str(max_publication_date),)
            )
            awaiting_run = (cursor.fetchone()[0] == 0)

            if awaiting_run:
                logging.info(f"Commencing model run for time horizon: '{str(min_publication_date)}' - '{str(max_publication_date)}'")
                cursor.execute(
                    """
                        INSERT INTO model.run (
                            publication,
                            min_publication_date,
                            max_publication_date
                        ) VALUES (
                            'New York Times',
                            %s,
                            %s
                        )
                        RETURNING model_run_id;
                    """,
                    (min_publication_date, max_publication_date,)
                )
                model_run_id = cursor.fetchone()[0]

                logging.info("Retrieving logistic growth input data")
                logit_inputs = get_logit_inputs(
                    conn, 
                    min_publication_date,
                    max_publication_date
                )

                logging.info("Modelling logistic growth across each resident term")
                logit_outputs = compute_batch_trend(logit_inputs)
                logit_outputs["model_run_id"] = model_run_id

                logging.info(f"Dumping model results into CSV format @ '{staging_path}'")
                logit_outputs.to_csv(staging_path, sep="|", index=False)

                logging.info("Loading results into remote database")
                load_logit_outputs(
                    cursor,
                    source_path=staging_path
                )
                conn.commit()
            else:
                logging.info("Run already complete; aborting!")


# ---- Command line tool ----
@click.command()
@click.option("--min_publication_date", type=click.DateTime(formats=["%Y-%m-%d"]), help="Starting publication date ('Yyyy-mm-dd')")
@click.option("--max_publication_date", type=click.DateTime(formats=["%Y-%m-%d"]), help="Ending publication date ('Yyyy-mm-dd')")
def main(
    min_publication_date: datetime,
    max_publication_date: datetime
):
    min_publication_date = min_publication_date.date()
    max_publication_date = max_publication_date.date()
    run_model(
        min_publication_date,
        max_publication_date
    )


if __name__ == "__main__":
    main()