/* WHICH gate stops _drawDiceShadows before the first paint? SUITE: exclude */
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
window._fkDiscardOk = true;
launchBossMatch();
let ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000);
if (!ok) { try { G = null; } catch (e) {} launchBossMatch();
  ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000); }
if (!ok) return { err: 'no idle' };
handleRoll();
await until(() => G.pool && G.pool.length >= 3, 9000);
await sleep(2800);

const out = {};
out.cv = !!document.getElementById('dsCanvas');
out.ml = window._mLight ? { on: window._mLight.on } : null;
out.tblImg = (typeof _tblImg !== 'undefined' && _tblImg) ?
  { complete: _tblImg.complete, nw: _tblImg.naturalWidth,
    src: (_tblImg.src || '').split('/').slice(-2).join('/').slice(0, 80) } : 'undefined';
out.d3x = window.D3X ? { on: D3X.on, tbl: !!D3X._tbl, dice: D3X.dice.length,
  settleK: (function () { try { return D3X._settleK(); } catch (e) { return 'ERR ' + e; } })(),
  mount: !!D3X.mount } : null;
if (window.D3X && D3X.dice.length) {
  out.perDie = D3X.dice.slice(0, 6).map(dd => ({
    match: !!dd.match, visible: !!(dd.obj && dd.obj.visible),
    parent: !!(dd.obj && dd.obj.parent),
    row: (function () { try { return D3X._rowKey(dd); } catch (e) { return 'ERR'; } })() }));
}
return out;
