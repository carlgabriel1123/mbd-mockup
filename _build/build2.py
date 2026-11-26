# Builds the Mind Body Designs mockup: home page, 41 product pages, shared css/js/data.
import json, os, re, html, sys, shutil
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
STORE = 'https://wearmbd.com'
CDN = 'https://cdn.shopify.com/s/files/1/0710/9145/4036/files/'
E = html.escape
ps = json.load(open(os.path.join(BASE, 'products_all.json'), encoding='utf-8'))['products']
cols = json.load(open(os.path.join(BASE, 'details.json'), encoding='utf-8'))['collections']
cmap = json.load(open(os.path.join(BASE, 'colormap.json'), encoding='utf-8'))
cat_of = {}
for key, name in (('bmp-collection', 'mind'), ('products-copy', 'body'), ('products-copy-copy', 'spirit')):
    for t in cols[key]: cat_of[t] = name
LABEL = {'mind': 'Mind', 'body': 'Body', 'spirit': 'Spirit'}
CAT_LINE = {'mind': 'Kindness, encouragement and reminders to keep going.', 'body': 'For the gym, the run and the yoga mat.', 'spirit': 'Faith, scripture, family and friendship.'}
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL', '4XL']
PRICES = ['34.95', '34.95', '34.95', '34.95', '35.95', '37.95', '38.95']

def clean(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    s = re.sub(r'\s*[—–]\s*', ', ', s)
    return re.sub(r'\s+', ' ', s).strip()
def short_title(t):
    t = clean(t).replace('“', '').replace('”', '').replace('"', '')
    return re.sub(r'\s+(Unisex\s+)?T-Shirt.*$', '', t).strip()
def f(src):
    assert src.startswith(CDN) and '?v=' in src, src
    return src[len(CDN):]
U = lambda file, w: f'{CDN}{file}&width={w}'

items = []
for p in ps:
    c = cat_of.get(p['title'])
    if not c: continue
    assert [o['values'] for o in p['options'] if o['name'] == 'Size'][0] == SIZES, p['handle']
    paras = [clean(x) for x in p['body_html'].split('</p>')]
    paras = [x for x in paras if x]
    m = cmap[p['handle']]
    col = []
    for name in [o['values'] for o in p['options'] if o['name'] == 'Color'][0]:
        vs = [next((v for v in p['variants'] if v['option1'] == name and v['option2'] == s), None) for s in SIZES]
        assert all(v is None or v['price'] == PRICES[i] for i, v in enumerate(vs)) and any(vs), (p['handle'], name)
        d = m[name]
        col.append([name, d.get('hex') or '#d8d2c8', f(d['flat']) if d['flat'] else None, f(d['life']) if d['life'] else None, [v['id'] if v else None for v in vs]])
        assert col[-1][2] or col[-1][3]
    first = f(p['images'][0]['src'])
    dc = next((i for i, x in enumerate(col) if first in (x[3], x[2])), 0)
    hero = col[dc][3] or first
    alt = col[dc][2] or f(p['images'][1]['src'])
    full = clean(p['title']).replace('“', '').replace('”', '').replace('"', '')
    items.append({'n': short_title(p['title']), 'f': full, 'h': p['handle'], 'c': c, 'p': PRICES[0], 'i': [hero, alt], 'col': col, 'dc': dc,
                  'paras': paras, 'd': re.split(r'(?<=[.!?])\s+', ' '.join(paras))[0]})
by = {k: [i for i in items if i['c'] == k] for k in LABEL}
mixed = []
while any(by.values()):
    for k in ('spirit', 'mind', 'body', 'spirit'):
        if by[k]: mixed.append(by[k].pop(0))
items = mixed
for i, it in enumerate(items): it['id'] = i
counts = {k: sum(1 for i in items if i['c'] == k) for k in LABEL}
pick = lambda part: next(i for i in items if part in i['h'])

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="preconnect" href="https://cdn.shopify.com"><link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=Young+Serif&display=swap" rel="stylesheet">'
def head(title, desc, canon, og, root, ld, ogtype='website'):
    return f'''<!doctype html>
<html lang="en-US" data-root="{root}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<!-- Mockup host only: keeps this demo out of Google. On the real store this line is removed. -->
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="en-us" href="{canon}">
<meta name="geo.region" content="US">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Mind Body Designs">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2f1e16">
<link rel="icon" href="{STORE}/cdn/shop/files/Golden_Lotus_Yoga_Emblem.png?crop=center&height=32&width=32">
{FONTS}
<script>try{{var t=new URLSearchParams(location.search).get('theme')||localStorage.getItem('mbd_theme');document.documentElement.dataset.theme=t==='sage'?'sage':'terracotta'}}catch(e){{}}</script>
<link rel="stylesheet" href="{root}assets/site.css">
{''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' + chr(10) for x in ld)}</head>'''

def header(root, home):
    h = '' if home else root + 'index.html'
    return f'''<div class="bar">Free US shipping over <b>$75</b>. Any 3 tees ship free.</div>
<header class="site">
  <div class="wrap nav">
    <a class="logo" href="{root}index.html" aria-label="Mind Body Designs home">
      <img src="{root}assets/lotus.png" alt="" width="58" height="44">
      <span>MIND BODY<small>DESIGNS</small></span>
    </a>
    <nav class="links" aria-label="Main">
      <a href="{h}#mind">Mind</a>
      <a href="{h}#body">Body</a>
      <a href="{h}#spirit">Spirit</a>
      <a href="{h}#gifts">Gifts</a>
      <a href="{h}#about">About</a>
      <a href="{h}#faq">Help</a>
    </nav>
    <button class="cart-btn" type="button" data-open-cart>Cart <b data-cart-n>0</b></button>
  </div>
</header>'''

def footer(root, home):
    h = '' if home else root + 'index.html'
    return f'''<footer>
  <div class="wrap">
    <div class="foot">
      <div class="foot-brand"><strong>Mind Body Designs</strong>Tees with a good message. Printed in the USA.</div>
      <div><h3>Shop</h3><ul><li><a href="{h}#mind">Mind</a></li><li><a href="{h}#body">Body</a></li><li><a href="{h}#spirit">Spirit</a></li><li><a href="{h}#gifts">Gift ideas</a></li></ul></div>
      <div><h3>Help</h3><ul><li><a href="{STORE}/policies/shipping-policy">Shipping</a></li><li><a href="{STORE}/policies/refund-policy">Returns</a></li><li><a href="{h}#faq">Questions</a></li><li><a href="{STORE}/pages/contact">Contact</a></li></ul></div>
      <div><h3>Brand</h3><ul><li><a href="{h}#about">About</a></li><li><a href="https://www.instagram.com/mindbodydesigns">Instagram</a></li><li><a href="{STORE}/policies/privacy-policy">Privacy</a></li><li><a href="{STORE}/policies/terms-of-service">Terms</a></li></ul></div>
    </div>
    <div class="legal"><span>© 2026 Mind Body Designs</span><span>Prices in USD. Ships within the United States.</span></div>
  </div>
</footer>
<div class="mock-pill">Design mockup for Cesar. Real shirts and prices from <a href="{STORE}">wearmbd.com</a><span>Colors:</span><button type="button" data-theme-btn="terracotta">Terracotta</button><button type="button" data-theme-btn="sage">Sage</button></div>
<script src="{root}assets/catalog.js"></script>
<script src="{root}assets/site.js"></script>'''

def card(it, root, eager=False):
    sw = ''.join(f'<i style="background:{c[1]}" title="{E(c[0])}"></i>' for c in it['col'][:5])
    more = f'<em>+{len(it["col"]) - 5}</em>' if len(it['col']) > 5 else ''
    url = f'{root}products/{it["h"]}.html'
    return f'''<li class="card" data-cat="{it['c']}">
  <div class="card-top">
    <a class="card-media" href="{url}" tabindex="-1" aria-hidden="true"><img src="{U(it['i'][0], 720)}" alt="" loading="{'eager' if eager else 'lazy'}" width="720" height="720"><img class="alt" src="{U(it['i'][1], 720)}" alt="" loading="lazy" width="720" height="720"></a>
    <button class="qadd" type="button" data-qv="{it['id']}" aria-label="Quick add: {E(it['n'])}"><span>Quick add</span><i aria-hidden="true">+</i></button>
  </div>
  <div class="card-body">
    <p class="card-cat">{LABEL[it['c']]}</p>
    <h3><a href="{url}">{E(it['n'])}</a></h3>
    <div class="card-row"><p class="price">${it['p']}</p><div class="dots" aria-label="{len(it['col'])} colors">{sw}{more}</div></div>
  </div>
</li>'''

# ---------- home ----------
hero = {'mind': pick('be-the-sunshine'), 'body': pick('lift-heavy'), 'spirit': pick('be-still-and-know')}
HERO_LINE = {'mind': 'Kind words and good reminders, for the days you need one.', 'body': 'Gym, run and yoga tees with a sense of humor.', 'spirit': 'Faith, family and scripture, drawn with care.'}
hero_imgs = ''.join(f'<img data-k="{k}" class="{"on" if k == "mind" else ""}" src="{U(v["i"][0], 1100)}" alt="{E(v["n"])} tee from the {LABEL[k]} collection" width="1100" height="1100" {"fetchpriority=high" if k == "mind" else "loading=lazy"}>' for k, v in hero.items())
hero_data = {k: {'name': v['n'], 'price': v['p'], 'h': v['h'], 'line': HERO_LINE[k]} for k, v in hero.items()}
FAQ = [
    ('What is Mind Body Designs?', 'Mind Body Designs is a US online shop for graphic T-shirts with positive, faith and fitness messages. Every design belongs to one of three collections: Mind (kindness and encouragement), Body (gym, running and yoga) and Spirit (Christian faith, family and friendship).'),
    ('How much do the shirts cost?', 'Every tee is $34.95 in sizes S to XL. 2XL is $35.95, 3XL is $37.95 and 4XL is $38.95. Orders over $75 ship free in the United States, so any three shirts ship free.'),
    ('Where are you located, and where are the shirts printed?', 'We are a US based company, and every order is printed in the USA.'),
    ('How long does shipping take?', 'Each shirt is printed after you order it. Orders usually ship within 7 to 14 days, then take 2 to 5 business days to arrive anywhere in the US. You get a tracking email as soon as it ships.'),
    ('Do you ship outside the United States?', 'Not yet. Right now we ship within the United States only.'),
    ('What are the shirts made of, and how do they fit?', 'They are heavyweight, garment-dyed cotton tees with a relaxed unisex fit and a soft, broken-in feel. Sizes run S to 4XL. If you like an oversized look, size up.'),
    ('What if my order arrives wrong or damaged?', 'Email us within 30 days and we will make it right with a reprint or a refund.'),
]
faq_html = ''.join(f'<details{" open" if i == 0 else ""}><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(FAQ))
DESC = 'Graphic tees with a good message. Faith, fitness and positive vibes T-shirts from $34.95, printed in the USA on heavyweight garment-dyed cotton. Free US shipping over $75.'
org = {'@context': 'https://schema.org', '@type': 'OnlineStore', '@id': STORE + '/#org', 'name': 'Mind Body Designs', 'alternateName': 'MBD', 'url': STORE + '/',
       'logo': STORE + '/cdn/shop/files/mind-body-designs-logo-no-background-no-est-2024_9647ece0-a3d0-4089-8e65-a8a99f051f0b.png',
       'description': DESC, 'sameAs': ['https://www.instagram.com/mindbodydesigns'], 'areaServed': {'@type': 'Country', 'name': 'United States'},
       'knowsAbout': ['Christian T-shirts', 'inspirational graphic tees', 'gym and workout shirts', 'yoga shirts', 'faith based apparel'],
       'hasMerchantReturnPolicy': {'@type': 'MerchantReturnPolicy', 'applicableCountry': 'US', 'returnPolicyCategory': 'https://schema.org/MerchantReturnFiniteReturnWindow', 'merchantReturnDays': 30}}
def offer(it):
    return {'@type': 'AggregateOffer', 'lowPrice': PRICES[0], 'highPrice': PRICES[-1], 'offerCount': sum(1 for c in it['col'] for v in c[4] if v), 'priceCurrency': 'USD', 'availability': 'https://schema.org/InStock',
            'url': f"{STORE}/products/{it['h']}", 'shippingDetails': {'@type': 'OfferShippingDetails', 'shippingDestination': {'@type': 'DefinedRegion', 'addressCountry': 'US'}}}
home_ld = [org,
    {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Mind Body Designs', 'url': STORE + '/', 'inLanguage': 'en-US', 'publisher': {'@id': STORE + '/#org'},
     'potentialAction': {'@type': 'SearchAction', 'target': STORE + '/search?q={search_term_string}', 'query-input': 'required name=search_term_string'}},
    {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]},
    {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Mind Body Designs T-shirts', 'numberOfItems': len(items),
     'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f"{STORE}/products/{it['h']}", 'name': it['f']} for i, it in enumerate(items)]}]
TILE = {'mind': pick('never-give-up'), 'body': pick('lift-heavy'), 'spirit': pick('peace-dove')}
lines = ''.join(f'''<a class="line" href="#{k}" style="--c:var(--{k})"><span><img src="{U(TILE[k]['i'][0], 800)}" alt="{E(TILE[k]['n'])} tee" loading="lazy" width="800" height="800"></span><h3>{LABEL[k]}</h3><p>{CAT_LINE[k]}</p><u>Shop {counts[k]} {LABEL[k]} tees</u></a>''' for k in LABEL)
GIFTS = [('trust-in-the-lord', 'For the friend who prays for you'), ('earn-the-burn', 'For your gym partner'), ('be-kind', 'For you')]
picks = ''.join(f'''<li><a href="products/{pick(h)['h']}.html"><img src="{U(pick(h)['i'][0], 600)}" alt="{E(pick(h)['n'])} tee" loading="lazy" width="600" height="660"><small>{cap}</small><b>{E(pick(h)['n'])}</b></a></li>''' for h, cap in GIFTS)

home = head('Mind Body Designs | Faith, Fitness and Positive Message T-Shirts, Printed in the USA', DESC, STORE + '/', U(hero['spirit']['i'][0], 1200), '', home_ld) + f'''
<body>
{header('', True)}
<main>
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <h1>Graphic tees with a good message</h1>
      <ul class="trio" aria-label="Choose a collection">
        <li><button type="button" data-k="mind" class="on" aria-pressed="true">Mind</button></li>
        <li><button type="button" data-k="body" aria-pressed="false">Body</button></li>
        <li><button type="button" data-k="spirit" aria-pressed="false">Spirit</button></li>
      </ul>
      <p class="hero-line" id="heroLine" aria-live="polite">{HERO_LINE['mind']}</p>
      <div class="hero-cta">
        <a class="btn gold" href="#mind" id="heroShop">Shop Mind tees</a>
        <a class="btn ghost" href="#shop">See all {len(items)}</a>
      </div>
      <p class="note"><b>$34.95 each.</b> Heavyweight garment-dyed cotton, S to 4XL.</p>
    </div>
    <div class="stage">
      {hero_imgs}
      <a class="tag" id="tag" href="products/{hero['mind']['h']}.html"><div><strong id="tagName">{E(hero['mind']['n'])}</strong><span id="tagPrice">${hero['mind']['p']}</span></div><em>View tee</em></a>
    </div>
  </div>
</section>

<div class="trust">
  <div class="wrap">
    <ul>
      <li><b>Printed in the USA</b>Made after you order, one shirt at a time</li>
      <li><b>Free shipping over $75</b>Any 3 tees ship free in the US</li>
      <li><b>S to 4XL</b>Relaxed unisex fit, up to 12 colors</li>
      <li><b>30 day promise</b>Wrong or damaged? We reprint or refund</li>
    </ul>
  </div>
</div>

<section id="shop">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2>Shop the tees</h2>
        <p>{len(items)} designs. Each one comes in up to 12 colors.</p>
      </div>
      <div class="tabs" role="group" aria-label="Filter by collection">
        <button type="button" data-f="all" aria-pressed="true">All <span>{len(items)}</span></button>
        <button type="button" data-f="mind" aria-pressed="false">Mind <span>{counts['mind']}</span></button>
        <button type="button" data-f="body" aria-pressed="false">Body <span>{counts['body']}</span></button>
        <button type="button" data-f="spirit" aria-pressed="false">Spirit <span>{counts['spirit']}</span></button>
      </div>
    </div>
    <ul class="grid" id="grid">
{chr(10).join(card(it, '', i < 4) for i, it in enumerate(items))}
    </ul>
    <div class="more"><button class="btn ghost" type="button" id="more">Show more tees</button></div>
  </div>
</section>

<section class="lines" id="lines">
  <div class="wrap">
    <div class="sec-head"><div><h2>Three collections</h2><p>The name is the map. Every design sits in Mind, Body or Spirit.</p></div></div>
    <div class="line-grid">{lines}</div>
  </div>
</section>

<section class="gift" id="gifts">
  <div class="wrap gift-grid">
    <div>
      <h2>Three tees, free shipping</h2>
      <p class="lead">One for the friend who prays for you, one for your gym partner and one for you. Any three tees clear the $75 free shipping line.</p>
      <div class="math" aria-label="Three tees at $34.95 total $104.85 and ship free">
        <div><b>$34.95</b><span>per tee</span></div>
        <div><b>× 3</b><span>$104.85</span></div>
        <div class="win"><b>$0</b><span>US shipping</span></div>
      </div>
      <p class="note">Buying a gift? Each shirt is printed after you order and ships in 7 to 14 days, so order early.</p>
    </div>
    <ul class="picks">{picks}</ul>
  </div>
</section>

<section class="facts" id="about">
  <div class="wrap facts-grid">
    <div>
      <h2>About Mind Body Designs</h2>
      <p class="about">Mind Body Designs is a US online T-shirt shop. We make graphic tees with positive, faith and fitness messages, printed to order in the USA.</p>
      <p class="about">Mind is for kindness and encouragement. Body is for the gym, the run and the yoga mat. Spirit is for faith, family and friendship.</p>
    </div>
    <dl class="spec">
      <div><dt>Price</dt><dd>$34.95 per tee in S to XL, up to $38.95 in 4XL</dd></div>
      <div><dt>Fabric</dt><dd>Heavyweight garment-dyed cotton with a soft, broken-in feel</dd></div>
      <div><dt>Fit and sizes</dt><dd>Relaxed unisex fit, S to 4XL</dd></div>
      <div><dt>Made in</dt><dd>Printed to order in the USA</dd></div>
      <div><dt>Shipping</dt><dd>Ships in 7 to 14 days, then 2 to 5 business days. US only. Free over $75.</dd></div>
      <div><dt>Returns</dt><dd>Wrong or damaged orders are reprinted or refunded within 30 days</dd></div>
    </dl>
  </div>
</section>

<section class="faq" id="faq">
  <div class="wrap faq-grid">
    <aside>
      <h2>Questions before you order</h2>
      <p>Not answered here? Send a message and a real person will reply.</p>
      <a class="btn ghost" href="{STORE}/pages/contact">Contact us</a>
    </aside>
    <div>{faq_html}</div>
  </div>
</section>

<section class="join">
  <div class="wrap">
    <div class="join-box">
      <div>
        <h2>10% off your first tee</h2>
        <p>And a note when new designs come out.</p>
      </div>
      <div>
        <form onsubmit="event.preventDefault();this.querySelector('button').textContent='Demo only';">
          <input type="email" placeholder="Your email" aria-label="Email address" required>
          <button class="btn" type="submit">Get my 10%</button>
        </form>
        <small>Mockup only. This form does not collect emails.</small>
      </div>
    </div>
  </div>
</section>
</main>
<script>window.MBD_HERO={json.dumps(hero_data, ensure_ascii=False)};</script>
{footer('', True)}
</body>
</html>
'''
os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'products'), exist_ok=True)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(home)

# ---------- product pages ----------
def pdp(it):
    root = '../'; k = it['c']; c0 = it['col'][it['dc']]
    n_col = len(it['col'])
    title = f"{it['n']} T-Shirt | Mind Body Designs"
    desc = f"{it['d']} $34.95, {n_col} colors, sizes S to 4XL. Printed in the USA. Free US shipping over $75."
    canon = f"{STORE}/products/{it['h']}"
    shots = [s for s in (c0[3], c0[2]) if s]
    ld = [{'@context': 'https://schema.org', '@type': 'Product', 'name': it['f'], 'description': ' '.join(it['paras']), 'url': canon,
           'image': [U(s, 1200) for s in shots], 'brand': {'@type': 'Brand', 'name': 'Mind Body Designs'}, 'category': f'T-Shirts > {LABEL[k]}',
           'material': 'Garment-dyed cotton', 'color': [c[0] for c in it['col']], 'size': SIZES, 'audience': {'@type': 'PeopleAudience', 'suggestedGender': 'unisex'}, 'offers': offer(it)},
          {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
              {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': STORE + '/'},
              {'@type': 'ListItem', 'position': 2, 'name': LABEL[k], 'item': STORE + '/collections/all'},
              {'@type': 'ListItem', 'position': 3, 'name': it['n']}]}]
    same = [x for x in items if x['c'] == k and x is not it]
    start = next((i for i, x in enumerate(same) if x['id'] > it['id']), 0)
    rel = (same[start:] + same[:start])[:4]
    rel += [x for x in items if x['c'] != k][it['id'] % 7:][:4 - len(rel)]
    sw = ''.join(f'<button type="button" data-ci="{i}" style="background:{c[1]}" aria-label="{E(c[0])}" aria-pressed="{str(i == it["dc"]).lower()}"></button>' for i, c in enumerate(it['col']))
    sz = ''.join(f'<button type="button" data-si="{i}" aria-pressed="false"{"" if c0[4][i] else " disabled"}>{s}</button>' for i, s in enumerate(SIZES))
    track = ''.join(f'<img src="{U(s, 1200)}" alt="{E(it["n"])} tee in {E(c0[0])}" width="1200" height="1200"{"" if i == 0 else " loading=lazy"}{" fetchpriority=high" if i == 0 else ""}>' for i, s in enumerate(shots))
    return head(title, desc, canon, U(shots[0], 1200), root, ld, 'product') + f'''
<body class="has-sticky">
{header(root, False)}
<main data-pdp="{it['h']}">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}index.html">Home</a><i>/</i><a href="{root}index.html#{k}">{LABEL[k]}</a><i>/</i><span>{E(it['n'])}</span></nav>
    <div class="pdp">
      <div class="gal">
        <div class="gal-track" tabindex="0" aria-label="Product photos">{track}</div>
        <div class="gal-thumbs"></div>
      </div>
      <div class="buy">
        <a class="buy-cat" href="{root}index.html#{k}" style="--c:var(--{k})">{LABEL[k]} collection</a>
        <h1>{E(it['f'])}</h1>
        <p class="buy-price"><b id="pPrice">${it['p']}</b><span id="pFrom">S to XL. 2XL and up from $35.95.</span></p>
        <p class="buy-lede">{E(it['d'])}</p>
        <div id="pick">
          <p class="lab"><b>Color</b><span data-color-name>{E(c0[0])}</span></p>
          <div class="sw" role="group" aria-label="Color">{sw}</div>
          <p class="lab"><b>Size</b><button class="link" type="button" id="fitLink">Size and fit</button></p>
          <div class="sz" role="group" aria-label="Size">{sz}</div>
        </div>
        <div class="buy-row">
          <div class="qty" id="qtyBox"><button type="button" data-q="-1" aria-label="One less">−</button><output id="qtyOut" aria-label="Quantity">1</output><button type="button" data-q="1" aria-label="One more">+</button></div>
          <button class="btn gold" type="button" id="addBtn">Add to cart</button>
        </div>
        <ul class="assure">
          <li><b>Arrives</b><span id="eta">Ships in 7 to 14 days, then 2 to 5 business days in transit.</span></li>
          <li><b>Free shipping</b><span>On US orders over $75. Any 3 tees qualify.</span></li>
          <li><b>Made to order</b><span>Printed in the USA after you order.</span></li>
          <li><b>30 day promise</b><span>Wrong or damaged? We reprint or refund.</span></li>
        </ul>
      </div>
    </div>

    <div class="below">
      <div class="desc">
        <h2>About this design</h2>
        {''.join(f'<p>{E(x)}</p>' for x in it['paras'])}
      </div>
      <div>
        <details open><summary>Fabric and feel</summary><div><p>Heavyweight garment-dyed cotton with a soft, broken-in feel from the first wear.</p><p>Comes in {n_col} colors: {E(', '.join(c[0] for c in it['col']))}.</p></div></details>
        <details id="fit"><summary>Size and fit</summary><div>
          <p>Relaxed unisex fit, sizes S to 4XL. For an oversized look, size up.</p>
          <table class="sizes"><tr><th>Size</th><td>S to XL</td><td>2XL</td><td>3XL</td><td>4XL</td></tr><tr><th>Price</th><td>$34.95</td><td>$35.95</td><td>$37.95</td><td>$38.95</td></tr></table>
          <p class="todo"><b>Note for Cesar:</b> the chest and length chart goes here. The chart on the live store is for a different shirt, so confirm the blank in Printify first.</p>
        </div></details>
        <details><summary>Shipping</summary><div><p>Each shirt is printed after you order. Orders ship within 7 to 14 days, then take 2 to 5 business days to arrive. You get a tracking email when it ships.</p><p>US orders only. Free shipping over $75.</p></div></details>
        <details><summary>Returns</summary><div><p>If your order arrives wrong or damaged, email us within 30 days and we will reprint it or refund you.</p></div></details>
      </div>
    </div>

    <section class="related" aria-labelledby="relH">
      <div class="sec-head"><div><h2 id="relH">More from {LABEL[k]}</h2><p>Add two more tees and US shipping is free.</p></div><a class="link" href="{root}index.html#{k}">See all {counts[k]}</a></div>
      <ul class="grid">
{chr(10).join(card(x, root) for x in rel)}
      </ul>
    </section>
  </div>
</main>
<div class="stickybuy"><div><strong>{E(it['n'])}</strong><span id="stickyInfo"></span></div><button class="btn gold" type="button" id="stickyAdd">Add to cart</button></div>
{footer(root, False)}
</body>
</html>
'''
for it in items:
    open(os.path.join(OUT, 'products', it['h'] + '.html'), 'w', encoding='utf-8').write(pdp(it))

data = {'base': CDN, 'sizes': SIZES, 'prices': PRICES, 'items': [{k: it[k] for k in ('id', 'n', 'h', 'c', 'p', 'col', 'dc')} for it in items]}
open(os.path.join(OUT, 'assets', 'catalog.js'), 'w', encoding='utf-8').write('window.MBD=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';')
for fn in ('site.css', 'site.js'): shutil.copy(os.path.join(BASE, 'site2', fn), os.path.join(OUT, 'assets', fn))

open(os.path.join(OUT, 'llms.txt'), 'w', encoding='utf-8').write(f'''# Mind Body Designs

> US online shop for graphic T-shirts with positive, faith and fitness messages. Tees from $34.95, printed to order in the USA on heavyweight garment-dyed cotton. Free US shipping over $75. Ships within the United States only.

## Collections
- Mind ({counts['mind']} designs): kindness, encouragement and mental health reminders
- Body ({counts['body']} designs): gym, running and yoga tees
- Spirit ({counts['spirit']} designs): Christian faith, scripture, family and friendship

## Facts
- Price: $34.95 in S to XL, $35.95 in 2XL, $37.95 in 3XL, $38.95 in 4XL
- Shipping: printed after ordering, ships in 7 to 14 days, 2 to 5 business days in transit, US only
- Returns: wrong or damaged orders are reprinted or refunded within 30 days
- Store: {STORE}

## Products
''' + '\n'.join(f"- [{it['f']}]({STORE}/products/{it['h']}): ${it['p']}, {LABEL[it['c']]} collection, {len(it['col'])} colors" for it in items) + '\n')
open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8').write('# Mockup only. The real store is https://wearmbd.com\nUser-agent: *\nDisallow: /\n')
pages = [os.path.join(OUT, 'index.html')] + [os.path.join(OUT, 'products', x) for x in os.listdir(os.path.join(OUT, 'products'))]
bad = [fn for fn in pages if re.search('[—–]', open(fn, encoding='utf-8').read())]
print('items', len(items), counts, 'pages with dashes:', bad, 'catalog KB', os.path.getsize(os.path.join(OUT, 'assets', 'catalog.js')) // 1024)
