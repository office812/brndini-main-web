#!/usr/bin/env bash
# Round 7 — Yoast SEO: shorten the default SEO title template for Posts
# (option key title-post inside wpseo_titles) to %%title%% so Google SERP
# titles are not padded with " | sitename" for every post.
#
# Run on the WordPress host (SSH) where WP-CLI is installed, from the site
# root, or pass --path=/path/to/wordpress.
#
# If posting to wp-admin/options.php manually (no WP-CLI): Yoast's new settings
# UI uses option_page=wpseo_page_settings (not wpseo_titles) and _wpnonce from
# the inline script yoast-seo-new-settings-js-extra → wpseoScriptData.nonce.
#
#   bash seo-audit/apply_yoast_post_title_template_round7.sh
#
# Verify afterwards:
#   wp option get wpseo_titles --format=json | jq -r '.["title-post"]'

set -euo pipefail

if ! command -v wp >/dev/null 2>&1; then
  echo "wp (WP-CLI) not found. Install WP-CLI or run the equivalent change in wp-admin:" >&2
  echo "Yoast SEO → Settings → Content types → Posts → SEO title → set to %%title%%" >&2
  exit 1
fi

wp option patch update wpseo_titles title-post '%%title%%' "$@"

echo "OK: title-post is now %%title%% (unless wp option patch reported an error above)."
