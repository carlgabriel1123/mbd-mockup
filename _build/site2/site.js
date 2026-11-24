(() => {
const D = window.MBD, ROOT = document.documentElement.dataset.root || '';
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const U = (f, w) => D.base + f + '&width=' + w;
const LABEL = {mind: 'Mind', body: 'Body', spirit: 'Spirit'};
const money = n => '$' + n.toFixed(2);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const FREE = 75, STORE = 'https://wearmbd.com';

/* ---------- cart (kept in this browser only; checkout hands off to the real store) ---------- */
let cart = [];
try { cart = JSON.parse(localStorage.getItem('mbd_cart')) || []; } catch (e) {}
const save = () => { try { localStorage.setItem('mbd_cart', JSON.stringify(cart)); } catch (e) {} };

document.body.insertAdjacentHTML('beforeend', `
<dialog id="cart" aria-labelledby="cartTitle"><div class="cart">
  <div class="cart-head"><h2 id="cartTitle">Your cart</h2><button class="x" type="button" data-close aria-label="Close cart">✕</button>
    <div class="meter"><span id="meterText"></span><i><u id="meterBar"></u></i></div></div>
  <ul class="cart-lines" id="cartLines"></ul>
  <div class="cart-empty" id="cartEmpty"><p>Your cart is empty.</p><a class="btn" href="${ROOT}index.html#shop">Shop the tees</a></div>
  <div class="cart-foot" id="cartFoot"><p><span>Subtotal</span><span id="cartSub"></span></p>
    <a class="btn gold wide" id="cartGo" target="_blank" rel="noopener">Check out on wearmbd.com</a>
    <small>Mockup cart. Checkout opens the real store with these shirts in it.</small></div>
</div></dialog>
<dialog id="qv" aria-labelledby="qvName"><div class="qv">
  <div class="qv-img"><img id="qvImg" alt=""></div>
  <div class="qv-info"><button class="x" type="button" data-close aria-label="Close">✕</button>
    <h2 id="qvName"></h2><p class="qv-price" id="qvPrice"></p>
    <div id="qvPick"></div>
    <button class="btn gold wide" type="button" id="qvAdd">Add to cart</button>
    <a class="link" id="qvMore">See full details</a>
  </div>
</div></dialog>`);
const cartDlg = $('#cart'), qvDlg = $('#qv');
[cartDlg, qvDlg].forEach(d => d.addEventListener('click', e => { if (e.target === d || e.target.closest('[data-close]')) d.close(); }));

function drawCart() {
  const n = cart.reduce((a, l) => a + l.q, 0), sub = cart.reduce((a, l) => a + l.q * l.p, 0);
  $$('[data-cart-n]').forEach(b => b.textContent = n);
  $('#cartEmpty').hidden = n > 0; $('#cartFoot').hidden = n === 0; $('#cartLines').hidden = n === 0;
  $('#meterText').textContent = n === 0 ? 'Free US shipping on orders over $75.' : sub >= FREE ? 'You have free US shipping.' : 'Add ' + money(FREE - sub) + ' more for free US shipping.';
  $('#meterBar').style.width = Math.min(100, sub / FREE * 100) + '%';
  $('#cartSub').textContent = money(sub);
  $('#cartGo').href = STORE + '/cart/' + cart.map(l => l.v + ':' + l.q).join(',');
  $('#cartLines').innerHTML = cart.map(l => `<li>
    <img src="${U(l.i, 200)}" alt="">
    <div><b>${esc(l.n)}</b><small>${esc(l.c)} / ${esc(l.s)}</small>
      <span class="qty" style="display:inline-flex"><button type="button" data-step="-1" data-v="${l.v}" aria-label="One less">−</button><output>${l.q}</output><button type="button" data-step="1" data-v="${l.v}" aria-label="One more">+</button></span>
      <button class="link rm" type="button" data-rm="${l.v}">Remove</button></div>
    <span>${money(l.q * l.p)}</span></li>`).join('');
}
$('#cartLines').addEventListener('click', e => {
  const s = e.target.closest('[data-step]'), r = e.target.closest('[data-rm]');
  if (s) { const l = cart.find(x => x.v == s.dataset.v); l.q += +s.dataset.step; if (l.q < 1) cart = cart.filter(x => x !== l); }
  else if (r) cart = cart.filter(x => x.v != r.dataset.rm);
  else return;
  save(); drawCart();
});
function addLine(it, ci, si, q) {
  const col = it.col[ci], v = col[4][si], l = cart.find(x => x.v === v);
  if (l) l.q += q; else cart.push({v, h: it.h, n: it.n, c: col[0], s: D.sizes[si], p: +D.prices[si], i: col[3] || col[2], q});
  save(); drawCart();
  if (qvDlg.open) qvDlg.close();
  cartDlg.showModal();
}
$$('[data-open-cart]').forEach(b => b.addEventListener('click', () => cartDlg.showModal()));
drawCart();

/* ---------- color + size picker, shared by quick view and the product page ---------- */
function pickerHTML(it, ci) {
  return `<p class="lab"><b>Color</b><span data-color-name>${esc(it.col[ci][0])}</span></p>
  <div class="sw" role="group" aria-label="Color">${it.col.map((c, i) => `<button type="button" data-ci="${i}" style="background:${c[1]}" aria-label="${esc(c[0])}" aria-pressed="${i === ci}"></button>`).join('')}</div>
  <p class="lab"><b>Size</b></p>
  <div class="sz" role="group" aria-label="Size">${D.sizes.map((s, i) => `<button type="button" data-si="${i}" aria-pressed="false"${it.col[ci][4][i] ? '' : ' disabled'}>${s}</button>`).join('')}</div>`;
}
function bindPicker(root, it, st, onChange) {
  root.addEventListener('click', e => {
    const c = e.target.closest('[data-ci]'), s = e.target.closest('[data-si]');
    if (c) {
      st.ci = +c.dataset.ci; $$('[data-ci]', root).forEach(b => b.setAttribute('aria-pressed', b === c)); $('[data-color-name]', root).textContent = it.col[st.ci][0];
      $$('[data-si]', root).forEach((b, i) => { b.disabled = !it.col[st.ci][4][i]; if (b.disabled && st.si === i) { st.si = -1; b.setAttribute('aria-pressed', false); } });
    }
    else if (s) { st.si = +s.dataset.si; $$('[data-si]', root).forEach(b => b.setAttribute('aria-pressed', b === s)); }
    else return;
    onChange();
  });
}
const needSize = (btn, root) => { btn.textContent = 'Pick a size first'; const f = $('[data-si]', root); if (f) f.focus(); };

/* ---------- quick add ---------- */
let qvIt, qvSt;
function openQV(id) {
  qvIt = D.items[id]; qvSt = {ci: qvIt.dc, si: -1};
  $('#qvName').textContent = qvIt.n; $('#qvMore').href = ROOT + 'products/' + qvIt.h + '.html';
  const box = $('#qvPick'), fresh = box.cloneNode(false); box.replaceWith(fresh);
  fresh.innerHTML = pickerHTML(qvIt, qvSt.ci);
  const draw = () => {
    const c = qvIt.col[qvSt.ci];
    $('#qvImg').src = U(c[3] || c[2], 900); $('#qvImg').alt = qvIt.n + ' tee in ' + c[0];
    $('#qvPrice').textContent = '$' + (qvSt.si < 0 ? D.prices[0] : D.prices[qvSt.si]);
    $('#qvAdd').textContent = 'Add to cart';
  };
  bindPicker(fresh, qvIt, qvSt, draw); draw();
  qvDlg.showModal();
}
$('#qvAdd').addEventListener('click', () => qvSt.si < 0 ? needSize($('#qvAdd'), $('#qvPick')) : addLine(qvIt, qvSt.ci, qvSt.si, 1));
document.addEventListener('click', e => { const b = e.target.closest('[data-qv]'); if (b) openQV(+b.dataset.qv); });

/* ---------- home ---------- */
if ($('.trio')) {
  const H = window.MBD_HERO; let cur = 'mind', timer;
  const setHero = (k, user) => {
    cur = k;
    $$('.trio button').forEach(b => { const on = b.dataset.k === k; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on); });
    $$('.stage img').forEach(i => i.classList.toggle('on', i.dataset.k === k));
    $('#heroLine').textContent = H[k].line;
    $('#heroShop').textContent = 'Shop ' + LABEL[k] + ' tees'; $('#heroShop').href = '#' + k;
    $('#tagName').textContent = H[k].name; $('#tagPrice').textContent = '$' + H[k].price;
    $('#tag').href = 'products/' + H[k].h + '.html';
    if (user) clearInterval(timer);
  };
  const order = ['mind', 'body', 'spirit'];
  $$('.trio button').forEach(b => { b.addEventListener('click', () => setHero(b.dataset.k, true)); b.addEventListener('mouseenter', () => setHero(b.dataset.k, true)); });
  setHero('mind');
  if (!matchMedia('(prefers-reduced-motion:reduce)').matches) timer = setInterval(() => setHero(order[(order.indexOf(cur) + 1) % 3]), 5000);

  let shown = 8, f = 'all';
  const render = () => {
    let n = 0;
    $$('#grid .card').forEach(c => { const ok = f === 'all' || c.dataset.cat === f, vis = ok && n < shown; if (ok) n++; c.hidden = !vis; });
    $('#more').parentElement.hidden = n <= shown;
  };
  const filter = k => { f = k; shown = 8; $$('.tabs button').forEach(b => b.setAttribute('aria-pressed', b.dataset.f === k)); render(); };
  $$('.tabs button').forEach(b => b.addEventListener('click', () => filter(b.dataset.f)));
  $('#more').addEventListener('click', () => { shown += 8; render(); });
  const fromHash = () => { const k = location.hash.slice(1); if (LABEL[k]) { filter(k); $('#shop').scrollIntoView(); } };
  addEventListener('hashchange', fromHash);
  render(); fromHash();
}

/* ---------- product page ---------- */
const pd = $('[data-pdp]');
if (pd) {
  const it = D.items.find(x => x.h === pd.dataset.pdp), st = {ci: it.dc, si: -1};
  const want = new URLSearchParams(location.search).get('color');
  if (want) { const i = it.col.findIndex(c => c[0].toLowerCase() === want.toLowerCase()); if (i >= 0) st.ci = i; }
  const track = $('.gal-track'), thumbs = $('.gal-thumbs'), add = $('#addBtn'), sAdd = $('#stickyAdd');
  let qty = 1;
  const draw = () => {
    const c = it.col[st.ci], shots = [[c[3], 'On model'], [c[2], 'Flat']].filter(s => s[0]);
    track.innerHTML = shots.map((s, i) => `<img src="${U(s[0], 1200)}" alt="${esc(it.n)} tee in ${esc(c[0])}, ${s[1].toLowerCase()}" width="1200" height="1200"${i ? ' loading="lazy"' : ''}>`).join('');
    thumbs.innerHTML = shots.length > 1 ? shots.map((s, i) => `<button type="button" data-shot="${i}" aria-pressed="${i === 0}"><img src="${U(s[0], 200)}" alt=""><span>${s[1]}</span></button>`).join('') : '';
    track.scrollLeft = 0;
    $$('[data-ci]', pd).forEach((b, i) => b.setAttribute('aria-pressed', i === st.ci));
    $('[data-color-name]', pd).textContent = c[0];
    const p = st.si < 0 ? D.prices[0] : D.prices[st.si];
    $('#pPrice').textContent = '$' + p;
    $('#pFrom').hidden = st.si >= 0;
    add.textContent = 'Add to cart'; sAdd.textContent = st.si < 0 ? 'Pick a size' : 'Add to cart';
    $('#stickyInfo').textContent = c[0] + (st.si < 0 ? '' : ' / ' + D.sizes[st.si]) + ' · $' + p;
  };
  bindPicker($('#pick'), it, st, draw); draw();
  thumbs.addEventListener('click', e => { const b = e.target.closest('[data-shot]'); if (b) track.scrollTo({left: b.dataset.shot * track.clientWidth, behavior: 'smooth'}); });
  track.addEventListener('scroll', () => { const i = Math.round(track.scrollLeft / track.clientWidth); $$('[data-shot]', thumbs).forEach((b, j) => b.setAttribute('aria-pressed', i === j)); }, {passive: true});
  $('#qtyBox').addEventListener('click', e => { const b = e.target.closest('[data-q]'); if (!b) return; qty = Math.max(1, Math.min(10, qty + +b.dataset.q)); $('#qtyOut').textContent = qty; });
  add.addEventListener('click', () => st.si < 0 ? needSize(add, $('#pick')) : addLine(it, st.ci, st.si, qty));
  sAdd.addEventListener('click', () => { if (st.si < 0) { $('.sz', pd).scrollIntoView({block: 'center'}); needSize(add, $('#pick')); } else addLine(it, st.ci, st.si, qty); });
  $('#fitLink').addEventListener('click', () => { const d = $('#fit'); d.open = true; d.scrollIntoView({block: 'center'}); });

  /* arrival window from the store's own policy: ships in 7 to 14 days, then 2 to 5 business days */
  const addBiz = (d, n) => { d = new Date(d); while (n > 0) { d.setDate(d.getDate() + 1); if (d.getDay() % 6) n--; } return d; };
  const plus = n => { const d = new Date(); d.setDate(d.getDate() + n); return d; };
  const fmt = d => d.toLocaleDateString('en-US', {month: 'short', day: 'numeric'});
  $('#eta').textContent = 'Order today and it should arrive ' + fmt(addBiz(plus(7), 2)) + ' to ' + fmt(addBiz(plus(14), 5)) + '.';

  const bar = $('.stickybuy');
  new IntersectionObserver(es => bar.classList.toggle('on', !es[0].isIntersecting && es[0].boundingClientRect.top < 0)).observe(add);
}
})();
