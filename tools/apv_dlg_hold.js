/* Show a dialogue bubble and HOLD it for the screenshot. SUITE: exclude */
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
_getS(); try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF, 14000)) return { err: 'no match' };
await sleep(2000);
DLG.show("The bones remember every hand that ever rolled them, friend.");
if (DLG.hideTimer) clearTimeout(DLG.hideTimer); /* hold it up */
await sleep(600);
const sr = document.getElementById('dlgScroll').getBoundingClientRect();
const tr = document.getElementById('dlgText').getBoundingClientRect();
return { shown: true, scrollTop: sr.top, gapTop:+(tr.top-sr.top).toFixed(1), gapBottom:+(sr.bottom-tr.bottom).toFixed(1),
  fs: getComputedStyle(document.getElementById('dlgText')).fontSize };
