import os
from pathlib import Path
from typing import List

import mysql.connector
from dotenv import load_dotenv
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, to_json


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

required_settings = {
    "MYSQL_HOST": MYSQL_HOST,
    "MYSQL_PORT": MYSQL_PORT,
    "MYSQL_DATABASE": MYSQL_DATABASE,
    "MYSQL_USER": MYSQL_USER,
    "MYSQL_PASSWORD": MYSQL_PASSWORD,
}

missing_settings = [
    name
    for name, value in required_settings.items()
    if not value
]

if missing_settings:
    missing = ", ".join(missing_settings)
    raise ValueError(f"Missing database settings: {missing}")

JDBC_URL = (
    f"jdbc:mysql://{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

def write_jobs_to_mysql(
    batch_df: DataFrame,
    _batch_id: int,
) -> None:
    if batch_df.isEmpty():
        return

    mysql_df = batch_df.dropDuplicates(["job_id"]).select(
        "job_id",
        "title",
        "company",
        "experience_level",
        "location",
        "remote",
        "description",
        to_json(col("ad_skills_found")).alias("ad_skills_found"),
        "ad_skills_count",
        "published_at",
        "job_url",
        "source",
        "ingested_at",
    )

    rows = mysql_df.collect()

    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        database=MYSQL_DATABASE,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
    )

    cursor = connection.cursor()

    sql = """
        INSERT INTO jobs (
            job_id,
            title,
            company,
            experience_level,
            location,
            remote,
            description,
            ad_skills_found,
            ad_skills_count,
            published_at,
            job_url,
            source,
            ingested_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            company = VALUES(company),
            experience_level = VALUES(experience_level),
            location = VALUES(location),
            remote = VALUES(remote),
            description = VALUES(description),
            ad_skills_found = VALUES(ad_skills_found),
            ad_skills_count = VALUES(ad_skills_count),
            published_at = VALUES(published_at),
            job_url = VALUES(job_url),
            source = VALUES(source),
            ingested_at = VALUES(ingested_at)
    """

    values = [
        tuple(row)
        for row in rows
    ]

    cursor.executemany(sql, values)
    connection.commit()

    cursor.close()
    connection.close()

def save_candidate_preferences(
    candidate_id: int,
    skills: List[str],
    experience_levels: List[str],
    match_frequency: str,
) -> None:
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        database=MYSQL_DATABASE,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE candidate_profiles
        SET match_frequency = %s
        WHERE candidate_id = %s
        """,
        (match_frequency, candidate_id),
    )

    cursor.execute(
        """
        DELETE FROM candidate_skills
        WHERE candidate_id = %s
        """,
        (candidate_id,),
    )

    if skills:
        cursor.executemany(
            """
            INSERT INTO candidate_skills (
                candidate_id,
                skill_name
            )
            VALUES (%s, %s)
            """,
            [
                (candidate_id, skill)
                for skill in skills
            ],
        )

    cursor.execute(
        """
        DELETE FROM candidate_experience_levels
        WHERE candidate_id = %s
        """,
        (candidate_id,),
    )

    if experience_levels:
        cursor.executemany(
            """
            INSERT INTO candidate_experience_levels (
                candidate_id,
                experience_level
            )
            VALUES (%s, %s)
            """,
            [
                (candidate_id, level)
                for level in experience_levels
            ],
        )

    connection.commit()

    cursor.close()
    connection.close()