/* WHY DID THE HESITATION BEAT FIRE 24 TIMES AND SAY NOTHING?
 * SUITE: exclude   (a measurement)
 *
 * apv_dlg_channels measured a whole match: _dlgHesitate called 24 times, zero
 * lines returned. That is the implausible-rate shape — a beat designed to fire
 * on roughly half of all close calls returning 0/24 is a broken gate, not a run
 * of bad luck, whatever the code reads like. So this opens it up.
 *
 * THREE GATES CAN SWALLOW IT, and they are told apart here because a fix aimed
 * at the wrong one would be indistinguishable from a fix that worked:
 *   1. `typeof G._oppAgg !== 'number'`  — the stash never reaches the caller
 *   2. agg outside 0.40–0.65           — the band is wrong for real matches
 *   3. _dlgEvent returns null          — no pool for this speaker's trait,
 *                                        i.e. the 36 lines are unreachable
 * Recorded per call, so the answer is a distribution and not one anecdote.
 *
 * AND IT RECORDS `trait` AND `art` EVERY TIME. P628 keyed its pools to the six
 * dialogue traits (…, strong) rather than PERSONAS (…, combo). If the seat's
 * trait is not one of the six the lines were written against, gate 3 is
 * unsatisfiable by construction and the band is innocent.
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

for (let a = 0; a < 3; a++) {
  tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break;
}
if (typeof launchSeat !== 'function') return { skip: 'launchSeat unreachable' };

const calls = [];
const realHes = window._dlgHesitate;
if (typeof realHes !== 'function') return { err: '_dlgHesitate is not a global function' };
window._dlgHesitate = function(willBank){
  const agg  = (typeof G !== 'undefined' && G) ? G._oppAgg : undefined;
  const art  = window._lastSeatArt, trait = window._lastSeatTrait;
  const moment = willBank ? 'banksafe' : 'push';
  /* ask _dlgEvent DIRECTLY, ignoring the band, so gate 3 is measured even on
     calls gate 2 would have rejected — otherwise the two are confounded */
  let direct = null; try { direct = _dlgEvent(moment); } catch(e) { direct = 'THREW:' + e; }
  const out = realHes.apply(this, arguments);
  calls.push({ agg: (typeof agg === 'number') ? +agg.toFixed(3) : String(agg),
               inBand: (typeof agg === 'number' && agg >= _HESITATE_LO && agg <= _HESITATE_HI),
               moment, art: art || null, trait: trait || null,
               poolHasLine: !!(direct && !/^THREW/.test(String(direct))),
               got: !!out });
  return out;
};

/* what pools actually exist for the six moments, independent of any match */
const poolNames = {};
try {
  PATRON_LINES.forEach(r => { if (/^trait:/.test(r.p) && /(push|banksafe)$/.test(r.p))
    poolNames[r.p] = (poolNames[r.p] || 0) + 1; });
} catch(e) {}

try { G = null; } catch (e) {}
try { launchSeat(0); } catch (e) { return { err: 'launchSeat threw: ' + e }; }
if (!await until(() => typeof G !== 'undefined' && G && G.pCards !== undefined, 14000))
  return { err: 'match never started' };

const btn = id => document.getElementById(id);
const on  = el => el && !el.classList.contains('disabled') && vis(el);
const DEADLINE = Date.now() + 150000;
while (Date.now() < DEADLINE && !(G && G._endMatchFired) && calls.length < 20) {
  await sleep(280);
  if (on(btn('btnBank'))) { tap(btn('btnBank')); continue; }
  if (G && G.phase === 'choosing' && G.pool) {
    let took = false;
    for (const d of G.pool.filter(x => !x.committed && !x.sel)) {
      try { toggleDie(d); } catch(e) { continue; }
      await sleep(70);
      if (on(btn('btnBank')) || on(btn('btnRoll'))) { took = true; break; }
      try { toggleDie(d); } catch(e) {}
    }
    if (took) continue;
  }
  if (on(btn('btnRoll'))) tap(btn('btnRoll'));
}

const aggs = calls.map(c => c.agg).filter(v => typeof v === 'number');
return {
  arm: 'gate-breakdown',
  calls: calls.length,
  /* CONTROL: no calls means the wrap never fired and every zero below is void */
  control: { wrapFired: calls.length > 0 },

  gate1_aggMissing: calls.filter(c => typeof c.agg !== 'number').length,
  gate2_outOfBand:  calls.filter(c => typeof c.agg === 'number' && !c.inBand).length,
  gate3_noPoolLine: calls.filter(c => c.inBand && !c.poolHasLine).length,
  passedAll:        calls.filter(c => c.got).length,

  band: [typeof _HESITATE_LO !== 'undefined' ? _HESITATE_LO : null,
         typeof _HESITATE_HI !== 'undefined' ? _HESITATE_HI : null],
  aggSeen: aggs,
  aggMin: aggs.length ? Math.min(...aggs) : null,
  aggMax: aggs.length ? Math.max(...aggs) : null,

  seatArt: [...new Set(calls.map(c => c.art))],
  seatTrait: [...new Set(calls.map(c => c.trait))],
  traitPoolsInTable: poolNames,
  sample: calls.slice(0, 8),
};
