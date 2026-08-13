/* WHICH CHIPS HOLD THE CANVAS HOSTAGE when a match gets no shadows?
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
  await until(() => document.querySelector('.nrdie'), 9000); await sleep(500);
  tap(document.querySelector('.nrdie')); await sleep(1200);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }
_getS(); try { G = null; } catch (e) {}
launchBossMatch();
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000);
handleRoll();
await until(() => G.pool && G.pool.length, 6000);
await sleep(2600);
const chips = D3X._liveChips(document).map(c => {
  let n = c, chain = [];
  while (n && chain.length < 5) { chain.push(n.id || n.className.split(' ')[0] || n.tagName); n = n.parentElement; }
  const r = c.getBoundingClientRect();
  return { chain: chain.join(' < '), w: +r.width.toFixed(0), h: +r.height.toFixed(0), x: +r.x.toFixed(0), y: +r.y.toFixed(0) };
});
const sc = document.getElementById('screen-match');
return {
  liveChips: chips,
  d3match: window.D3_MATCH,
  dieCount: sc.querySelectorAll('.die').length,
  d3onCount: sc.querySelectorAll('.die.d3on').length,
  withD3: [].slice.call(sc.querySelectorAll('.die.d3on')).filter(e => !!e._d3).length,
  scActive: sc.classList.contains('active'),
  d3xReady: D3X.ready, d3xFail: D3X.fail,
  matchAdopted: D3X.dice.filter(d => d.match).length,
  tbl: !!D3X._tbl,
  matchOn: D3X._matchOn,
  screen: (document.querySelector('.screen.active') || {}).id
};
