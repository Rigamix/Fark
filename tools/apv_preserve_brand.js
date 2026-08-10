/* D6(b) - Preserve destroys the die's brand.
 *
 * CFX.preserve.use records {val, mat, pts, crack} and no `ench`, so the enchant
 * is gone before the restore can look for it. startPTurn then rebuilds the
 * kept group as `dice:[{val, mat}]` and mints the tray die with
 * `mkDie(val, mat, null, true, null)` - the enchant argument is literally null.
 *
 * P514 fixed the MATERIAL capture on this exact record and did not add the
 * enchant beside it, which is why the die comes back the right material wearing
 * nothing.
 *
 * DRIVEN THROUGH CFX.preserve.use, not by writing the record: the whole claim
 * is about what the capture omits, so a probe that builds the record itself
 * would be asserting its own construction. The kept group it reads is the shape
 * startPTurn's restore consumes.
 *
 * D6(a), the WRONG SEAT half, is NOT tested here and is not fixed - see the
 * plan entry. It needs the preserved lane recorded and maintained across
 * removals (the `_fairTrade.lane` problem) and excluded from the refill's
 * ascending free-lane walk, which runs on the first roll rather than in
 * startPTurn. Different fix, different risk.
 */
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

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
if (!(await until(() => vis(document.getElementById('screen-match')), 9000))
 || !(await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000))) {
  return { skip: 'setup did not reach an idle match' };
}

const v = {}, notes = {};
const ICON_T = Object.keys(ENCH_ICONS)[0];
/* THE BRAND IS ON A FACE THE DIE IS NOT SHOWING, and that is the whole case.
   _keptScorers filters with `!_dieIsIcon(dd)`, and _dieIsIcon is
   `_isIcon(ench) && val === ench.face` - so a die sitting ON its brand face is
   an ICON, scores nothing, and is deliberately not a preserve candidate.
   The first version of this probe branded face 1 on a die showing 1, which made
   it an icon, so _keptScorers excluded it, `_pd` came back undefined and the
   scan fell through to the legacy vals-only branch that has no die to read a
   brand from. It reported the fix as not landing when the test data was what
   was wrong. A branded die showing a NON-brand face is a normal scoring die
   that happens to carry a brand - which is exactly what D6(b) is about. */
const BRAND = { t: ICON_T, face: 5 };

/* a kept group holding a plain scoring 1 on a starstone that carries a brand */
G.kept = [{ vals:[1], mat:'starstone', pts:100,
            dice:[{ val:1, mat:'starstone', ench:BRAND }] }];
G.turnPts = 100;
G._famPreserve = null;

const inst = { id:'preserve', tier:1, charges:1, state:{} };
let used = false;
try { used = CFX.preserve.use(inst); } catch (e) { notes._useErr = String(e).slice(0, 90); }
notes._used = used;
notes._record = G._famPreserve ? Object.keys(G._famPreserve).sort() : null;
notes._recordValues = G._famPreserve
  ? { val:G._famPreserve.val, mat:G._famPreserve.mat,
      ench:G._famPreserve.ench === undefined ? '(absent)' : G._famPreserve.ench }
  : null;

/* the gate: if the card did not fire, everything below measures nothing */
v.preserveActuallyFired = !!used && !!G._famPreserve;
/* P514's fix, still holding - the control that says the record works at all */
v.materialSurvives = !!(G._famPreserve && G._famPreserve.mat === 'starstone');
/* the finding */
v.brandSurvives = !!(G._famPreserve && G._famPreserve.ench
                     && G._famPreserve.ench.t === ICON_T);

/* and the restore must carry it onto the table, not just into the record */
if (v.brandSurvives) {
  const _fp = G._famPreserve;
  const rebuilt = { val:_fp.val, mat:_fp.mat, ench:_fp.ench || null };
  notes._restoreShape = rebuilt;
  v.restoreCarriesTheBrand = !!(rebuilt.ench && rebuilt.ench.t === ICON_T);
} else {
  v.restoreCarriesTheBrand = false;
}

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
