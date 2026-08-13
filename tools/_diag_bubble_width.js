/* WHERE DOES THE BUBBLE'S WIDTH GO? The example line still sets 3 lines after
 * the Raritas swap; every box in the chain gets measured before any number
 * moves. SUITE: exclude */
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
_getS(); try { G = null; } catch (e) {}
launchBossMatch();
await until(() => typeof G !== 'undefined' && G, 12000); await sleep(2200);

/* instrument the fitter: what does IT see on a fresh show? */
window._fitLog = [];
const _fit = window._bbFitWidth;
window._bbFitWidth = function (el) {
  const maxW = el.clientWidth;
  const lh2 = parseFloat(getComputedStyle(el).lineHeight);
  const minH = (() => { const h = el.scrollHeight; return h; })();
  const r = _fit.apply(this, arguments);
  window._fitLog.push({ maxW, linesAtMaxW: Math.round(minH / lh2), returned: Math.round(r) });
  return r;
};
DLG.oppKey = DLG.oppKey || 'GROG';
DLG.show("Heard something odd today. Someone important, coming through. Nobody's said a name yet.");
await sleep(500);

const box = document.getElementById('dlgBox'), inner = box.querySelector('.dlg-inner'),
      scroll = document.getElementById('dlgScroll'), dt = document.getElementById('dlgText');
const g = el => { if (!el) return null; const c = getComputedStyle(el), r = el.getBoundingClientRect();
  return { w: +r.width.toFixed(1), maxW: c.maxWidth, pad: c.padding, marg: c.margin, flex: c.flex }; };

/* what would the text need for two lines? dt is a FLEX ITEM - width alone is
   overridden by shrink, so flex:none for the experiment */
const lh = parseFloat(getComputedStyle(dt).lineHeight);
dt.style.flex = 'none'; scroll.style.maxWidth = 'none'; scroll.style.width = 'auto';
dt.style.width = '';
const naturalLines = Math.round(dt.scrollHeight / lh);
let need2 = null;
for (let w = 200; w <= 500; w += 5) {
  dt.style.width = w + 'px';
  if (Math.round(dt.scrollHeight / lh) <= 2) { need2 = w; break; }
}
dt.style.width = ''; dt.style.flex = ''; scroll.style.maxWidth = ''; scroll.style.width = '';
try { dlgBubblePaint(scroll, dt, 1); } catch (e) {}

return {
  fitLog: window._fitLog,
  screen: document.getElementById('screen-match').getBoundingClientRect().width,
  box: g(box), inner: g(inner), scroll: g(scroll), text: g(dt),
  textClientW: dt.clientWidth,
  naturalLinesAtFullWidth: naturalLines,
  pxNeededForTwoLines: need2,
  portraitVisible: vis(box.querySelector('.dlg-portrait'))
};
