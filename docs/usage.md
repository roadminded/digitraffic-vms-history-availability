# Usage

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your own Digitraffic user identifier before running the scripts:

```bash
export DIGITRAFFIC_USER="MyOrg/vms-history-scan"
```

## Scan selected devices

Scan a selected set of VMS devices using a text file containing
one device ID per line:

```bash
python scripts/scan_history_availability.py \
  --device-file test_devices.txt
```

Example `test_devices.txt`:

```text
KRM01
KRM010305
KRM011552
```

When scanning devices from a file, the script also prints a summary of device
statuses and overall completion progress.

## Scan incomplete devices

Scan the next incomplete devices from the current Digitraffic VMS list:

```bash
python scripts/scan_history_availability.py --limit 10
```

Completed devices are skipped automatically.
See [Scan state and resuming](#scan-state-and-resuming) for details.

## Request limits and delays

Each scan run is limited to 500 history API requests, with a maximum of
50 days per device.

The `--request-delay` option controls the delay between history API requests
in seconds (default: 0.2 seconds).

For example, to use a slower request rate:

```bash
python scripts/scan_history_availability.py \
  --limit 10 \
  --request-delay 2.0
```

The delay controls request pacing but does not guarantee a fixed
API request rate.

## GitHub Actions scheduling

GitHub Actions runs the background scan twice daily at 00:17 and 15:17 UTC,
using a 2-second request delay.

Each run selects up to 10 incomplete devices and uses a maximum of
500 history API requests.

Scheduled runs may start later than their configured times due to
GitHub Actions scheduling delays.

## Inspect a single device

For quick manual inspection of one VMS device, the script queries the
default recent history returned by the Digitraffic API:

```bash
python scripts/inspect_history.py KRM010305
```

To inspect history for a specific historical date, use `--date`:

```bash
python scripts/inspect_history.py KRM010305 --date 2021-01-02
```

The helper prints the request URL, HTTP status, response type, number of
returned observations, earliest and latest `effectDate` values, and the first
returned observation.

These inspection commands do not update `data/state.json`.

## Scan state and resuming

Scan progress is stored in `data/state.json`, including the verification range,
current scan cursor, and status of each device.

The state is saved after each processed device and when the scan exits normally
or is interrupted. Subsequent runs automatically resume incomplete device scans
from their stored cursors.

Devices with `complete` or `no_observations` status are skipped in normal `--limit`
scans. When using `--device-file`, all specified devices are included, but completed
devices require no additional history requests.

GitHub Actions also commits updated scan state to the repository. Before running
local scans, pull the latest changes:

```bash
git pull
```

After a local scan, commit and push the updated `data/state.json` to keep
the GitHub Actions scan in sync.

Avoid running local and GitHub Actions scans simultaneously against different
copies of the state file.