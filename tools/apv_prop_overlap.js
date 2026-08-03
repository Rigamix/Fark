/* THE PROPS RULE, AS REWRITTEN — do props overlap dice, tags, cards or buttons?
 *
 * The match brief used to ban props from a central VERTICAL band, x 15-85.
 * Measured, the dice occupy x 7.7-97.6 inside a narrow HORIZONTAL strip at
 * y 43-54, so a vertical-band rule cannot express "keep clear of the dice" and
 * props violated it while composing correctly. The brief now states the rule it
 * always meant: PROPS NEVER OVERLAP DICE, TAGS, CARDS OR BUTTONS.
 *
 * SHOWING THE OLD RULE WAS BADLY SHAPED DOES NOT SHOW THE ART WAS FINE. Both
 * could be true - the axis wrong AND some props still encroaching on the strip
 * that actually matters. This is the check that separates them, and it is the
 * acceptance test the brief now names.
 *
 * HEIGHTS ARE NOT IN THE TEMPLATE. Props store {n,x,y,w,rot}; height comes from
 * ASPECT, which is function-scoped inside the props renderer. Read out of the
 * served SOURCE, the same way apv_table_totality reads it, and marked as such -
 * it proves the literal in the file, not the live object. */
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

const out = { notes: [], overlaps: [], checked: 0 };

/* ── ASPECT, out of the source ── */
let ASP = {};
try {
  const src = await (await fetch('fark_proto.html')).text();
  const m = src.match(/\bASPECT\s*=\s*\{([\s\S]*?)\n\s*\};/);
  if (!m) { out.notes.push('ASPECT literal not found in source'); }
  else {
    const re = /([A-Za-z0-9_]+)\s*:\s*\[\s*([\d.]+)\s*,\s*([\d.]+)\s*\]/g;
    let k; while ((k = re.exec(m[1])) !== null) ASP[k[1]] = [ +k[2], +k[3] ];
  }
} catch(e) { out.notes.push('source read: ' + e.message); }
out.aspectKeys = Object.keys(ASP).length;
/* the game falls back from `mug01` to `mug` — mirror that, or every numbered
   prop reports an unknown aspect and the check silently covers nothing */
const baseOf = n => String(n || '').replace(/_?\d+$/, '');
const aspOf  = n => ASP[n] || ASP[baseOf(n)] || null;

/* ── drive to a live table WITH DICE ON IT ── */
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
/* THE DICE ARE THE POINT OF THIS CHECK, so getting them onto the table is a
   precondition, not a best effort. The first version tapped ROLL, waited, and
   then collected whatever happened to be there - it found two buttons and no
   dice, and reported zero overlaps. A pass against a board with no dice on it
   is exactly the "it did not fail" that means nothing. */
let rolled = false;
for (let attempt = 0; attempt < 3 && !rolled; attempt++) {
  const roll = [...document.querySelectorAll('button,div')]
    .filter(e => vis(e) && /^ROLL$/i.test((e.textContent || '').trim()))[0];
  if (roll) tap(roll);
  rolled = await until(() => [...document.querySelectorAll('.die')].filter(vis).length >= 3, 12000);
  if (!rolled) await sleep(1200);
}
out.rolled = rolled;
/* let the throw settle - a die mid-flight is not where it lands */
await sleep(3000);
out.diceVisibleAtTest = [...document.querySelectorAll('.die')].filter(vis).length;

const stage = document.getElementById('screen-match').getBoundingClientRect();
const SW = stage.width, SH = stage.height;
const toPct = r => ({ L: 100*(r.left-stage.left)/SW, R: 100*(r.right-stage.left)/SW,
                      T: 100*(r.top-stage.top)/SH,  B: 100*(r.bottom-stage.top)/SH });

/* the things props must not cover */
const TARGETS = [];
function collect(sel, label) {
  [...document.querySelectorAll(sel)].filter(vis).forEach(el => TARGETS.push({ label, box: toPct(el.getBoundingClientRect()) }));
}
collect('.die', 'die');
collect('.seltag, .sel-tag', 'tag');
collect('#keptTray', 'kept tray');
collect('.match-btn', 'button');
collect('.mcard', 'card');
out.targetCount = TARGETS.length;
out.targetKinds = [...new Set(TARGETS.map(t => t.label))];

/* ── the test ── */
const T = window.FK_PROP_TEMPLATES || [];
out.templateCount = T.length;
const unknown = [];
T.forEach(t => (t.props || []).forEach(p => {
  const a = aspOf(p.n);
  if (!a) { unknown.push(p.n); return; }
  const hPct = (p.w * (a[1]/a[0])) * (SW/SH);   /* width% -> height%, via the stage ratio */
  const box = { L: p.x - p.w/2, R: p.x + p.w/2, T: p.y - hPct/2, B: p.y + hPct/2 };
  out.checked++;
  TARGETS.forEach(tg => {
    if (box.R > tg.box.L && box.L < tg.box.R && box.B > tg.box.T && box.T < tg.box.B) {
      out.overlaps.push({ template: t.name, prop: p.n, hits: tg.label,
        prop_box: [+box.L.toFixed(1), +box.T.toFixed(1), +box.R.toFixed(1), +box.B.toFixed(1)],
        target_box: [+tg.box.L.toFixed(1), +tg.box.T.toFixed(1), +tg.box.R.toFixed(1), +tg.box.B.toFixed(1)] });
    }
  });
}));
out.unknownAspect = [...new Set(unknown)];

/* A COUNT IS NOT COVERAGE. The first run passed `targetsFound` on two buttons
   and zero dice. The assertion has to name the kind that matters, or the check
   can quietly test nothing and still go green. */
out.verdict = {
  aspectReadable:   out.aspectKeys > 0,
  everyPropSized:   out.unknownAspect.length === 0,
  diceOnTable:      (out.diceVisibleAtTest || 0) >= 3,
  targetsFound:     out.targetKinds.indexOf('die') >= 0,
  noPropOverlapsUI: out.overlaps.length === 0
};
return out;
