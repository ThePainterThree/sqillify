from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SqillifyKafkaReader").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

raw_jobs = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "sqillify-jobs")
    .option("startingOffsets", "earliest")
    .load()
)

job_msgs = raw_jobs.selectExpr("CAST(value AS STRING) AS job_json")

query = (
    job_msgs.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", "false")
    .option("numRows", 3)
    .trigger(availableNow=True)
    .start()
)

query.awaitTermination()
spark.stop()