/* D23b follow-up: the SLEEVED chip's counter reads the live roll count.
 * SUITE: exclude */
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
_getS(); S.run.sleeve='drill_order'; save();
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G._tell, 14000)) return { err: 'no match' };
await until(() => !document.querySelector('.handicap-splash'), 9000);
await sleep(400);
out.tell = G._tell.id; out.sleeve = G._sleeve;
const chipTxt = () => { const a=document.getElementById('famAux');
  const c=a&&[...a.children].find(x=>/SLEEVED/.test(x.textContent));
  return c?c.textContent.replace(/\s+/g,' ').trim():null; };
out.at0 = chipTxt();
G.turnRollCount = 2; famRenderRow();
out.at2 = chipTxt();
G.turnRollCount = 5; famRenderRow();       /* past cap: clamps at 3/3 */
out.at5 = chipTxt();
out.capAt5 = _drillCap();
out.rollLockedClass = (()=>{ _updateDrillLock();
  const b=document.getElementById('btnRoll'); return b?b.className:null; })();
return out;
