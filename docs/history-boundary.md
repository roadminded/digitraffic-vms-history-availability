# VMS history availability boundary

Digitraffic has stored variable sign data and supported history queries since
at least September 2019:

- `DEVICE_DATA` storage was introduced in September 2019.
- A variable sign history query was added shortly afterwards.
- History functionality was further developed during 2020–2021.

However, initial API observations suggest that the
**oldest history currently retrievable for some long-lived devices may begin around 2021-10-28**.

This date should **not yet be treated as a confirmed global retention boundary**.
It may represent a shared migration, cleanup, or other historical data cutoff
rather than the beginning of VMS data collection.

The scanner can be used to test whether multiple older devices converge on
the same earliest retrievable date. If they do, this may provide a practical
lower bound for future scans.

References:

- Digitraffic `DPO-864` VMS data storage, September 2019
- Digitraffic `DPO-864` history implementation, September 2019
- Digitraffic `DPO-1186` history improvements, September 2020