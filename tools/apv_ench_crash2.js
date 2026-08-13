/* Repro v2: every other way into/around the enchant page. SUITE: exclude */
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
_getS(); S.run.gold = 2000;

/* A. shop, ench tab, QUICKSILVER (last panel, whole-die path) */
try{ showScreen('shop'); }catch(e){errs.push({msg:'A showScreen '+e, stack:e.stack});}
await sleep(500);
const host = document.getElementById('gbShop');
try{ host._setTab('ench'); }catch(e){errs.push({msg:'A setTab '+e, stack:e.stack});}
await sleep(400);
try{ _stEnchTap('quicksilver'); }catch(e){errs.push({msg:'A qsTap '+e, stack:e.stack});}
await sleep(300);
try{ const d=document.querySelector('#stEnchPickTray .stPickDie:not(.taken)'); if(d) tap(d); }catch(e){errs.push({msg:'A qsDie '+e, stack:e.stack});}
await sleep(1800);
step('A quicksilver done, pick on:'+!!(document.getElementById('stEnchPick')&&document.getElementById('stEnchPick').classList.contains('on')));

/* B. close the picker (repaints the shop while tab-ench) */
try{ _stEnchPickClose(); }catch(e){errs.push({msg:'B close '+e, stack:e.stack});}
await sleep(500);
step('B close+repaint, panels:'+document.querySelectorAll('.stEnch').length);
/* B2: the swallowed repaint - call _gbShop(false) bare to see if it throws */
try{ _gbShop(false); step('B2 _gbShop(false) ok'); }catch(e){ step('B2 _gbShop(false) THREW'); errs.push({msg:'B2 '+String(e), stack:e.stack}); }
await sleep(400);

/* C. tap another brand and buy on a second die, then a THIRD on a taken die */
try{ host._setTab&&document.getElementById('gbShop')._setTab('ench'); }catch(e){}
await sleep(300);
try{ _stEnchTap('tithe'); }catch(e){errs.push({msg:'C tap '+e, stack:e.stack});}
await sleep(300);
try{ const d=document.querySelector('#stEnchPickTray .stPickDie:not(.taken)'); if(d) tap(d); }catch(e){errs.push({msg:'C die '+e, stack:e.stack});}
await sleep(1800);
try{ _stEnchPickClose(); }catch(e){errs.push({msg:'C close '+e, stack:e.stack});}
await sleep(400);
step('C second brand');

/* D. leave to gauntlet, come back while _gbShopTab is still ench */
try{ showScreen('gauntlet'); }catch(e){errs.push({msg:'D gauntlet '+e, stack:e.stack});}
await sleep(500);
try{ showScreen('shop'); }catch(e){ step('D re-enter THREW'); errs.push({msg:'D shop '+String(e), stack:e.stack}); }
await sleep(600);
step('D re-enter shop tab='+(typeof _gbShopTab!=='undefined'?_gbShopTab:'?')+' panels:'+document.querySelectorAll('.stEnch').length);

/* E. save/reload the state path: save() then _getS fresh and repaint */
try{ save(); localStorage&&void 0; S=null; _getS(); _gbShop(true); step('E reload-ish repaint ok'); }
catch(e){ step('E THREW'); errs.push({msg:'E '+String(e), stack:e.stack}); }
await sleep(500);

/* F. the old sheet fallback path: _gbEnchantPick then _gbEnchantDie */
try{ _gbEnchantPick('ward'); step('F pick sheet open:'+!!document.querySelector('#gbSheet.on')); }
catch(e){ step('F pick THREW'); errs.push({msg:'F pick '+String(e), stack:e.stack}); }
await sleep(300);
try{ _gbEnchantDie('ward',2); step('F die ok'); }
catch(e){ step('F die THREW'); errs.push({msg:'F die '+String(e), stack:e.stack}); }
await sleep(400);
try{ _gbSheetClose(); _gbModalClose(); }catch(e){}

out.dieEnch = (S&&S.run&&S.run.dieEnch)||null;
out.errors = errs;
return out;
