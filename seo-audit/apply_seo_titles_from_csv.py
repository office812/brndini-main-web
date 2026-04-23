#!/usr/bin/env python3
"""
Apply custom Yoast SEO titles (and optional meta descriptions) from a CSV.

CSV columns (header required):
  type,id,seo_title,meta_desc
  — type: post | page
  — id: numeric WordPress ID
  — seo_title: written to _yoast_wpseo_title (empty cell = skip)
  — meta_desc: written to _yoast_wpseo_metadesc (empty cell = skip)

Prerequisite: upload mu-plugins/brndini-yoast-rest-meta.php to the site
(wp-content/mu-plugins/) so these meta keys are REST-writable.

Usage:
  export WORDPRESS_USERNAME=... WORDPRESS_APP_PASSWORD=...
  python3 seo-audit/apply_seo_titles_from_csv.py path/to/filled.csv
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

BASE = os.environ.get("WORDPRESS_URL", "https://brndini.co.il").rstrip("/")
USER = os.environ.get("WORDPRESS_USERNAME", "").strip()
PASSWORD = os.environ.get("WORDPRESS_APP_PASSWORD", "").strip()


def auth_header() -> str:
    if not USER or not PASSWORD:
        print("Set WORDPRESS_USERNAME and WORDPRESS_APP_PASSWORD", file=sys.stderr)
        sys.exit(2)
    return "Basic " + base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "User-Agent": "brndini-yoast-import",
            "Authorization": auth_header(),
            "Content-Type": "application/json",
        },
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=90, context=ctx) as r:
        return json.loads(r.read().decode())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    args = ap.parse_args()

    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("Empty CSV", file=sys.stderr)
            sys.exit(1)
        rows = list(reader)

    ok = 0
    skip = 0
    err = 0

    for row in rows:
        typ = (row.get("type") or "").strip().lower()
        rid = (row.get("id") or "").strip()
        seo_title = (row.get("seo_title") or "").strip()
        meta_desc = (row.get("meta_desc") or "").strip()

        if typ not in ("post", "page") or not rid.isdigit():
            skip += 1
            continue
        if not seo_title and not meta_desc:
            skip += 1
            continue

        meta: dict[str, str] = {}
        if seo_title:
            meta["_yoast_wpseo_title"] = seo_title
        if meta_desc:
            meta["_yoast_wpseo_metadesc"] = meta_desc

        endpoint = f"{BASE}/wp-json/wp/v2/{'posts' if typ == 'post' else 'pages'}/{rid}"
        try:
            out = post_json(endpoint, {"meta": meta})
            m = out.get("meta") or {}
            if seo_title and m.get("_yoast_wpseo_title") != seo_title:
                print(f"WARN {typ} {rid}: title may not persist (REST meta not registered?)", file=sys.stderr)
            ok += 1
            print(f"OK {typ} {rid}")
        except urllib.error.HTTPError as e:
            err += 1
            body = e.read().decode()[:400]
            print(f"ERR {typ} {rid} HTTP {e.code}: {body}", file=sys.stderr)
        time.sleep(0.2)

    print(f"\nDone: ok={ok} skip={skip} err={err}", file=sys.stderr)


if __name__ == "__main__":
    main()
