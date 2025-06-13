import argparse
import hashlib
import os
import pandas as pd
import requests
from typing import Any, Dict, List



def send_track(write_key: str, user_id: str, event: str, properties: Dict[str, Any]):
    """Send a track call to Segment."""
    url = "https://api.segment.io/v1/track"
    payload = {
        "userId": user_id,
        "event": event,
        "properties": properties,
    }
    response = requests.post(url, json=payload, auth=(write_key, ""))
    response.raise_for_status()

def send_batch(write_key: str, batch: List[Dict[str, Any]]):
    """Send a batch of track calls to Segment."""
    url = "https://api.segment.io/v1/batch"
    payload = {"batch": batch}
    response = requests.post(url, json=payload, auth=(write_key, ""))
    response.raise_for_status()


def process_excel(
    path: str,
    write_key: str,
    user_id_col: str,
    event_col: str,
    email_col: str,
    phone_col: str,
    batch_size: int,
    hash_id: bool,
    hash_phone: bool,
):
    """Process the Excel file and send track events."""
    df = pd.read_excel(path)
    if user_id_col not in df.columns:
        if email_col in df.columns:
            user_id_col = email_col
        else:
            raise KeyError(
                f"Neither '{user_id_col}' nor '{email_col}' columns found in Excel"
            )
    batch: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        user_id = row[user_id_col]
        if hash_id:
            user_id = hashlib.sha256(str(user_id).encode()).hexdigest()
        event = row[event_col]
        properties = row.drop([event_col], errors="ignore").to_dict()
        if user_id_col != email_col:
            properties.pop(user_id_col, None)
        if phone_col in properties and hash_phone:
            properties[phone_col] = hashlib.sha256(str(properties[phone_col]).encode()).hexdigest()
        batch.append({"userId": user_id, "event": event, "properties": properties})
        if len(batch) >= batch_size:
            send_batch(write_key, batch)
            batch.clear()
    if batch:
        send_batch(write_key, batch)


def parse_args():
    parser = argparse.ArgumentParser(description="Process Excel and send events to Segment")
    parser.add_argument("excel_file", help="Path to Excel file")

    parser.add_argument(
        "--user-id-col",
        default="userId",
        help="Column name containing the user ID",
    )
    parser.add_argument(
        "--event-col",
        default="event",
        help="Column name containing the event name",
    )
    parser.add_argument(
        "--email-col",
        default="email",
        help="Fallback column containing email when user ID is missing",
    )
    parser.add_argument(
        "--phone-col",
        default="phone_number",
        help="Column containing phone numbers to optionally hash",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of events to send in each batch",
    )
    parser.add_argument(
        "--hash-id",
        action="store_true",
        help="Hash the identifier before sending to Segment",
    )
    parser.add_argument(
        "--hash-phone",
        action="store_true",
        help="Hash phone numbers before sending to Segment",
    )
    parser.add_argument(
        "--write-key",
        default=os.getenv("SEGMENT_WRITE_KEY"),
        help="Segment write key",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.write_key:
        raise SystemExit("Segment write key not provided. Set SEGMENT_WRITE_KEY env variable or use --write-key.")

    process_excel(
        args.excel_file,
        args.write_key,
        args.user_id_col,
        args.event_col,
        args.email_col,
        args.phone_col,
        args.batch_size,
        args.hash_id,
        args.hash_phone,
    )
