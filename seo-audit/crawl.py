#!/usr/bin/env python3
import urllib.request, json, re, gzip, html as htmllib, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

pages = json.load(open('/tmp/seo/all_pages.json'))
posts = json.load(open('/tmp/seo/all_posts_light.json'))

items = []
for p in pages:
    if p.get('status')!='publish': continue
    t = p['title']
    items.append({'type':'page','id':p['id'],'slug':p['slug'],'url':p['link'],
                  'title_raw': t.get('raw', t.get('rendered',''))})
for p in posts:
    if p.get('status')!='publish': continue
    t = p['title']
    items.append({'type':'post','id':p['id'],'slug':p['slug'],'url':p['link'],
                  'title_raw': t.get('raw', t.get('rendered',''))})

print(f'Items to crawl: {len(items)}', flush=True)

IMG_RE   = re.compile(r'<img\b[^>]*>', re.I)
A_RE     = re.compile(r'<a\b[^>]*>', re.I)
H1_RE    = re.compile(r'<h1\b[^>]*>(.*?)</h1>', re.I|re.S)
H2_RE    = re.compile(r'<h2\b[^>]*>(.*?)</h2>', re.I|re.S)
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.I|re.S)
META_DESC_RE = re.compile(r'<meta[^>]+name=[\'"]description[\'"][^>]*content=[\'"]([^\'"]*)[\'"]', re.I)
META_DESC_RE2= re.compile(r'<meta[^>]+content=[\'"]([^\'"]*)[\'"][^>]*name=[\'"]description[\'"]', re.I)
CANON_RE = re.compile(r'<link[^>]+rel=[\'"]canonical[\'"][^>]*href=[\'"]([^\'"]*)[\'"]', re.I)
ROBOTS_RE= re.compile(r'<meta[^>]+name=[\'"]robots[\'"][^>]*content=[\'"]([^\'"]*)[\'"]', re.I)
MAIN_RE  = re.compile(r'<(main|article)\b[^>]*>([\s\S]*?)</\1>', re.I)
SCRIPT_STYLE_RE = re.compile(r'<(script|style)[^>]*>[\s\S]*?</\1>', re.I)

def strip_tags(s):
    s = SCRIPT_STYLE_RE.sub('', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = htmllib.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

def parse_attr(tag, name):
    m = re.search(r'\b'+name+r'\s*=\s*[\'"]([^\'"]*)[\'"]', tag, re.I)
    return m.group(1) if m else None

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={
        'User-Agent':'Mozilla/5.0 SEO-audit',
        'Accept-Encoding':'gzip',
    })
    r = urllib.request.urlopen(req, timeout=timeout)
    raw = r.read()
    if r.headers.get('Content-Encoding')=='gzip':
        raw = gzip.decompress(raw)
    return r.status, raw.decode('utf-8', errors='replace'), dict(r.headers)

def process(it):
    try:
        status, body, _ = fetch(it['url'])
    except Exception as e:
        return {**it, 'error': str(e)[:120]}

    rec = {**it, 'http':status}
    m = TITLE_RE.search(body); rec['doc_title'] = strip_tags(m.group(1)) if m else ''
    m = META_DESC_RE.search(body) or META_DESC_RE2.search(body)
    rec['meta_desc'] = m.group(1) if m else ''
    m = CANON_RE.search(body); rec['canonical'] = m.group(1) if m else ''
    m = ROBOTS_RE.search(body); rec['robots'] = m.group(1) if m else ''

    mainm = MAIN_RE.search(body)
    main_html = mainm.group(2) if mainm else body
    rec['has_main'] = bool(mainm)

    h1s = [strip_tags(x) for x in H1_RE.findall(main_html)]
    rec['h1s'] = h1s
    rec['h1_count'] = len(h1s)
    rec['h2_count'] = len(H2_RE.findall(main_html))

    img_data = []
    for tag in IMG_RE.findall(main_html):
        src = parse_attr(tag, 'src') or ''
        alt = parse_attr(tag, 'alt')
        if src.startswith('data:'): continue
        img_data.append({'src':src, 'alt': alt if alt is not None else None})
    rec['img_count'] = len(img_data)
    rec['img_missing_alt'] = sum(1 for x in img_data if x['alt'] is None or x['alt'].strip()=='')
    rec['imgs'] = img_data

    links = []
    for tag in A_RE.findall(main_html):
        href = parse_attr(tag, 'href') or ''
        if not href or href.startswith(('#','mailto:','tel:','javascript:')): continue
        links.append(href)
    rec['links'] = links
    rec['link_count'] = len(links)

    rec['word_count'] = len(strip_tags(main_html).split())
    return rec

records = []
errors = []
t0 = time.time()
done = 0
with ThreadPoolExecutor(max_workers=16) as pool:
    futures = {pool.submit(process, it): it for it in items}
    for f in as_completed(futures):
        rec = f.result()
        if 'error' in rec:
            errors.append((rec['url'], rec['error']))
        records.append(rec)
        done += 1
        if done % 25 == 0 or done == len(items):
            elapsed = time.time()-t0
            print(f'  {done}/{len(items)}  ({elapsed:.0f}s, {done/elapsed:.1f} req/s)', flush=True)

with open('/tmp/seo/crawl.json','w') as f:
    json.dump({'records':records,'errors':errors}, f, ensure_ascii=False)
print(f'Done: {len(records)} records, {len(errors)} errors', flush=True)
