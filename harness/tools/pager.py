"""A stand-in pager. Alertmanager posts to it; it prints each notification
and keeps them, so `make pages` and the rehearsal can read them back.

    POST /alert    Alertmanager's webhook
    GET  /pages    every notification received, oldest first
    DELETE /pages  forget them
"""

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

pages = []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def reply(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
        for alert in body.get("alerts", []):
            page = {
                "received_at": datetime.now(timezone.utc).isoformat(),
                "status": alert.get("status"),
                "alert": alert.get("labels", {}).get("alertname"),
                "labels": alert.get("labels", {}),
                "annotations": alert.get("annotations", {}),
            }
            pages.append(page)
            print(json.dumps(page), flush=True)
        self.reply(200, {"ok": True})

    def do_GET(self):
        self.reply(200, pages)

    def do_DELETE(self):
        pages.clear()
        self.reply(200, {"cleared": True})


ThreadingHTTPServer(("0.0.0.0", 9099), Handler).serve_forever()
