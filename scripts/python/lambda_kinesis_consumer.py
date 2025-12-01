import base64
import json
import logging
import time
from datetime import datetime
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

## code to send alerts to SNS + SQS
sns_client = boto3.client("sns")
sqs_client = boto3.client("sqs")

ALERTS_TOPIC_ARN = os.environ.get("ALERTS_TOPIC_ARN")
ALERTS_QUEUE_URL = os.environ.get("ALERTS_QUEUE_URL")


# === CONFIG: update bucket name if needed ===
QUARANTINE_BUCKET = "airline-delay-monitoring-dev-processed-data"
QUARANTINE_PREFIX = "streaming/quarantine/flightevents"


def is_valid_event(event_obj: dict) -> bool:
    """
    Streaming data quality rules:
      - Required fields present
      - Distance > 0
      - Delays within a reasonable range
    """
    required_fields = [
        "flightdate",
        "uniquecarrier",
        "flightnum",
        "origin",
        "dest",
        "depdelay",
        "arrdelay",
        "distance",
    ]
    for f in required_fields:
        if f not in event_obj or event_obj[f] in (None, ""):
            return False

    try:
        distance = float(event_obj["distance"])
        depdelay = float(event_obj["depdelay"])
        arrdelay = float(event_obj["arrdelay"])
    except (ValueError, TypeError):
        return False

    if distance <= 0:
        return False

    # Basic sanity bounds for delays
    if not (-60 <= depdelay <= 1440):
        return False
    if not (-60 <= arrdelay <= 1440):
        return False

    return True


def classify_alert(event_obj: dict) -> str | None:
    """
    Decide if this event should raise an alert.
    Returns alert type string or None.
    """
    depdelay = float(event_obj["depdelay"])
    arrdelay = float(event_obj["arrdelay"])

    if depdelay >= 60:
        return "SEVERE_DEPARTURE_DELAY"
    if arrdelay >= 60:
        return "SEVERE_ARRIVAL_DELAY"
    if depdelay >= 30 and arrdelay >= 30:
        return "PERSISTENT_ROUTE_DELAY"

    return None


def build_alert_payload(event_obj: dict, alert_type: str) -> dict:
    """
    Create a small JSON-friendly alert object.
    """
    return {
        "alert_type": alert_type,
        "flightdate": event_obj.get("flightdate"),
        "uniquecarrier": event_obj.get("uniquecarrier"),
        "flightnum": event_obj.get("flightnum"),
        "origin": event_obj.get("origin"),
        "dest": event_obj.get("dest"),
        "depdelay": event_obj.get("depdelay"),
        "arrdelay": event_obj.get("arrdelay"),
        "distance": event_obj.get("distance"),
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "message": f"{alert_type} for {event_obj.get('uniquecarrier')} "
                   f"{event_obj.get('flightnum')} {event_obj.get('origin')}->{event_obj.get('dest')}",
    }


def write_bad_events_to_s3(bad_events: list[dict]) -> None:
    """
    Write a batch of bad events to a JSON file in S3 quarantine location.
    Each line is one JSON object.
    """
    if not bad_events:
        return

    ts_ms = int(time.time() * 1000)
    key = f"{QUARANTINE_PREFIX}/bad_events_{ts_ms}.json"

    body = "\n".join(json.dumps(e) for e in bad_events)

    s3_client.put_object(
        Bucket=QUARANTINE_BUCKET,
        Key=key,
        Body=body.encode("utf-8"),
    )

    logger.warning(
        "Wrote %d bad events to S3 quarantine at s3://%s/%s",
        len(bad_events),
        QUARANTINE_BUCKET,
        key,
    )


def lambda_handler(event, context):
    """
    Kinesis → Lambda handler.

    - Reads records from Kinesis
    - Decodes base64 payload
    - Parses JSON flight events
    - Applies streaming DQ and quarantines bad events
    - Classifies alerts (currently logged only)
    """
    records_processed = 0
    records_failed = 0
    bad_events: list[dict] = []

    for record in event.get("Records", []):
        try:
            kinesis_data = record["kinesis"]["data"]
            payload_bytes = base64.b64decode(kinesis_data)
            payload_str = payload_bytes.decode("utf-8")
            event_obj = json.loads(payload_str)

            # DQ check
            if not is_valid_event(event_obj):
                bad_events.append(event_obj)
                continue

            # Normal event logging
            logger.info(
                "Flight event: carrier=%s flightnum=%s origin=%s dest=%s "
                "depdelay=%s arrdelay=%s flightdate=%s",
                event_obj.get("uniquecarrier"),
                event_obj.get("flightnum"),
                event_obj.get("origin"),
                event_obj.get("dest"),
                event_obj.get("depdelay"),
                event_obj.get("arrdelay"),
                event_obj.get("flightdate"),
            )

            # Alert classification
            alert_type = classify_alert(event_obj)
            if alert_type:
                alert_payload = build_alert_payload(event_obj, alert_type)
                logger.info("ALERT: %s", json.dumps(alert_payload))
                publish_alert(alert_payload)



            records_processed += 1

        except Exception as e:
            logger.error("Failed to process record: %s", e, exc_info=True)
            records_failed += 1

    # Quarantine bad events
    write_bad_events_to_s3(bad_events)

    logger.info(
        "Batch complete. Processed=%d, BadDQ=%d, Failed=%d",
        records_processed,
        len(bad_events),
        records_failed,
    )

    return {
        "statusCode": 200,
        "processed": records_processed,
        "bad_dq": len(bad_events),
        "failed": records_failed,
    }




##helper to publish alerts:
def publish_alert(alert_payload: dict) -> None:
    """
    Send alert to SNS topic and SQS queue.
    """
    alert_json = json.dumps(alert_payload)

    if ALERTS_TOPIC_ARN:
        sns_client.publish(
            TopicArn=ALERTS_TOPIC_ARN,
            Message=alert_json,
            Subject=f"Flight delay alert: {alert_payload.get('alert_type')}",
        )

    if ALERTS_QUEUE_URL:
        sqs_client.send_message(
            QueueUrl=ALERTS_QUEUE_URL,
            MessageBody=alert_json,
        )
