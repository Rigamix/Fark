/* D6a: the deal honours the preserved SEAT - a lane marked _pvLane gets no
 * fresh die while the amber holds its occupant. SUITE: exclude */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!vis(el)) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => document.querySelector('.nrdie'), 9000); await sleep(500);
  tap(document.querySelector('.nrdie')); await sleep(1200);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }
_getS(); try { G = null; } catch (e) {}
launchBossMatch();
let ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000);
if (!ok) { try { G = null; } catch (e) {} launchBossMatch();
  ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000); }
if (!ok) return { err: 'no idle' };
/* claim seat 2 BEFORE the first deal - the initial deal runs through the
   same _freeLanes walk the restore turn uses, so this drives the REAL code
   with a non-empty result (the earlier reroll variant produced poolLen 0 and
   a vacuously-true assertion). */
G._pvLane = 2;
G.numDice = G.matchDice.length - 1; /* the amber pays one die, like the restore */
handleRoll();
if (!await until(() => G.pool && G.pool.length >= 4, 8000)) return { err: 'no pool' };
await sleep(2200);
const out = { dealt: G.pool.map(d => d.lane).sort(), poolLen: G.pool.length,
  numDice: G.numDice, matchLen: G.matchDice.length };
out.preservedSeatUntouched = G.pool.length > 0 && !G.pool.some(d => d.lane === 2);
out.lanesUnique = new Set(G.pool.map(d => d.lane)).size === G.pool.length;
return out;
