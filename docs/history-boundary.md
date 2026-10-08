# VMS history availability boundary

Finland's Digitraffic.fi service, operated by Fintraffic Road, has stored
variable sign data and supported history queries since at least September 2019:

- `DEVICE_DATA` storage was introduced in September 2019.
- A variable sign history query was added shortly afterwards.

## Digitraffic history retention

According to Digitraffic support (8 October 2026), no fixed retention period
has currently been decided for VMS history data.

Historical data availability depends on when each device was connected to
the Digitraffic system.

This means there is no confirmed global history retention boundary, and
the earliest available observations may differ between devices.

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

- [Digitraffic Development Roadmap](https://www.digitraffic.fi/en/development-roadmap/)
  — DPO-864: Variable speed limit signs and information boards (September 2019).
- [Digitraffic support / Solita](https://groups.google.com/g/roaddigitrafficfi/c/kMuj5Zo-OaY)
  — Response on VMS history retention and device-specific availability (8 October 2026).