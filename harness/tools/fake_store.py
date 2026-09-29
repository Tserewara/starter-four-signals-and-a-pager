"""The catalog's price store, faked. The service asks it for every SKU it
serves; the fault controls make it fail or slow down on demand.

    GET    /items/{sku}        {"sku": ..., "price": 1299, "currency": "BRL"}
    PUT    /_control/fault     {"error_every": N, "latency_ms": M}
    DELETE /_control/fault
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

state = {"error_every": 0, "latency_ms": 0, "calls": 0}
lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def reply(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self.reply(200, {"status": "ok"})
        if not self.path.startswith("/items/"):
            return self.reply(404, {"detail": "not found"})
        sku = self.path.removeprefix("/items/")
        with lock:
            state["calls"] += 1
            call, every, latency = state["calls"], state["error_every"], state["latency_ms"]
        if latency:
            time.sleep(latency / 1000)
        if every and call % every == 0:
            return self.reply(503, {"detail": "price store unavailable"})
        self.reply(200, {"sku": sku, "price": 1299, "currency": "BRL"})

    def do_PUT(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
        with lock:
            state.update(error_every=int(body.get("error_every", 0)),
                         latency_ms=int(body.get("latency_ms", 0)), calls=0)
            self.reply(200, {k: state[k] for k in ("error_every", "latency_ms")})

    def do_DELETE(self):
        with lock:
            state.update(error_every=0, latency_ms=0, calls=0)
        self.reply(200, {"cleared": True})


ThreadingHTTPServer(("0.0.0.0", 9100), Handler).serve_forever()
