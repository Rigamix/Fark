/* D25 re-derivation: does the player's Blessed Confiscation still push a
 * seventh seat, and is it reachable in the current build?
 * SUITE: exclude
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

/* 1. Is the card offered by the boss-reward pool for Ambrose? (static check on live data) */
const amb = RUNGS[7];
out.ambroseHasCard = (amb.cardPool||[]).includes('blessed_confiscation');
const pool=[];
(amb.cardPool||[]).forEach(cid=>{const cd=getNpcCard(cid);if(cd)pool.push(cd);});
const active=pool.find(c=>c.type==='active');
out.rewardGuaranteedActive = active ? active.id : null;

/* 2. Equip it in the boss slot exactly as _rewardSelectCard / _showLegendDraft do */
S.run.cards[0]='blessed_confiscation';
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.matchDice && G.matchDice.length, 14000)) return { err: 'no match' };
await sleep(2000);

out.pCards = [...(G.pCards||[])];
out.usedCards = G.activeCardState ? {...G.activeCardState.usedCards} : null;
out.phaseAtStart = G.phase;
out.canActivateAtStart = canActivateCard('blessed_confiscation');
/* Reach the 'idle' window via the game's own turn entry — startPTurn is the
 * canonical start of every player turn and is what sets phase='idle'. */
startPTurn();
await until(()=>G.phase==='idle', 4000);
out.phaseAtTest = G.phase;
out.canActivate = canActivateCard('blessed_confiscation');

out.before = { matchDice: [...G.matchDice], len: G.matchDice.length,
  enchLen: (G._enchArr||[]).length, opp: G.matchOppDice.length, numDice: G.numDice };

activateCard('blessed_confiscation');
await sleep(300);

out.after = { matchDice: [...G.matchDice], len: G.matchDice.length,
  enchLen: (G._enchArr||[]).length, opp: G.matchOppDice.length, numDice: G.numDice };
out.seventhSeatPushed = out.after.len === out.before.len + 1;
out.enchDesynced = out.after.len !== out.after.enchLen;

/* Does the seventh seat actually get DEALT on the next turn?
 * startPTurn recomputes numDice from matchDice.length. */
startPTurn();
await until(()=>G.phase==='idle', 4000);
out.nextTurn = { numDice: G.numDice, matchDiceLen: G.matchDice.length };
handleRoll();
await until(()=>G.phase==='choosing'||G.phase==='rolling', 5000);
await sleep(2500);
out.rolled = { poolLen: (G.pool||[]).length, phase: G.phase };
return out;
