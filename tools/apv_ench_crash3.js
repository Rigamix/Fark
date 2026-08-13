/* Repro v3: brand dice at the shop, then PLAY - does the match crash? SUITE: exclude */
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
window.addEventListener('error', e => errs.push({msg:String(e.message), stack:e.error&&e.error.stack?String(e.error.stack):null, src:e.filename+':'+e.lineno+':'+e.colno }));
window.addEventListener('unhandledrejection', e => errs.push({msg:'rej: '+String(e.reason), stack:e.reason&&e.reason.stack?String(e.reason.stack):null}));
const out = { steps: [] };
const step = s => out.steps.push(s + ' [errs:' + errs.length + ']');

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }
step('run:'+!!(S&&S.run));
_getS(); S.run.gold = 3000;

/* brand through the real shop flow: one icon brand + quicksilver */
showScreen('shop'); await sleep(500);
const host = document.getElementById('gbShop');
try{ host._setTab('ench'); }catch(e){errs.push({msg:'setTab '+e,stack:e.stack});}
await sleep(400);
for (const k of ['tithe','ward','quicksilver']) {
  try{ _stEnchTap(k); }catch(e){errs.push({msg:k+' tap '+e,stack:e.stack});}
  await sleep(250);
  try{ const d=document.querySelector('#stEnchPickTray .stPickDie:not(.taken)'); if(d) tap(d); }catch(e){errs.push({msg:k+' die '+e,stack:e.stack});}
  await sleep(1600);
  try{ _stEnchPickClose(); }catch(e){errs.push({msg:k+' close '+e,stack:e.stack});}
  await sleep(400);
}
step('branded: '+JSON.stringify(S.run.dieEnch));

/* back out and play a seat match */
showScreen('gauntlet'); await sleep(600);
try{ launchSeat(0); step('launchSeat ok'); }
catch(e){ step('launchSeat THREW'); errs.push({msg:'launchSeat '+String(e), stack:e.stack}); }
if(!await until(()=>typeof G!=='undefined'&&G&&G.dice&&G.dice.length,12000)) step('no match G');
await sleep(2500);
step('match up, screen='+(document.querySelector('.screen.active')||{}).id);

/* roll a few times through the real button */
for (let r=0;r<4;r++){
  const btn=document.getElementById('rollBtn')||document.querySelector('#btnRoll,.roll-btn');
  try{ if(btn&&vis(btn)) tap(btn); else if(typeof doRoll==='function') doRoll(); }
  catch(e){ errs.push({msg:'roll'+r+' '+String(e), stack:e.stack}); }
  await sleep(2600);
  step('roll'+r+' done');
  /* keep any scoring die selected then roll again if possible */
  try{ const d=document.querySelector('#diceArea .die-wrap:not(.kept)'); if(d) tap(d); }catch(e){}
  await sleep(500);
}
out.errors = errs;
return out;
