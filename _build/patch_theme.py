# One-off: adds the terracotta theme (default) and keeps sage as a switchable option.
import os
B = os.path.dirname(os.path.abspath(__file__))
def sub(s, old, new, n=1):
    assert s.count(old) >= 1, old
    return s.replace(old, new) if n == 0 else s.replace(old, new, n)

p = os.path.join(B, 'site2', 'site.css'); s = open(p, encoding='utf-8').read()
a = s.index(':root{'); b = s.index('*{box-sizing')
s = s[:a] + ''':root{
  /* terracotta (default) */
  --ink:#2f1e16; --soft:#6b584c; --paper:#fffaf5; --sand:#f5ebe0; --line:#e8d9ca; --mute:#e4d0c1;
  --gold:#8a6417; --marigold:#eaa221; --sage:#5f7464; --clay:#b5552f;
  --bar:#2f1e16; --band:#b5552f; --band-tile:#9c4726; --dark:#2f1e16; --dark-line:#4a3327; --on-dark:#ead9cc; --on-band:#fbe9dc;
  --cta:#b5552f; --cta-h:#9c4726; --cta-ink:#fff; --tint:#f3d9c6;
  --mind:#eaa221; --body:#b5552f; --spirit:#5f7464;
  --disp:'Young Serif',Georgia,serif; --text:'Figtree',system-ui,sans-serif;
  --r:6px; --wrap:1240px;
}
[data-theme=sage]{
  --ink:#1f2a24; --soft:#55615a; --paper:#fffdf9; --sand:#f3ede4; --line:#e2dacd; --mute:#d5ccbc;
  --clay:#c2633d;
  --bar:#1f2a24; --band:#1f2a24; --band-tile:#2c3a32; --dark:#1f2a24; --dark-line:#36443b; --on-dark:#c9cfc9; --on-band:#c9cfc9;
  --cta:#eaa221; --cta-h:#f2b33d; --cta-ink:#1f2a24; --tint:#eaa221;
  --body:#c2633d;
}
''' + s[b:]
s = sub(s, '.btn.gold{background:var(--marigold);border-color:var(--marigold);color:var(--ink)}', '.btn.gold{background:var(--cta);border-color:var(--cta);color:var(--cta-ink)}')
s = sub(s, '.btn.gold:hover{background:#f2b33d;border-color:#f2b33d}', '.btn.gold:hover{background:var(--cta-h);border-color:var(--cta-h)}')
s = sub(s, '.bar{background:var(--ink);', '.bar{background:var(--bar);')
s = sub(s, 'color:#d5ccbc;transition:color .3s}', 'color:var(--mute);transition:color .3s}')
s = sub(s, '.lines{background:var(--ink);color:#e9e1d2}', '.lines{background:var(--band);color:var(--on-band)}')
s = sub(s, '.lines .sec-head p{color:#c9cfc9}', '.lines .sec-head p{color:var(--on-band)}')
s = sub(s, 'overflow:hidden;background:#2c3a32}', 'overflow:hidden;background:var(--band-tile)}')
s = sub(s, '.line p{margin:0 0 8px;color:#c9cfc9}', '.line p{margin:0 0 8px;color:var(--on-band)}')
s = sub(s, '.line u{font-weight:600;color:#fff;text-underline-offset:4px;text-decoration-color:var(--c)}', '.line u{font-weight:600;color:#fff;text-underline-offset:4px}')
s = sub(s, '.math .win{background:var(--marigold)}', '.math .win{background:var(--tint)}')
s = sub(s, '.join-box{background:var(--marigold);', '.join-box{background:var(--tint);')
s = sub(s, 'footer{background:var(--ink);color:#c9cfc9;', 'footer{background:var(--dark);color:var(--on-dark);')
s = sub(s, '.legal{border-top:1px solid #36443b;', '.legal{border-top:1px solid var(--dark-line);')
s = sub(s, '.mock-pill a{font-weight:600}', '.mock-pill a{font-weight:600}\n.mock-pill button{border:1px solid var(--line);background:none;border-radius:4px;padding:2px 8px;margin-left:4px;font-size:.76rem}\n.mock-pill button[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:#fff}\n.mock-pill span{margin-left:10px}')
s = sub(s, 'border-radius:0;border:0;text-align:center;background:var(--marigold);font-size:.76rem}', 'border-radius:0;border:0;text-align:center;background:var(--sand);font-size:.76rem;padding:10px 12px}')
open(p, 'w', encoding='utf-8').write(s)

p = os.path.join(B, 'site2', 'site.js'); s = open(p, encoding='utf-8').read()
s = sub(s, "/* ---------- home ---------- */", """/* ---------- mockup only: color theme switch ---------- */
const setTheme = t => { document.documentElement.dataset.theme = t; try { localStorage.setItem('mbd_theme', t); } catch (e) {} $$('[data-theme-btn]').forEach(b => b.setAttribute('aria-pressed', b.dataset.themeBtn === t)); };
$$('[data-theme-btn]').forEach(b => b.addEventListener('click', () => setTheme(b.dataset.themeBtn)));
setTheme(document.documentElement.dataset.theme || 'terracotta');

/* ---------- home ---------- */""")
open(p, 'w', encoding='utf-8').write(s)

p = os.path.join(B, 'build2.py'); s = open(p, encoding='utf-8').read()
s = sub(s, '<link rel="stylesheet" href="{root}assets/site.css">', '''<script>try{{var t=new URLSearchParams(location.search).get('theme')||localStorage.getItem('mbd_theme');document.documentElement.dataset.theme=t==='sage'?'sage':'terracotta'}}catch(e){{}}</script>
<link rel="stylesheet" href="{root}assets/site.css">''')
s = sub(s, '''Real shirts and prices from <a href="{STORE}">wearmbd.com</a></div>''', '''Real shirts and prices from <a href="{STORE}">wearmbd.com</a><span>Colors:</span><button type="button" data-theme-btn="terracotta">Terracotta</button><button type="button" data-theme-btn="sage">Sage</button></div>''')
s = sub(s, '<meta name="theme-color" content="#1f2a24">', '<meta name="theme-color" content="#2f1e16">')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
