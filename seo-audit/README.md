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

### Round 7 — Yoast post title template + hub→category inlink

These **mutate** the live WordPress site. They are not part of the read-only crawl.

```bash
# (A) On the WordPress host with WP-CLI — shorten default post SEO titles
bash seo-audit/apply_yoast_post_title_template_round7.sh

# (B) From any machine with credentials — add archive CTA to hub page 1851
export WORDPRESS_USERNAME='...'
export WORDPRESS_APP_PASSWORD='...'
python3 seo-audit/apply_internal_link_hub_round7.py
```

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
