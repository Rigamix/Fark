/* PROPS vs DICE — OCCLUSION, measured off the rendered DOM.
 *
 * RULED: the invariant is occlusion, not overlap. Dice paint above props, which
 * is the only physically coherent order for a table where the dice are the one
 * thing in motion and the props are set-dressing under everything. So a prop
 * box touching a die box is a die RESTING ON CLUTTER — the composition working.
 * The failure is a die rendering partially hidden BEHIND a prop.
 *
 *   occlusion = geometric overlap AND the prop painting above the die
 *
 * The overlap half is kept because it is the precondition; only the verdict
 * changed. That is why this file was reinterpreted rather than replaced —
 * deleting it and building a successor would have left prop placement with
 * zero coverage in between.
 *
 * TWO EARLIER VERSIONS OF THIS CHECK WERE WRONG, both in ways that produced a
 * confident number:
 *
 *   1. It reported ZERO overlaps having found two UI targets, both buttons,
 *      because the roll had not put dice on the table. A pass against a board
 *      with no dice is the same "it did not fail" as a suite that never ran.
 *      Now: the roll retries, the throw settles, and the verdict asserts on the
 *      KIND of target found, never the count.
 *
 *   2. It computed prop boxes from the template as L = x - w/2, assuming x was
 *      a centre. The renderer writes `left:x%; top:y%`, so x is the LEFT EDGE —
 *      every prop was shifted half its width. It also ignored the per-prop
 *      `rotate()`, which changes the painted extent.
 *      Now: boxes come from getBoundingClientRect on the live <img> elements.
 *      No origin assumption, no aspect table, rotation included by
 *      construction. Read what the browser laid out, not what the data implies.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = { bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2 };
  el.dispatchEvent(new PointerEvent('pointerdown', o)); el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o)); return true; };

const out = { notes: [], overlaps: [], occlusions: [] };

/* ── a live table, with dice actually on it ── */
tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
await until(() => vis(document.getElementById('screen-match')), 9000);
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 14000);

let rolled = false;
for (let attempt = 0; attempt < 3 && !rolled; attempt++) {
  const roll = [...document.querySelectorAll('button,div')]
    .filter(e => vis(e) && /^ROLL$/i.test((e.textContent || '').trim()))[0];
  if (roll) tap(roll);
  rolled = await until(() => [...document.querySelectorAll('.die')].filter(vis).length >= 3, 12000);
  if (!rolled) await sleep(1200);
}
out.rolled = rolled;
await sleep(3000);                       /* a die mid-flight is not where it lands */

/* ── the two casts, both off the rendered DOM ── */
const props = [...document.querySelectorAll('#matchProps img')].filter(vis);
const dice  = [...document.querySelectorAll('.die')].filter(vis);
out.propsRendered = props.length;
out.diceRendered  = dice.length;
/* which template actually dressed this table — FK_PROP_PIN means one ships,
   so counting overlaps across every authored template overstates the problem */
out.pinnedTemplate = (typeof window.FK_PROP_PIN !== 'undefined') ? window.FK_PROP_PIN : null;
out.templatesAuthored = (window.FK_PROP_TEMPLATES || []).length;

/* Paint order for two absolutely-positioned siblings with no z-index is
   DOM order. compareDocumentPosition gives that without guessing. */
function paintsAbove(a, b) {
  const za = +getComputedStyle(a).zIndex, zb = +getComputedStyle(b).zIndex;
  if (!isNaN(za) && !isNaN(zb) && za !== zb) return za > zb;
  return !!(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_PRECEDING);
}

for (const p of props) {
  const pb = p.getBoundingClientRect();
  for (const d of dice) {
    const db = d.getBoundingClientRect();
    if (!(pb.right > db.left && pb.left < db.right && pb.bottom > db.top && pb.top < db.bottom)) continue;
    const name = (p.getAttribute('src') || '').split('/').pop().split('?')[0];
    const above = paintsAbove(p, d);
    const rec = { prop: name, propAboveDie: above };
    out.overlaps.push(rec);
    if (above) out.occlusions.push(rec);   /* the only real failure */
  }
}

out.verdict = {
  diceOnTable:    out.diceRendered >= 3,
  propsRendered:  out.propsRendered > 0,
  /* THE RULED INVARIANT. Overlap is reported, never asserted on. */
  noDieOccluded:  out.occlusions.length === 0
};
return out;
