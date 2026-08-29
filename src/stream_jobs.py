import json
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import ArrayType, BooleanType, StringType, StructField, StructType
from matching import add_experience_level, add_skill_matches, filter_suitable_jobs

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_FILE = PROJECT_ROOT / "skills.json"

with open(SKILLS_FILE, "r", encoding="utf-8") as file:
    SKILLS = json.load(file)

spark = SparkSession.builder.appName("SqillifyKafkaReader").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

job_schema = StructType([
    StructField("job_id", StringType()),
    StructField("title", StringType()),
    StructField("company", StringType()),
    StructField("location", StringType()),
    StructField("remote", BooleanType()),
    StructField("job_types", ArrayType(StringType())),
    StructField("tags", ArrayType(StringType())),
    StructField("description", StringType()),
    StructField("published_at", StringType()),
    StructField("job_url", StringType()),
    StructField("source", StringType()),
])

raw_jobs = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "sqillify-jobs")
    .option("startingOffsets", "earliest")
    .load()
)

job_msgs = raw_jobs.selectExpr("CAST(value AS STRING) AS job_json")

jobs_df = (
    job_msgs
    .select(
        from_json(
            col("job_json"),
            job_schema,
        ).alias("job")
    )
    .select("job.*")
)

jobs_df = add_experience_level(jobs_df)
jobs_df = add_skill_matches(jobs_df, SKILLS)
matched_jobs_df = filter_suitable_jobs(jobs_df)

output = matched_jobs_df.select(
    "title",
    "company",
    "experience_level",
    "location",
    "remote",
    "matched_skills",
    "match_count",
    "job_url",
)

query = (
    output.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", False)
    .option("numRows", 5)
    .trigger(availableNow=True)
    .start()
)

query.awaitTermination()

spark.stop()