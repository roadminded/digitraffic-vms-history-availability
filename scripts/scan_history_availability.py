#!/usr/bin/env python3
"""
Scan Digitraffic VMS history availability across multiple devices.

The initial version fetches the current VMS device list and extracts
unique device IDs for later history scanning.
"""

import argparse

import requests


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
    """Fetch and summarize the current VMS device list."""

    parser = argparse.ArgumentParser(
        description="Scan Digitraffic VMS history availability."
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of devices to process.",
    )

    args = parser.parse_args()

    data = fetch_signs()
    device_ids = extract_device_ids(data)

    print(f"Found {len(device_ids)} unique VMS device IDs.")

    if args.limit is not None:
        device_ids = device_ids[:args.limit]

    print(f"Processing {len(device_ids)} VMS device IDs.")

    for device_id in device_ids:
        print(device_id)


if __name__ == "__main__":
    main()