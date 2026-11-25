#!/usr/bin/env python3
"""ASO Screenshot Studio renderer.

  python3 render.py options <config.json> <out_dir>        # 5 direction previews to choose from
  python3 render.py build   <config.json> <out_dir> --ios floating --android bigtype

Needs: Google Chrome or Chromium, Python 3.8+, Pillow (pip install pillow).
"""
import argparse, concurrent.futures as cf, json, os, shutil, subprocess, sys, tempfile, time, urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent / 'engine'
DIRECTIONS = {
    'floating': ('A', 'Floating Cards', 'Tilted 3D phone with the key moments popping out as glowing cards. Explains the product best.'),
    'bigtype': ('B', 'Big Type', 'Oversized two-tone headline on white, phone tilting in from the corner. Most readable at thumbnail size.'),
    'brandbold': ('C', 'Brand Bold', 'Brand colour field, centred 3D phone and a bold brand arc. Strongest brand recognition.'),
    'photo': ('D', 'Photo-led', 'Real people up top, the phone and two benefits below. Builds trust fastest (needs photos).'),
    'panorama': ('E', 'Panorama', 'One continuous scene that starts in the Google Play landscape image and flows across every screen.'),
}
IOS = [('6.9in', 1290, 2796), ('6.5in', 1242, 2688)]
ANDROID_RENDER = (1290, 2293)   # 9:16 — Google Play rejects screenshots longer than 2:1
ANDROID_OUT = (1080, 1920)


def chrome():
    for c in [os.environ.get('CHROME'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              '/Applications/Chromium.app/Contents/MacOS/Chromium', shutil.which('google-chrome'),
              shutil.which('google-chrome-stable'), shutil.which('chromium'), shutil.which('chromium-browser')]:
        if c and Path(c).exists():
            return c
    sys.exit('Chrome/Chromium not found. Install it or set CHROME=/path/to/chrome.')


def stage(cfg_path, out):
    """Copy the engine into out/_build and write cfg.js with absolute asset URIs."""
    cfg_path = Path(cfg_path).resolve()
    cfg = json.loads(cfg_path.read_text())
    base = cfg_path.parent
    uri = lambda p: p if (not p or p.startswith(('http://', 'https://', 'data:', 'file:'))) else (base / p).resolve().as_uri()
    b = cfg.setdefault('brand', {})
    for k in ('logo', 'logo_light', 'logo_dark'):
        if b.get(k):
            b[k] = uri(b[k])
    cfg['screens'] = {k: uri(v) for k, v in (cfg.get('screens') or {}).items()}
    cfg['photos'] = [uri(p) for p in cfg.get('photos') or []]
    build = Path(out) / '_build'
    build.mkdir(parents=True, exist_ok=True)
    for f in ('engine.js', 'style.css', 'frame.html'):
        shutil.copy(ENGINE / f, build / f)
    fams = [b.get('font_head') or 'Poppins', b.get('font_body') or b.get('font_head') or 'Inter']
    q = '&'.join('family=' + urllib.parse.quote(f.replace(' ', '+'), safe='+') + ':wght@400;500;600;700;800' for f in dict.fromkeys(fams))
    (build / 'fonts.css').write_text(f"@import url('https://fonts.googleapis.com/css2?{q}&display=swap');\n")
    (build / 'cfg.js').write_text('window.CFG = ' + json.dumps(cfg, ensure_ascii=False) + ';\n')
    return build, cfg


def shot(build, query, outfile, w, h, ch):
    url = (build / 'frame.html').as_uri() + '?' + query
    for _ in range(3):
        prof = tempfile.mkdtemp()
        try:
            subprocess.run([ch, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={prof}',
                            '--allow-file-access-from-files', '--virtual-time-budget=9000', f'--window-size={w},{h}',
                            f'--screenshot={outfile}', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        except subprocess.TimeoutExpired:
            pass
        finally:
            shutil.rmtree(prof, ignore_errors=True)
        if Path(outfile).exists() and Path(outfile).stat().st_size > 0:
            return outfile
    print('FAILED', outfile)


def run(jobs, build):
    ch = chrome()
    with cf.ThreadPoolExecutor(min(6, os.cpu_count() or 4)) as ex:
        list(ex.map(lambda j: shot(build, *j, ch), jobs))


def resize(src, dst, size):
    from PIL import Image
    Image.open(src).convert('RGB').resize(size, Image.LANCZOS).save(dst, optimize=True)


def pdf(html_path, pdf_path):
    prof = tempfile.mkdtemp()
    subprocess.run([chrome(), '--headless=new', '--disable-gpu', f'--user-data-dir={prof}', '--allow-file-access-from-files',
                    '--virtual-time-budget=8000', '--no-pdf-header-footer', f'--print-to-pdf={pdf_path}', Path(html_path).as_uri()],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    shutil.rmtree(prof, ignore_errors=True)


PAGE_CSS = """@page{size:297mm 210mm;margin:0}body{margin:0;font-family:-apple-system,Helvetica,Arial,sans-serif;color:#14294a}
.p{width:297mm;height:210mm;padding:28px 40px;box-sizing:border-box;page-break-after:always;position:relative;overflow:hidden}
h1{font-size:28px;margin:0 0 4px}h2{font-size:22px;margin:0}.k{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#dc1d47;font-weight:700}
p{font-size:12px;line-height:1.5;color:#4a5b73;margin:6px 0 14px}.row{display:flex;gap:10px;align-items:flex-start}
.row img{border-radius:8px;box-shadow:0 3px 10px rgba(0,0,0,.18);display:block}.cap{font-size:9px;color:#6b7a90;margin-top:4px}"""


def options(cfg_path, out):
    out = Path(out); od = out / 'options'; od.mkdir(parents=True, exist_ok=True)
    build, cfg = stage(cfg_path, out)
    n = min(3, len(cfg['frames']))
    jobs = []
    for d in DIRECTIONS:
        jobs.append((f'dir={d}&part=land&h=2796', str(od / f'{d}_0_landscape.png'), 1920, 1080))
        jobs += [(f'dir={d}&part={i}&h=2796', str(od / f'{d}_{i + 1}.png'), 1290, 2796) for i in range(n)]
    t = time.time(); run(jobs, build)
    # contact sheet
    from PIL import Image, ImageDraw
    Hh = 520; rows = []
    for d, (letter, name, _) in DIRECTIONS.items():
        ims = [Image.open(od / f'{d}_0_landscape.png').convert('RGB').resize((round(Hh * 16 / 9), Hh))]
        ims += [Image.open(od / f'{d}_{i + 1}.png').convert('RGB').resize((round(Hh * 1290 / 2796), Hh)) for i in range(n)]
        r = Image.new('RGB', (sum(i.width for i in ims) + 14 * len(ims) + 260, Hh + 20), 'white')
        ImageDraw.Draw(r).text((10, Hh // 2), f'{letter}  {name}', fill='#14294a')
        x = 260
        for im in ims: r.paste(im, (x, 10)); x += im.width + 14
        rows.append(r)
    sheet = Image.new('RGB', (max(r.width for r in rows), sum(r.height for r in rows)), 'white')
    y = 0
    for r in rows: sheet.paste(r, (0, y)); y += r.height
    sheet.save(out / 'options_sheet.png')
    # PDF
    H0 = 300; lw = round(H0 * 16 / 9); pw = round(H0 * 1290 / 2796)
    pages = [f"<div class='p' style='background:#0f2742;color:#fff'><div class='k'>App Store &amp; Google Play</div><h1 style='color:#fff;font-size:40px;margin-top:120px'>{cfg['app']['name']}: screenshot directions</h1><p style='color:#ffffffcc;font-size:15px'>Five design options, each shown as it would appear on Google Play: landscape lead image, then the first {n} screenshots. iOS starts at the first portrait screen. Pick one for iOS and one for Android.</p></div>"]
    for d, (letter, name, desc) in DIRECTIONS.items():
        strip = f"<img src='options/{d}_0_landscape.png' style='width:{lw}px;height:{H0}px'>" + ''.join(f"<img src='options/{d}_{i + 1}.png' style='width:{pw}px;height:{H0}px'>" for i in range(n))
        pages.append(f"<div class='p'><div class='k'>Option {letter}</div><h2>{name}</h2><p>{desc}</p><div class='row'>{strip}</div></div>")
    html = out / 'options.html'
    html.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{PAGE_CSS}</style></head><body>{''.join(pages)}</body></html>")
    pdf(html, out / 'options.pdf')
    print(f'Rendered {len(jobs)} previews in {time.time() - t:.0f}s ->', out / 'options.pdf', out / 'options_sheet.png')


def build(cfg_path, out, ios_dir, android_dir):
    out = Path(out); build_dir, cfg = stage(cfg_path, out)
    n = len(cfg['frames']); raw = out / '_raw'; raw.mkdir(parents=True, exist_ok=True)
    jobs = [(f'dir={ios_dir}&part={i}&h=2796', str(raw / f'ios_{i + 1:02d}.png'), 1290, 2796) for i in range(n)]
    aw, ah = ANDROID_RENDER
    jobs += [(f'dir={android_dir}&part={i}&h={ah}', str(raw / f'and_{i + 1:02d}.png'), aw, ah) for i in range(n)]
    jobs += [(f'dir={android_dir}&part=land&h={ah}', str(raw / 'and_land.png'), 1920, 1080),
             (f'dir={android_dir}&part=fg&h={ah}', str(raw / 'and_fg.png'), 1024, 500)]
    t = time.time(); run(jobs, build_dir)
    slug = ''.join(c for c in cfg['app']['name'] if c.isalnum()) or 'App'
    for label, w, h in IOS:
        d = out / 'ios' / label; d.mkdir(parents=True, exist_ok=True)
        for i in range(n):
            src = raw / f'ios_{i + 1:02d}.png'
            dst = d / f'{slug}_iOS_{label}_{i + 1:02d}.png'
            shutil.copy(src, dst) if (w, h) == (1290, 2796) else resize(src, dst, (w, h))
    ad = out / 'android'; ad.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        resize(raw / f'and_{i + 1:02d}.png', ad / f'{slug}_Play_{i + 1:02d}_1080x1920.png', ANDROID_OUT)
    shutil.copy(raw / 'and_land.png', ad / f'{slug}_Play_00_landscape_1920x1080.png')
    shutil.copy(raw / 'and_fg.png', ad / f'{slug}_Play_feature-graphic_1024x500.png')
    # review PDF
    pw = 150
    ios_strip = ''.join(f"<div><img src='_raw/ios_{i + 1:02d}.png' style='width:{pw}px;height:{round(pw * 2796 / 1290)}px'><div class='cap'>{i + 1:02d}</div></div>" for i in range(n))
    and_strip = f"<div><img src='_raw/and_land.png' style='width:{round(260 * 16 / 9)}px;height:260px'><div class='cap'>Landscape lead</div></div>" + ''.join(f"<div><img src='_raw/and_{i + 1:02d}.png' style='width:146px;height:260px'><div class='cap'>{i + 1:02d}</div></div>" for i in range(n))
    pages = [f"<div class='p'><div class='k'>App Store · Option {DIRECTIONS[ios_dir][0]} {DIRECTIONS[ios_dir][1]}</div><h2>{cfg['app']['name']} — iOS screenshots</h2><p>1290 × 2796 (6.9″) and 1242 × 2688 (6.5″).</p><div class='row' style='flex-wrap:wrap'>{ios_strip}</div></div>",
             f"<div class='p'><div class='k'>Google Play · Option {DIRECTIONS[android_dir][0]} {DIRECTIONS[android_dir][1]}</div><h2>{cfg['app']['name']} — Google Play</h2><p>Phone screenshots 1080 × 1920, landscape lead 1920 × 1080, feature graphic 1024 × 500.</p><div class='row' style='flex-wrap:wrap'>{and_strip}</div><div style='margin-top:14px'><img src='_raw/and_fg.png' style='width:360px;height:176px;border-radius:8px'><div class='cap'>Feature graphic</div></div></div>"]
    html = out / 'review.html'
    html.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{PAGE_CSS}</style></head><body>{''.join(pages)}</body></html>")
    pdf(html, out / 'review.pdf')
    print(f'Built {len(jobs)} creatives in {time.time() - t:.0f}s ->', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['options', 'build'])
    ap.add_argument('config'); ap.add_argument('out')
    ap.add_argument('--ios', default='floating', choices=list(DIRECTIONS))
    ap.add_argument('--android', default=None, choices=list(DIRECTIONS))
    a = ap.parse_args()
    if a.cmd == 'options':
        options(a.config, a.out)
    else:
        build(a.config, a.out, a.ios, a.android or a.ios)
