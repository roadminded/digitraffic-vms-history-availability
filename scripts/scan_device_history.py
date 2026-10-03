#!/usr/bin/env python3
"""
Scan Digitraffic VMS history for a single device over a date range.

The script queries one UTC date at a time and summarizes the observations
found within the requested period.
"""

import argparse
from datetime import date
import json

from history_scan import scan_device_history


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

    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the scan result as JSON.",
    )

    args = parser.parse_args()

    if args.start_date > args.end_date:
        parser.error("--from must be before or equal to --to")

    result = scan_device_history(
        device_id=args.device_id,
        start_date=args.start_date,
        end_date=args.end_date,
        verbose=not args.json,
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print()
    print(f"Device: {result['device_id']}")
    print(
        f"Period: {result['scan_start_date']} - "
        f"{result['scan_end_date']}"
    )
    print(f"Days checked: {result['days_checked']}")
    print(
        f"Days with observations: "
        f"{result['days_with_observations']}"
    )
    print(f"Observations: {result['observations']}")
    print(
        f"Earliest observed date: "
        f"{result['earliest_observed_date'] or 'none'}"
    )
    print(
        f"Earliest effectDate: "
        f"{result['earliest_effect_date'] or 'none'}"
    )
    print(
        f"Latest effectDate: "
        f"{result['latest_effect_date'] or 'none'}"
    )


if __name__ == "__main__":
    main()