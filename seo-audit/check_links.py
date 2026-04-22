#!/usr/bin/env python3
"""Re-check links — properly encode Hebrew URLs."""
import urllib.request, urllib.parse, json, time
from concurrent.futures import ThreadPoolExecutor, as_completed

links = json.load(open('/tmp/seo/internal_links.json'))
urls = list(links.keys())

def safe_url(u):
    """Encode non-ASCII chars in URL path."""
    try:
        u.encode('ascii')
        return u
    except UnicodeEncodeError:
        p = urllib.parse.urlsplit(u)
        # quote path and query
        path = urllib.parse.quote(p.path, safe='/%')
        query = urllib.parse.quote(p.query, safe='=&%')
        return urllib.parse.urlunsplit((p.scheme, p.netloc, path, query, p.fragment))

def check(u):
    safe = safe_url(u)
    try:
        req = urllib.request.Request(safe, method='HEAD', headers={'User-Agent':'Mozilla/5.0 SEO-audit'})
        r = urllib.request.urlopen(req, timeout=45)
        return (u, r.status, r.url)
    except urllib.error.HTTPError as e:
        if e.code == 405:
            try:
                req2 = urllib.request.Request(safe, headers={'User-Agent':'Mozilla/5.0 SEO-audit'})
                r2 = urllib.request.urlopen(req2, timeout=45)
                return (u, r2.status, r2.url)
            except Exception as e2:
                return (u, getattr(e2,'code','ERR'), str(e2)[:80])
        return (u, e.code, safe)
    except Exception as e:
        return (u, 'ERR', str(e)[:80])

results = []
done = 0
t0 = time.time()
with ThreadPoolExecutor(max_workers=16) as pool:
    futs = {pool.submit(check, u): u for u in urls}
    for f in as_completed(futs):
        results.append(f.result())
        done += 1
        if done % 50 == 0:
            print(f'  {done}/{len(urls)} ({time.time()-t0:.0f}s)', flush=True)

with open('/tmp/seo/link_status.json','w') as f:
    json.dump(results, f, ensure_ascii=False)

from collections import Counter
c = Counter(s for _,s,_ in results)
print('Status distribution:')
for s,n in sorted(c.items(), key=lambda kv: str(kv[0])):
    print(f'  {s}: {n}')

nonok = [r for r in results if not (isinstance(r[1], int) and 200 <= r[1] < 300)]
print(f'\nNon-2xx: {len(nonok)}')
for u,s,extra in sorted(nonok, key=lambda x: str(x[1])):
    print(f'  [{s}] {u}')
