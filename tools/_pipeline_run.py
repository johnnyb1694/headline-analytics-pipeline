"""Administer the deployment that was enacted by `_pipeline_deploy.py`

You can alternatively run the same logic presented here from the command line like so:

````
# e.g. suppose we run for year 2024 and month 10
prefect deployment run --params '{"year": 2024, "month": 10}' 'main-nytas/headline-analytics-pipeline'
````
"""
import prefect.main # must be imported due to known issue: https://github.com/PrefectHQ/prefect/issues/15957
import click
import datetime
from prefect.deployments import run_deployment


TODAY = datetime.date.today()
FIRST = TODAY.replace(day=1)
LATEST_PERIOD = FIRST - datetime.timedelta(days=1)

@click.command
@click.option("-y", "--year", type=int, help="Year of interest")
@click.option("-m", "--month", type=int, help="Month of interest (1-12)")
def run_pipeline(
    year: int = LATEST_PERIOD.year,
    month: int = LATEST_PERIOD.month
) -> None:
    run_deployment(
        name="main-nytas/headline-analytics-pipeline",
        parameters={
            "year": year,
            "month": month
        }
    )


if __name__ == "__main__":
    run_pipeline()

