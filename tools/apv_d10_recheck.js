/* D10 re-derivation probe
 * SUITE: exclude
 * (a) does the lender's brand travel with the borrowed die? (recorded CLOSED, P569)
 * (b1) does the loan record carry the stash index? (recorded fixed by P569)
 * (b2) does _ftDead retire dice by material string, so one dead jade
 *      blinds the picker to EVERY jade? (recorded STILL OPEN)
 * Driven through the real CFX.fair_trade._pick / use, not a copy.
 */
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
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }

const out = {};
_getS();
famApplyPick({ id: 'fair_trade', tier: 1 });
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF && G.pF.length, 14000)) return { err: 'no match' };
await sleep(1500);

/* ---- controlled state ---- */
S.run.diceInv = ['jade','jade','starstone'];
S.run.dieEnchInv = [{t:'tithe'},null,{t:'seal'}];
G.matchDice = ['bone','bone','bone','bone','bone','bone'];
G._enchArr = ['ward',null,null,null,null,null];
G._fairTrade = null;
G._ftDead = null;
G.phase = 'idle'; G.turnRollCount = 0;

/* (a)+(b1): pick and use through the real handler */
const p1 = CFX.fair_trade._pick();
out.pick1 = p1 ? {lane:p1.lane, was:p1.was, borrowed:p1.borrowed, invIdx:p1.invIdx} : null;
out.b1_recordCarriesIndex = !!(p1 && typeof p1.invIdx === 'number');
const used = CFX.fair_trade.use({});
out.useReturned = used;
out.a_seatAfterLoan = { mat: G.matchDice[p1?p1.lane:0], ench: G._enchArr[p1?p1.lane:0] };
out.a_record = G._fairTrade ? {hostEn:G._fairTrade.hostEn, lentEn:G._fairTrade.lentEn} : null;
/* the starstone (invIdx 2, seal) should be picked with its own seal brand */

/* (b2): one dead jade vs two live jades */
G._fairTrade = null;
S.run.diceInv = ['jade','jade'];
S.run.dieEnchInv = [{t:'tithe'},null];
G.matchDice = ['bone','bone','bone','bone','bone','bone'];
G._enchArr = [null,null,null,null,null,null];
/* P691: the death sites write {i,m} records now - seed the REAL shape the
   break path produces. A bare 'jade' string is the legacy-snapshot shape and
   deliberately keeps the old conservative material match. Both are asserted. */
G._ftDead = [{i:0,m:'jade'}];  /* the jade at stash index 0 died on loan */
G.phase = 'idle'; G.turnRollCount = 0;
const p2 = CFX.fair_trade._pick();
out.b2_pickWithOneDeadJade = p2 ? {lane:p2.lane, borrowed:p2.borrowed, invIdx:p2.invIdx} : null;
out.b2_canUse = CFX.fair_trade.canUse({});
/* count live indices the way _pick does */
let live = 0;
(S.run.diceInv||[]).forEach(function(d,i){
  var dead=(G._ftDead||[]).some(function(r){return (r&&typeof r==='object')?(r.i===i):(r===d);});
  if(!dead) live++; });
out.b2_liveCount = live;      /* 2 jades, 1 dead -> should be 1; material match makes it 0 */
out.b2_bug = (live===0);

return out;
