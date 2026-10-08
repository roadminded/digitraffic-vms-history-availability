#!/usr/bin/env python3
"""
Inspect the Digitraffic VMS signs endpoint.

The script fetches the current variable sign dataset and prints a short
summary of the response structure for manual inspection.
"""

import json

import requests
from digitraffic_config import get_digitraffic_user


API_URL = "https://tie.digitraffic.fi/api/variable-sign/v1/signs"
DIGITRAFFIC_USER = get_digitraffic_user()


def fetch_signs() -> object:
    """Fetch the current VMS dataset from the Digitraffic API."""

    response = requests.get(
        API_URL,
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
        print(f"Response body: {response.text[:500]}")

    response.raise_for_status()

    return response.json()


def inspect_response(data: object) -> None:
    """Print a short summary of the current VMS response."""

    print()
    print(f"Top-level type: {type(data).__name__}")

    if isinstance(data, dict):
        print(f"Top-level keys: {', '.join(data.keys())}")

        features = data.get("features")

        if isinstance(features, list):
            print(f"Features: {len(features)}")

            if features:
                print()
                print("First feature:")
                print(json.dumps(features[0], indent=2, ensure_ascii=False))

            return

    if isinstance(data, list):
        print(f"Items: {len(data)}")

        if data:
            print()
            print("First item:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))

        return

    print("Unexpected response structure.")


def get_device_ids(data: object) -> list[str]:
    """Extract VMS device IDs from a Digitraffic signs response."""

    if not isinstance(data, dict):
        return []

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

    return device_ids


def main() -> None:
    """Fetch and inspect the current VMS dataset."""

    data = fetch_signs()
    inspect_response(data)

    device_ids = get_device_ids(data)

    print()
    print(f"Device IDs: {len(device_ids)}")
    print(f"Unique device IDs: {len(set(device_ids))}")
    print("First 10 device IDs:")

    for device_id in device_ids[:10]:
        print(device_id)


if __name__ == "__main__":
    main()