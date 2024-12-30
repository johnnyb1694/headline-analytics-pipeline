"""Administer the deployment that was enacted by `_pipeline_deploy.py`

You can alternatively run the same logic presented here from the command line like so:

````
# e.g. suppose we run for year 2024 and month 10
prefect deployment run --params '{"year": 2024, "month": 10}' 'main-nytas/newton-nytas-pipeline'
````
"""
import prefect.main # must be imported due to known issue: https://github.com/PrefectHQ/prefect/issues/15957
from prefect.deployments import run_deployment


def run_pipeline() -> None:
    run_deployment(
        name="main-nytas/newton-nytas-pipeline",
        parameters={
            "year": 2024,
            "month": 9
        }
    )


if __name__ == "__main__":
    run_pipeline()

