import argparse
import os
import statistics
import time
import urllib.error
import urllib.request

API_URL = os.environ.get("API_URL", "http://localhost:8020")


def run(count):
    latencies = []
    errors = 0
    for index in range(count):
        started = time.perf_counter()
        request = urllib.request.Request(f"{API_URL}/v1/catalog/sku-{index % 10}")
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                response.read()
                if response.status >= 500:
                    errors += 1
        except urllib.error.HTTPError as exc:
            errors += int(exc.code >= 500)
        except (urllib.error.URLError, TimeoutError):
            errors += 1
        latencies.append((time.perf_counter() - started) * 1000)
        time.sleep(0.01)
    ordered = sorted(latencies)
    p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
    print(f"requests={count} errors={errors} error_rate={errors / count:.3f} mean_ms={statistics.mean(latencies):.1f} p95_ms={p95:.1f}", flush=True)


parser = argparse.ArgumentParser()
parser.add_argument("--count", type=int, default=100)
parser.add_argument("--loop", action="store_true")
args = parser.parse_args()
if args.loop:
    while True:
        run(args.count)
        time.sleep(1)
else:
    run(args.count)
