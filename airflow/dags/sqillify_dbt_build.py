from datetime import timedelta

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="sqillify_dbt_build",
    description="Build and test Sqillify's dbt models.",
    start_date=pendulum.datetime(2026, 9, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["sqillify", "dbt"],
) as dag:

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "/opt/dbt/venv/bin/python -m dbt.cli.main build "
            "--project-dir /opt/sqillify_dbt "
            "--profiles-dir /opt/dbt/profiles"
        ),
        cwd="/opt/sqillify_dbt",
        execution_timeout=timedelta(minutes=15),
        do_xcom_push=False,
    )