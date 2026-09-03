import json
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import ArrayType, BooleanType, StringType, StructField, StructType
from database import write_jobs_to_mysql
from matching import add_experience_level, extract_ad_skills

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_FILE = PROJECT_ROOT / "skills.json"

with open(SKILLS_FILE, "r", encoding="utf-8") as file:
    SKILLS_LIST = json.load(file)

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
jobs_df = extract_ad_skills(jobs_df, SKILLS_LIST)
jobs_df = jobs_df.withColumn("ingested_at", current_timestamp())

checkpoint_path = (
    PROJECT_ROOT
    / "data"
    / "checkpoints"
    / "mysql_jobs"
)

query = (
    jobs_df.writeStream
    .foreachBatch(write_jobs_to_mysql)
    .outputMode("append")
    .option("checkpointLocation", str(checkpoint_path))
    .trigger(processingTime="60 seconds")
    .start()
)

query.awaitTermination()
spark.stop()