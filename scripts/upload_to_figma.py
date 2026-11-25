#!/usr/bin/env python3
"""Upload rendered PNGs to Figma after `upload_assets` returned single-use URLs.

  python3 upload_to_figma.py <urls.json> <figma_manifest.json> [--group "iOS 6.9in"]

urls.json: a JSON list of submitUrl strings, in the same order as the manifest rows being uploaded
(the order of the nodeIds passed to upload_assets). Prints {name: imageHash}.
"""
import argparse, json, subprocess, sys

ap = argparse.ArgumentParser(); ap.add_argument('urls'); ap.add_argument('manifest'); ap.add_argument('--group')
a = ap.parse_args()
urls = json.load(open(a.urls)); rows = json.load(open(a.manifest))
if a.group: rows = [r for r in rows if r['group'] == a.group]
if len(urls) != len(rows): sys.exit(f'{len(urls)} URLs for {len(rows)} files: they must match one to one')
out = {}
for u, r in zip(urls, rows):
    p = subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: image/png', '--data-binary', '@' + r['path'], u], capture_output=True, text=True)
    try: out[r['name']] = json.loads(p.stdout).get('imageHash')
    except Exception: out[r['name']] = 'FAILED: ' + p.stdout[:120]
print(json.dumps(out, indent=1))
