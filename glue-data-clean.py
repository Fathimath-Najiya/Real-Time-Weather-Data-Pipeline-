glue-data-clean code

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, from_unixtime

# ── 1. INITIALISE GLUE ──────────────────────────────────────────
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'REDSHIFT_PASSWORD'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# ── 2. CONFIGURATION ─────────────────────────────────────────────
S3_BUCKET = "weather-pipeline-najiya"
S3_PATH = f"s3://{S3_BUCKET}/raw/weather/"
REDSHIFT_URL = "jdbc:redshift://default-workgrouweather-pipeline.874119032623.ap-south-1.redshift-serverless.amazonaws.com:5439/dev"
REDSHIFT_USER = "admin"
REDSHIFT_PASSWORD = args['REDSHIFT_PASSWORD']
REDSHIFT_TABLE = "weather_data"

# ── 3. READ RAW JSON FROM S3 ─────────────────────────────────────
# recursiveFileLookup reads files from ALL subfolders (Kochi, Bangalore etc.)
# multiLine handles JSON spread across multiple lines
df = spark.read \
    .option("multiLine", True) \
    .option("recursiveFileLookup", True) \
    .json(S3_PATH)

# ── 4. EXTRACT ONLY THE FIELDS YOU NEED ──────────────────────────
transformed_df = df.select(
    col("name").alias("city"),
    col("sys.country").alias("country"),
    col("main.temp").alias("temperature"),
    col("main.feels_like").alias("feels_like"),
    col("main.humidity").alias("humidity"),
    col("wind.speed").alias("wind_speed"),
    col("weather")[0]["description"].alias("description"),
    from_unixtime(col("dt")).alias("recorded_at")
)

# ── 5. WRITE CLEAN DATA TO REDSHIFT ──────────────────────────────
transformed_df.write \
    .format("jdbc") \
    .option("url", REDSHIFT_URL) \
    .option("dbtable", REDSHIFT_TABLE) \
    .option("user", REDSHIFT_USER) \
    .option("password", REDSHIFT_PASSWORD) \
    .option("driver", "com.amazon.redshift.jdbc42.Driver") \
    .mode("append") \
    .save()

# ── 6. CLOSE THE JOB ─────────────────────────────────────────────
job.commit()
