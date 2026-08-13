/* MUSIC DUCK CENSUS PROBE — confirm dead-air is reachable and ducks the music gain.
 * SUITE: exclude */
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
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.target, 14000)) return { err: 'no match' };
await sleep(2600);

out.layer = _bgCurrentLayer;
out.target = G.target;
out.gainBefore = {
  tavern: BG_TAVERN.gain ? BG_TAVERN.gain.gain.value : null,
  boss: BG_BOSS.gain ? BG_BOSS.gain.gain.value : null,
  amb: BG_AMB['gain'+BG_AMB.active] ? BG_AMB['gain'+BG_AMB.active].gain.value : null
};
out.deadAirBefore = _deadAirOn;

/* Push opponent score to 85% of target and hit the turn-boundary check */
G.oPts = Math.ceil(G.target*0.86);
_checkDeadAir();
await sleep(1400); /* let the 1100ms _fadeGain ramp finish */

out.deadAirAfter = _deadAirOn;
out.gainAfter = {
  tavern: BG_TAVERN.gain ? BG_TAVERN.gain.gain.value : null,
  boss: BG_BOSS.gain ? BG_BOSS.gain.gain.value : null,
  amb: BG_AMB['gain'+BG_AMB.active] ? BG_AMB['gain'+BG_AMB.active].gain.value : null
};
out.statusMsg = (document.getElementById('statusMsg')||{}).textContent || null;
out.deadAirClass = document.getElementById('screen-match').classList.contains('dead-air');
return out;
