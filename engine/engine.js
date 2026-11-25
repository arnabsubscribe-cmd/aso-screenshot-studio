// ASO Screenshot Studio — rendering engine.
// Reads window.CFG (written by scripts/render.py) and draws one store creative per page load.
// Query string: dir=<direction>&part=<index|land|fg>&h=<portrait height>
(function () {
  const C = window.CFG, B = C.brand || {};
  const q = new URLSearchParams(location.search);
  const DIR = q.get('dir') || 'floating', PART = q.get('part') || '0', H = +(q.get('h') || 2796), W = 1290;

  // ---------- colours & fonts ----------
  const hexToRgb = h => { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); const n = parseInt(h, 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; };
  const mix = (a, b, t) => { const x = hexToRgb(a), y = hexToRgb(b); return '#' + x.map((v, i) => Math.round(v + (y[i] - v) * t).toString(16).padStart(2, '0')).join(''); };
  const rgba = (h, a) => `rgba(${hexToRgb(h).join(',')},${a})`;
  const PR = B.primary || '#163758', AC = B.accent || '#dc1d47', AC2 = B.accent2 || mix(AC, '#ffd27a', .7);
  const DK = B.bg_dark || mix(PR, '#000000', .35), LT = B.bg_light || '#eef2f8', TX = B.text_dark || mix(PR, '#000000', .15);
  const FH = `'${B.font_head || 'Poppins'}', sans-serif`, FB = `'${B.font_body || B.font_head || 'Inter'}', sans-serif`;
  const root = document.documentElement.style;
  root.setProperty('--fh', FH); root.setProperty('--fb', FB); root.setProperty('--ac', AC); root.setProperty('--tx', TX);
  root.setProperty('--glow', `0 0 0 5px ${rgba(mix(AC, '#ffffff', .4), .7)}, 0 0 70px 12px ${rgba(AC, .55)}, 0 40px 80px rgba(3,12,26,.45)`);

  const HSCALE = () => (H >= 2600 ? 1 : .8);
  const nl = s => (s || '').replace(/\n/g, '<br>');
  const LONG = f => ((f.headline || '') + (f.accent || '')).length > 30;
  const head = (f, o) => `<div class="hl" style="font:${o.weight || 800} ${Math.round(o.size * (o.land ? 1 : HSCALE()))}px/${o.lh || 1.06} ${FH};letter-spacing:${o.ls || '-.015em'};color:${o.color};text-align:${o.align || 'left'}">${nl(f.headline)}${f.accent ? `<br><span style="color:${o.accent}">${nl(f.accent)}</span>` : ''}</div>`;
  const sub = (f, o) => f.sub ? `<div style="font:600 ${o.size}px/1.35 ${FB};color:${o.color};margin-top:${o.mt || 28}px;text-align:${o.align || 'left'}">${nl(f.sub)}</div>` : '';
  const tag = (f, bg) => f.tag ? `<div class="tag" style="background:${bg}">${f.tag}</div>` : '';
  const logo = (dark, h) => { const src = dark ? (B.logo_light || B.logo) : (B.logo_dark || B.logo); return src ? `<img src="${src}" style="height:${h}px;display:block">` : `<div style="font:800 ${h * .7}px ${FH};color:${dark ? '#fff' : TX}">${C.app && C.app.name || ''}</div>`; };
  const scr = k => (C.screens || {})[k];

  // ---------- phone + cards ----------
  const phoneHTML = k => `<div class="phone"><div class="screen">${scr(k) ? `<img src="${scr(k)}">` : `<div class="noscr">Add screen “${k || ''}”</div>`}</div><div class="island"></div></div>`;
  function textCard(c, i) {
    const P = { left: [-90, 520], right: [400, 860], bottom: [30, 1180], top: [60, 300] };
    const [x, y] = P[c.pos || ['left', 'right', 'bottom'][i % 3]];
    return `<div class="tcard${i === 0 ? ' hl' : ''}" style="left:${x}px;top:${y}px">${c.label ? `<div class="tl">${c.label}</div>` : ''}<div class="tt">${c.title || ''}</div>${c.sub ? `<div class="ts">${c.sub}</div>` : ''}</div>`;
  }
  const cardsOf = f => f.cards || (f.card ? [f.card] : []);
  const cardsHTML = f => cardsOf(f).map((c, i) => c.type === 'crop'
    ? `<div class="crop${c.highlight === false ? '' : ' hl'}" data-src="${scr(c.from || f.screen) || ''}" data-box="${c.box.join(',')}" data-pop="${c.pop || 1.14}"></div>`
    : textCard(c, i)).join('');
  const phone3d = (f, x, y, s, ry, rx, rz, cards = true) => `<div class="stage" style="left:${x}px;top:${y}px"><div class="tilt" style="transform:rotateZ(${rz}deg) rotateY(${ry}deg) rotateX(${rx}deg) scale(${s})">${phoneHTML(f.screen)}${cards ? cardsHTML(f) : ''}</div></div>`;
  const flatPhone = (f, x, y, s, rot) => `<div class="flat" style="left:${x}px;top:${y}px;transform:rotate(${rot}deg) scale(${s})">${phoneHTML(f.screen)}</div>`;
  const arcShape = (cx, top, R, rot, color, op = 1, band = .48) => `<div class="arc" style="left:${cx - R}px;top:${top}px;width:${2 * R}px;height:${R}px;background:radial-gradient(circle at 50% 0,transparent ${R * (1 - band) - 1}px,${color} ${R * (1 - band)}px,${color} ${R - 1}px,transparent ${R}px);transform:rotate(${rot}deg);opacity:${op}"></div>`;
  const ringShape = (cx, top, R, rot, color, op = 1) => arcShape(cx, top, R, rot, color, op, .04);
  // Decoration follows the brand's own design language: brand.motif = glow (default) | blob | ring | dots | arc | custom | none
  const MOTIF = (B.motif || (B.motif_image ? 'custom' : 'glow')).toLowerCase();
  function deco(cx, top, R, rot, color, op = 1) {
    switch (MOTIF) {
      case 'none': return '';
      case 'arc': return arcShape(cx, top, R, rot, color, op);
      case 'ring': return `<div class="arc" style="left:${cx - R}px;top:${top - R * .5}px;width:${2 * R}px;height:${2 * R}px;border-radius:50%;border:${Math.round(R * .09)}px solid ${color};opacity:${op * .9}"></div>`;
      case 'blob': return `<div class="arc" style="left:${cx - R * .8}px;top:${top - R * .3}px;width:${1.6 * R}px;height:${1.45 * R}px;border-radius:42% 58% 63% 37% / 41% 44% 56% 59%;background:${color};transform:rotate(${rot}deg);opacity:${op}"></div>`;
      case 'dots': return `<div class="arc" style="left:${cx - R * .8}px;top:${top - R * .2}px;width:${1.6 * R}px;height:${1.6 * R}px;background:radial-gradient(${color} 22%,transparent 24%) 0 0/56px 56px;-webkit-mask:radial-gradient(circle,#000 30%,transparent 70%);opacity:${op * .8}"></div>`;
      case 'custom': return B.motif_image ? `<img class="arc" src="${B.motif_image}" style="left:${cx - R}px;top:${top - R * .2}px;width:${2 * R}px;transform:rotate(${rot}deg);opacity:${op}">` : '';
      default: return `<div class="arc" style="left:${cx - R * 1.2}px;top:${top - R * .7}px;width:${2.4 * R}px;height:${2.4 * R}px;border-radius:50%;background:radial-gradient(circle,${rgba(color, .55)} 0%,${rgba(color, .18)} 38%,${rgba(color, 0)} 68%);opacity:${op}"></div>`;
    }
  }
  const arc = (cx, top, R, rot, color, op = 1) => deco(cx, top, R, rot, color, op);
  const ring = (cx, top, R, rot, color, op = 1) => (MOTIF === 'arc' ? ringShape(cx, top, R, rot, color, op) : ['ring', 'dots', 'blob', 'glow'].includes(MOTIF) ? deco(cx, top, R * .8, rot, color, op * .6) : '');
  const blob = (x, y, d, c, op) => `<div class="arc" style="left:${x}px;top:${y}px;width:${d}px;height:${d}px;border-radius:50%;background:${c};opacity:${op}"></div>`;
  const BG_DARK = `radial-gradient(ellipse 95% 55% at 22% 10%,${mix(PR, '#ffffff', .1)} 0%,${PR} 42%,${DK} 100%)`;
  const BG_LIGHT = `radial-gradient(ellipse 80% 60% at 60% 60%,#ffffff 0%,${mix(LT, '#ffffff', .5)} 45%,${LT} 100%)`;
  const tall = H >= 2600, ps = tall ? 1.22 : 1.08, hs = tall ? 1 : .8;
  const photo = i => { const p = C.photos || []; return p.length ? p[i % p.length] : null; };
  const pts = f => f.points || (f.sub ? [[f.sub, '']] : []);

  // ---------- portrait directions ----------
  const P = {};
  P.floating = (f, i) => {
    const light = (C.options || {}).floating_theme === 'light';
    return { bg: light ? BG_LIGHT : BG_DARK, html: `
      ${light ? '' : blob(-420, H * .54, 1300, mix(PR, '#ffffff', .12), .35)}
      ${arc(1260, H * .54, 620, 180, AC)}
      <div class="txt" style="left:150px;right:80px;top:${i === 0 ? 170 : 300}px">
        ${i === 0 ? `<div style="margin-bottom:70px">${logo(!light, 104)}</div>` : ''}${tag(f, AC)}
        ${head(f, { size: LONG(f) ? 124 : 136, color: light ? TX : '#fff', accent: AC, weight: 700, lh: 1.1 })}
        ${sub(f, { size: 46, color: light ? '#6b7a90' : 'rgba(255,255,255,.78)' })}</div>
      ${phone3d(f, 95, 0, ps, 10, 5, -7)}` };
  };
  P.bigtype = (f, i) => ({ bg: '#ffffff', html: `
      ${ring(210, H * .74, 410, 0, AC, .55)}
      <div class="txt" style="left:110px;right:90px;top:150px">
        <div style="margin-bottom:${i === 0 ? 90 : 100}px">${logo(false, i === 0 ? 100 : 84)}</div>${tag(f, TX)}
        ${head(f, { size: LONG(f) ? 168 : 190, color: TX, accent: AC, lh: .98, ls: '-.02em' })}
        ${sub(f, { size: 50, color: '#6b7a90', mt: 44 })}</div>
      ${flatPhone(f, 300, 0, tall ? 1.12 : 1, -6)}` });
  P.brandbold = (f, i) => {
    const r = [[-16, 6], [14, 5], [-14, 6]][i % 3];
    return { bg: `radial-gradient(ellipse 70% 45% at 50% 62%,${mix(PR, '#ffffff', .2)} 0%,${PR} 45%,${DK} 100%)`, html: `
      ${arc(645, H * .62, 800, 0, AC)}
      <div class="txt" style="left:90px;right:90px;top:150px;text-align:center">
        <div style="display:flex;justify-content:center;margin-bottom:50px">${logo(true, i === 0 ? 104 : 80)}</div>${tag(f, AC)}
        ${head(f, { size: LONG(f) ? 112 : 124, color: '#fff', accent: AC2, align: 'center' })}</div>
      ${phone3d(f, 115, 0, tall ? 1.16 : 1.02, r[0], r[1], r[0] > 0 ? 2 : -2)}` };
  };
  P.photo = (f, i) => {
    const ph = photo(i), top = H * .56;
    return { bg: PR, html: `
      <div class="arc" style="left:0;top:0;width:1290px;height:${top}px;background:${ph ? `url('${ph}') center 22%/cover` : `linear-gradient(135deg,${mix(PR, '#ffffff', .25)},${PR})`}"></div>
      <div class="arc" style="left:0;top:0;width:1290px;height:${top + 2}px;background:linear-gradient(180deg,${rgba(DK, .5)} 0%,${rgba(PR, 0)} 20%,${rgba(PR, 0)} 44%,${rgba(PR, .92)} 82%,${PR} 100%)"></div>
      ${arc(1130, top - 130, 280, 0, AC)}
      <div class="txt" style="left:110px;top:120px">${logo(true, i === 0 ? 104 : 80)}</div>
      <div class="arc" style="left:110px;right:90px;top:${H * .386}px;z-index:5">${tag(f, AC)}${head(f, { size: LONG(f) ? 104 : 120, color: '#fff', accent: AC, weight: 700, lh: 1.1 })}</div>
      <div class="arc" style="left:90px;top:${H * .63}px;width:520px;z-index:5">${pts(f).slice(0, 2).map(([a, b]) => `<div style="display:flex;gap:30px;align-items:flex-start;margin-bottom:60px"><div style="width:96px;height:96px;border-radius:50%;background:${AC};flex:none"></div><div><div style="font:700 46px/1.2 ${FH};color:#fff">${a}</div>${b ? `<div style="font:500 34px/1.35 ${FB};color:rgba(255,255,255,.75);margin-top:8px">${b}</div>` : ''}</div></div>`).join('')}</div>
      ${flatPhone(f, 600, H * .53, tall ? .78 : .66, 0)}` };
  };
  // panorama: one continuous scene across the landscape lead + every portrait
  const LW = H * 16 / 9;
  function scene(total) {
    let svg = '', d = `M -50 ${H * .86}`;
    for (let x = 0; x < total + 1300; x += 1300) d += ` C ${x + 320} ${H * .72}, ${x + 760} ${H * .98}, ${x + 1300} ${H * .84}`;
    svg = `<svg width="${total}" height="${H}" style="position:absolute;left:0;top:0"><path d="${d}" fill="none" stroke="#fff" stroke-width="14" stroke-dasharray="6 40" stroke-linecap="round" opacity=".75"/></svg>`;
    let rings = '';
    for (let k = 0; LW + k * W < total + W; k++) {
      const cx = LW + k * W;
      rings += k % 2 ? arc(cx, H * .7, 640, 0, AC, .95) : ring(cx, H * .14, 520, 180, '#ffffff', .25);
    }
    return `${arc(LW * .62, H * .66, 900, 0, AC2, .9)}${rings}${svg}`;
  }
  P.panorama = (f, i) => {
    const n = (C.frames || []).length, total = LW + n * W;
    return { bg: `linear-gradient(180deg,${mix(PR, '#ffffff', .08)} 0%,${PR} 55%,${DK} 100%)`, html: `
      <div class="arc" style="left:${-(LW + i * W)}px;top:0;width:${total}px;height:${H}px">${scene(total)}</div>
      <div class="txt" style="left:110px;right:110px;top:${i === 0 ? 150 : 300}px">${i === 0 ? `<div style="margin-bottom:60px">${logo(true, 100)}</div>` : ''}${tag(f, AC)}
        ${head(f, { size: LONG(f) ? 116 : 128, color: '#fff', accent: AC2 })}${sub(f, { size: 46, color: 'rgba(255,255,255,.8)' })}</div>
      ${phone3d(f, 140, 0, tall ? 1.14 : 1, [-4, 3, -3][i % 3], 4, [-4, 3, -3][i % 3])}` };
  };

  // ---------- landscape leads (1920 x 1080) ----------
  const L = {};
  const LH = o => Object.assign(o, { land: 1 });
  const LF = () => C.landscape || C.frames[0];
  L.floating = f => { const light = (C.options || {}).floating_theme === 'light'; return { bg: light ? BG_LIGHT : BG_DARK, html: `
      ${arc(1560, 620, 760, 0, AC)}
      <div class="txt" style="left:110px;top:130px;width:860px"><div style="margin-bottom:60px">${logo(!light, 74)}</div>
        ${head(f, { land: 1,  size: 92, color: light ? TX : '#fff', accent: AC, weight: 700, lh: 1.1 })}${sub(f, { size: 32, color: light ? '#6b7a90' : 'rgba(255,255,255,.8)' })}</div>
      ${phone3d(f, 1080, 90, .7, 12, 5, -8)}` }; };
  L.bigtype = f => ({ bg: '#ffffff', html: `${ring(160, 800, 280, 0, AC, .55)}
      <div class="txt" style="left:100px;top:120px;width:1000px"><div style="margin-bottom:60px">${logo(false, 66)}</div>
        ${head(f, { land: 1,  size: 132, color: TX, accent: AC, lh: 1, ls: '-.02em' })}${sub(f, { size: 32, color: '#6b7a90' })}</div>
      ${flatPhone(f, 1120, 110, .72, -7)}` });
  L.brandbold = f => ({ bg: `radial-gradient(ellipse 70% 70% at 75% 55%,${mix(PR, '#ffffff', .2)} 0%,${PR} 45%,${DK} 100%)`, html: `
      ${arc(1560, 600, 600, 0, AC)}
      <div class="txt" style="left:110px;top:130px;width:900px"><div style="margin-bottom:60px">${logo(true, 74)}</div>
        ${head(f, { land: 1,  size: 92, color: '#fff', accent: AC2 })}${sub(f, { size: 32, color: 'rgba(255,255,255,.8)' })}</div>
      ${phone3d(f, 1130, 70, .68, -16, 4, 4, false)}` });
  L.photo = f => { const ph = photo(0); return { bg: PR, html: `
      <div class="arc" style="left:0;top:0;width:1000px;height:1080px;background:${ph ? `url('${ph}') center 20%/cover` : `linear-gradient(135deg,${mix(PR, '#ffffff', .25)},${PR})`}"></div>
      <div class="arc" style="left:0;top:0;width:1002px;height:1080px;background:linear-gradient(90deg,${rgba(PR, 0)} 50%,${PR} 100%)"></div>
      ${arc(1700, 1010, 420, 180, AC)}
      <div class="txt" style="left:1040px;top:130px;width:800px"><div style="margin-bottom:54px">${logo(true, 70)}</div>
        ${head(f, { land: 1,  size: 80, color: '#fff', accent: AC, weight: 700, lh: 1.1 })}
        ${pts(f).slice(0, 2).map(([a, b], k) => `<div style="display:flex;gap:22px;align-items:center;margin-top:${k ? 28 : 56}px"><div style="width:72px;height:72px;border-radius:50%;background:${AC};flex:none"></div><div><div style="font:700 34px ${FH};color:#fff">${a}</div>${b ? `<div style="font:500 25px ${FB};color:rgba(255,255,255,.75)">${b}</div>` : ''}</div></div>`).join('')}</div>` }; };
  L.panorama = f => { const n = (C.frames || []).length, total = LW + n * W, s = 1080 / H; return { bg: DK, html: `
      <div class="arc" style="left:0;top:0;width:${LW}px;height:${H}px;transform:scale(${s});transform-origin:0 0;overflow:hidden;background:linear-gradient(180deg,${mix(PR, '#ffffff', .08)} 0%,${PR} 55%,${DK} 100%)"><div class="arc" style="left:0;top:0;width:${total}px;height:${H}px">${scene(total)}</div></div>
      <div class="txt" style="left:110px;top:130px;width:900px"><div style="margin-bottom:60px">${logo(true, 74)}</div>
        ${head(f, { land: 1,  size: 92, color: '#fff', accent: AC2 })}${sub(f, { size: 32, color: 'rgba(255,255,255,.8)' })}</div>
      ${phone3d(f, 1160, 80, .66, -12, 4, -4, false)}` }; };

  // ---------- compose ----------
  const o = document.getElementById('o');
  if (PART === 'land' || PART === 'fg') {
    const r = (L[DIR] || L.floating)(LF());
    const land = `<div class="frame" style="width:1920px;height:1080px;background:${r.bg}">${r.html}</div>`;
    o.innerHTML = PART === 'land' ? land : `<div class="frame" style="width:1024px;height:500px;background:${DK}"><div style="position:absolute;left:0;top:-38px;transform:scale(${1024 / 1920});transform-origin:0 0">${land}</div></div>`;
  } else {
    const i = +PART, f = C.frames[i];
    const r = (P[DIR] || P.floating)(f, i);
    o.innerHTML = `<div class="frame" data-fit="1" style="width:${W}px;height:${H}px;background:${r.bg}">${r.html}</div>`;
  }

  // ---------- post-layout: crop cards + phone placement under the headline ----------
  function fit() {
    document.querySelectorAll('.frame[data-fit]').forEach(fr => {
      const t = fr.querySelector('.txt'), st = fr.querySelector('.stage, .flat');
      if (!t || !st || DIR === 'photo') return;
      const min = 700;
      st.style.top = Math.max(min, Math.min(H * .52, t.offsetTop + t.offsetHeight + 70)) + 'px';
    });
  }
  const jobs = [...document.querySelectorAll('.crop')].map(el => new Promise(res => {
    const img = new Image();
    img.onload = () => {
      const [bx, by, bw, bh] = el.dataset.box.split(',').map(Number), pop = +el.dataset.pop;
      const nw = img.naturalWidth, nh = img.naturalHeight, SW = 836, SH = 1814;
      const sc = Math.max(SW / nw, SH / nh), ox = (nw * sc - SW) / 2, oy = (nh * sc - SH) / 2;
      const w = bw * nw * sc * pop, h = bh * nh * sc * pop;
      const cx = 22 + (bx + bw / 2) * nw * sc - ox, cy = 22 + (by + bh / 2) * nh * sc - oy;
      Object.assign(el.style, { left: (cx - w / 2 - 30) + 'px', top: (cy - h / 2) + 'px', width: w + 'px', height: h + 'px', borderRadius: Math.min(h / 2, 34 * pop) + 'px' });
      el.innerHTML = `<img src="${el.dataset.src}" style="width:${nw * sc * pop}px;height:${nh * sc * pop}px;left:${-bx * nw * sc * pop}px;top:${-by * nh * sc * pop}px">`;
      res();
    };
    img.onerror = res; img.src = el.dataset.src;
  }));
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => Promise.all(jobs)).then(() => { fit(); document.body.dataset.ready = '1'; });
})();
