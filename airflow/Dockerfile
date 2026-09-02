FROM apache/airflow:3.3.1-python3.11

USER root
RUN mkdir -p /opt/dbt \
    && chown airflow:root /opt/dbt

USER airflow

COPY --chown=airflow:root requirements-dbt.txt /opt/dbt/requirements.txt

# keep dbt dependencies separate from Airflow
RUN python -m venv /opt/dbt/venv \
    && /opt/dbt/venv/bin/python -m pip --isolated install \
        --no-cache-dir -r /opt/dbt/requirements.txt \
    && /opt/dbt/venv/bin/python -m pip check