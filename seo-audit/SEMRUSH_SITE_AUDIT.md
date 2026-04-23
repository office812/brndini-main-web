# Semrush Site Audit — enable JS rendering (brndini.co.il)

After deploying the `/whatsapp/` bridge and the body-end snippet that rewrites `wa.me` links at runtime, Semrush’s default crawler still sees raw `wa.me` URLs unless **JavaScript rendering** is on.

## Steps (Semrush UI)

1. Open your **Site Audit** project for `brndini.co.il`.
2. Go to **Project settings** (gear icon) → **Site Audit** section.
3. Find **JS rendering** (or “Crawl with JavaScript” / similar wording) and set it to **Enabled**.
4. Save, then **Re-run audit** (or start a new crawl).

## What to expect

- Fewer false “broken external link” hits on `wa.me` (bots are often blocked; JS rewrite points crawlers to first-party `/whatsapp/`).
- Crawl may take longer and consume more crawl budget.

## Verify without Semrush

Open any page in Chrome DevTools → Elements → search for `href` containing `wa.me`. After JS runs, links should rewrite to `/whatsapp/` (check in the DOM after load).
