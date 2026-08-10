/* P560 - Last Stand records the die's material and, until now, dropped its brand.
 *
 * `G.kept.push({vals:[freeV[0]], mat:d.mat, pts:600, dice:[{val, mat}]})` builds
 * a kept group from a LIVE POOL DIE. `d` carries `d.ench` - the same object
 * `_rollD` and `_dieIsIcon` read - and the branch's own gate is
 * `!_dieIsIcon(free[0])`, so the die is explicitly NOT sitting on its brand
 * face. A die branded on a different face scoring as a plain 1 or 5 is exactly
 * the case D6(b) was about, and this is the second site with that shape.
 *
 * It matters because the kept group is not a display record: `_keptScorers`,
 * `CFX.preserve.use` and every downstream icon check read `k.dice[].ench`.
 *
 * DRIVEN THROUGH THE REAL BRANCH, gated on the branch having fired - a probe
 * that asserts a field on a group nobody pushed would pass on an empty table,
 * which is how the D3 probe passed against a broken build earlier.
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
/* branded on face 5 while SHOWING 1: a plain scoring die that carries a brand.
   Branding the shown face would make it an icon and the branch's own
   !_dieIsIcon gate would refuse to fire - the D6(b) test-data trap. */
const BRAND = { t: ICON_T, face: 5 };

G.pCards = (G.pCards || []).concat(['last_stand']);
G.kept = []; G.turnPts = 0; G.phase = 'choosing'; G.turnRollCount = 1;
G.pool = [{ lane:0, mat:'starstone', val:1, committed:false, _frozen:false,
            sel:false, ench:BRAND, el:document.createElement('div') }];

notes._preconditions = {
  hasCard: G.pCards.includes('last_stand'),
  freeCount: G.pool.filter(d => !d.committed).length,
  val: G.pool[0].val,
  isIcon: _dieIsIcon(G.pool[0])   /* must be FALSE or the branch refuses */
};
try { _afterRollImpl(); } catch (e) { notes._err = String(e).slice(0, 90); }

const grp = (G.kept || [])[0] || null;
notes._group = grp ? { pts: grp.pts, mat: grp.mat,
                       die: grp.dice && grp.dice[0] } : null;

/* THE GATE: a field assertion on a group nobody pushed proves nothing */
v.lastStandActuallyFired = !!(grp && grp.pts === 600);
v.materialRecorded = !!(grp && grp.dice && grp.dice[0] && grp.dice[0].mat === 'starstone');
v.brandRecorded = !!(grp && grp.dice && grp.dice[0] && grp.dice[0].ench
                     && grp.dice[0].ench.t === ICON_T);

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
