/* The painted Game Over, loss state. SUITE: exclude */
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
  await until(() => document.querySelector('.nrdie'), 9000); await sleep(500);
  tap(document.querySelector('.nrdie')); await sleep(1200);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }
_getS();
S.run.tier = 99;  /* full clear: the WIN state, the surface _gbBarred still owns */ S.run.gold = 385; S.run._featsThisRun = 3;
S.run.fcards = [{id:'tamper',tier:1},{id:'powder_keg',tier:2}]; S.run.finv = [];

showScreen('gameover');
await sleep(900);
return { statsShown: [...document.querySelectorAll('#gbBarred .go-stat b')].map(e => e.textContent),
  bannerVisible: vis(document.querySelector('#gbBarred .go-banner')),
  btns: [...document.querySelectorAll('#gbBarred .go-btn span')].map(e => e.textContent),
  noGreybox: !document.querySelector('#gbBarred .gbx-box') };
