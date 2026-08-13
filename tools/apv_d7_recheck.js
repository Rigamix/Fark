/* D7 re-derivation: roll-forces buffer clearing (P556/P556b)
 * SUITE: exclude
 * Three arms, all against the live functions:
 *  A. arm a peek with a length that CANNOT match free count, call
 *     famApplyRollForces -> buffer must be null after (spent by the roll).
 *  B. arm both buffers, call endPTurn's clearing path via _clearRollForces
 *     presence check + call startPTurn-equivalent: we call the real
 *     endPTurn? too heavy - instead assert the call sites exist in the
 *     live function sources (Function.prototype.toString of startPTurn /
 *     endPTurn) AND directly verify _clearRollForces nulls both.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const tap = el => { if(!el) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }

const out = {};
_getS();
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && Array.isArray(G.pool), 14000)) return { err: 'no G' };
await until(() => G.pool.length > 0, 12000);
out.poolLen = G.pool.length; out.phase = G.phase;
await sleep(1500);

/* A: mismatched peek is spent, not left armed */
G._famPeekVals = [9,9,9,9,9,9,9]; /* length 7, can never equal free count */
G._famHoneyVal = null;
const freeCount = G.pool.filter(d=>!d.committed&&!d._frozen).length;
famApplyRollForces();
out.armA = { freeCount, peekAfterMismatchApply: G._famPeekVals, cleared: G._famPeekVals===null };

/* B: _clearRollForces nulls both */
G._famPeekVals = [1,2,3]; G._famHoneyVal = 5;
_clearRollForces();
out.armB = { peek: G._famPeekVals, honey: G._famHoneyVal };

/* C: the two lifecycle call sites exist in the LIVE functions */
out.armC = {
  startPTurnCalls: /_clearRollForces\(\)/.test(startPTurn.toString()),
  endPTurnCalls: /_clearRollForces\(\)/.test(endPTurn.toString()),
  applyCallsAtEnd: /_clearRollForces\(\);/.test(famApplyRollForces.toString())
};
return out;
