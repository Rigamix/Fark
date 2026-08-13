/* Why does the boss match not reach idle now? SUITE: exclude */
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
window.addEventListener('error', e => errs.push(String(e.message) + ' @' + e.lineno));
for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => document.querySelector('.nrdie'), 9000); await sleep(500);
  tap(document.querySelector('.nrdie')); await sleep(1200);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }
_getS(); try { G = null; } catch (e) {}
let threw = null;
try { launchBossMatch(); } catch (e) { threw = String(e && e.stack || e).slice(0, 400); }
const timeline = [];
for (let t = 0; t < 24; t++) {
  timeline.push((typeof G !== 'undefined' && G) ? G.phase : 'noG');
  if (G && G.phase === 'idle') break;
  await sleep(500);
}
return { threw, errs: errs.slice(0, 5), timeline: timeline.join(','),
  atMatch: vis(document.getElementById('screen-match')),
  runOk: !!(S && S.run) };
