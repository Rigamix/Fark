/* Repro probe: fresh run -> shop -> ENCHANTS tab -> tap a brand -> pick a die.
 * Captures every window error with full stack. SUITE: exclude */
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
window.addEventListener('unhandledrejection', e => errs.push({msg:'unhandledrejection: '+String(e.reason), stack:e.reason&&e.reason.stack?String(e.reason.stack):null}));

const out = { steps: [] };

/* fresh run */
for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }
out.steps.push('run:'+!!(S&&S.run));

_getS(); S.run.gold = 500; /* afford everything */

/* open the shop */
try { showScreen('shop'); out.steps.push('showScreen ok'); }
catch(e){ out.steps.push('showScreen THREW'); errs.push({msg:String(e), stack:e.stack}); }
await sleep(600);
const host = document.getElementById('gbShop');
out.shopUp = vis(host);

/* flip to the enchant tab exactly as a tap on the right half of the strip does */
try {
  const strip = document.getElementById('stTabStrip');
  if (strip) { const r = strip.getBoundingClientRect();
    const o = {bubbles:true,cancelable:true,clientX:r.left+r.width*0.8,clientY:r.top+r.height/2,pointerId:7};
    strip.dispatchEvent(new PointerEvent('pointerdown',o));
    strip.dispatchEvent(new PointerEvent('pointerup',o));
    strip.dispatchEvent(new MouseEvent('click',o));
    out.steps.push('strip tapped');
  } else if (host && host._setTab) { host._setTab('ench'); out.steps.push('_setTab used'); }
} catch(e){ errs.push({msg:'tab flip: '+String(e), stack:e.stack}); }
await sleep(700);
out.enchPanels = document.querySelectorAll('.stEnch').length;
out.tabEnch = host ? host.classList.contains('tab-ench') : null;

/* tap the first enchant panel (tithe) */
try { const p = document.querySelector('.stEnch:not(.dim)');
  out.firstPanel = p ? p.textContent.trim().slice(0,30) : null;
  if (p) tap(p); out.steps.push('panel tapped');
} catch(e){ errs.push({msg:'panel tap: '+String(e), stack:e.stack}); }
await sleep(700);
const box = document.getElementById('stEnchPick');
out.pickOpen = !!(box && box.classList.contains('on'));

/* pick die 0 */
try { const d = document.querySelector('#stEnchPickTray .stPickDie:not(.taken)');
  out.dieFound = !!d;
  if (d) tap(d); out.steps.push('die tapped');
} catch(e){ errs.push({msg:'die tap: '+String(e), stack:e.stack}); }
await sleep(2200);

out.errors = errs;
return out;
