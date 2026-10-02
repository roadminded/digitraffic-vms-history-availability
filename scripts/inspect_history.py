#!/usr/bin/env python3
"""
Small inspection tool for testing the Digitraffic VMS history API.

The script queries history for a single VMS device, optionally for a specific
date, and prints the response structure for manual inspection.
"""

import argparse
import json
from datetime import date

import requests


API_URL = "https://tie.digitraffic.fi/api/variable-sign/v1/signs/history"
DIGITRAFFIC_USER = "RoadMinded/digitraffic-vms-history-availability"


def fetch_history(device_id: str, effective_date: str | None = None) -> list[dict]:
    """Fetch VMS history for one device from the Digitraffic API."""

    params = {
        "deviceId": device_id,
    }

    if effective_date:
        params["effectiveDate"] = effective_date

    response = requests.get(
        API_URL,
        params=params,
        headers={
            "Digitraffic-User": DIGITRAFFIC_USER,
            "Accept": "application/json",
        },
        timeout=30,
    )

    print(f"Request: {response.url}")
    print(f"HTTP: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    if not response.ok:
        print(f"Response body: {response.text}")

    response.raise_for_status()

    return response.json()


def inspect_response(data: object) -> None:
    """Print a short summary and the first returned item."""

    print()
    print(f"Top-level type: {type(data).__name__}")

    if isinstance(data, list):
        print(f"Items: {len(data)}")

        if not data:
            print("No observations returned.")
            return

        dates = [
            item.get("effectDate")
            for item in data
            if isinstance(item, dict) and item.get("effectDate")
        ]

        if dates:
            print(f"Latest effectDate: {max(dates)}")
            print(f"Earliest effectDate: {min(dates)}")

        print()
        print("First item:")
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
        return

    if isinstance(data, dict):
        print(f"Top-level keys: {', '.join(data.keys())}")

        features = data.get("features", [])

        print(f"Features: {len(features)}")

        if not features:
            print("No observations returned.")
            return

        print()
        print("First feature:")
        print(json.dumps(features[0], indent=2, ensure_ascii=False))
        return

    print("Unexpected response structure.")


def main() -> None:
    """Parse command-line arguments, fetch VMS history, and inspect the response."""
    parser = argparse.ArgumentParser(
        description="Inspect Digitraffic VMS history API responses."
    )
    parser.add_argument(
        "device_id",
        help="Digitraffic VMS device ID, e.g. KRM011552",
    )
    parser.add_argument(
        "--date",
        dest="effective_date",
        type=date.fromisoformat,
        help="Historical date in YYYY-MM-DD format",
    )

    args = parser.parse_args()

    effective_date = (
        args.effective_date.isoformat()
        if args.effective_date
        else None
    )

    data = fetch_history(
        device_id=args.device_id,
        effective_date=effective_date,
    )

    inspect_response(data)


if __name__ == "__main__":
    main()