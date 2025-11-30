###Script to upload FlightData.csv to S3 using boto3 

import boto3
from botocore.exceptions import ClientError
import os

# 1. Configuration: CHANGE ONLY IF YOUR NAMES DIFFER
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "airline-delay-monitoring-dev-raw-data"
S3_KEY = "raw/flights/FlightData.csv"

# Local path to the CSV inside your project
# This builds: <project_root>/data/raw/FlightData.csv
LOCAL_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  # go up from scripts/python/
    "data",
    "raw",
    "FlightData.csv",
)

def upload_file_to_s3():
    """
    Uploads the local FlightData.csv file to the raw S3 bucket using boto3.
    """
    # 2. Create an S3 client (uses your AWS credentials and region)
    s3_client = boto3.client("s3", region_name=AWS_REGION)

    print(f"Local file path: {LOCAL_FILE_PATH}")
    if not os.path.exists(LOCAL_FILE_PATH):
        raise FileNotFoundError(f"File not found: {LOCAL_FILE_PATH}")

    try:
        # 3. Upload the file to S3
        print(f"Uploading to s3://{S3_BUCKET_NAME}/{S3_KEY} ...")
        s3_client.upload_file(
            Filename=LOCAL_FILE_PATH,
            Bucket=S3_BUCKET_NAME,
            Key=S3_KEY,
        )
        print("Upload successful.")
    except ClientError as e:
        print(f"Error uploading file: {e}")
        raise

if __name__ == "__main__":
    upload_file_to_s3()









""" Line-by-line explanation:

AWS_REGION: Region where the S3 bucket lives (us-east-1).

S3_BUCKET_NAME: Raw bucket Terraform created.

S3_KEY: “Path” inside the bucket: raw/flights/FlightData.csv.

LOCAL_FILE_PATH: Dynamically builds the absolute path to data/raw/FlightData.csv based on the script’s location.

boto3.client("s3", region_name=AWS_REGION): Creates a client for S3 using your configured credentials.

upload_file(...): Sends the local file to S3 at that bucket/key.

if name == "main": Ensures upload_file_to_s3() runs when you execute this script directly. """