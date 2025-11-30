
# Glue ETL job: clean FlightData (raw -> processed) and write partitioned Parquet to S3.

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F
import sys

# 1. Read job name from Glue arguments
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

# 2. Create Spark and Glue contexts
sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

# 3. Configuration
GLUE_DATABASE_NAME = "airline_delay_monitoring_dev_db"
RAW_TABLE_NAME = "airline_delay_monitoring_dev_raw_data"  # exact crawler table name
PROCESSED_BUCKET_NAME = "airline-delay-monitoring-dev-processed-data"

# 4. Read raw FlightData from Glue Catalog
raw_dyf = glue_context.create_dynamic_frame.from_catalog(
    database=GLUE_DATABASE_NAME,
    table_name=RAW_TABLE_NAME,
)

# 5. Convert DynamicFrame to Spark DataFrame
df = raw_dyf.toDF()

# 6. Fix numeric and boolean types using lowercase column names
df = (
    df
    .withColumn("year", F.col("year").cast("int"))
    .withColumn("month", F.col("month").cast("int"))
    .withColumn("dayofmonth", F.col("dayofmonth").cast("int"))
    .withColumn("dayofweek", F.col("dayofweek").cast("int"))
    .withColumn("deptime", F.col("deptime").cast("int"))
    .withColumn("crsdeptime", F.col("crsdeptime").cast("int"))
    .withColumn("arrtime", F.col("arrtime").cast("int"))
    .withColumn("crsarrtime", F.col("crsarrtime").cast("int"))
    .withColumn("flightnum", F.col("flightnum").cast("int"))
    .withColumn("actualelapsedtime", F.col("actualelapsedtime").cast("int"))
    .withColumn("crselapsedtime", F.col("crselapsedtime").cast("int"))
    .withColumn("airtime", F.col("airtime").cast("int"))
    .withColumn("arrdelay", F.col("arrdelay").cast("int"))
    .withColumn("depdelay", F.col("depdelay").cast("int"))
    .withColumn("distance", F.col("distance").cast("int"))
    .withColumn("taxiin", F.col("taxiin").cast("int"))
    .withColumn("taxiout", F.col("taxiout").cast("int"))
    .withColumn("cancelled", (F.col("cancelled").cast("int") > 0))
    .withColumn("diverted", (F.col("diverted").cast("int") > 0))
    .withColumn("carrierdelay", F.col("carrierdelay").cast("int"))
    .withColumn("weatherdelay", F.col("weatherdelay").cast("int"))
    .withColumn("nasdelay", F.col("nasdelay").cast("int"))
    .withColumn("securitydelay", F.col("securitydelay").cast("int"))
    .withColumn("lateaircraftdelay", F.col("lateaircraftdelay").cast("int"))
)

# 7. Trim and uppercase key string codes
df = (
    df
    .withColumn("uniquecarrier", F.upper(F.trim(F.col("uniquecarrier"))))
    .withColumn("origin", F.upper(F.trim(F.col("origin"))))
    .withColumn("dest", F.upper(F.trim(F.col("dest"))))
    .withColumn("cancellationcode", F.upper(F.trim(F.col("cancellationcode"))))
)

# 8. Handle NULLs for delay fields (fill with 0)
df = (
    df
    .withColumn("arrdelay", F.coalesce(F.col("arrdelay"), F.lit(0)))
    .withColumn("depdelay", F.coalesce(F.col("depdelay"), F.lit(0)))
    .withColumn("carrierdelay", F.coalesce(F.col("carrierdelay"), F.lit(0)))
    .withColumn("weatherdelay", F.coalesce(F.col("weatherdelay"), F.lit(0)))
    .withColumn("nasdelay", F.coalesce(F.col("nasdelay"), F.lit(0)))
    .withColumn("securitydelay", F.coalesce(F.col("securitydelay"), F.lit(0)))
    .withColumn("lateaircraftdelay", F.coalesce(F.col("lateaircraftdelay"), F.lit(0)))
)

# 9. Build FlightDate and dep_scheduled_ts from year/month/dayofmonth + crsdeptime
df = (
    df
    .withColumn(
        "flightdate",
        F.to_date(
            F.concat_ws(
                "-",
                F.col("year").cast("string"),
                F.lpad(F.col("month").cast("string"), 2, "0"),
                F.lpad(F.col("dayofmonth").cast("string"), 2, "0"),
            ),
            "yyyy-MM-dd",
        ),
    )
    .withColumn("crsdeptime_padded", F.lpad(F.col("crsdeptime").cast("string"), 4, "0"))
    .withColumn("crsdephour", F.col("crsdeptime_padded").substr(1, 2))
    .withColumn("crsdepminute", F.col("crsdeptime_padded").substr(3, 2))
    .withColumn(
        "dep_scheduled_ts",
        F.to_timestamp(
            F.concat_ws(
                " ",
                F.date_format(F.col("flightdate"), "yyyy-MM-dd"),
                F.concat_ws(
                    ":",
                    F.col("crsdephour"),
                    F.col("crsdepminute"),
                    F.lit("00"),
                ),
            ),
            "yyyy-MM-dd HH:mm:ss",
        ),
    )
)


# 10. Filter bad data (basic rules)
df = df.filter(
    (F.col("distance") > 0) &
    (F.col("arrdelay") >= 0) &
    (F.col("depdelay") >= 0)
)

# 11. Remove duplicates (same flightdate + flightnum + origin + dest)
key_cols = ["flightdate", "flightnum", "origin", "dest"]
df = df.dropDuplicates(key_cols)

# 12. Create flags and analytics fields
df = (
    df
    .withColumn("isdelayed", F.col("arrdelay") > 15)
    .withColumn("totaldelay", F.col("depdelay") + F.col("arrdelay"))
)

# 13. Select final columns (including partition columns year, month)
final_df = df.select(
    "year",
    "month",
    "dayofmonth",
    "dayofweek",
    "flightdate",
    "uniquecarrier",
    "flightnum",
    "tailnum",
    "origin",
    "dest",
    "deptime",
    "crsdeptime",
    "arrtime",
    "crsarrtime",
    "actualelapsedtime",
    "crselapsedtime",
    "airtime",
    "arrdelay",
    "depdelay",
    "distance",
    "taxiin",
    "taxiout",
    "cancelled",
    "cancellationcode",
    "diverted",
    "carrierdelay",
    "weatherdelay",
    "nasdelay",
    "securitydelay",
    "lateaircraftdelay",
    "dep_scheduled_ts",
    "isdelayed",
    "totaldelay",
)

# 14. Write partitioned Parquet to processed S3 (by year, month)
output_path = f"s3://{PROCESSED_BUCKET_NAME}/processed/flights/"

(
    final_df
    .write
    .mode("overwrite")       # dev mode; can change to "append" later
    .partitionBy("year", "month")
    .parquet(output_path)
)

# 15. Commit job
job.commit()












































""" #Purpose: Read from raw Glue table → write Parquet to processed S3  TEST_RUN.

# Glue ETL job: copy raw FlightData from CSV (via Glue table) to Parquet in processed S3.

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
import sys

# 1. Read job name from Glue arguments (Glue boilerplate)
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

# 2. Create Spark and Glue contexts (entry point for Glue + Spark)
sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

# 3. Configuration: set your database, table, and output bucket
GLUE_DATABASE_NAME = "airline_delay_monitoring_dev_db"
RAW_TABLE_NAME = "airline_delay_monitoring_dev_raw_data"  # from crawler output
PROCESSED_BUCKET_NAME = "airline-delay-monitoring-dev-processed-data"

# 4. Read raw FlightData from Glue Catalog (this points to the CSV in S3 raw)
raw_dyf = glue_context.create_dynamic_frame.from_catalog(
    database=GLUE_DATABASE_NAME,
    table_name=RAW_TABLE_NAME,
)

# 5. Convert DynamicFrame to Spark DataFrame (easier to work with using Spark APIs)
raw_df = raw_dyf.toDF()

# 6. Define output path for Parquet in the processed bucket
output_path = f"s3://{PROCESSED_BUCKET_NAME}/processed/flights/"

# 7. Write DataFrame as Parquet to processed S3 (overwrite for easy reruns)
raw_df.write.mode("overwrite").parquet(output_path)

# 8. Commit the Glue job (required Glue boilerplate)
job.commit()
 """