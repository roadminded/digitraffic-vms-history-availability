# Digitraffic VMS History Availability

Tracks the earliest retrievable variable message sign (VMS) history from the Finnish Digitraffic road traffic API.

## Purpose

Digitraffic provides historical data for variable message signs.
The practical availability of older history may vary by device and over time.

This project aims to determine and publish the earliest VMS observation that can currently be retrieved for each device. The resulting data can help users estimate whether a requested historical analysis period is available before running larger queries.

## Project status

Early development.

The first step is to study the current Digitraffic VMS history API behaviour
and define a reliable method for determining historical data availability.

Published results should not be interpreted as device commissioning dates or as proof of continuous data coverage.

## Roadmap

- [x] Create initial VMS history inspection script
- [x] Verify date-specific history queries with `effectiveDate`
- [x] Add date-range inspection for a single device
- [ ] Define a reliable method for finding the earliest retrievable observation
- [ ] Generate `data/latest.json` and `data/latest.csv`
- [ ] Add automated tests
- [ ] Add scheduled GitHub Actions update

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

Data retrieved from Digitraffic remains subject to the terms and conditions applicable to the original data source.

## Maintainer

RoadMinded Systems Oy
