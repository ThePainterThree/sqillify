from datetime import timedelta
import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook
from airflow.providers.common.sql.sensors.sql import SqlSensor

def notify_slack_failure(context):
    task_instance = context["task_instance"]

    message = (
        "🚨 *Sqillify Airflow failure*\n"
        f"*DAG:* {task_instance.dag_id}\n"
        f"*Task:* {task_instance.task_id}\n"
        f"*Run:* {context.get('run_id')}\n"
        f"*Log:* {task_instance.log_url}"
    )

    SlackWebhookHook(
        slack_webhook_conn_id="slack_sqillify_alerts"
    ).send(text=message)

with DAG(
    dag_id="sqillify_dbt_build",
    description="Build and test Sqillify's dbt models.",
    start_date=pendulum.datetime(2026, 9, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["sqillify", "dbt"],
) as dag:

    collect_jobs = BashOperator(
    task_id="collect_jobs",
    bash_command="python /opt/sqillify/src/collect_jobs.py",
    )

    prepare_jobs = BashOperator(
    task_id="prepare_jobs",
    bash_command="python /opt/sqillify/src/prepare_jobs.py",
    )

    wait_for_fresh_mysql = SqlSensor(
    task_id="wait_for_fresh_mysql",
    conn_id="sqillify_mysql",
    sql="""
    SELECT COUNT(*)
    FROM jobs
    WHERE ingested_at >=
    '{{ dag_run.start_date.astimezone().strftime("%Y-%m-%d %H:%M:%S") }}'
    """,
    poke_interval=30,
    timeout=600,
    mode="reschedule",
    )

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
        on_failure_callback=notify_slack_failure,
    )

collect_jobs >> prepare_jobs >> wait_for_fresh_mysql >> dbt_build