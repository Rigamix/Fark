/* Repro v5: every plaque, every die, until the rack is full. SUITE: exclude */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!vis(el)) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
const errs = [];
window.addEventListener('error', e => errs.push({msg:String(e.message), stack:e.error&&e.error.stack, src:e.filename+':'+e.lineno+':'+e.colno }));
const out = { steps: [] };
for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }
_getS(); S.run.gold = 99999;
showScreen('shop'); await sleep(500);
document.getElementById('gbShop')._setTab('ench'); await sleep(400);
for (const k of ENCH_GRID) {
  try{ _stEnchTap(k); }catch(e){ errs.push({msg:k+' tap: '+String(e), stack:e.stack}); }
  await sleep(250);
  const dies = [...document.querySelectorAll('#stEnchPickTray .stPickDie')];
  const free = dies.find(d=>!d.classList.contains('taken'));
  try{ if(free) tap(free); }catch(e){ errs.push({msg:k+' die: '+String(e), stack:e.stack}); }
  await sleep(1600);
  try{ _stEnchPickClose(); }catch(e){ errs.push({msg:k+' close: '+String(e), stack:e.stack}); }
  await sleep(400);
  out.steps.push(k+' free:'+!!free+' errs:'+errs.length);
}
out.dieEnch = S.run.dieEnch;
/* now every die taken: tap plaques again */
for (const k of ['tithe','quicksilver']) {
  try{ _stEnchTap(k); }catch(e){ errs.push({msg:k+'2 tap: '+String(e), stack:e.stack}); }
  await sleep(250);
  try{ _stEnchPickClose(); }catch(e){ errs.push({msg:k+'2 close: '+String(e), stack:e.stack}); }
  await sleep(250);
}
/* and play a boss match with a fully branded rack */
showScreen('gauntlet'); await sleep(500);
try{ launchBossMatch(); out.steps.push('boss launched'); }catch(e){ errs.push({msg:'boss: '+String(e), stack:e.stack}); }
await until(()=>typeof G!=='undefined'&&G&&G.pool!==undefined,12000);
await sleep(2500);
for (let r=0;r<3;r++){ try{ if(typeof handleRoll==='function'&&G&&G.phase!=='over') handleRoll(); }catch(e){ errs.push({msg:'roll'+r+': '+String(e), stack:e.stack}); } await sleep(2600); }
out.matchScreen=(document.querySelector('.screen.active')||{}).id;
out.errors = errs;
return out;
