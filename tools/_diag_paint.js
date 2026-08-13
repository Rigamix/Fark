/* WHY DO THE TIP AND THE SCALE COMPUTE BUT NOT PAINT?
 * SUITE: exclude
 * Reads PIXELS, not styles: after each forced state, the page draws itself
 * into a canvas via CanvasRenderingContext2D.drawWindow? Not available -
 * so instead: getImageData is impossible for DOM. PLAN B: compare the
 * bounding boxes the compositor reports (getBoundingClientRect DOES include
 * standalone scale if it is applied for real). A card computed scale:1.3
 * whose rect equals its unscaled size is NOT being scaled in layout/paint -
 * that one measurement separates "compositor ignored it" from "capture bug".
 */
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
_getS();
famApplyPick({ id: 'powder_keg', tier: 2 });
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF && G.pF.length, 14000)) return { err: 'no match' };
await sleep(2600);

/* keep the compositor fed: one tiny perpetual animation via rAF */
const beat=document.createElement('div');
beat.style.cssText='position:fixed;left:0;top:0;width:2px;height:2px;background:rgba(255,255,255,.02);z-index:99999';
document.body.appendChild(beat);
(function pump(){beat.style.opacity=(Math.sin(performance.now()/200)+1)/2*0.04+0.01;requestAnimationFrame(pump);})();
DLG.oppKey = DLG.oppKey || 'GROG';
DLG.show("Heard something odd today. Someone important, coming through. Nobody's said a name yet.");
await sleep(300);
const card = document.querySelector('#famRowP .fcv');
const before = card.getBoundingClientRect().width;

/* record every close with a stack, and stamp state into a corner badge the
   screenshot can read */
window._closeLog = [];
const _cfc = window._cardFocusClose;
window._cardFocusClose = function () {
  window._closeLog.push({ t: Math.round(performance.now()),
    stack: String(new Error().stack).split(String.fromCharCode(10)).slice(2, 5).join(' | ') });
  return _cfc.apply(this, arguments);
};
/* catch the tip's killer: every removal primitive, logged when it touches it */
window._tipKill = [];
const NL = String.fromCharCode(10);
const _rm = Element.prototype.remove;
Element.prototype.remove = function () {
  if (this.id === 'cardFocusTip')
    window._tipKill.push({ via: 'remove', t: Math.round(performance.now()),
      stack: String(new Error().stack).split(NL).slice(2, 6).join(' | ') });
  return _rm.apply(this, arguments);
};
const _rc = Node.prototype.removeChild;
Node.prototype.removeChild = function (ch) {
  if (ch && ch.id === 'cardFocusTip')
    window._tipKill.push({ via: 'removeChild', t: Math.round(performance.now()),
      stack: String(new Error().stack).split(NL).slice(2, 6).join(' | ') });
  return _rc.apply(this, arguments);
};
new MutationObserver(muts => muts.forEach(m => m.removedNodes && [...m.removedNodes].forEach(n => {
  if (n.id === 'cardFocusTip')
    window._tipKill.push({ via: 'observed@' + (m.target.id || m.target.className), t: Math.round(performance.now()) });
}))).observe(document.getElementById('screen-match'), { childList: true, subtree: false });
const badge = document.createElement('div');
badge.style.cssText = 'position:fixed;left:0;top:0;width:26px;height:26px;z-index:99999;pointer-events:none';
document.body.appendChild(badge);
(function paintBadge(){
  badge.style.background = document.getElementById('cardFocusTip') ? '#00ff00' : '#ff0000';
  requestAnimationFrame(paintBadge);
})();
famCardTap(0);
await sleep(500);
const after = card.getBoundingClientRect().width;

const tip = document.getElementById('cardFocusTip');
const w0 = tip ? tip.querySelector('span.w') : null;
const out = {
  cardW_before: +before.toFixed(1),
  cardW_focused: +after.toFixed(1),
  scaleAppliedInLayout: after > before * 1.2,
  computedScale: getComputedStyle(card).scale,
  tip: !!tip
};
if (w0) {
  const r1 = w0.getBoundingClientRect();
  out.word = { w: +r1.width.toFixed(1), h: +r1.height.toFixed(1),
               opacity: getComputedStyle(w0).opacity };
}
/* how many of everything exist, and WHERE is the element I measured? */
out.famRowPCount = document.querySelectorAll('[id="famRowP"]').length;
out.screenMatchCount = document.querySelectorAll('[id="screen-match"]').length;
out.fcvInRowP = document.querySelectorAll('#famRowP .fcv').length;
out.allPKCards = [...document.querySelectorAll('.fcv[data-cid="powder_keg"]')].map(e => {
  const r = e.getBoundingClientRect();
  return { inRowP: !!e.closest('[id="famRowP"]'), x: +r.x.toFixed(0), y: +r.y.toFixed(0),
           w: +r.width.toFixed(0), focused: e.classList.contains('focus') };
});
/* everything whose box contains the painted card's centre, by geometry */
const px = 215, py = 690;
out.atPoint = [...document.querySelectorAll('*')].filter(e => {
  const r = e.getBoundingClientRect();
  return r.width > 8 && r.width < 300 && r.left <= px && px <= r.right && r.top <= py && py <= r.bottom;
}).slice(0, 20).map(e => {
  const r = e.getBoundingClientRect(), c = getComputedStyle(e);
  return (e.tagName + ' ' + (e.id || e.className && String(e.className).slice(0, 30) || '') +
    ' cid=' + (e.dataset ? e.dataset.cid : '') + ' w=' + r.width.toFixed(0) +
    ' z=' + c.zIndex + ' pos=' + c.position);
});
out.frozenIframe = document.querySelectorAll('iframe,canvas').length;
out.canvases = [...document.querySelectorAll('canvas')].map(cv => {
  const r = cv.getBoundingClientRect();
  return { id: cv.id, w: +r.width.toFixed(0), h: +r.height.toFixed(0), x: +r.x.toFixed(0), y: +r.y.toFixed(0) };
}).filter(c => c.w > 50);
await sleep(2600);
out.closeLog = window._closeLog; out.tipKill = window._tipKill;
return out;
