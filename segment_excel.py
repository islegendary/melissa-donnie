import argparse
import os
import pandas as pd
import requests
from typing import Any, Dict

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


def process_excel(path: str, write_key: str, user_id_col: str, event_col: str):
    """Process the Excel file and send track events."""
    df = pd.read_excel(path)
    for _, row in df.iterrows():
        user_id = row[user_id_col]
        event = row[event_col]
        properties = row.drop([user_id_col, event_col]).to_dict()
        send_track(write_key, user_id, event, properties)


def parse_args():
    parser = argparse.ArgumentParser(description="Process Excel and send events to Segment")
    parser.add_argument("excel_file", help="Path to Excel file")
    parser.add_argument("--user-id-col", default="userId", help="Column name containing the user ID")
    parser.add_argument("--event-col", default="event", help="Column name containing the event name")
    parser.add_argument("--write-key", default=os.getenv("SEGMENT_WRITE_KEY"), help="Segment write key")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.write_key:
        raise SystemExit("Segment write key not provided. Set SEGMENT_WRITE_KEY env variable or use --write-key.")
    process_excel(args.excel_file, args.write_key, args.user_id_col, args.event_col)
