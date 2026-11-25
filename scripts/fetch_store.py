#!/usr/bin/env python3
"""Read an app's public store listings and website basics into one JSON summary.

  python3 fetch_store.py --play "<play url>" --appstore "<app store url>" --website "<url>" [--country ae] [--download DIR]

Without --download nothing but the listing text is fetched. With --download DIR the
store screenshots, app icon and website logo candidates are saved into DIR
(only do this after the user agrees — these images belong to the app owner).
"""
import argparse, html, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read().decode('utf-8', 'ignore')


def play(url):
    pid = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('id', [None])[0]
    s = get(f'https://play.google.com/store/apps/details?id={pid}&hl=en')
    out = {'id': pid}
    m = re.search(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S)
    if m:
        try:
            ld = json.loads(m.group(1)); out.update(title=ld.get('name'), short=ld.get('description'), icon=ld.get('image'),
                                                     rating=(ld.get('aggregateRating') or {}).get('ratingValue'))
        except Exception:
            pass
    m = re.search(r'data-g-id="description"[^>]*>(.*?)</div>', s, re.S)
    if m:
        out['description'] = html.unescape(re.sub(r'<br\s*/?>', '\n', re.sub(r'<(?!br)[^>]+>', '', m.group(1))))
    shots = re.findall(r'(https://play-lh\.googleusercontent\.com/[^"\s=]+)=w\d+-h\d+[^"]*"[^>]*alt="Screenshot image"', s)
    out['screenshots'] = list(dict.fromkeys(u + '=w1440' for u in shots))
    return out


def appstore(url, country):
    m = re.search(r'id(\d+)', url)
    cc = (re.search(r'apps\.apple\.com/([a-z]{2})/', url) or [None, country])[1]
    j = json.loads(get(f'https://itunes.apple.com/lookup?id={m.group(1)}&country={cc}'))
    r = (j.get('results') or [{}])[0]
    return {'id': m.group(1), 'title': r.get('trackName'), 'subtitle': None, 'description': r.get('description'),
            'icon': r.get('artworkUrl512'), 'rating': r.get('averageUserRating'), 'genre': r.get('primaryGenreName'),
            'screenshots': r.get('screenshotUrls') or [], 'ipad_screenshots': r.get('ipadScreenshotUrls') or []}


def website(url):
    s = get(url)
    meta = lambda n: (re.search(rf'<meta[^>]+(?:name|property)="{n}"[^>]+content="([^"]*)"', s, re.I) or [None, None])[1]
    colors = re.findall(r'#[0-9a-fA-F]{6}\b', s)
    common = sorted({c.lower() for c in colors}, key=lambda c: -colors.count(c))[:12]
    fonts = list(dict.fromkeys(re.findall(r'fonts\.googleapis\.com/css2?\?family=([^&":]+)', s)))
    logos = [urllib.parse.urljoin(url, u) for u in re.findall(r'<img[^>]+src="([^"]+)"[^>]*(?:logo|brand)', s, re.I)[:4]]
    logos += [urllib.parse.urljoin(url, u) for u in re.findall(r'<img[^>]+(?:logo|brand)[^>]+src="([^"]+)"', s, re.I)[:4]]
    return {'title': (re.search(r'<title>(.*?)</title>', s, re.S) or [None, None])[1], 'description': meta('description') or meta('og:description'),
            'theme_color': meta('theme-color'), 'og_image': meta('og:image'), 'hex_colors_by_frequency': common,
            'google_fonts': [f.replace('+', ' ') for f in fonts], 'logo_candidates': list(dict.fromkeys(logos))}


def download(info, d):
    d = Path(d); d.mkdir(parents=True, exist_ok=True); saved = []
    def grab(u, name):
        try:
            data = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
            ext = '.png' if data[:4] == b'\x89PNG' else '.jpg' if data[:2] == b'\xff\xd8' else '.webp' if data[8:12] == b'WEBP' else '.svg' if b'<svg' in data[:300] else '.bin'
            p = d / (name + ext); p.write_bytes(data); saved.append(str(p))
        except Exception as e:
            print('skip', u, e, file=sys.stderr)
    for store in ('play', 'appstore'):
        s = info.get(store) or {}
        for i, u in enumerate(s.get('screenshots', [])[:10]): grab(u, f'{store}_screenshot_{i + 1:02d}')
        if s.get('icon'): grab(s['icon'], f'{store}_icon')
    for i, u in enumerate((info.get('website') or {}).get('logo_candidates', [])[:4]): grab(u, f'website_logo_{i + 1}')
    return saved


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--play'); ap.add_argument('--appstore'); ap.add_argument('--website')
    ap.add_argument('--country', default='us'); ap.add_argument('--download')
    a = ap.parse_args(); info = {}
    for key, fn, arg in (('play', play, a.play), ('appstore', lambda u: appstore(u, a.country), a.appstore), ('website', website, a.website)):
        if arg:
            try: info[key] = fn(arg)
            except Exception as e: info[key] = {'error': str(e)}
    if a.download: info['downloaded'] = download(info, a.download)
    print(json.dumps(info, indent=1, ensure_ascii=False))
