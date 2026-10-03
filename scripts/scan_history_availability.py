#!/usr/bin/env python3
"""
Scan Digitraffic VMS history availability across multiple devices.

The initial version fetches the current VMS device list and extracts
unique device IDs for later history scanning.
"""

import argparse
from datetime import date

import requests
from history_scan import scan_device_history


SIGNS_API_URL = "https://tie.digitraffic.fi/api/variable-sign/v1/signs"
DIGITRAFFIC_USER = "RoadMinded/digitraffic-vms-history-availability"


def fetch_signs() -> dict:
    """Fetch the current VMS dataset from the Digitraffic API."""

    response = requests.get(
        SIGNS_API_URL,
        headers={
            "Digitraffic-User": DIGITRAFFIC_USER,
            "Accept": "application/json",
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def extract_device_ids(data: dict) -> list[str]:
    """Extract unique VMS device IDs from a Digitraffic signs response."""

    features = data.get("features")

    if not isinstance(features, list):
        return []

    device_ids = []

    for feature in features:
        if not isinstance(feature, dict):
            continue

        properties = feature.get("properties")

        if not isinstance(properties, dict):
            continue

        device_id = properties.get("id")

        if isinstance(device_id, str) and device_id:
            device_ids.append(device_id)

    return sorted(set(device_ids))


def main() -> None:
    """Fetch VMS devices and scan their history over a date range."""

    parser = argparse.ArgumentParser(
        description="Scan Digitraffic VMS history availability."
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Number of devices to process.",
    )

    parser.add_argument(
        "--from",
        dest="start_date",
        type=date.fromisoformat,
        required=True,
        help="Start date in YYYY-MM-DD format",
    )

    parser.add_argument(
        "--to",
        dest="end_date",
        type=date.fromisoformat,
        required=True,
        help="End date in YYYY-MM-DD format",
    )

    args = parser.parse_args()

    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be zero or greater")

    if args.limit is None:
        parser.error("--limit is required while multi-device scanning is experimental")

    if args.start_date > args.end_date:
        parser.error("--from must be before or equal to --to")

    data = fetch_signs()
    device_ids = extract_device_ids(data)

    print(f"Found {len(device_ids)} unique VMS device IDs.")

    device_ids = device_ids[:args.limit]

    print(f"Processing {len(device_ids)} VMS device IDs.")

    # Scan each device's history within the specified date range.
    results = []

    for device_id in device_ids:
        print()
        print(f"Scanning {device_id}...")

        result = scan_device_history(
            device_id=device_id,
            start_date=args.start_date,
            end_date=args.end_date,
            verbose=False,
        )

        print(
            f"{device_id}: "
            f"{result['earliest_observed_date'] or 'no observations'}"
        )

        results.append(result)

    print()
    print(f"Collected {len(results)} scan results.")


if __name__ == "__main__":
    main()