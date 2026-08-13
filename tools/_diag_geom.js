/* Live geometry for P677: roll's left edge, pause's box, turn label spans.
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
_getS(); try { G = null; } catch (e) {}
launchBossMatch();
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 16000);
await sleep(400);
const g = id => { const e = document.getElementById(id) || document.querySelector(id);
  if (!e) return null; const r = e.getBoundingClientRect();
  return { l: +r.left.toFixed(1), t: +r.top.toFixed(1), w: +r.width.toFixed(1), h: +r.height.toFixed(1) }; };
const w = document.getElementById('turnNum').querySelector('.tn-w');
const n = document.getElementById('turnNum').querySelector('.tn-n');
return {
  screen: g('screen-match'),
  roll: g('.match-btn-roll'),
  pause: g('matchPause'),
  tnW: w ? { fs: getComputedStyle(w).fontSize, text: w.textContent } : null,
  tnN: n ? { fs: getComputedStyle(n).fontSize, text: n.textContent } : null
};
