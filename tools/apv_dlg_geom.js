/* DIALOGUE BUBBLE GEOMETRY + TRANSITION FACTS, measured live.
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
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }

const out = {};
_getS();
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF, 14000)) return { err: 'no match' };
await sleep(2000);

DLG.show("The bones remember every hand that ever rolled them, friend.");
await sleep(700); /* let the show transition settle */

const match = document.getElementById('screen-match') || document.querySelector('#screen-match');
const box = document.getElementById('dlgBox');
const scroll = document.getElementById('dlgScroll');
const text = document.getElementById('dlgText');
const svg = scroll.querySelector('svg.dlg-bubble');

const mr = match.getBoundingClientRect(), sr = scroll.getBoundingClientRect(),
      tr = text.getBoundingClientRect(), vr = svg ? svg.getBoundingClientRect() : null;
const cs = getComputedStyle(scroll), ct = getComputedStyle(text), cb = getComputedStyle(box);

out.viewport = { w: innerWidth, h: innerHeight, dpr: devicePixelRatio };
out.matchRect = { w: +mr.width.toFixed(1), h: +mr.height.toFixed(1) };
out.fontSizePx = ct.fontSize;
out.cqwPx = +(mr.width/100).toFixed(2);
out.lineHeight = ct.lineHeight;
out.scrollPadding = cs.padding;
out.scrollRect = { w:+sr.width.toFixed(1), h:+sr.height.toFixed(1), top:+sr.top.toFixed(1) };
out.textRect = { w:+tr.width.toFixed(1), h:+tr.height.toFixed(1) };
out.gapTop = +(tr.top - sr.top).toFixed(1);
out.gapBottom = +(sr.bottom - tr.bottom).toFixed(1);
if (vr) {
  out.svgRect = { w:+vr.width.toFixed(1), h:+vr.height.toFixed(1) };
  out.textInSvg = { top:+(tr.top-vr.top).toFixed(1), bottom:+(vr.bottom-tr.bottom).toFixed(1) };
}
out.scrollTransition = cs.transition;
out.scrollScale = cs.scale;
out.boxTransition = cb.transition;
out.boxOpacity = cb.opacity;

/* does ANY stylesheet rule mention .hiding? */
let hidingRules = [];
for (const sh of document.styleSheets) { try {
  for (const r of sh.cssRules) if (r.selectorText && /hiding/.test(r.selectorText)) hidingRules.push(r.selectorText);
} catch(e){} }
out.hidingRules = hidingRules;

/* snapshot of the HIDE sequence: sample scale+opacity over time */
DLG.hide();
const samples = [];
for (let t = 0; t <= 600; t += 100) {
  await sleep(t === 0 ? 0 : 100);
  samples.push({ t, scale: getComputedStyle(scroll).scale, boxOp: +(+getComputedStyle(box).opacity).toFixed(2) });
}
out.hideSamples = samples;
return out;
