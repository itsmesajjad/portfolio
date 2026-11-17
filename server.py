#!/usr/bin/env python3
"""
Sajjad — portfolio server.

Serves the single-page portfolio and exposes /api/profile, a small,
dependency-free live feed of the public Behance profile (stats + projects).
Results are cached for 10 minutes.

Usage:
    python server.py                 # http://127.0.0.1:8000
    python server.py --port 5500
    python server.py --no-open       # do not launch a browser
    python server.py --host 0.0.0.0  # expose on your local network
"""

import argparse
import html as html_module
import json
import os
import re
import threading
import time
import urllib.request
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
BEHANCE_URL = "https://www.behance.net/sajjadhossain31"
CACHE_SECONDS = 600
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
}

_cache = {"at": 0.0, "data": None}
_cache_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Behance parsing
# ---------------------------------------------------------------------------
def _plain_text(html):
    """Reduce a page to readable text so stats are not confused with markup."""
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html_module.unescape(text)
    return re.sub(r"\s+", " ", text)


def _stat(text, label):
    """Read a stat such as 'Project Views 3,235' from the page text."""
    match = re.search(re.escape(label) + r"\s*([0-9][0-9,]*)", text)
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


def _projects(html, limit=12):
    """Extract public gallery links + cover images from the profile HTML."""
    ids = list(dict.fromkeys(re.findall(r"/gallery/(\d+)/", html)))
    projects = []

    for project_id in ids:
        slug_match = re.search(r"/gallery/%s/([A-Za-z0-9._-]+)" % project_id, html)
        if not slug_match:
            continue
        slug = slug_match.group(1)
        cover = None
        title = None

        for match in re.finditer(re.escape(project_id), html):
            segment = html[match.start(): match.start() + 6000]
            found = re.search(
                r'"covers":\{"allAvailable":\[\{"url":"(https:[^"]+?)"', segment
            )
            if not found:
                continue
            cover = found.group(1).replace("\\/", "/")
            name = re.search(r'"name":"([^"]{2,100})"', segment)
            title = name.group(1) if name else None
            break

        if not cover:
            continue

        if not title:
            title = slug.replace("-", " ").replace("_", " ")

        projects.append(
            {
                "id": project_id,
                "title": title,
                "slug": slug,
                "url": "https://www.behance.net/gallery/%s/%s" % (project_id, slug),
                "cover": cover,
            }
        )

        if len(projects) >= limit:
            break

    return projects


def fetch_profile():
    request = urllib.request.Request(BEHANCE_URL, headers=REQUEST_HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", "ignore")

    text = _plain_text(html)

    data = {
        "source": "behance",
        "url": BEHANCE_URL,
        "synced": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "views": _stat(text, "Project Views"),
        "appreciations": _stat(text, "Appreciations"),
        "followers": _stat(text, "Followers"),
        "following": _stat(text, "Following"),
        "projects": _projects(html),
    }

    if data["views"] is None and data["followers"] is None:
        raise RuntimeError("Behance response did not contain the expected stats")

    return data


def get_profile(force=False):
    with _cache_lock:
        cached = _cache["data"]
        fresh = (time.time() - _cache["at"]) < CACHE_SECONDS
        if cached and fresh and not force:
            return cached

    data = fetch_profile()

    with _cache_lock:
        _cache["data"] = data
        _cache["at"] = time.time()

    return data


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------
class PortfolioHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if self.path.split("?")[0].rstrip("/") == "/api/profile":
            self._send_profile()
            return
        super().do_GET()

    def _send_profile(self):
        try:
            payload = get_profile()
            body = json.dumps(payload).encode("utf-8")
            status = 200
        except Exception as exc:  # noqa: BLE001 - report any upstream failure
            body = json.dumps({"error": str(exc)}).encode("utf-8")
            status = 502

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        if self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-store")
        elif self.path in ("/", "/index.html"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        if args and str(args[0]).startswith("GET /api"):
            return
        super().log_message(fmt, *args)


def main():
    parser = argparse.ArgumentParser(description="Serve the Sajjad portfolio.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="port to listen on (default: 8000)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="host to bind (default: 127.0.0.1, use 0.0.0.0 for LAN)",
    )
    parser.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), PortfolioHandler)
    url = "http://%s:%d/" % ("127.0.0.1" if args.host == "0.0.0.0" else args.host, args.port)

    print("")
    print("  Sajjad — Portfolio")
    print("  ------------------------------")
    print("  Local:   %s" % url)
    print("  Live:    %s/api/profile" % url.rstrip("/"))
    print("  Behance: %s" % BEHANCE_URL)
    print("  Stop:    Ctrl + C")
    print("")

    # Warm the live-data cache in the background so the page syncs instantly.
    def warm():
        try:
            get_profile()
            print("  [live] Behance data cached.")
        except Exception as exc:  # noqa: BLE001
            print("  [live] Behance unavailable: %s" % exc)

    threading.Thread(target=warm, daemon=True).start()

    if not args.no_open:
        threading.Timer(0.9, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
