# Digitraffic VMS History Availability

Tracks the earliest retrievable variable message sign (VMS) history from
Finland's Digitraffic road traffic API, operated by Fintraffic Road.

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
- scheduled twice-daily scanning with GitHub Actions
- configurable delay between history API requests
- scan status summaries and completion progress for selected device sets

The current implementation is intentionally small and focused on practical
history availability checks.

The current Digitraffic `/api/variable-sign/v1/signs` response contains
more than 500 unique published VMS device IDs, providing a substantial
device set for history availability scanning.

## Quick start

Install dependencies:

```bash
pip install -r requirements.txt
```

Set Digitraffic user header:

```bash
export DIGITRAFFIC_USER="MyOrg/vms-history-scan"
```

Use the provided `test_devices.txt` containing one VMS device ID per line,
then run:

```bash
python scripts/scan_history_availability.py \
  --device-file test_devices.txt \
  --request-delay 1.0
```

For selected-device scanning, request delays, scheduled runs,
and inspection commands, see the [Usage guide](docs/usage.md)

## Historical boundary

The project currently uses **2021-01-01** as its historical scan lower bound.
This is a practical project boundary, not a limitation of the Digitraffic API.

For details on historical data availability, retention and scan boundary
configuration, see [`docs/history-boundary.md`](docs/history-boundary.md)

## Priority requests

If you need availability information for specific VMS devices, you are welcome
to open an issue and suggest device IDs for prioritised scanning.

## Roadmap

Completed and planned changes. Planned items are potential future improvements
and do not represent commitments.

- [x] Create initial VMS history inspection script
- [x] Verify date-specific history queries with `effectiveDate`
- [x] Add date-range inspection for a single device
- [x] Add resumable multi-device history scanning
- [x] Add persistent scan state
- [x] Add selected-device scanning from a file
- [x] Add scheduled background scanning
- [x] Add scan summary output for the selected device set (`--device-file`),
      including counts for completed, in-progress, error, and no-observation
      devices
- [ ] Add automated tests
- [ ] Add selected-device rescanning ("reset") from an earlier lower bound
      using a device list file
- [ ] Generate `data/latest.json` and `data/latest.csv` as result summaries
- [ ] Publish automatically updated VMS history availability statistics
      in the GitHub README

## Data source

Data is retrieved from the Finnish Digitraffic road traffic API,
operated by Fintraffic Road.

- [Digitraffic Road Traffic API documentation](https://www.digitraffic.fi/en/road-traffic/)
- [Digitraffic Variable Signs](https://www.digitraffic.fi/en/road-traffic/#variable-signs)

For historical background and retention information, see
[`docs/history-boundary.md`](docs/history-boundary.md).

## License

The source code in this repository is licensed under the MIT License.

See [LICENSE](LICENSE).

Data retrieved from Digitraffic remains subject to the terms and conditions
applicable to the original data source.

## Maintainer

RoadMinded Systems Oy
