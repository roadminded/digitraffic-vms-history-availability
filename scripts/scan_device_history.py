#!/usr/bin/env python3
"""
Scan Digitraffic VMS history for a single device over a date range.

The script queries one UTC date at a time and summarizes the observations
found within the requested period.
"""

import argparse
from datetime import date, timedelta
import time

import requests


API_URL = "https://tie.digitraffic.fi/api/variable-sign/v1/signs/history"
DIGITRAFFIC_USER = "RoadMinded/digitraffic-vms-history-availability"

REQUEST_DELAY_SECONDS = 0.2 # Delay between API requests in seconds to avoid rate limiting


def fetch_history(device_id: str, effective_date: str) -> list[dict]:
    """Fetch VMS history for one device and one date."""

    response = requests.get(
        API_URL,
        params={
            "deviceId": device_id,
            "effectiveDate": effective_date,
        },
        headers={
            "Digitraffic-User": DIGITRAFFIC_USER,
            "Accept": "application/json",
        },
        timeout=30,
    )

    if not response.ok:
        print(
            f"{effective_date}: HTTP {response.status_code} "
            f"{response.text[:200]}"
        )

    response.raise_for_status()

    return response.json()


def iter_dates(start_date: date, end_date: date):
    """Yield dates from start_date to end_date, inclusive."""

    current = start_date

    while current <= end_date:
        yield current
        current += timedelta(days=1)


def scan_device_history(
    device_id: str,
    start_date: date,
    end_date: date,
) -> None:
    """Scan a date range and print a summary of available VMS history."""

    days_checked = 0
    days_with_observations = 0
    total_observations = 0

    earliest_effect_date = None
    latest_effect_date = None

    for current_date in iter_dates(start_date, end_date):
        date_text = current_date.isoformat()

        observations = fetch_history(
            device_id=device_id,
            effective_date=date_text,
        )

        days_checked += 1

        if not observations:
            print(f"{date_text}: 0")
            time.sleep(REQUEST_DELAY_SECONDS)
            continue

        days_with_observations += 1
        total_observations += len(observations)

        effect_dates = [
            item.get("effectDate")
            for item in observations
            if isinstance(item, dict) and item.get("effectDate")
        ]

        if effect_dates:
            day_earliest = min(effect_dates)
            day_latest = max(effect_dates)

            if (
                earliest_effect_date is None
                or day_earliest < earliest_effect_date
            ):
                earliest_effect_date = day_earliest

            if (
                latest_effect_date is None
                or day_latest > latest_effect_date
            ):
                latest_effect_date = day_latest

        print(f"{date_text}: {len(observations)}")

        time.sleep(REQUEST_DELAY_SECONDS)

    print()
    print(f"Device: {device_id}")
    print(f"Period: {start_date} - {end_date}")
    print(f"Days checked: {days_checked}")
    print(f"Days with observations: {days_with_observations}")
    print(f"Observations: {total_observations}")
    print(f"Earliest effectDate: {earliest_effect_date or 'none'}")
    print(f"Latest effectDate: {latest_effect_date or 'none'}")


def main() -> None:
    """Parse command-line arguments and scan one device over a date range."""

    parser = argparse.ArgumentParser(
        description="Scan Digitraffic VMS history over a date range."
    )

    parser.add_argument(
        "device_id",
        help="Digitraffic VMS device ID, e.g. KRM011552",
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

    if args.start_date > args.end_date:
        parser.error("--from must be before or equal to --to")

    scan_device_history(
        device_id=args.device_id,
        start_date=args.start_date,
        end_date=args.end_date,
    )


if __name__ == "__main__":
    main()