/* A BOSS MATCH WITH TAMPER PLAYED — the rival's broken card, shaking and grey.
 * SUITE: exclude
 *
 * Shoots the state the P666/P668 probe verifies numerically, so the numbers and
 * the picture come from the same run. Boss, not patron: _famInitOpp only deals
 * the rival family cards when _bossKey(rung) is truthy, so a patron seat has
 * nothing to break and this would photograph an empty row.
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

_getS();
famApplyPick({ id: 'tamper', tier: 1 });
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF && G.pF.length, 14000))
  return { err: 'boss match never started' };
await sleep(2600);

const idx = G.pF.findIndex(c => c && c.id === 'tamper');
if (idx < 0 || !(G.oF || []).some(o => o && !o.broken))
  return { err: 'nothing to break', rival: (G.oF||[]).map(c=>c&&c.id) };

famUse(idx);
/* the burst starts right after this returns, so the frames catch the shake */
return { broke: (G.oF || []).filter(c => c.broken).map(c => c.id) };
