/* Measure why "Small bank's still a bank." wraps to two lines. SUITE: exclude */
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
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF !== undefined, 14000)) return { err: 'no match' };
await sleep(2600);

const out = {};
DLG.oppKey = DLG.oppKey || "GROG";
/* instrument _bbFitWidth */
const f = window._bbFitWidth;
window._bbFitWidth = function(el){
  el.style.width=''; el.style.whiteSpace='nowrap';
  const natural = el.scrollWidth;
  const naturalRect = el.getBoundingClientRect().width;
  el.style.whiteSpace='';
  const maxW = el.clientWidth;
  const r = f.apply(this, arguments);
  window._fitR = { natural, naturalRect, maxW, r };
  return r;
};
if (DLG.hideTimer) clearTimeout(DLG.hideTimer);
DLG.show("Small bank's still a bank.");
await sleep(400);

const textEl = document.getElementById('dlgText');
const cs = getComputedStyle(textEl);
const rects = textEl.getClientRects();
/* count rendered lines via a range over the text */
const rng = document.createRange(); rng.selectNodeContents(textEl);
const lineTops = [...rng.getClientRects()].map(r=>Math.round(r.top));
const uniqTops = [...new Set(lineTops)];
out.fit = window._fitR;
out.measured = {
  clientWidth: textEl.clientWidth,
  scrollWidth: textEl.scrollWidth,
  scrollHeight: textEl.scrollHeight,
  styleWidth: textEl.style.width,
  rectW: textEl.getBoundingClientRect().width,
  rectH: textEl.getBoundingClientRect().height,
  lineHeight: cs.lineHeight, fontSize: cs.fontSize,
  linesByHeight: textEl.getBoundingClientRect().height / parseFloat(cs.lineHeight),
  uniqLineTops: uniqTops.length,
  boxSizing: cs.boxSizing,
  textWrap: cs.textWrap || cs.textWrapMode,
  letterSpacing: cs.letterSpacing, wordSpacing: cs.wordSpacing,
  innerLen: textEl.innerHTML.length,
  text: textEl.textContent
};
/* what does it look like re-measured nowrap AFTER the width pin? */
const saveW = textEl.style.width;
textEl.style.whiteSpace='nowrap'; textEl.style.width='';
out.recheck = { naturalNow: textEl.scrollWidth, naturalRect: textEl.getBoundingClientRect().width };
textEl.style.whiteSpace=''; textEl.style.width=saveW;

/* scroll container */
const sc = document.getElementById('dlgScroll');
out.scroll = { clientWidth: sc.clientWidth, offsetWidth: sc.offsetWidth,
  maxWidth: getComputedStyle(sc).maxWidth, padding: getComputedStyle(sc).padding };
out.viewport = { w: innerWidth, h: innerHeight };
return out;
