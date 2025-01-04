"""Dedicated script for configuring and running the Prefect pipeline.

---- Pre-run Configuration ----

0. (Optional) If pushing image to remote, export `DOCKER_HOST` environment variable and authenticate with
Docker Hub from within your local environment (depends on OS and setup)

````
export DOCKER_HOST="unix:///Users/Johnny/.docker/run/docker.sock"
````

1. Start the Prefect server

````
prefect server start
````

2. Create a work pool for the Docker image

````
prefect work-pool create --type docker --base-job-template config/base-job-template.json docker-pool
````

3. Start a 'worker' to poll the aforementioned pool (via the Prefect API) for jobs

````
prefect worker start --pool docker-pool
````

---- Notes ----

Following all of the steps listed above, you can now create a deployment using the 
Python source code listed in the script below.

A deployment converts your Python functions into objects that are callable by the Prefect API.

NOTE: 

* You *must* ensure that the Docker context is accessible from Prefect (check `docker context ls` for more info on this)
* There are some known issues with `psycopg2` - if you are to include this in your deployment, ensure
that the relevant requirements.txt file specifies `psycopg2-binary` otherwise you may encounter build errors
* When a Prefect worker administers a Docker image, remember that - by default - the container will
run inside its own network environment *unless* you specify otherwise. Since the Postgres database
is running inside its own network, you need to share information about this network alias with
the Prefect worker (you can do this in the UI or by changing the deployment configuration inside `prefect.yaml`)

---- Rough 'Flow(s)' Schematic ----

Flows:

-> ELT pipeline to load frequency statistics 
-> Logistic growth model to fit 'trend' parameter statistics to each term / topic

These flows are sufficiently independent; technically, there is no requirement for the logistic growth
model to be fit as part of the ELT process (and vice versa).

This script concerns the first flow (ELT).

Environment Variables:

- Database connection parameters
- (If applicable) Docker host configuration
- NYT API key

Parameters:

- Year 
- Month
- Model (Y/N)

Flow (ELT)
----
cron: (0 0 1 * *) -> first day of each month at midnight
----
|--> Open connection to Postgres database (context-managed) (Task)
|--> Extract data 'as at' the given year and month (Task)
|--> Load extracted data into staging area of Postgres database
|--> Transform loaded data via `dbt` framework

"""
import os
import datetime
from prefect import flow
from prefect.logging import get_run_logger
from dotenv import load_dotenv
from _pipeline_tasks import (
    establish_dwh_connection, 
    stage_nytas_archive_to_csv,
    ingest_nytas_archive,
    trigger_dbt_flow
)
from psycopg2.errors import DatabaseError, OperationalError
load_dotenv()


TODAY = datetime.date.today()
FIRST = TODAY.replace(day=1)
LATEST_PERIOD = FIRST - datetime.timedelta(days=1)


@flow(log_prints=True)
def main_nytas(
    year: int = LATEST_PERIOD.year,
    month: int = LATEST_PERIOD.month
):
    """Extracts, loads and transforms a given NYT Archive Search ('nytas') metadata archive
    for the given as at date (as prescribed by `year` and `month`)

    :param year: integer year of interest, defaults to LATEST_PERIOD.year
    :param month: integer month of interest, defaults to LATEST_PERIOD.month
    """
    # Setup
    logger = get_run_logger()
    source_staging_path = f"{year}_{month}_nytas.csv"

    # Run
    try:
        
        logger.info(f"Configuring database connection")
        with establish_dwh_connection(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PWD"),
            host="publications-db"
        ) as conn:
            logger.info(f"Successfully established connection to: '{str(conn)}'")

            logger.info(f"Staging data from NYT Archive Search locally @ '{source_staging_path}'")
            stage_nytas_archive_to_csv(
                nytas_api_key=os.getenv("NYTAS_API_KEY"),
                year=year,
                month=month,
                staging_path=source_staging_path
            )

            logger.info(f"Ingesting data @ '{source_staging_path}' into Postgres database @ '{str(conn)}'")
            ingest_nytas_archive(
                conn=conn,
                source_path=source_staging_path
            )

            logger.info(f"Running `dbt` transformation models")
            trigger_dbt_flow()
    
    except OperationalError as e:
        logger.error(f"Connectivity could not be established to DWH: '{str(e)}'")
    except DatabaseError as e:
        conn.rollback()
        logger.error(f"ELT pipeline encountered a fatal database error: '{str(e)}'")
    else:
        conn.commit()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    
    main_nytas.deploy(
        name="headline-analytics-pipeline",
        work_pool_name="docker-pool",
        image="dededex/headline-analytics-pipeline:v0.0.0.9000",
        job_variables={
            "DOCKER_HOST": "unix:///Users/Johnny/.docker/run/docker.sock"
        },
        push=False,
        cron="0 0 1 * *"
    )
