<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# AGENTS.md

Operating rules for AI coding agents working in this repo.

## Project overview

`brndini-main-web` is a server-rendered Next.js 16 (App Router) + React 19 dashboard (Hebrew, RTL) that reads pages, posts, and categories from the live WordPress site `brndini.co.il` via the WP REST API. It is **not** a CMS replacement — it's a thin read/write client plus a sibling toolkit (`seo-audit/`) of scripts and docs that audit and mutate the same WordPress site.

## Tech stack

- **Next.js** `16.2.2` (App Router, `force-dynamic`), **React** `19.2.4`
- **TypeScript** (`strict: true`), path alias `@/* → ./src/*`
- **Tailwind CSS v4** via `@tailwindcss/postcss`
- **ESLint 9** with `eslint-config-next` flat config (`core-web-vitals` + `typescript`)
- **Package manager:** `npm` (committed `package-lock.json`)
- **Python 3** + `urllib`/`requests` for `seo-audit/` tooling
- **WordPress REST API** (Application Password auth) as the backend

## Repo layout

- `src/app/` — App Router entrypoint (`layout.tsx`, `page.tsx`, `globals.css`)
- `src/lib/wordpress.ts` — typed WP REST client (pages, posts, categories, media)
- `public/` — static SVGs only
- `seo-audit/` — **live-site tooling**, not part of the Next.js build:
  - `*.py` / `*.sh` — audit, linking, image, Yoast helpers
  - `mu-plugins/brndini-yoast-rest-meta.php` — WordPress plugin that exposes `yoast_seo_title` / `yoast_seo_metadesc` over REST
  - `README.md`, `YOAST_CUSTOM_SEO_GUIDE.md`, `SEMRUSH_SITE_AUDIT.md`, `OPTIONAL_INFRA.md`, `SEO_META_FIXES_ROUND7.md`, `findings.json`, `long_titles_suggestions.csv`
  - `credentials.example` (template) — never commit `credentials.local`
- `next.config.ts`, `postcss.config.mjs`, `eslint.config.mjs`, `tsconfig.json` — stock configs

## Setup

```bash
npm install
# minimum env for the dashboard to render (see src/lib/wordpress.ts)
export WORDPRESS_URL=https://brndini.co.il
export WORDPRESS_USERNAME='<wp-user>'
export WORDPRESS_APP_PASSWORD='<application-password>'
npm run dev
```

For `seo-audit/` scripts, prefer `seo-audit/credentials.local` (gitignored) over exported env vars — see `seo-audit/credentials.example`.

## Commands

| Task | Command |
|------|---------|
| Dev server (`http://localhost:3000`) | `npm run dev` |
| Production build | `npm run build` |
| Start built app | `npm start` |
| Lint | `npm run lint` |

There is **no** `test`, `typecheck`, or `format` script. Use `npx tsc --noEmit` ad-hoc if you need a typecheck; do not add a script to `package.json` for a one-off.

## Code style

- TypeScript `strict`: no `any`; prefer `unknown` + narrowing. `noEmit` is on — do not check in compiled output.
- Keep server components server-only; this app relies on `export const dynamic = 'force-dynamic'` for WP-backed pages — preserve that on any route that calls `wpFetch`.
- RTL-first UI: every new page/container should be wrapped `dir="rtl"` consistent with `src/app/page.tsx`.
- Brand colors in use: `#253F55` (primary), `#6EC1E4` (accent). Match existing Tailwind usage.
- Keep imports via the `@/` alias; do not introduce deep relative imports (`../../..`).
- Before committing TS/TSX: `npm run lint` must pass.
- Python (`seo-audit/`): stdlib + `requests`; 4-space indent; idempotent scripts (`already patched` / `nothing to do` path).

## Testing

There is no automated test suite. For behavior changes:

- **Dashboard (`src/`):** verify `npm run build` completes and `npm run dev` renders the homepage against a real WP host (the default is `https://brndini.co.il`).
- **`seo-audit/` scripts that mutate the live site:** first run `python3 seo-audit/verify_plan_round7.py` (read-only) before and after, and sanity-check `yoast_head_json` for a sample URL via the WP REST API.

## Commit & PR conventions

- Observed style (keep it): short imperative subjects, optional scope prefix, e.g.:
  - `seo-audit: Yoast REST fields yoast_seo_title/metadesc + CSV import`
  - `Round 7: implement plan (scripts, Semrush, meta fallbacks)`
- One logical change per commit.
- Do **not** force-push or amend existing commits unless explicitly asked.
- Branch prefix for agent work is `cursor/<short-slug>-3d33`. Do not leave the current branch unless asked.
- PRs open as **draft** by default. If a `PULL_REQUEST_TEMPLATE.md` appears later, use it.

## Do / Don't

- ✅ Prefer editing existing files over adding new ones; keep `src/` minimal.
- ✅ Run `npm run lint` before committing TypeScript changes.
- ✅ For `seo-audit/` work, update `seo-audit/findings.json` to reflect new live-site state in the same commit.
- ❌ Never commit `seo-audit/credentials.local`, `.env*`, or any Application Password / admin credential. `.gitignore` enforces this — do not override.
- ❌ Do not hand-edit `package-lock.json`; let `npm install` manage it.
- ❌ Do not commit `node_modules/`, `.next/`, `coverage/`, `__pycache__/`, or `next-env.d.ts`.
- ❌ Do not invent package.json scripts that aren't used; do not pin to a test framework that isn't installed.
- ❌ Do not run `seo-audit/` mutate-the-site scripts without explicit user intent — they hit production WordPress.

## Secrets & environment

Consumed by `src/lib/wordpress.ts` and most `seo-audit/*` scripts:

| Variable | Purpose |
|----------|---------|
| `WORDPRESS_URL` | Base WP origin (default `https://brndini.co.il`) |
| `WORDPRESS_USERNAME` | WP user login for Application Password auth |
| `WORDPRESS_APP_PASSWORD` | WP Application Password (spaces allowed) |

Never hardcode these. For the audit toolkit, fill `seo-audit/credentials.local` from `seo-audit/credentials.example`. If running in Cursor Cloud Agents, set them as project Secrets in the Cursor Dashboard so they are injected into the VM.

## Known gotchas

- Next.js 16 + React 19: APIs moved since older training data — consult `node_modules/next/dist/docs/` before assuming an API exists (see banner above).
- `export const dynamic = 'force-dynamic'` is intentional on WP-backed pages; removing it causes stale builds to embed remote HTML.
- The Yoast REST plugin (`seo-audit/mu-plugins/brndini-yoast-rest-meta.php`) **must be activated** on the WordPress side — if `GET /wp/v2/posts/{id}?_fields=yoast_seo_title,yoast_seo_metadesc` returns only `id`, the plugin is installed but inactive.
- Yoast's own settings save on this host uses `option_page=wpseo_page_settings` (not `wpseo_titles`) — see `seo-audit/apply_yoast_post_title_template_round7.sh`.
- `force-dynamic` + missing `WORDPRESS_APP_PASSWORD` → the homepage crashes at request time; set creds or stub the client before `npm run dev`.

## Cursor Cloud specific instructions

- The VM is ephemeral: `npm install` runs fresh each boot unless the base image or startup script is updated via an env-setup agent at `cursor.com/onboard`.
- `seo-audit/credentials.local` does **not** travel between runs — use Cursor Secrets for `WORDPRESS_*` instead.
- Git identity is preconfigured — do not change `user.email` / `user.name`.
- Current working branches follow `cursor/<slug>-3d33`; create new ones with the same prefix.
