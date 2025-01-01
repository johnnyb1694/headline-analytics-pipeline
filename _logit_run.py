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


@click.command
@click.option("-a", "--as-at", type=int, help="As at date (in fomat 'Yyyy-mm-dd')")
@click.option("-t", "--time-horizon-months", type=int, help="# of training months in advance of 'as at'")
def run_logit_growth_fitting(
    as_at: datetime.date | str = FIRST,
    time_horizon_months: int = 6
) -> None:
    run_deployment(
        name="main-logit-growth/headline-analytics-logit-model",
        parameters={
            "as_at": as_at,
            "time_horizon_months": time_horizon_months
        }
    )


if __name__ == "__main__":
    run_logit_growth_fitting()

