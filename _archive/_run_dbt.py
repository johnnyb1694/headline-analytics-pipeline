from dbt.cli.main import dbtRunner
from pathlib import Path


PROJECT_DIR = Path(__file__).parent
PATH_DBT_PROFILES = PROJECT_DIR / "config"
PATH_DBT_PROJECT = PROJECT_DIR / "src" / "data_transformer"


def execute_dbt_run(
    dbt_project_path: Path | str = PATH_DBT_PROJECT,
    dbt_profiles_path: Path | str = PATH_DBT_PROFILES
) -> None:
    """Run all dbt models in succession

    :param dbt_project_path: path to project containing `dbt_project.yml`, defaults to PATH_DBT_PROJECT
    """
    dbt = dbtRunner()

    # Pre-seed any data (e.g. stop words)
    seed_args = [
        "seed",
        "--project-dir", dbt_project_path, 
        "--profiles-dir", dbt_profiles_path
    ]
    dbt.invoke(seed_args)

    # Run all models in succession
    run_args = [
        "run", 
        "--project-dir", dbt_project_path, 
        "--profiles-dir", dbt_profiles_path
    ]
    dbt.invoke(run_args)


if __name__ == "__main__":
    execute_dbt_run()