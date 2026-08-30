import os
from pathlib import Path
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

JDBC_URL = f"jdbc:mysql://{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

def write_jobs_to_mysql(
    batch_df: DataFrame,
    _batch_id: int,
) -> None:
    if batch_df.isEmpty():
        return

    mysql_df = batch_df.select(
        "job_id",
        "title",
        "company",
        "experience_level",
        "location",
        "remote",
        "description",
        to_json(col("matched_skills")).alias("matched_skills"),
        "match_count",
        "published_at",
        "job_url",
        "source",
    )

    (
        mysql_df.write
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "matched_jobs")
        .option("user", MYSQL_USER)
        .option("password", MYSQL_PASSWORD)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .mode("append")
        .save()
    )