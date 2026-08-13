/* Repro v4: does the enchant page leak D3X dice / crash over repeated flips? SUITE: exclude */
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
_getS(); S.run.gold = 800;
showScreen('shop'); await sleep(500);
const host = document.getElementById('gbShop');
const count = () => { try{ return {d3:(D3X.dice||[]).length, live:(D3X.dice||[]).filter(d=>d.chip&&d.chip.isConnected).length}; }catch(e){ return {err:String(e)}; } };
out.atStart = count();

/* 12 tab flips */
for (let i=0;i<12;i++){ host._setTab(i%2?'dice':'ench'); await sleep(150); }
out.afterFlips = count();

/* open/close the picker 8 times */
host._setTab('ench'); await sleep(200);
for (let i=0;i<8;i++){ try{_stEnchTap('tithe');}catch(e){errs.push({msg:String(e),stack:e.stack});} await sleep(200);
  try{_stEnchPickClose();}catch(e){errs.push({msg:String(e),stack:e.stack});} await sleep(200); }
out.afterPickers = count();

/* leave/re-enter the shop 6 times */
for (let i=0;i<6;i++){ showScreen('gauntlet'); await sleep(200); showScreen('shop'); await sleep(300); }
out.afterReentries = count();
out.errors = errs;
return out;
