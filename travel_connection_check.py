#!/usr/bin/env python3
"""travel-connection-check: log latency, jitter, packet loss and download speed on any network.

Uses public Cloudflare speed-test endpoints (speed.cloudflare.com). Standard library only.
Maintained by NXTL eSIM (https://nxtlsim.com).
"""
import argparse, csv, os, socket, statistics, sys, time, urllib.request
from datetime import datetime, timezone

HOST = "speed.cloudflare.com"
DOWN_URL = "https://speed.cloudflare.com/__down?bytes={n}"
TRACE_URL = "https://speed.cloudflare.com/cdn-cgi/trace"
UA = {"User-Agent": "travel-connection-check/1.0 (+https://github.com/nxtlsim/travel-connection-check)"}


def tcp_ping(host, count, timeout):
    """TCP connect RTT to port 443 (works without root, unlike ICMP). Failed connects count as loss."""
    rtts = []
    for _ in range(count):
        t0 = time.perf_counter()
        try:
            with socket.create_connection((host, 443), timeout=timeout):
                rtts.append((time.perf_counter() - t0) * 1000)
        except OSError:
            pass
        time.sleep(0.2)
    loss = 100.0 * (count - len(rtts)) / count
    jitter = statistics.mean(abs(a - b) for a, b in zip(rtts, rtts[1:])) if len(rtts) > 1 else 0.0
    return rtts, loss, jitter


def trace():
    try:
        with urllib.request.urlopen(urllib.request.Request(TRACE_URL, headers=UA), timeout=10) as r:
            return dict(l.split("=", 1) for l in r.read().decode().splitlines() if "=" in l)
    except Exception:
        return {}


def download(total_bytes, timeout):
    """Download total_bytes in chunks of up to 25 MB; returns (bytes_received, seconds)."""
    got, t0 = 0, time.perf_counter()
    remaining = total_bytes
    while remaining > 0:
        n = min(remaining, 25_000_000)
        req = urllib.request.Request(DOWN_URL.format(n=n), headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            while chunk := r.read(65536):
                got += len(chunk)
        remaining -= n
    return got, time.perf_counter() - t0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check connection quality and log it to CSV.")
    ap.add_argument("--country", default="", help="label, e.g. JP or 'Japan'")
    ap.add_argument("--network", default="", help="carrier/network name you are on, e.g. 'NXTL eSIM / Docomo'")
    ap.add_argument("--mb", type=float, default=10, help="download test size in MB (default 10)")
    ap.add_argument("--pings", type=int, default=10, help="number of latency probes (default 10)")
    ap.add_argument("--no-download", action="store_true", help="latency only (uses ~0.1 MB or less)")
    ap.add_argument("--price-per-gb", type=float, help="your data rate per GB to estimate the test's cost")
    ap.add_argument("--currency", default="EUR", help="currency label for --price-per-gb")
    ap.add_argument("--csv", default="connection_log.csv", help="CSV file to append to")
    ap.add_argument("--timeout", type=float, default=30)
    a = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    info = trace()
    print(f"Testing via Cloudflare edge {info.get('colo', '?')} (your IP country: {info.get('loc', '?')})")

    rtts, loss, jitter = tcp_ping(HOST, a.pings, a.timeout / 3)
    lat = statistics.median(rtts) if rtts else float("nan")
    print(f"Latency  {lat:7.1f} ms (median)   Jitter {jitter:6.1f} ms   Loss {loss:5.1f} %")

    got, secs, mbps = 0, 0.0, float("nan")
    if not a.no_download:
        try:
            got, secs = download(int(a.mb * 1_000_000), a.timeout)
            mbps = got * 8 / secs / 1_000_000
            print(f"Download {mbps:7.1f} Mbps ({got/1e6:.1f} MB in {secs:.1f} s)")
        except Exception as e:
            print(f"Download failed: {e}")

    # Approximate data used: payload + ~4 KB per HTTPS/TCP handshake (estimate, not metered).
    overhead = (len(rtts) + 3) * 4096
    used_mb = (got + overhead) / 1_000_000
    print(f"Data used by this test: ~{used_mb:.2f} MB (approx.)")
    cost = ""
    if a.price_per_gb is not None:
        cost = round(used_mb / 1000 * a.price_per_gb, 4)
        print(f"Estimated cost at {a.price_per_gb} {a.currency}/GB: {cost} {a.currency}")

    row = {"timestamp_utc": ts, "country": a.country, "network": a.network,
           "cf_colo": info.get("colo", ""), "ip_country": info.get("loc", ""),
           "latency_ms": "" if lat != lat else round(lat, 1), "jitter_ms": round(jitter, 1), "loss_pct": round(loss, 1),
           "download_mbps": "" if mbps != mbps else round(mbps, 2), "data_used_mb": round(used_mb, 2),
           "price_per_gb": a.price_per_gb if a.price_per_gb is not None else "",
           "currency": a.currency if a.price_per_gb is not None else "", "est_cost": cost}
    new = not os.path.exists(a.csv)
    with open(a.csv, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)
    print(f"Logged to {a.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
