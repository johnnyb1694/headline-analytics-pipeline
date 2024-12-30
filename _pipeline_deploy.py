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
prefect work-pool create --type docker --base-job-template base-job-template.json local-pool
````

3. Start a 'worker' to poll the aforementioned pool (via the Prefect API) for jobs

````
prefect worker start --pool local-pool
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

---- Rough 'Flow' Schematic ----

Environment Variables:

- Database connection parameters
- (If applicable) Docker host configuration
- NYT API key

Parameters:

- Year 
- Month
- Model (Y/N)

Tasks:

newton-elt-flow (Flow)
--> Open connection to Postgres database (context-managed) (Task)
--> Extract data 'as at' the given year and month (Task)
- Task 3: Load extracted data into staging area of Postgres database
- Task 4: Transform loaded data via `dbt` framework
- Task 5: If applicable, download logit inputs
- Task 6: If applicable, administer logistic growth model fit
- Task 6: If applicable, upload logistic growth fit to Postgres database

"""
import os
import datetime
import subprocess
from prefect import flow
from prefect.logging import get_run_logger
from dotenv import load_dotenv
from _pipeline_tasks import (
    establish_dwh_connection, 
    stage_nytas_archive_to_csv,
    ingest_nytas_archive
)
load_dotenv()


TODAY = datetime.date.today()
FIRST = TODAY.replace(day=1)
LATEST_PERIOD = FIRST - datetime.timedelta(days=1)


@flow
def main_nytas(
    year: int = LATEST_PERIOD.year,
    month: int = LATEST_PERIOD.month
):
    # Setup
    logger = get_run_logger()
    staging_path = f"{year}_{month}_nytas.csv"

    # Run
    logger.info(f"Configuring database connection parameters")
    conn = establish_dwh_connection(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PWD")
    )
    logger.info(f"Successfully established connection to: '{str(conn)}'")

    logger.info(f"Staging data from NYT Archive Search locally @ '{staging_path}'")
    stage_nytas_archive_to_csv(
        nytas_api_key=os.getenv("NYTAS_API_KEY"),
        year=year,
        month=month,
        staging_path=staging_path
    )

    logger.info(f"Ingesting data @ '{staging_path}' into Postgres database @ '{str(conn)}'")
    ingest_nytas_archive(
        conn=conn,
        source_path=staging_path
    )

    logger.info(f"Current working directory structure: {subprocess.run(["ls", "-l"])}")


if __name__ == "__main__":
    main_nytas.deploy(
        name="newton-nytas-pipeline",
        work_pool_name="local-pool",
        image="dededex/newton-pipeline:v0.0.0.9000",
        job_variables={
            "DOCKER_HOST": "unix:///Users/Johnny/.docker/run/docker.sock"
        }
    )
