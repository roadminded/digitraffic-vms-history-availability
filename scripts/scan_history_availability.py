#!/usr/bin/env python3
"""
Scan Digitraffic VMS history availability across multiple devices.

The script fetches the current VMS device list and advances persistent
baseline scans for selected devices.
"""

import argparse
import json
from pathlib import Path
from datetime import date, datetime

import requests
from history_scan import advance_device_baseline

# Maximum number of VMS history API requests per script run.
MAX_HISTORY_REQUESTS_PER_RUN = 500

# Maximum number of days to scan for one device during a single run.
MAX_DAYS_PER_DEVICE_PER_RUN = 50

# Path to the JSON file where the script's state is stored.
STATE_FILE = Path("data/state.json")

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

    if not isinstance(data, dict):
        raise ValueError(
            "Unexpected /signs response type: "
            f"{type(data).__name__}"
        )

    features = data.get("features")

    if not isinstance(features, list):
        raise ValueError(
            "Digitraffic /signs response is missing "
            "a valid features list."
        )
    
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


def validate_device_state(
    device_id: str,
    device_state: object,
) -> None:
    """Validate one persistent device scan state."""

    if not isinstance(device_state, dict):
        raise ValueError(
            f"State for device {device_id} must be a JSON object."
        )

    status = device_state.get("status")

    valid_statuses = {
        "pending",
        "in_progress",
        "complete",
        "no_observations",
        "error",
    }

    if status not in valid_statuses:
        raise ValueError(
            f"Device {device_id} has invalid status: {status!r}"
        )

    date_fields = (
        "verified_from",
        "verified_through",
        "scan_cursor_date",
        "earliest_observed_date",
    )

    for field_name in date_fields:
        value = device_state.get(field_name)

        if value is None:
            continue

        if not isinstance(value, str):
            raise ValueError(
                f"Device {device_id} field {field_name} "
                "must be a date string or null."
            )

        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                f"Device {device_id} field {field_name} "
                f"contains an invalid date: {value!r}"
            ) from exc

    active_statuses = {
        "pending",
        "in_progress",
        "error",
    }

    if status in active_statuses:
        cursor = device_state.get("scan_cursor_date")

        if not isinstance(cursor, str):
            raise ValueError(
                f"Device {device_id} with status {status!r} "
                "must have a valid scan_cursor_date."
            )

    earliest_effect_date = device_state.get(
        "earliest_effect_date"
    )

    if earliest_effect_date is not None:
        if not isinstance(earliest_effect_date, str):
            raise ValueError(
                f"Device {device_id} field earliest_effect_date "
                "must be a datetime string or null."
            )

        try:
            datetime.fromisoformat(
                earliest_effect_date.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError(
                f"Device {device_id} field earliest_effect_date "
                f"contains an invalid datetime: "
                f"{earliest_effect_date!r}"
            ) from exc


def load_state() -> dict:
    """Load and validate persistent scan state from disk."""

    with STATE_FILE.open("r", encoding="utf-8") as file:
        state = json.load(file)

    if not isinstance(state, dict):
        raise ValueError("State file must contain a JSON object.")

    if state.get("schema_version") != 1:
        raise ValueError(
            "Unsupported or missing state schema_version."
        )

    scan_lower_bound = state.get("scan_lower_bound")

    if not isinstance(scan_lower_bound, str):
        raise ValueError(
            "State file is missing a valid scan_lower_bound."
        )

    try:
        date.fromisoformat(scan_lower_bound)
    except ValueError as exc:
        raise ValueError(
            "State file contains an invalid scan_lower_bound: "
            f"{scan_lower_bound!r}"
        ) from exc

    devices = state.get("devices")

    if not isinstance(devices, dict):
        raise ValueError(
            "State file is missing a valid devices object."
        )

    for device_id, device_state in devices.items():
        if not isinstance(device_id, str) or not device_id:
            raise ValueError(
                "State file contains an invalid device ID."
            )

        validate_device_state(
            device_id=device_id,
            device_state=device_state,
        )

    return state


def save_state(state: dict) -> None:
    """Save persistent scan state to disk atomically."""

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    temp_file = STATE_FILE.with_suffix(".tmp")

    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(
            state,
            file,
            indent=2,
            sort_keys=True,
        )
        file.write("\n")

    temp_file.replace(STATE_FILE)


def load_device_ids_from_file(path: Path) -> list[str]:
    """Load unique VMS device IDs from a text file."""

    device_ids = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            device_ids.append(line)

    return list(dict.fromkeys(device_ids))


def select_device_ids(
    available_device_ids: list[str],
    devices_state: dict,
    limit: int | None,
    device_file: Path | None,
) -> list[str]:
    """Select VMS device IDs based on CLI arguments."""

    if device_file is not None:
        requested_device_ids = load_device_ids_from_file(
            device_file
        )

        unknown_device_ids = [
            device_id
            for device_id in requested_device_ids
            if device_id not in available_device_ids
        ]

        if unknown_device_ids:
            print(
                "Warning: device ID(s) not present in the current "
                "/signs response: "
                + ", ".join(unknown_device_ids)
            )

        return requested_device_ids

    terminal_statuses = {
        "complete",
        "no_observations",
    }

    selectable_device_ids = [
        device_id
        for device_id in available_device_ids
        if (
            device_id not in devices_state
            or devices_state[device_id].get("status")
            not in terminal_statuses
        )
    ]

    return selectable_device_ids[:limit]


def main() -> None:
    """Fetch VMS devices and advance their persistent baseline scans."""

    parser = argparse.ArgumentParser(
        description="Scan Digitraffic VMS history availability."
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Number of devices to process.",
    )

    parser.add_argument(
        "--device-file",
        type=Path,
        help="Text file containing one VMS device ID per line.",
    )

    args = parser.parse_args()

    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be zero or greater")

    if args.limit is None and args.device_file is None:
        parser.error(
            "Either --limit or --device-file is required "
            "while multi-device scanning is experimental"
        )

    if args.limit is not None and args.device_file is not None:
        parser.error("--limit and --device-file cannot be used together")

    state = load_state()

    data = fetch_signs()
    available_device_ids = extract_device_ids(data)

    print(
        f"Found {len(available_device_ids)} unique VMS device IDs."
    )

    device_ids = select_device_ids(
        available_device_ids=available_device_ids,
        devices_state=state["devices"],
        limit=args.limit,
        device_file=args.device_file,
    )

    print(f"Processing {len(device_ids)} VMS device IDs.")

    remaining_requests = MAX_HISTORY_REQUESTS_PER_RUN

    # Advance the persistent baseline scan for each device within the request budget.
    devices_state = state.setdefault("devices", {})

    try:
        for device_id in device_ids:
            if remaining_requests <= 0:
                print("Request budget exhausted.")
                break

            print()
            print(f"Scanning {device_id}...")

            device_state = devices_state.get(device_id)

            if device_state is None:
                lower_bound = state["scan_lower_bound"]

                device_state = {
                    "status": "pending",
                    "verified_from": lower_bound,
                    "verified_through": None,
                    "scan_cursor_date": lower_bound,
                    "earliest_observed_date": None,
                    "earliest_effect_date": None,
                    "last_error": None,
                }

                devices_state[device_id] = device_state

            max_days = min(
                remaining_requests,
                MAX_DAYS_PER_DEVICE_PER_RUN,
            )

            scan_result = advance_device_baseline(
                device_id=device_id,
                device_state=device_state,
                max_days=max_days,
            )

            requests_used = scan_result["requests_used"]
            remaining_requests -= requests_used

            devices_state[device_id] = scan_result["state"]
            save_state(state)

            print(
                f"{device_id}: "
                f"{scan_result['state']['status']} "
                f"(requests: {requests_used})"
            )

    except KeyboardInterrupt:
        print()
        print("Scan interrupted by user.")

    finally:
        save_state(state)

    print()
    print(
        f"Run complete. Requests used: "
        f"{MAX_HISTORY_REQUESTS_PER_RUN - remaining_requests}"
    )


if __name__ == "__main__":
    main()