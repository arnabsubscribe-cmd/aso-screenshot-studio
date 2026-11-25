#!/usr/bin/env python3
"""Generate placeholder app screens + logos for the fictional 'Parcelly' demo (no real brand assets)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).resolve().parent
(D / 'screens').mkdir(exist_ok=True)
W, H = 1170, 2532
NAVY, RED, BG, MUT = '#163758', '#e8475f', '#f3f6fa', '#7a879b'
F = lambda s: ImageFont.load_default(size=s)


def base(title):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 360], fill=NAVY)
    d.text((70, 70), '9:41', font=F(44), fill='white')
    d.text((70, 220), title, font=F(72), fill='white')
    d.rectangle([420, H - 30, 750, H - 18], fill='#111111')
    return im, d


def card(d, y, h, title, sub=None, fill='white', fg=NAVY, r=40):
    d.rounded_rectangle([60, y, W - 60, y + h], radius=r, fill=fill, outline='#dfe5ee', width=3)
    d.text((110, y + 40), title, font=F(54), fill=fg)
    if sub: d.text((110, y + 115), sub, font=F(40), fill=MUT if fill == 'white' else '#c9d4e3')


def save(im, n): im.save(D / 'screens' / f'{n}.png')


im, d = base('Hi Sam')
d.rounded_rectangle([60, 300, W - 60, 430], radius=60, fill='white'); d.text((130, 340), 'Track your parcel', font=F(50), fill=MUT)
for k, t in enumerate(['Same day', 'Movers', 'Abroad']):
    x = 60 + k * 360; d.rounded_rectangle([x, 520, x + 330, 860], radius=40, fill='white', outline='#dfe5ee', width=3)
    d.ellipse([x + 105, 570, x + 225, 690], fill=RED); d.text((x + 60, 740), t, font=F(46), fill=NAVY)
card(d, 960, 230, 'Gift to Mum', 'Arriving in 18 min'); card(d, 1240, 230, 'Documents', 'Delivered 10:42')
save(im, 'home')

im, d = base('Send a parcel')
card(d, 440, 200, 'Pickup', 'Marina Gate 2'); card(d, 680, 200, 'Drop-off', 'Al Nahda, Sharjah')
for k, (t, p) in enumerate([('Express', '$12'), ('Same day', '$8'), ('Next day', '$5')]):
    card(d, 960 + k * 230, 200, t, p, fill=NAVY if k == 0 else 'white', fg='white' if k == 0 else NAVY)
d.rounded_rectangle([200, 1760, W - 200, 1900], radius=70, fill=RED); d.text((420, 1800), 'Book now', font=F(56), fill='white')
save(im, 'book')

im, d = base('Tracking')
d.rectangle([0, 360, W, 1500], fill='#e3e9f2')
for x in range(0, W, 180): d.line([x, 360, x + 200, 1500], fill='white', width=18)
d.line([(250, 1300), (500, 1000), (760, 1050), (930, 700)], fill=RED, width=16); d.ellipse([900, 660, 970, 730], fill=NAVY)
for k, t in enumerate(['Picked up', 'Out for delivery', 'Delivered']):
    card(d, 1560 + k * 210, 180, t, ['10:05', '10:21', 'Soon'][k])
save(im, 'track')

im, d = base('Wallet')
d.rounded_rectangle([60, 430, W - 60, 900], radius=50, fill=NAVY); d.text((120, 500), 'Balance', font=F(46), fill='#c9d4e3'); d.text((120, 580), '$128.40', font=F(110), fill='white')
for k, a in enumerate(['$20', '$50', '$100']):
    x = 60 + k * 360; d.rounded_rectangle([x, 980, x + 330, 1150], radius=36, fill=RED if k == 1 else 'white', outline='#dfe5ee', width=3); d.text((x + 110, 1040), a, font=F(56), fill='white' if k == 1 else NAVY)
card(d, 1250, 200, 'Top up', 'Card ending 4021')
save(im, 'wallet')

im, d = base('Send abroad')
card(d, 440, 230, 'Sending from', 'United Arab Emirates'); card(d, 710, 230, 'Sending to', 'India')
card(d, 1000, 200, 'Parcel · 3 kg', 'Price shown before you book')
save(im, 'abroad')

im, d = base('Move home')
for k, t in enumerate(['Studio', '1 bedroom', '2 bedroom', 'Villa']):
    card(d, 440 + k * 220, 190, t, 'Packing included', fill=NAVY if k == 1 else 'white', fg='white' if k == 1 else NAVY)
d.text((90, 1400), 'Quote: $340', font=F(66), fill=NAVY)
save(im, 'move')

for name, col in [('logo_light', 'white'), ('logo_dark', NAVY)]:
    lg = Image.new('RGBA', (900, 200), (0, 0, 0, 0)); g = ImageDraw.Draw(lg)
    g.rounded_rectangle([0, 10, 180, 190], radius=46, fill=RED); g.text((60, 40), 'P', font=F(120), fill='white')
    g.text((220, 30), 'Parcelly', font=F(130), fill=col); lg.save(D / f'{name}.png')
print('demo assets written to', D)
