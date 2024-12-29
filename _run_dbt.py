from dbt.cli.main import dbtRunner
from pathlib import Path


PROJECT_DIR = Path(__file__).parent
PATH_DBT_PROJECT = PROJECT_DIR / "src" / "data_transformer"


def execute_dbt_run(
    dbt_project_path: Path | str = PATH_DBT_PROJECT
) -> None:
    """Run all dbt models in succession

    :param dbt_project_path: path to project containing `dbt_project.yml`, defaults to PATH_DBT_PROJECT
    """
    dbt = dbtRunner()
    cli_args = ["run", "--project-dir", dbt_project_path]
    dbt.invoke(cli_args)


if __name__ == "__main__":
    execute_dbt_run()