# VMS history availability boundary

Finland's Digitraffic.fi service, operated by Fintraffic Road, has stored
variable sign data and supported history queries since at least September 2019:

- `DEVICE_DATA` storage was introduced in September 2019.
- A variable sign history query was added shortly afterwards.

## Project VMS history boundary

For this project, the historical scan lower bound is currently set to
**2021-01-01**.

This is a practical project boundary, not a statement that older VMS history
does not exist. The Digitraffic API may contain retrievable observations from
before this date.

## Project scanner functionality

The scanner advances forward from the configured lower bound until it finds
the earliest retrievable observation for each device. This makes it possible
to document practical history availability on a device-by-device basis.

The earliest retrievable date may differ between devices and should not be
interpreted as a confirmed global retention boundary. Differences may reflect
device commissioning dates, migrations, cleanup, historical data gaps, or
other changes in the source data.

## References

Relevant VMS development items are documented in the
[Digitraffic Development Roadmap](https://www.digitraffic.fi/en/development-roadmap/)

- Digitraffic `DPO-864` — variable speed limit signs and information boards,
  September 2019