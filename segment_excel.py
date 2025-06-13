import argparse
import hashlib
import os
from typing import Any, Dict

import pandas as pd
import requests

EVENT_NAME = "Checked In"
WRITE_KEY = os.getenv("SEGMENT_WRITE_KEY", "YOUR_WRITE_KEY")


def clean_email(email: str) -> str:
    return str(email).strip().lower()


def clean_phone(phone: str) -> str:
    return "".join(filter(str.isdigit, str(phone)))


def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def send_track(write_key: str, user_id: str, traits: Dict[str, Any], properties: Dict[str, Any], timestamp: str) -> None:
    """Send a track call to Segment."""
    url = "https://api.segment.io/v1/track"
    payload = {
        "userId": user_id,
        "event": EVENT_NAME,
        "properties": properties,
        "context": {"traits": traits},
        "timestamp": timestamp,
    }
    response = requests.post(url, json=payload, auth=(write_key, ""))
    response.raise_for_status()


def process_excel(path: str, write_key: str) -> None:
    """Read the Excel file and send each row as a Segment track event."""
    df = pd.read_excel(path)
    required = [
        "email",
        "phone",
        "club_name",
        "club_location",
        "membership_level",
        "timestamp",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {', '.join(missing)}")

    for _, row in df.iterrows():
        email = clean_email(row["email"])
        phone = clean_phone(row["phone"])
        hashed_email = hash_value(email)
        hashed_phone = hash_value(phone)

        traits = {
            "email": email,
            "hashed_email": hashed_email,
            "phone": phone,
            "hashed_phone": hashed_phone,
        }

        properties = {
            "club_name": row["club_name"],
            "club_location": row["club_location"],
            "membership_level": row["membership_level"],
        }

        ts = pd.to_datetime(row["timestamp"], utc=True).isoformat().replace("+00:00", "Z")

        send_track(write_key, hashed_email, traits, properties, ts)


def parse_args():
    parser = argparse.ArgumentParser(description="Send Excel rows to Segment")
    parser.add_argument("excel_file", help="Path to Excel file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if WRITE_KEY == "YOUR_WRITE_KEY":
        raise SystemExit("Please set SEGMENT_WRITE_KEY environment variable or edit WRITE_KEY in the script.")

    process_excel(args.excel_file, WRITE_KEY)
