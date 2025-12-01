#Producer script for jan month for test((read January data + DQ + JSON preview))
import json
import io

import boto3
import pandas as pd


# ====== CONFIG (edit these) ======
AWS_REGION = "us-east-1"  # Your AWS region
S3_BUCKET = "airline-delay-monitoring-dev-raw-data"  # Raw bucket name
S3_KEY = "raw/flights/FlightData.csv"  # Path/key of the 2008 CSV file in that bucket
YEAR_FILTER = 2008
MONTH_FILTER = 1
# ================================


def read_csv_from_s3(bucket: str, key: str) -> pd.DataFrame:
    """
    Read a CSV file from S3 into a pandas DataFrame.
    """
    s3 = boto3.client("s3", region_name=AWS_REGION)
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read()              # Download file contents as bytes
    df = pd.read_csv(io.BytesIO(body))     # Let pandas parse CSV into a table
    return df


def filter_january_and_apply_dq(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only January 2008 flights and apply simple data quality rules:
      - Distance > 0
      - ArrDelay and DepDelay are not null
    """
    # Filter rows for January 2008 only
    jan_df = df[(df["Year"] == YEAR_FILTER) & (df["Month"] == MONTH_FILTER)]

    # Basic streaming DQ rules
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
    Convert one DataFrame row into a small JSON-ready event.
    """
    # Build ISO date string from Year, Month, DayofMonth
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


def main():
    # 1) Read the raw CSV into a DataFrame
    print("Reading raw CSV from S3...")
    df = read_csv_from_s3(S3_BUCKET, S3_KEY)

    # 2) Filter to January 2008 and apply basic DQ rules
    good_df = filter_january_and_apply_dq(df)

    # 3) Show a few sample JSON events that we will later send to Kinesis
    print("\nSample JSON events (first 5):")
    for _, row in good_df.head(5).iterrows():
        event = build_event(row)
        print(json.dumps(event))

    print("\nStep 1 complete: January filter, DQ, and JSON structure are OK.")
    print("Next step will be sending these events to Kinesis.")


if __name__ == "__main__":
    main()
