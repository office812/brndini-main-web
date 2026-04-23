# SEO Audit — brndini.co.il

Audit performed 2026-04-22 via REST API probing + headless HTTP crawling.

## Files

- **`findings.json`** — machine-readable summary of the audit scope, health, actions taken, and items requiring human action.
- **`long_titles_suggestions.csv`** — 41 posts/pages whose `<title>` exceeds 65 characters, with shortened suggestions ready to paste into Yoast's per-post "SEO title" field.
- **`crawl.py`** — parallel HTML crawler that walks `/wp/v2/pages` + `/wp/v2/posts` lists, fetches each live URL, and extracts titles, meta descriptions, H1s, canonicals, robots, images+alt, word count, and internal/external links.
- **`check_links.py`** — validates every unique internal URL via HEAD requests (with Hebrew URL encoding).
- **`check_external.py`** — same for external links. Warning: some government/NGO sites block HEAD; manually verify with a real browser UA before treating them as broken.

## Running

All scripts rely on pre-fetched JSON from the WordPress REST API:

```bash
# Populate /tmp/seo/all_pages.json and /tmp/seo/all_posts_light.json first
python3 seo-audit/crawl.py          # ~1 min
python3 seo-audit/check_links.py    # ~1.5 min
python3 seo-audit/check_external.py # ~30s
```

### Round 7 — full plan automation (live site)

These **mutate** the live WordPress site.

**One-shot (recommended):** copy `seo-audit/credentials.example` → `seo-audit/credentials.local`, fill Application Password, then:

```bash
python3 seo-audit/apply_plan_round7.py   # hub link + tries Yoast meta on 3 posts
python3 seo-audit/verify_plan_round7.py # read-only: hub marker + meta lengths
```

**Yoast post title template** (`%%title%%` only — fixes long SERP titles site-wide) is **not** in that script; run on the WP host:

```bash
bash seo-audit/apply_yoast_post_title_template_round7.sh
```

Or **wp-admin** → Yoast SEO → **Settings** → **Content types** → **Posts** → SEO title → `%%title%%`.

**If meta POST is ignored by WordPress:** paste the three short descriptions from `seo-audit/SEO_META_FIXES_ROUND7.md`.

**Semrush:** see `seo-audit/SEMRUSH_SITE_AUDIT.md` (enable JS rendering, re-crawl).

**Optional infra (HSTS, LinkedIn PHP, double-slash):** `seo-audit/OPTIONAL_INFRA.md`.

Legacy single-purpose scripts still work: `apply_internal_link_hub_round7.py`, `apply_yoast_post_title_template_round7.sh`.

### כותרת SEO + מטא מותאמים לכל פוסט/עמוד (ייבוא המוני)

מדריך מלא: **`seo-audit/YOAST_CUSTOM_SEO_GUIDE.md`**.

1. התקן והפעל את התוסף **Brndini Yoast REST** (ZIP מתיקיית `seo-audit/mu-plugins/brndini-yoast-rest-meta/`) או העתק ל־`wp-content/mu-plugins/`.
2. ייצא CSV: `python3 seo-audit/export_yoast_csv_template.py > template.csv`
3. מלא `seo_title` / `meta_desc` — הסקריפט שולח ל־REST בשדות **`yoast_seo_title`** ו־**`yoast_seo_metadesc`**.
4. `python3 seo-audit/apply_seo_titles_from_csv.py template.csv`

## Summary of findings

Site is in very good SEO health:

- 100% canonical, 100% meta description, 100% H1 across 296 indexable URLs
- Schema already covers WebPage / BreadcrumbList / Organization / ProfessionalService / SearchAction
- Sitemap includes 100% of indexable pages
- 7 broken internal URLs identified in a hardcoded footer (brndini-seo-master plugin); all fixed via Yoast 301 redirects (verified live)

Items requiring wp-admin access (cannot be fixed via REST API):

1. **Yoast title template**: 41 titles exceed 65 chars. Root cause is the template `%%title%% %%sep%% %%sitename%%` which appends ~22 chars. Change to `%%title%%` under Yoast → Search Appearance → Content Types → Posts.
2. **LinkedIn URL in footer**: hardcoded `linkedin.com/company/brndini` returns 404; should be `linkedin.com/company/mdn-il` (the plugin `brndini-seo-master` is a custom PHP plugin that is not REST-editable).
3. **Per-post SEO title overrides**: Yoast Premium does not expose `_yoast_wpseo_title` for REST write. If the site-wide template fix in (1) is accepted, (3) becomes redundant.
