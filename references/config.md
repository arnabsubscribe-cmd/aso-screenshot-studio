# config.json schema

Paths are relative to the folder that holds `config.json`. Colours are hex.

```jsonc
{
  "app": { "name": "Parcelly", "website": "https://…", "play": "https://play.google.com/…", "appstore": "https://apps.apple.com/…" },
  "brand": {
    "primary": "#163758",      // dark brand colour, used for dark backgrounds
    "accent": "#e8475f",       // bright brand colour: accent words, arcs, glow
    "accent2": "#ffc46b",      // optional warm secondary (Brand Bold + Panorama accent words)
    "bg_dark": "#0b2340",      // optional, defaults to primary darkened
    "bg_light": "#eef2f8",     // optional, light backgrounds
    "text_dark": "#14294a",    // optional, dark text on light backgrounds
    "font_head": "Poppins",    // any Google Font
    "font_body": "Montserrat",
    "logo_light": "assets/logo_white.png",   // for dark backgrounds
    "logo_dark": "assets/logo_color.png",    // for light backgrounds
    "motif": "glow",           // background decoration from the brand's design language:
                               // glow (default) | blob | ring | dots | arc | none | custom
    "motif_image": "assets/brand_shape.png"  // with "custom": the brand's own shape/pattern (transparent PNG/SVG)
  },
  "options": { "floating_theme": "dark" },     // or "light"
  "screens": { "home": "assets/screens/home.png", "book": "…" },   // raw app screenshots (any phone size)
  "photos": ["assets/photos/rider.jpg"],       // for Photo-led; cycles across frames
  "landscape": { /* a frame object used for the Play landscape lead + feature graphic; defaults to frames[0] */ },
  "frames": [ /* 6–7 frame objects, in store order */ ]
}
```

## Frame object

| key | required | notes |
|---|---|---|
| `headline` | yes | Use `\n` for line breaks. 2 lines max, ~22 characters per line. |
| `accent` | no | Shown on its own line in the accent colour. The key words. |
| `sub` | no | One short supporting line. |
| `tag` | no | Small pill above the headline (e.g. the service name). |
| `screen` | yes | Key into `screens`. A missing image renders a labelled placeholder. |
| `card` / `cards` | no | Pop-out card(s), see below. |
| `points` | no | `[["Title","Sub"], …]` two benefit rows for Photo-led. |

## Cards

**Crop card** (recommended): lifts a region of the real screen out and enlarges it with a glow.
```json
{ "type": "crop", "box": [0.05, 0.12, 0.90, 0.05], "pop": 1.14, "from": "home", "highlight": true }
```
`box` = `[x, y, width, height]` as fractions of the screenshot image. `from` defaults to the frame's screen.
To find a box: open the screenshot, note the pixel rectangle of one element, divide by image width/height.

**Text card**: a white card with label / title / sub. Positions: `left`, `right`, `bottom`, `top`.
```json
{ "type": "text", "label": "Live", "title": "Rider arriving", "sub": "18 min away", "pos": "left" }
```
Only use figures the client has confirmed.

## Choosing the motif
Decoration must come from the client's own design language. If they have a signature shape (a curve, symbol, pattern, illustration), export it and use `custom`. Otherwise:
- `glow` — soft light in the accent colour; neutral, works for any brand (default)
- `blob` — organic shape; friendly consumer brands
- `ring` — clean circle outline; fintech, utilities
- `dots` — dot pattern; technical / B2B
- `arc` — half-ring band; only if the brand actually uses an arc
- `none` — just the gradient
