/* Z-ORDER + PERSPECTIVE FACTS for dice canvas vs card rows, in a live boss match. */
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

const out = {};
_getS();
famApplyPick({ id: 'powder_keg', tier: 2 });
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF && G.pF.length, 14000)) return { err: 'no match' };
await sleep(2600);

tap(document.getElementById('btnRoll'));
await sleep(2500);
const sc = document.getElementById('screen-match');
const cv = document.getElementById('d3xCanvas');
out.canvas = cv ? { parentId: cv.parentElement.id, zIndex: getComputedStyle(cv).zIndex,
  position: getComputedStyle(cv).position } : 'missing';
const ids = ['famRowO','famRowP','diceArea','oppDiceRow','playerDiceRow'];
out.rows = {};
ids.forEach(id=>{ const e=document.getElementById(id); if(!e){out.rows[id]='missing';return;}
  const s=getComputedStyle(e);
  out.rows[id]={ parent: e.parentElement.id||e.parentElement.className, position:s.position,
    zIndex:s.zIndex, transform:s.transform, rotate:s.rotate, perspective:s.perspective };
});
/* which children of #screen-match establish stacking (order + z) */
out.scChildren = [...sc.children].map(e=>{
  const s=getComputedStyle(e);
  return { id: e.id||('.'+String(e.className).split(' ')[0]), z: s.zIndex, pos: s.position };
});
/* do rival dice overlap rival cards geometrically? */
const ro=document.getElementById('famRowO').getBoundingClientRect();
const od=document.getElementById('oppDiceRow');
out.oppRowRect={fam:{t:ro.top,b:ro.bottom},opp:od?{t:od.getBoundingClientRect().top,b:od.getBoundingClientRect().bottom}:null};
out.fk3d=document.documentElement.classList.contains('fk3d');
out.d3xMount = (window.D3X&&D3X.mount)? (D3X.mount.id||'anon') : null;
out.d3x = window.D3X ? { ready: !!D3X.ready, fail: D3X.fail||null, on: !!D3X.on,
  matchOn: !!D3X._matchOn, hasThree: typeof THREE!=='undefined' } : 'no D3X';
out.dieClasses = [...document.querySelectorAll('#playerDiceRow .die')].slice(0,2).map(e=>e.className);
out.phase = G && G.phase;
return out;
