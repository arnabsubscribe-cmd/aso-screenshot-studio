---
name: aso-screenshot-studio
description: Design App Store and Google Play screenshot sets for any mobile app, in the app's own brand. Ask for the app name, website, store links and any design language (Figma link, brand guidelines, logo, brand shapes, photos), research the brand and listing, write the screenshot copy, render 5 design directions to choose from, then build the full iOS + Android set (6–7 portrait screenshots, Play landscape lead, feature graphic) as upload-ready PNGs plus a review PDF. Use when someone asks for store screenshots, ASO creatives, app store graphics, custom product pages / custom store listing visuals, or a Play feature graphic.
---

# ASO Screenshot Studio

Turns an app's website + store listing into polished, on-brand store screenshots. The renderer is HTML + headless Chrome, so every frame is exact-size and repeatable.

Files in this skill:
- `scripts/fetch_store.py` — reads the Play / App Store listing (iTunes Lookup API) and website basics (colours, fonts, logo candidates).
- `scripts/render.py` — `options` renders the 5 directions; `build` renders the final set.
- `engine/` — the layout engine (`engine.js`), shared by both commands.
- `references/config.md` — the `config.json` schema. Read it before writing a config.
- `references/copy-and-specs.md` — headline rules, store sizes, review checklist.
- `examples/demo/` — a complete working config for a fictional app (run `python3 examples/demo/make_demo_assets.py` first).

Requirements: Google Chrome or Chromium, Python 3.8+, Pillow (`pip install pillow`). Fonts load from Google Fonts, so rendering needs internet.

## Workflow

### 1. Ask for the inputs (one message)
This skill is brand-neutral: it must never reuse another client's shapes, colours or layouts. Everything visual comes from the user's own brand. Ask, in one message:
1. **App name** (and a project name for the output folder).
2. **Website URL** and **store links** (App Store and/or Google Play; one is enough).
3. **Design language — do you have any of these?** (share whatever exists)
   - a **Figma link** (brand file, design system or app designs)
   - **brand guidelines** (PDF / link) with colours, fonts and logo rules
   - **logo files** (a white version for dark backgrounds and a colour version)
   - **brand shapes / patterns / illustrations** they use in ads (e.g. a signature curve, icon set, texture)
   - **photos** of real people, vehicles or products they own
   - reference apps or screenshots whose style they like
4. **Real app screens:** 5–7 raw phone screenshots of the main flows (much better than the store's existing marketing images).
5. Market/country and any copy that must be used.

Use what they give:
- **Figma link:** if the Figma MCP is connected, read it (`get_metadata`, `get_screenshot`, `get_variable_defs` for colours/type, export logos and screens with `get_screenshot` or download_assets). If it isn't connected, ask them to sign in to Figma via `/mcp`, or to export the logo and screens as PNG.
- **Guidelines PDF:** read the colour codes, fonts, logo rules and any signature shape; note do's and don'ts and follow them.
- **Brand shape:** save it as a transparent PNG/SVG and set `brand.motif = "custom"` with `brand.motif_image`. Otherwise pick a neutral motif (`glow`, `blob`, `ring`, `dots`, `none`) that suits the brand — see `references/config.md`.
- **Nothing supplied:** derive colours, fonts and logo from the website (step 2) and use `motif: "glow"`. Say so, and that the result will be more generic than with their real brand assets.

### 2. Research
- Run `python3 scripts/fetch_store.py --play <url> --appstore <url> --website <url> --country <cc>` and read the result: listing title, description, features, rating, genre, brand colours, Google Fonts, logo candidates.
- Unless the user supplied guidelines/Figma, pick brand tokens: `primary` (dark brand colour for backgrounds), `accent` (the brand's bright colour), `accent2` (a warm secondary), fonts (use the site's Google Font if it has one, else Poppins/Montserrat). Check contrast: white text must read on `primary`.
- **Downloading store screenshots, icons or logos needs the user's OK** (they belong to the app owner). When they agree, re-run with `--download <project>/assets/store`. Store screenshots are usually already-designed marketing frames; prefer raw screens from the user. If only marketing frames exist, tell the user the set will reuse them and look weaker.
- Logo: prefer the user's file. Need a white version for dark backgrounds (`logo_light`) and a dark one (`logo_dark`). Without a logo, the engine sets the app name in the headline font.

### 3. Write the story (6–7 frames)
Follow `references/copy-and-specs.md`. Typical arc: 1 hero promise → 3–4 core features (one per frame, in order of what users search for) → trust / tracking / payment → closing. Each frame: `headline` (2 lines max), `accent` (the key words, shown in the accent colour), optional `sub`, `tag`, `points` (for Photo-led), and a `card` that pops out of the screen.
- Cards: use `{"type":"crop","box":[x,y,w,h]}` (fractions of the screenshot) to lift a real UI element out of the screen — the strongest look. Find the boxes by viewing each screen image; the box should hug one element (a search bar, price row, status card). Use `{"type":"text",...}` only for facts the user has confirmed.
- Keep claims to what the listing/website says. Never invent prices, ratings, times or awards.
- Write `config.json` in a project folder (e.g. `~/aso/<project>/config.json`) with asset paths relative to it.

### 4. Show the options and let the user choose
Run `python3 scripts/render.py options <project>/config.json <project>/out` (~15 s). Show `out/options_sheet.png` (and point to `out/options.pdf`). The five directions:

| id | Option | Best for |
|---|---|---|
| `floating` | A · Floating Cards (dark; set `options.floating_theme: "light"` for light) | Explaining the product; real UI pops out as glowing cards |
| `bigtype` | B · Big Type | Readability at thumbnail size, B2B, utilities |
| `brandbold` | C · Brand Bold | Strong brands, centred 3D phone |
| `photo` | D · Photo-led | Services with people (delivery, moving, health). Needs `photos` |
| `panorama` | E · Panorama | Memorable, continuous scene; Play landscape lead flows into the screens |

Ask with AskUserQuestion: one question for **iOS** and one for **Android**, each listing the 5 options (they may pick different ones). Also ask light vs dark if they pick A.

### 5. Build
Run `python3 scripts/render.py build <project>/config.json <project>/out --ios <id> --android <id>`. Output:
- `out/ios/6.9in/*.png` (1290×2796) and `out/ios/6.5in/*.png` (1242×2688)
- `out/android/*_1080x1920.png` (9:16 — Play rejects screenshots longer than 2:1), `*_landscape_1920x1080.png`, `*_feature-graphic_1024x500.png`
- `out/review.pdf`

Look at the review images before reporting. Fix overlaps or bad crops by editing `config.json` (shorter headline, adjust a crop `box`, change `screen`) and re-running. Then tell the user what was made, which frames use real screens vs placeholders, and what still needs their confirmation (claims, photos, translations).

### 6. Optional follow-ups
- **Custom product pages / custom store listings:** copy the config, change frames for the audience, render again.
- **Figma:** if the Figma MCP is connected, upload the PNGs or rebuild frames with `use_figma` so a designer can edit them.
- **Localisation:** duplicate the config with translated strings (get translations from the client; don't machine-translate for production).
