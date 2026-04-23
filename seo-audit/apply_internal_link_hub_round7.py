#!/usr/bin/env python3
"""
Round 7 — internal link from the Website-building hub page (ID 1851) to the
"אתרים" category archive. Improves crawl paths for tools that weight *page*
inlinks more than *post* cross-links (paginated archive posts appear from
page 2 onward).

Requires Application Password auth (same vars as src/lib/wordpress.ts):
  export WORDPRESS_URL=https://brndini.co.il
  export WORDPRESS_USERNAME='...'
  export WORDPRESS_APP_PASSWORD='...'

Then: python3 seo-audit/apply_internal_link_hub_round7.py
"""
from __future__ import annotations

import base64
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("WORDPRESS_URL", "https://brndini.co.il").rstrip("/")
USER = os.environ.get("WORDPRESS_USERNAME", "").strip()
PASSWORD = os.environ.get("WORDPRESS_APP_PASSWORD", "").strip()

PAGE_ID = 1851
CATEGORY_URL = (
    "https://brndini.co.il/category/%d7%90%d7%aa%d7%a8%d7%99%d7%9d/"
)

MARKER_BEFORE = "</p>\n\n<p>מחפשים חברה"

EXTRA = (
    "</p>\n\n"
    "<p>רוצים להעמיק? בארכיון "
    f'<a href="{CATEGORY_URL}">מאמרים על בניית אתרים וחוויית משתמש</a> '
    "מופיעים כל הפוסטים בנושא, כולל תכנים חדשים שמוצגים בעמודים המאוחרים "
    "של הרשימה בעקבות עדכוני האתר.</p>\n\n"
    "<p>מחפשים חברה"
)


def auth_header() -> str:
    if not USER or not PASSWORD:
        print(
            "Missing WORDPRESS_USERNAME or WORDPRESS_APP_PASSWORD in environment.",
            file=sys.stderr,
        )
        sys.exit(2)
    token = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
    return f"Basic {token}"


def main() -> None:
    ctx = ssl.create_default_context()
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))

    get_req = urllib.request.Request(
        f"{BASE}/wp-json/wp/v2/pages/{PAGE_ID}?context=edit",
        headers={"User-Agent": "brndini-seo-round7", "Authorization": auth_header()},
    )
    try:
        with opener.open(get_req, timeout=60) as resp:
            page = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"GET page failed: {e.code} {e.read().decode()[:800]}", file=sys.stderr)
        sys.exit(1)

    rendered = page.get("content", {}).get("rendered", "") or ""
    if CATEGORY_URL in rendered and "מופיעים כל הפוסטים בנושא" in rendered:
        print("Hub page already contains Round-7 archive CTA; nothing to do.")
        return

    if MARKER_BEFORE not in rendered:
        print(
            "Unexpected page HTML: anchor text pattern not found; aborting.",
            file=sys.stderr,
        )
        sys.exit(1)

    new_html = rendered.replace(MARKER_BEFORE, EXTRA, 1)

    payload = json.dumps({"content": new_html}).encode()

    post_req = urllib.request.Request(
        f"{BASE}/wp-json/wp/v2/pages/{PAGE_ID}",
        data=payload,
        headers={
            "User-Agent": "brndini-seo-round7",
            "Authorization": auth_header(),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with opener.open(post_req, timeout=90) as resp:
            out = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"POST page failed: {e.code} {e.read().decode()[:800]}", file=sys.stderr)
        sys.exit(1)

    print("Updated page", PAGE_ID, "modified:", out.get("modified"))


if __name__ == "__main__":
    main()
