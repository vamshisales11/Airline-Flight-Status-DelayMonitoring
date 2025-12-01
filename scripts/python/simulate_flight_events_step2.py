#extend this same script to actually send those JSON events into Kinesis.
##this is actual producer which puts records into kinesis data stream, step1.py was test

import json
import io
import time

import boto3
import pandas as pd


# ====== CONFIG (edit these) ======
AWS_REGION = "us-east-1"  # Your AWS region
S3_BUCKET = "airline-delay-monitoring-dev-raw-data"
S3_KEY = "raw/flights/FlightData.csv"

KINESIS_STREAM_NAME = "airline-delay-monitoring-dev-flight-stream"  # existing Kinesis Data Stream

YEAR_FILTER = 2008
MONTH_FILTER = 1

MAX_EVENTS = 5000   #limiting total records to b streamed to 5000 because I have arount 180000 records in jan month
# How fast to send events (seconds between records)
EVENT_SLEEP_SECONDS = 0.1  # 0.1 = ~10 events per second
# ================================


def read_csv_from_s3(bucket: str, key: str) -> pd.DataFrame:
    """
    Read a CSV file from S3 into a pandas DataFrame.
    """
    s3 = boto3.client("s3", region_name=AWS_REGION)
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read()
    df = pd.read_csv(io.BytesIO(body))
    return df


def filter_january_and_apply_dq(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only January 2008 flights and apply simple data quality rules:
      - Distance > 0
      - ArrDelay and DepDelay are not null
    """
    jan_df = df[(df["Year"] == YEAR_FILTER) & (df["Month"] == MONTH_FILTER)]

    dq_mask = (
        (jan_df["Distance"] > 0)
        & jan_df["ArrDelay"].notna()
        & jan_df["DepDelay"].notna()
    )

    good_df = jan_df[dq_mask].copy()
    bad_df = jan_df[~dq_mask].copy()

    print(f"Total January rows: {len(jan_df)}")
    print(f"  Good rows (pass DQ): {len(good_df)}")
    print(f"  Bad rows (fail DQ): {len(bad_df)}")

    return good_df


def build_event(row: pd.Series) -> dict:
    """
    Convert a DataFrame row into a small JSON event.
    """
    flightdate = f"{int(row['Year']):04d}-{int(row['Month']):02d}-{int(row['DayofMonth']):02d}"

    event = {
        "flightdate": flightdate,
        "uniquecarrier": str(row["UniqueCarrier"]).strip(),
        "flightnum": int(row["FlightNum"]),
        "origin": str(row["Origin"]).strip(),
        "dest": str(row["Dest"]).strip(),
        "depdelay": float(row["DepDelay"]),
        "arrdelay": float(row["ArrDelay"]),
        "distance": float(row["Distance"]),
        "cancelled": int(row["Cancelled"]) if "Cancelled" in row else 0,
        "diverted": int(row["Diverted"]) if "Diverted" in row else 0,
    }
    return event


def send_events_to_kinesis(df: pd.DataFrame):
    """
    Iterate over good rows, build JSON events, and send them to Kinesis.
    """
    kinesis = boto3.client("kinesis", region_name=AWS_REGION)

    sent_count = 0

    for _, row in df.iterrows():
        if sent_count >= MAX_EVENTS:   # <<--- stop after MAX_EVENTS
            break

        event = build_event(row)
        data_bytes = json.dumps(event).encode("utf-8")
        partition_key = event["origin"] or "unknown"

        kinesis.put_record(
            StreamName=KINESIS_STREAM_NAME,
            Data=data_bytes,
            PartitionKey=partition_key,
        )

        sent_count += 1
        time.sleep(EVENT_SLEEP_SECONDS)

        if sent_count % 1000 == 0:
            print(f"Sent {sent_count} events to Kinesis...")

    print(f"Finished sending {sent_count} events to Kinesis stream '{KINESIS_STREAM_NAME}'.")



def main():
    print("Reading raw CSV from S3...")
    df = read_csv_from_s3(S3_BUCKET, S3_KEY)

    print("Filtering January data and applying DQ...")
    good_df = filter_january_and_apply_dq(df)

    print("\nSending events to Kinesis...")
    send_events_to_kinesis(good_df)

    print("Producer finished. You now have January events in the 'flightevents' stream.")


if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
"""     
Brief explanation of new pieces
New imports

time: used for sleep between events, so we don’t blast Kinesis too fast.

New config values

KINESIS_STREAM_NAME: name of your Kinesis Data Stream (flightevents from the docs).​

EVENT_SLEEP_SECONDS: how many seconds to wait between each record; controls event rate.

send_events_to_kinesis function

Creates a Kinesis client: boto3.client("kinesis", region_name=AWS_REGION).

Loops all good January rows.

For each row:

Builds the event dict using build_event.

Converts event to bytes: json.dumps(event).encode("utf-8").

Uses origin airport as PartitionKey.

Calls kinesis.put_record(...) to send the event to the stream.

Sleeps EVENT_SLEEP_SECONDS to simulate real time.

Prints progress every 1000 events and a final summary.

main changes

After filtering and DQ, calls send_events_to_kinesis(good_df) instead of just printing samples.
 """

