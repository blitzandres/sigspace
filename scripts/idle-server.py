#!/usr/bin/env python3
"""Static SIGSPACE preview. Exits after 1 hour with no requests."""
from __future__ import annotations

import http.server
import os
import socketserver
import sys
import threading
import time

PORT = int(os.environ.get("PORT", "8765"))
IDLE = int(os.environ.get("IDLE_SECONDS", "3600"))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

last = time.time()
lock = threading.Lock()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        global last
        with lock:
            last = time.time()
        return super().do_GET()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def watch() -> None:
    while True:
        time.sleep(15)
        with lock:
            idle = time.time() - last
        if idle >= IDLE:
            sys.stderr.write(
                "\n[idle-server] no requests for %ds, shutting down to save resources\n"
                % int(idle)
            )
            os._exit(0)


if __name__ == "__main__":
    threading.Thread(target=watch, daemon=True).start()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        sys.stderr.write(
            "[idle-server] http://127.0.0.1:%d/   idle-timeout=%ds\n" % (PORT, IDLE)
        )
        httpd.serve_forever()
