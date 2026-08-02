/* SUITE: exclude — measurement.
 *
 * apv_feat_wall_p425 found four trinkets with real boxes and the screenshot
 * showed bare wood. A box is not a pixel. This reads the computed style and
 * the stacking context for each one, and samples the actual canvas underneath
 * the first trinket's centre, so "it is laid out" and "it is visible" stop
 * being the same claim. */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };

const out = {};
_getS();
S.featsDone = S.featsDone || {}; S.featsPinned = S.featsPinned || {};
['high_roller','clean_night','death_and_taxes','no_claim'].forEach(id => {
  S.featsDone[id] = 1; S.featsPinned[id] = 1;/* PINNED: unpinned ones are mid-ceremony */
});
try { save(); } catch(e) {}

try { famLoadoutShow(); } catch(e) { out.showErr = String(e); }
await until(() => document.querySelector('#gbLoadout .loFeat'), 9000);
await sleep(1600);

const host = document.getElementById('gbLoadout');
out.hostBox = host ? (() => { const r = host.getBoundingClientRect();
  return { x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) }; })() : null;

out.trinkets = [...document.querySelectorAll('#gbLoadout .loFeat')].map(el => {
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  const img = el.tagName === 'IMG' ? el : el.querySelector('img');
  return {
    png: el.dataset.png || null,
    cls: el.className,
    box: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)],
    opacity: s.opacity, display: s.display, visibility: s.visibility,
    zIndex: s.zIndex, position: s.position, transform: s.transform,
    filter: s.filter,
    natural: img ? img.naturalWidth + 'x' + img.naturalHeight : 'no img',
    /* what the browser says is actually on top at this point */
    topmostHere: (() => { const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      return e ? (e.className || e.tagName) + '' : null; })()
  };
});

/* the wall art itself — if it paints OVER the nails, that is the answer */
out.layers = [...document.querySelectorAll('#gbLoadout > *')].slice(0, 12).map(el => {
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return { cls: (el.className || el.tagName) + '', z: s.zIndex, pos: s.position,
           box: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)] };
});

out.verdict = {
  allOpaque:   out.trinkets.every(t => +t.opacity > 0.9),
  allOnTop:    out.trinkets.every(t => /loFeat/.test(t.topmostHere || '')),
  allDecoded:  out.trinkets.every(t => t.natural !== '0x0' && t.natural !== 'no img')
};
return out;
