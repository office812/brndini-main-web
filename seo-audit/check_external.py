#!/usr/bin/env python3
import urllib.request, json, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ext = json.load(open('/tmp/seo/external_links.json'))
urls = list(ext.keys())
print(f'Checking {len(urls)} external URLs...')

def check(u):
    req = urllib.request.Request(u, method='HEAD', headers={'User-Agent':'Mozilla/5.0 SEO-audit'})
    try:
        r = urllib.request.urlopen(req, timeout=20)
        return (u, r.status, r.url if r.url != u else '')
    except urllib.error.HTTPError as e:
        return (u, e.code, '')
    except Exception as e:
        return (u, 'ERR', str(e)[:80])

results = []
with ThreadPoolExecutor(max_workers=10) as pool:
    futs = {pool.submit(check, u): u for u in urls}
    for f in as_completed(futs):
        results.append(f.result())

ok, bad = [], []
for r in results:
    u, s, _ = r
    if isinstance(s, int) and 200 <= s < 400:
        ok.append(r)
    else:
        bad.append(r)

print(f'OK: {len(ok)}  bad: {len(bad)}')
print('\nBad external links:')
for u, s, extra in sorted(bad, key=lambda x: str(x[1])):
    sources = ext.get(u, [])[:3]
    print(f'  [{s}] {u}')
    print(f'    appears on post/page IDs: {sources}')
