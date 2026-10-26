# travel-connection-check

![travel-connection-check](social-preview.png)

Is the hotel Wi‑Fi, the café hotspot or your travel eSIM actually good enough for a video call? Run one command, get **latency, jitter, packet loss and download speed**, and keep a CSV log of every network you test across countries. It also tells you **how much data the test itself used**, and what that cost at your per-GB rate.

Maintained by [NXTL eSIM](https://nxtlsim.com). Works on any connection and any provider.

## Who it's for
- Digital nomads and remote workers comparing hotel Wi‑Fi vs mobile data before a call.
- Travellers logging how their eSIM performs per country and network.
- Teams checking a backup or failover line (see [esim-iot-backup-guides](https://github.com/nxtlsim/esim-iot-backup-guides)).

## Quick start
```bash
git clone https://github.com/nxtlsim/travel-connection-check
cd travel-connection-check
python3 travel_connection_check.py --country JP --network "Docomo via eSIM"
```
No dependencies: Python 3.8+ standard library only. Works on macOS, Linux, Windows and Termux (Android).

Example output:
```
Testing via Cloudflare edge VNO (your IP country: LT)
Latency     21.3 ms (median)   Jitter    1.5 ms   Loss   0.0 %
Download    72.4 Mbps (10.0 MB in 1.1 s)
Data used by this test: ~10.05 MB (approx.)
Estimated cost at 2.5 EUR/GB: 0.0251 EUR
Logged to connection_log.csv
```

## Options
| Flag | Default | Meaning |
|---|---|---|
| `--country` | | Free-text label stored in the CSV |
| `--network` | | Carrier / network name you are on (you type it) |
| `--mb` | `10` | Download test size in MB. Lower it on metered data |
| `--pings` | `10` | Latency probes (TCP connect to port 443, no root needed) |
| `--no-download` | | Latency only, uses about 0.05 MB |
| `--price-per-gb` | | Your data rate per GB, to estimate what the test cost |
| `--currency` | `EUR` | Label for the price |
| `--csv` | `connection_log.csv` | File to append results to |

## Estimating the cost of the test
On pay-as-you-go mobile data every MB counts. Pass your own rate:

```bash
python3 travel_connection_check.py --mb 5 --price-per-gb 3.20 --currency EUR
```
With NXTL eSIM, look up the per-GB rate for the country and network you are on at [nxtlsim.com/pricing](https://nxtlsim.com/pricing/) or the country page (e.g. [Japan](https://nxtlsim.com/esim/japan/)), then pass it with `--price-per-gb`. No prices are hard-coded here, so the estimate always uses the rate you enter.

## How it measures
- **Latency/jitter/loss:** TCP connect time to `speed.cloudflare.com:443`; jitter = mean difference between consecutive probes; failed connects count as loss.
- **Download:** `https://speed.cloudflare.com/__down?bytes=N` (Cloudflare's public speed-test endpoint).
- **Location:** `https://speed.cloudflare.com/cdn-cgi/trace` gives the Cloudflare edge and your IP's country.
- **Data used:** bytes downloaded + an approximate 4 KB per connection. An estimate, not a carrier-metered figure.

## CSV columns
`timestamp_utc, country, network, cf_colo, ip_country, latency_ms, jitter_ms, loss_pct, download_mbps, data_used_mb, price_per_gb, currency, est_cost`

## Links
- NXTL eSIM, pay-as-you-go travel data: https://nxtlsim.com
- Destinations: https://nxtlsim.com/esim-destinations/

## License
MIT © NXTL eSIM. This repository is maintained by NXTL eSIM. Cloudflare is a trademark of Cloudflare, Inc.; this project is not affiliated with Cloudflare.
