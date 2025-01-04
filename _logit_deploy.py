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

This script concerns the second flow (logit).

Environment Variables:

- Database connection parameters
- (If applicable) Docker host configuration
- NYT API key

Parameters:

- Year 
- Month
- Model (Y/N)

Flow (Logit Growth Model)
----
cron: (0 1 1 * *) -> first day of each month at 1 hour past midnight
----
|--> Download logit inputs for the given as at date and time horizon
|--> Administer logistic growth model fit
|--> Upload logistic growth fit to Postgres database

"""
import os
import datetime
from dateutil.relativedelta import relativedelta
from prefect import flow
from prefect.logging import get_run_logger
from dotenv import load_dotenv
from pathlib import Path
from _logit_tasks import (
    establish_dwh_connection,
    get_model_run_id,
    assign_model_run_id,
    get_logit_inputs,
    fit_logit_batch,
    ingest_logit_outputs
)
from psycopg2.errors import DatabaseError, OperationalError
load_dotenv()


TODAY = datetime.date.today()
FIRST = TODAY.replace(day=1)


@flow(log_prints=True)
def main_logit_growth(
    as_at: str = str(FIRST),
    time_horizon_months: int = 6
):
    """Fits a logistic growth model (and stores the results in the data warehouse) for the given
    `as_at` and time horizon.

    :param as_at: as at date, defaults to `FIRST` (i.e. the first day of the 'current' month)
    :param time_horizon_months: length of time over which to compute the growth statistics;
                                determines volume of data to train on, defaults to 6
    """
    # Setup
    logger = get_run_logger()
    logit_end_date = datetime.datetime.strptime(as_at, "%Y-%m-%d")
    logit_start_date = logit_end_date - relativedelta(months=time_horizon_months)
    staging_path = f"{str(logit_start_date)}_{str(logit_end_date)}_logit_out.csv"

    # Run
    try:

        logger.info(f"Configuring database connection")
        with establish_dwh_connection(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PWD"),
            host="localhost"
        ) as conn:
            logger.info(f"Successfully established connection to: '{str(conn)}'")

            existing_model_run_id = get_model_run_id(conn, str(logit_start_date), str(logit_end_date))
            if existing_model_run_id:
                logger.info(f"Model already fitted (see `dwh.model.run` with id '{existing_model_run_id}')")
                return
            else:
                model_run_id = assign_model_run_id(conn, str(logit_start_date), str(logit_end_date))

            logger.info(f"Downloading latest logit inputs as at: '{str(as_at)}' (time horizon: 6 months)")
            logit_inputs = get_logit_inputs(
                conn,
                start_date=str(logit_start_date),
                end_date=str(logit_end_date)
            )

            logger.info(f"Fitting logistic growth model to every headline term / topic")
            logit_outputs = fit_logit_batch(logit_inputs)
            logit_outputs["model_run_id"] = model_run_id

            logger.info(f"Dumping model results into CSV format @ '{staging_path}'")
            logit_outputs.to_csv(staging_path, sep="|", index=False)

            logger.info(f"Ingesting results into Postgres instance @ '{str(conn)}'")
            ingest_logit_outputs(
                conn,
                staging_path
            )

    except OperationalError as e:
        logger.error(f"Connectivity could not be established to DWH: '{str(e)}'")
    except DatabaseError as e:
        conn.rollback()
        logger.error(f"Logistic fitting exercise encountered a fatal database error: '{str(e)}'")
    else:
        conn.commit()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":

    main_logit_growth.deploy(
        name="headline-analytics-logit-model",
        work_pool_name="docker-pool",
        image="dededex/headline-analytics-logit-model:v0.0.0.9000",
        job_variables={
            "DOCKER_HOST": "unix:///Users/Johnny/.docker/run/docker.sock"
        },
        push=False,
        cron="0 1 1 * *"
    )
