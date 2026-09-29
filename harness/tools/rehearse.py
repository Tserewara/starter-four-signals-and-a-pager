"""The paging rehearsal: turn a fault on while the background traffic runs,
and time how long until the pager receives a firing alert.

    python3 rehearse.py error      every fifth price-store call fails
    python3 rehearse.py latency    every price-store call takes 2.5 seconds

It first clears any fault and waits until no alert has fired for QUIET
seconds (200 by default, longer than the lab's slowest window), so a
rehearsal is never paged by what the one before it left in the windows. It
clears the fault again when it is done.
"""

import json
import os
import urllib.parse
import sys
import time
import urllib.request
from datetime import datetime

STORE = os.environ.get("STORE_URL", "http://store:9100")
PAGER = os.environ.get("PAGER_URL", "http://pager:9099")
PROM = os.environ.get("PROMETHEUS_URL", "http://prometheus:9090")
FAULTS = {"error": {"error_every": 5, "latency_ms": 250}, "latency": {"latency_ms": 2500}}
TIMEOUT = 300
QUIET = int(os.environ.get("QUIET", "200"))


def call(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read() or b"null")


def fired_recently() -> bool:
    """Any alert firing at some point in the last QUIET seconds. Prometheus's
    own ALERTS series, so it works whatever the rules are called."""
    query = urllib.parse.quote(f'max_over_time(ALERTS{{alertstate="firing"}}[{QUIET}s])')
    return bool(call("GET", f"{PROM}/api/v1/query?query={query}")["data"]["result"])


kind = sys.argv[1] if len(sys.argv) > 1 else "error"
call("DELETE", f"{STORE}/_control/fault")
waited = time.time()
if fired_recently():
    print(f"waiting until no alert has fired for {QUIET}s ...", flush=True)
while fired_recently():
    if time.time() - waited > QUIET + TIMEOUT:
        sys.exit("alerts keep firing with no fault on; check your rules")
    time.sleep(5)
call("DELETE", f"{PAGER}/pages")

call("PUT", f"{STORE}/_control/fault", FAULTS[kind])
t0 = time.time()
print(f"fault={kind} on at {datetime.now().strftime('%H:%M:%S')}", flush=True)
try:
    while time.time() - t0 < TIMEOUT:
        pages = [p for p in call("GET", f"{PAGER}/pages") if p["status"] == "firing"]
        if pages:
            first = pages[0]
            print(f"fault={kind} first_page={first['alert']} seconds={time.time() - t0:.0f}", flush=True)
            for key, value in first["annotations"].items():
                print(f"  {key}: {value}")
            break
        time.sleep(1)
    else:
        print(f"fault={kind} no page within {TIMEOUT}s", flush=True)
finally:
    call("DELETE", f"{STORE}/_control/fault")
