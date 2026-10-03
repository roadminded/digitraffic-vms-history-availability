# Digitraffic VMS History Availability

Tracks the earliest retrievable variable message sign (VMS) history from
the Finnish Digitraffic road traffic API.

## Purpose

Digitraffic provides historical data for variable message signs, but the
practical availability of older history may vary by device and over time.

This project scans VMS history availability and records the earliest
observation found for each device within a verified date range.

The results can help determine whether a requested historical analysis
period is available before running larger queries.

Published results should not be interpreted as device commissioning dates
or as proof of continuous data coverage.

## Current status

The project currently supports:

- persistent and resumable history scanning
- a configurable lower scan boundary (2021-01-01)
- scanning selected devices from a text file
- gradual background scanning of incomplete devices
- request limits and per-device scan limits
- persistent scan state in data/state.json
- scheduled weekly scanning with GitHub Actions

The current implementation is intentionally small and focused on practical
history availability checks.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Scan specific devices from a text file:

```bash
python scripts/scan_history_availability.py \
  --device-file test_devices.txt
```

The file contains one VMS device ID per line:

```text
KRM01
KRM010305
KRM011552
```

Scan the next incomplete devices from the current Digitraffic VMS list:

```bash
python scripts/scan_history_availability.py --limit 10
```

Completed devices are skipped automatically.

Scan progress is stored in:

```text
data/state.json
```

Interrupted or partial scans can continue from the stored cursor
on the next run.

## Historical boundary

The default verification boundary is:

```text
2021-01-01
```

This is a practical project boundary, not a claim that older
Digitraffic VMS data does not exist.

See [`docs/history-boundary.md`](docs/history-boundary.md)
for additional background.

## Priority requests and possible future improvements

If you need availability information for specific VMS devices, you are welcome
to open an issue and suggest device IDs for prioritised scanning.

Possible future improvements may include:

- geographic device selection using a bounding box
- GeoJSON or other area-based device selection
- published `latest.json` and `latest.csv` availability snapshots
- additional automated validation and tests

These are potential development directions rather than committed features.

## Roadmap

- [x] Create initial VMS history inspection script
- [x] Verify date-specific history queries with `effectiveDate`
- [x] Add date-range inspection for a single device
- [x] Add resumable multi-device history scanning
- [x] Add persistent scan state
- [x] Add selected-device scanning from a file
- [x] Add scheduled background scanning
- [ ] Generate `data/latest.json` and `data/latest.csv`
- [ ] Add automated tests

## Planned outputs

The project is expected to publish machine-readable availability data in
formats such as:

- `data/latest.json`
- `data/latest.csv`

These files may later be consumed by other applications and traffic analysis services.

## Data source

Data is retrieved from the Finnish Digitraffic road traffic API.

Digitraffic documentation:

https://www.digitraffic.fi/en/road-traffic/

## License

The source code in this repository is licensed under the MIT License.

See [LICENSE](LICENSE).

Data retrieved from Digitraffic remains subject to the terms and conditions
applicable to the original data source.

## Maintainer

RoadMinded Systems Oy
