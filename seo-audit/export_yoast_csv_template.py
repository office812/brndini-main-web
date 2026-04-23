#!/usr/bin/env python3
"""
Export a CSV template for custom Yoast SEO titles (and optional meta descriptions).

Columns:
  type, id, url, post_title, yoast_title_now, yoast_desc_now, seo_title, meta_desc

Fill seo_title + meta_desc (leave blank to skip updating that field on import).
Requires: mu-plugins/brndini-yoast-rest-meta.php on the site for import to work.

Usage:
  export WORDPRESS_USERNAME=... WORDPRESS_APP_PASSWORD=...
  python3 seo-audit/export_yoast_csv_template.py > seo-custom-export.csv
"""
from __future__ import annotations

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
    token = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
    return f"Basic {token}"


def fetch_json(url: str) -> list | dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "brndini-yoast-export", "Authorization": auth_header()},
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
        return json.loads(r.read().decode())


def collect(endpoint: str, type_label: str) -> list[dict]:
    rows: list[dict] = []
    page = 1
    while True:
        url = f"{BASE}/wp-json/wp/v2/{endpoint}?context=edit&per_page=50&page={page}&status=publish"
        try:
            batch = fetch_json(url)
        except urllib.error.HTTPError as e:
            if e.code == 400:
                break
            raise
        if not batch:
            break
        for p in batch:
            tid = p["id"]
            link = p.get("link", "")
            title_obj = p.get("title") or {}
            post_title = title_obj.get("raw") or title_obj.get("rendered", "")
            yo_title = (p.get("yoast_seo_title") or "").strip()
            yo_desc = (p.get("yoast_seo_metadesc") or "").strip()
            meta = p.get("meta") or {}
            if not yo_title:
                yo_title = meta.get("_yoast_wpseo_title") or ""
            if not yo_desc:
                yo_desc = meta.get("_yoast_wpseo_metadesc") or ""
            yj = p.get("yoast_head_json") or {}
            if not yo_title:
                yo_title = yj.get("title", "") or ""
            if not yo_desc:
                yo_desc = yj.get("description", "") or ""
            rows.append(
                {
                    "type": type_label,
                    "id": tid,
                    "url": link,
                    "post_title": post_title.replace("\n", " ").strip(),
                    "yoast_title_now": (yo_title or "").replace("\n", " ").strip(),
                    "yoast_desc_now": (yo_desc or "").replace("\n", " ").strip(),
                    "seo_title": "",
                    "meta_desc": "",
                }
            )
        if len(batch) < 50:
            break
        page += 1
        time.sleep(0.15)
    return rows


def main() -> None:
    rows = collect("posts", "post") + collect("pages", "page")
    w = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            "type",
            "id",
            "url",
            "post_title",
            "yoast_title_now",
            "yoast_desc_now",
            "seo_title",
            "meta_desc",
        ],
        extrasaction="ignore",
    )
    w.writeheader()
    for row in rows:
        w.writerow(row)
    print(f"# Exported {len(rows)} rows", file=sys.stderr)


if __name__ == "__main__":
    main()
