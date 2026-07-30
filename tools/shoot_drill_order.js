/* DRILL ORDER — is "Hot Dice rolls free" reachable, and does the lock message
 * fit on the screen?
 *
 * Backlog 4. Plays a real match (see shoot_play.js), installs Brutus's tell,
 * then walks the turn to the roll cap. Faces are forced between rolls so the
 * walk is repeatable — the subject here is the ROLL button and its message, not
 * the scoring engine, and an unlucky roll would otherwise bust the turn before
 * the cap is reached.
 *
 *   node tools/shoot.js --eval-file tools/shoot_drill_order.js --out drill.png
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(70); }
  return false; };
const trace = [];
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = (el, why) => { if (!vis(el)) { trace.push('SKIP ' + why); return false; }
  const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown', o));
  el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o)); trace.push('tap ' + why); return true; };

tap(document.getElementById('hsBtnBottom'), 'NEW RUN'); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie'), 'die'); await sleep(1300);
tap(document.getElementById('nrTakeBtn'), 'TAKE IT'); await sleep(1900);
const pt = [...document.querySelectorAll('.ptcard')].filter(vis)[0];
if (pt) { tap(pt, 'patron'); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')]
  .filter(e => vis(e) && e.children.length <= 1 && /^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if (sit) { tap(sit, 'SIT DOWN'); if (sit.parentElement) tap(sit.parentElement, 'parent'); }
await until(() => vis(document.getElementById('screen-match')), 9000);
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 14000);

/* Brutus's tell, from the real definition */
G._tell = _tellById('drill_order');
G._tellState = {};
/* _initTellHUD BUILDS the badge; _updateTellHUD only refreshes its numbers, so
   swapping the tell in needs both or #drillVal never exists. */
try { _initTellHUD(); _updateTellHUD(); } catch (e) {}

const rollBtn = () => document.getElementById('btnRoll');
const locked = () => rollBtn().classList.contains('roll-locked');
const dis = id => { const e = document.getElementById(id); return e && e.classList.contains('disabled') ? 'off' : 'on'; };
const statEl = () => { const b = document.getElementById('statusBot'), t = document.getElementById('statusTop');
  return (b && (b.textContent||'').trim()) ? b : t; };
const snap = label => { const se = statEl(), sr = se ? se.getBoundingClientRect() : null;
  return { label, count: G.turnRollCount, phase: G.phase,
    ROLL: dis('btnRoll'), rollLocked: locked(), BANK: dis('btnBank'),
    pointerEvents: getComputedStyle(rollBtn()).pointerEvents,
    free: G.pool.filter(d => !d.committed).length,
    status: se ? (se.textContent||'').trim() : '',
    statusBox: sr ? [Math.round(sr.left), Math.round(sr.width)] : null,
    fitsScreen: sr ? (sr.left >= 0 && sr.right <= innerWidth) : null,
    drillHud: ((document.getElementById('drillVal')||{}).textContent)||null,
    turnPts: G.turnPts }; };
const freeDice = () => G.pool.filter(d => !d.committed);
/* force faces so the walk to the cap is repeatable */
const force = vals => { freeDice().forEach((d, i) => { d.val = vals[i % vals.length];
    try { reDrawDieFace(d); } catch (e) {} }); try { refreshSelUI(); } catch (e) {} };
const rollWait = async why => { tap(rollBtn(), 'ROLL ' + why);
  await until(() => G.phase === 'choosing' || G.phase === 'idle', 12000); await sleep(350);
  trace.push('after ' + why + ': count=' + G.turnRollCount + ' free=' + freeDice().length); };

const steps = [];
const errs = []; window.addEventListener('error', e => errs.push(String(e.message)));

/* three rolls, keeping one scoring die each time, to reach the cap */
await rollWait('#1');
force([1, 2, 2, 2, 2, 2]); tap(freeDice()[0].el, 'keep the 1'); await sleep(300);
await rollWait('#2');
force([1, 2, 2, 2, 2]); tap(freeDice()[0].el, 'keep the 1'); await sleep(300);
await rollWait('#3');
steps.push(snap('at the cap, nothing selected'));

/* partial selection: still blocked, and the message has to be readable */
force([1, 5, 2, 2]);
tap(freeDice()[0].el, 'select one die'); await sleep(300);
steps.push(snap('capped, partial selection — want rollLocked=true'));
tap(rollBtn(), 'ROLL at cap (refused)'); await sleep(400);
steps.push(snap('after refused press — want the lock message, on screen'));

/* every die selected: this press clears the row, which is the free hot roll */
force([1, 5, 1, 5]);
freeDice().forEach(d => { if (!d.sel) tap(d.el, 'select ' + d.val); });
await sleep(400);
steps.push(snap('capped, whole row selected — want rollLocked=false'));
const before = { count: G.turnRollCount, pPts: G.pPts };
/* who spends an allowance slot on the free roll? */
const bumps = [];
(function trapCount(){
  let v = G.turnRollCount;
  Object.defineProperty(G, 'turnRollCount', { configurable: true,
    get(){ return v; },
    set(nv){ if (nv > v) bumps.push(v + '->' + nv + ' :: ' + (new Error().stack||'')
        .split(String.fromCharCode(10)).slice(1,4)
        .map(l=>l.replace(/^\s*at\s*/,'').replace(/\s*\(.*$/,'')).join(' < '));
      v = nv; } });
})();
tap(rollBtn(), 'ROLL (hot dice, free)');
await until(() => G.phase === 'choosing' || G.phase === 'idle', 14000);
await sleep(600);
steps.push(snap('after the free roll — want 6 fresh dice'));

return { trace, steps, errs, before, bumps,
  drillHud: (document.getElementById('drillVal')||{}).textContent,
  hotFired: !!G._lastHotDice, countAfter: G.turnRollCount,
  poolAfter: G.pool.length, freeAfter: G.pool.filter(d => !d.committed).length,
  screenW: innerWidth };
