# Optional infrastructure (not in this Next.js repo)

## HSTS (`Strict-Transport-Security`)

- **Cloudways:** Application → **Security** → **Headers** (or equivalent) → add HSTS with a sensible `max-age` (e.g. ≥ 15552000) after confirming HTTPS everywhere.
- **Cloudflare:** enable HSTS in SSL/TLS settings (only if you have Cloudflare access).

Yoast / WordPress REST cannot set transport security headers for HTML pages served via CDN.

## LinkedIn URL in `brndini-seo-master` (PHP)

The custom plugin lives on the **WordPress server**, not in `office812/brndini-main-web`. To remove reliance on the Elementor snippet that rewrites `linkedin.com/company/brndini` → `mdn-il`, edit the plugin source on the host and deploy, then remove the snippet if desired.

## Double-slash URL canonical edge case

Some URLs with `//` in the path may 200 with a canonical pointing to the homepage. Impact is low (no internal links use this pattern). Fixing usually requires theme/redirect rules or server rewrite — track as a separate infra task if needed.
