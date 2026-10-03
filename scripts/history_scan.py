"""
Scan Digitraffic VMS history for a single device over a date range.

The module provides functions to fetch historical data for a specific
VMS device and summarize the observations found within the requested period.
"""
from datetime import date, timedelta
import time

import requests


API_URL = "https://tie.digitraffic.fi/api/variable-sign/v1/signs/history"
DIGITRAFFIC_USER = "RoadMinded/digitraffic-vms-history-availability"

# Delay between API requests to reduce the risk of rate limiting.
REQUEST_DELAY_SECONDS = 0.2


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
    verbose: bool = True,
) -> dict[str, object]:
    """Scan a date range and return a summary of available VMS history."""

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
            if verbose:
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

        if verbose:
            print(f"{date_text}: {len(observations)}")

        time.sleep(REQUEST_DELAY_SECONDS)

    earliest_observed_date = (
        earliest_effect_date[:10]
        if earliest_effect_date
        else None
    )

    return {
        "device_id": device_id,
        "scan_start_date": start_date.isoformat(),
        "scan_end_date": end_date.isoformat(),
        "earliest_effect_date": earliest_effect_date,
        "latest_effect_date": latest_effect_date,
        "days_checked": days_checked,
        "days_with_observations": days_with_observations,
        "observations": total_observations,
        "earliest_observed_date": earliest_observed_date,
    }

