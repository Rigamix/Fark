/* Does routing through _legalKeeps stay inert when a WILD die is present?
   SUITE: exclude — investigates, does not claim.

   apv_keep_control swept 852 rolls and found K[0] identical to used[] on both
   points and dice. It swept ALL-BONE with cards=[]. Reading scoreSelection
   afterwards turned up two ways that result may not transfer:

     1. consume-extras cards let a selection keep non-scoring dice. Checked:
        bookends/twin_fury/sevens_gift/lucky_seven/ascending are all in CARDS
        with NPC_CARDS=0, and _orderSensitive keys off the_ladder/ascending.
        Player-only, so it cannot reach the rival. Not a risk.

     2. WILD MATERIALS. scoreSelection scores a second time treating each wild
        as the face it shows and keeps whichever is worth more - "a Jade 6 can
        never be a 6" otherwise. scoreRoll alone does not. jade/jade2 are in
        the straights persona's dieBias, so the rival CAN hold them.

   If K[0].pts can exceed r.total with a wild in hand, then wiring the NPC keep
   through _legalKeeps is NOT inert and the persona before/after would be
   measuring two changes at once. That is the whole reason for the split. */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };

tap(document.getElementById('hsBtnBottom')); await sleep(2000);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 12000);
tap(document.querySelector('.nrdie')); await sleep(1500);
tap(document.getElementById('nrTakeBtn')); await sleep(2400);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 12000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1800); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
await until(() => vis(document.getElementById('screen-match')), 12000);
const ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 40000);
if (!ok || typeof G === 'undefined' || !G) return { skip: 'no idle match' };

const out = {};

/* 1. which materials are actually wild, per the game's own definition? */
const wilds = [];
try {
  const mats = ['bone','iron','lead','brass','crystal','amber','flint','jade','jade2','obsidian','silver'];
  for (const m of mats) {
    const dt = getDie(m);
    if (dt && dt.effect && /^wild_/.test(dt.effect.mechanic || '')) wilds.push(m);
  }
} catch (e) { out.wildProbeErr = String(e).slice(0, 80); }
out.wildMaterials = wilds;

/* 2. is a wild material reachable for the rival? */
try {
  const bias = Object.keys(PERSONAS).map(k => k + ':' + PERSONAS[k].dieBias.filter(m => wilds.indexOf(m) >= 0).join('/'));
  out.personaWildBias = bias.filter(b => !/:$/.test(b));
} catch (e) {}

/* 3. THE MEASUREMENT. Same comparison apv_keep_control makes, but with a wild
      in the dice rather than all-bone. */
function multisets(n) {
  const res = [], cur = [];
  (function rec(s) { if (cur.length === n) { res.push(cur.slice()); return; }
    for (let f = s; f <= 6; f++) { cur.push(f); rec(f); cur.pop(); } })(1);
  return res;
}

const W = wilds[0] || 'jade';
let checked = 0, ptsDiff = 0, diceDiff = 0;
const ex = [];

/* one wild in the first seat, rest bone - the cheapest way to make the
   second pass fire without exploding the search space */
for (let n = 2; n <= 5; n++) {
  for (const vals of multisets(n)) {
    const mats = vals.map((_, i) => (i === 0 ? W : 'bone'));
    const free = vals.map((v, i) => ({ val: v, mat: mats[i] }));
    let r, K;
    try {
      r = scoreRoll(vals, [], 0, {}, mats);
      K = _legalKeeps(vals.map((v, i) => ({ val: v, mat: mats[i] })), 'o');
    } catch (e) { continue; }
    const dead = !r || !r.total || r.total <= 0;
    if (dead) continue;
    if (!K.length) { ptsDiff++; if (ex.length < 6) ex.push(vals.join('') + '[' + W + '@0] scores ' + r.total + ' but 0 candidates'); continue; }
    checked++;
    const usedN = r.used ? r.used.filter(Boolean).length : 0;
    if (K[0].pts !== r.total) {
      ptsDiff++;
      if (ex.length < 6) ex.push(vals.join('') + '[' + W + '@0] best=' + K[0].pts + ' vs maximal=' + r.total);
    } else if (K[0].sel.length !== usedN) {
      diceDiff++;
      if (ex.length < 6) ex.push(vals.join('') + '[' + W + '@0] bestKeeps=' + K[0].sel.length + ' vs used=' + usedN);
    }
  }
}
out.rollsChecked = checked;
out.ptsDivergences = ptsDiff;
out.diceDivergences = diceDiff;
out.examples = ex;
return out;
