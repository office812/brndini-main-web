#!/usr/bin/env python3
"""Read-only checks for Round 7 plan (no credentials)."""
from __future__ import annotations

import json
import re
import urllib.request

BASE = "https://brndini.co.il"
PAGE_ID = 1851
POST_IDS = (322835, 322826, 322505)
MARKER = "מופיעים כל הפוסטים בנושא"


def main() -> None:
    req = urllib.request.Request(
        f"{BASE}/wp-json/wp/v2/pages/{PAGE_ID}",
        headers={"User-Agent": "verify-plan-round7"},
    )
    page = json.loads(urllib.request.urlopen(req, timeout=60).read())
    html = page.get("content", {}).get("rendered", "") or ""
    cat = "category/%d7%90%d7%aa%d7%a8%d7%99%d7%9d"
    print("[hub 1851] category link in body:", cat in html)
    print("[hub 1851] Round-7 CTA marker:", MARKER in html)

    for pid in POST_IDS:
        r = urllib.request.Request(
            f"{BASE}/wp-json/wp/v2/posts/{pid}",
            headers={"User-Agent": "verify-plan-round7"},
        )
        post = json.loads(urllib.request.urlopen(r, timeout=60).read())
        desc = (post.get("yoast_head_json") or {}).get("description") or ""
        print(f"[post {pid}] yoast description length: {len(desc)}")
        if len(desc) > 160:
            print(f"  snippet: {desc[:100]}…")


if __name__ == "__main__":
    main()
