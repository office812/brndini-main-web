#!/usr/bin/env python3
"""
Apply Round-7 SEO plan items that touch WordPress (hub link + Yoast meta).

1) Page 1851 — inject visible paragraph linking to category archive "אתרים".
2) Posts 322835, 322826, 322505 — set Yoast meta description from the public
   excerpt (already &lt; 160 chars) if REST exposes writable meta.

Yoast *site-wide* post title template (%%title%% only) is NOT writable via
standard WP REST; use apply_yoast_post_title_template_round7.sh with WP-CLI
on the server, or wp-admin.

Credentials (pick one):
  export WORDPRESS_USERNAME=... WORDPRESS_APP_PASSWORD=...
Or create file seo-audit/credentials.local (gitignored), lines:
  WORDPRESS_USERNAME=...
  WORDPRESS_APP_PASSWORD=...
Optional: WORDPRESS_URL=https://brndini.co.il
"""
from __future__ import annotations

import base64
import html
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

def base_url() -> str:
    return os.environ.get("WORDPRESS_URL", "https://brndini.co.il").rstrip("/")

CRED_FILE = Path(__file__).resolve().parent / "credentials.local"

PAGE_ID = 1851
CATEGORY_URL = "https://brndini.co.il/category/%d7%90%d7%aa%d7%a8%d7%99%d7%9d/"
MARKER_BEFORE = "</p>\n\n<p>מחפשים חברה"
EXTRA = (
    "</p>\n\n"
    "<p>רוצים להעמיק? בארכיון "
    f'<a href="{CATEGORY_URL}">מאמרים על בניית אתרים וחוויית משתמש</a> '
    "מופיעים כל הפוסטים בנושא, כולל תכנים חדשים שמוצגים בעמודים המאוחרים "
    "של הרשימה בעקבות עדכוני האתר.</p>\n\n"
    "<p>מחפשים חברה"
)

# Posts where yoast_head_json.description exceeded 160 chars (sync with excerpt)
META_POST_IDS = (322835, 322826, 322505)


USER = os.environ.get("WORDPRESS_USERNAME", "").strip()
PASSWORD = os.environ.get("WORDPRESS_APP_PASSWORD", "").strip()
_BASE_OVERRIDE: str | None = None


def load_credentials_file() -> None:
    """Merge KEY=value lines from credentials.local (non-empty values override env)."""
    global USER, PASSWORD, _BASE_OVERRIDE
    if not CRED_FILE.is_file():
        return
    for raw in CRED_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if not v:
            continue
        if k == "WORDPRESS_USERNAME":
            USER = v
        elif k == "WORDPRESS_APP_PASSWORD":
            PASSWORD = v
        elif k == "WORDPRESS_URL":
            _BASE_OVERRIDE = v.rstrip("/")


def effective_base() -> str:
    return _BASE_OVERRIDE if _BASE_OVERRIDE else base_url()


def auth_header() -> str:
    if not USER or not PASSWORD:
        print(
            "Missing credentials. Set WORDPRESS_USERNAME + WORDPRESS_APP_PASSWORD\n"
            f"or create {CRED_FILE} — see seo-audit/credentials.example",
            file=sys.stderr,
        )
        sys.exit(2)
    token = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
    return f"Basic {token}"


def json_request(
    opener: urllib.request.OpenerDirector,
    method: str,
    url: str,
    *,
    data: dict | None = None,
) -> tuple[int, dict]:
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "User-Agent": "brndini-seo-plan-round7",
            "Authorization": auth_header(),
            **({"Content-Type": "application/json"} if body else {}),
        },
    )
    with opener.open(req, timeout=120) as resp:
        raw = resp.read().decode()
        return resp.status, json.loads(raw) if raw.strip() else {}


def excerpt_plain(post: dict) -> str:
    raw = post.get("excerpt", {}).get("rendered", "") or ""
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    return re.sub(r"\s+", " ", raw).strip()


def apply_hub_link(opener: urllib.request.OpenerDirector) -> None:
    b = effective_base()
    _, page = json_request(
        opener,
        "GET",
        f"{b}/wp-json/wp/v2/pages/{PAGE_ID}?context=edit",
    )
    rendered = page.get("content", {}).get("rendered", "") or ""
    if CATEGORY_URL in rendered and "מופיעים כל הפוסטים בנושא" in rendered:
        print("[hub] already patched")
        return
    if MARKER_BEFORE not in rendered:
        print("[hub] marker not found — page HTML changed; abort hub step", file=sys.stderr)
        sys.exit(1)
    new_html = rendered.replace(MARKER_BEFORE, EXTRA, 1)
    _, out = json_request(
        opener,
        "POST",
        f"{b}/wp-json/wp/v2/pages/{PAGE_ID}",
        data={"content": new_html},
    )
    print("[hub] updated page", PAGE_ID, "modified:", out.get("modified"))


def apply_meta_from_excerpt(opener: urllib.request.OpenerDirector) -> None:
    b = effective_base()
    for pid in META_POST_IDS:
        _, post = json_request(
            opener,
            "GET",
            f"{b}/wp-json/wp/v2/posts/{pid}?context=edit",
        )
        meta = post.get("meta") or {}
        excerpt = excerpt_plain(post)
        if not excerpt:
            print(f"[meta] post {pid}: empty excerpt, skip", file=sys.stderr)
            continue
        if len(excerpt) > 155:
            excerpt = excerpt[:152].rstrip() + "…"
        key = "_yoast_wpseo_metadesc"
        if key not in meta and key not in str(meta):
            # meta may be empty object if not registered for REST — try POST anyway
            pass
        _, updated = json_request(
            opener,
            "POST",
            f"{b}/wp-json/wp/v2/posts/{pid}",
            data={"meta": {key: excerpt}},
        )
        meta2 = updated.get("meta") or {}
        got = meta2.get(key) if isinstance(meta2, dict) else None
        if got == excerpt:
            print(f"[meta] post {pid}: set {key} OK ({len(excerpt)} chars)")
        else:
            print(
                f"[meta] post {pid}: REST may not persist Yoast meta (got {repr(got)[:80]}). "
                "Register _yoast_wpseo_metadesc with show_in_rest or edit in wp-admin.",
                file=sys.stderr,
            )


def main() -> None:
    load_credentials_file()
    ctx = ssl.create_default_context()
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))

    apply_hub_link(opener)
    apply_meta_from_excerpt(opener)
    print("\nYoast post title template: run on WP host:")
    print("  bash seo-audit/apply_yoast_post_title_template_round7.sh")
    print("Or wp-admin → Yoast SEO → Settings → Content types → Posts → SEO title → %%title%%")


if __name__ == "__main__":
    main()
