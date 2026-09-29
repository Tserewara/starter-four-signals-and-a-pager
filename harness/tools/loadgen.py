"""Traffic for the catalog.

    python3 loadgen.py --count 100            one sample, then a summary line
    python3 loadgen.py --rate 10              steady background traffic, forever

Only HTTP: it knows the service's URL and its one public route.
"""

import argparse
import os
import random
import statistics
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

SERVICE_URL = os.environ.get("SERVICE_URL", "http://localhost:8020")


def one() -> tuple[int, float]:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(f"{SERVICE_URL}/v1/catalog/sku-{random.randint(1, 40)}", timeout=10) as r:
            r.read()
            status = r.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        status = 0
    return status, (time.perf_counter() - started) * 1000


def sample(count: int) -> None:
    with ThreadPoolExecutor(10) as pool:
        results = list(pool.map(lambda _: one(), range(count)))
    latencies = sorted(ms for _, ms in results)
    errors = sum(1 for status, _ in results if status == 0 or status >= 500)
    p95 = latencies[max(0, int(len(latencies) * 0.95) - 1)]
    print(f"requests={count} errors={errors} error_rate={errors / count:.3f} "
          f"mean_ms={statistics.mean(latencies):.1f} p95_ms={p95:.1f}", flush=True)


def steady(rate: float) -> None:
    pool = ThreadPoolExecutor(64)
    while True:
        started = time.perf_counter()
        pool.submit(one)
        time.sleep(max(0.0, 1 / rate - (time.perf_counter() - started)))


parser = argparse.ArgumentParser()
parser.add_argument("--count", type=int)
parser.add_argument("--rate", type=float)
args = parser.parse_args()
if args.rate:
    steady(args.rate)
else:
    sample(args.count or 100)
