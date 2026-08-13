/* P697b/698: win-screen SHELF focus + rebalanced layout, end to end.
 * geometry -> tap offer card -> zoom + scrim + #foFocusPanel with CLAIM ->
 * scrim-tap closes -> refocus -> CLAIM -> pick lands -> deck tap reads.
 * SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
/* HEADLESS TRUTH SERUM: on a static surface this browser produces no frames
 * on demand, so a CSS transition never resolves its start time and pins the
 * computed value at its FROM state (outranking even !important). Kill the
 * focus fades so computed values show the cascade; the fades themselves are
 * the shelf pattern, device-proven. Measured: same rules, transition:none ->
 * opacity 1; with transition -> 0 forever, playState running, currentTime 0. */
const _ts=document.createElement('style');
_ts.textContent='#foFocusScrim,#foFocusPanel,#end-ov .fo-card,#end-ov .fo-slot{transition:none !important}';
document.head.appendChild(_ts);
tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(2200);
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
try{dbgWin();}catch(e){}
await until(()=>vis(document.getElementById('end-ov')),9000);
await sleep(3000);
const box=sel=>{const e=document.querySelector(sel);if(!e)return null;const r=e.getBoundingClientRect();
 return {t:+(100*r.top/innerHeight).toFixed(1),b:+(100*r.bottom/innerHeight).toFixed(1)};};
const out={geo:{title:box('#end-ov .fo-title'),offer:box('#end-ov .fo-offer'),
 slot0:box('#end-ov .fo-slot'),deck:box('#end-ov .fo-deck'),skip:box('#end-ov>.fo-skip'),
 panel:box('#end-ov .win-panel')}};
out.clearance=+(out.geo.skip.t-Math.max(out.geo.deck.b,out.geo.slot0.b)).toFixed(1);

/* tap the middle offer card -> the SHELF focus */
tap(document.querySelectorAll('#end-ov .fo-offer .fcv')[1]);await sleep(1100);
const ov=document.getElementById('end-ov');
const pan=document.getElementById('foFocusPanel');
out.focus={cls:ov.classList.contains('fo-focus'),
 zoomed:!!document.querySelector('#end-ov .fo-card.zoom'),
 scrimVisible:vis(document.getElementById('foFocusScrim')),
 panelVisible:vis(pan),
 fname:!!(pan&&pan.querySelector('.fname')),
 fdesc:!!(pan&&pan.querySelector('.fdesc')),
 claimBtn:vis(document.getElementById('foClaimBtn')),
 closeBtn:vis(document.getElementById('foFBack')),
 othersHidden:[...document.querySelectorAll('#end-ov .fo-card:not(.zoom)')].every(e=>+getComputedStyle(e).opacity<0.05),
 skipHidden:+getComputedStyle(document.querySelector('#end-ov>.fo-skip')).opacity<0.05,
 sheetOpen:(()=>{const sh=document.getElementById('gbSheet');return !!(sh&&sh.classList.contains('on'));})()};

/* scrim tap closes */
tap(document.getElementById('foFocusScrim'));await sleep(800);
out.scrimCloses=!ov.classList.contains('fo-focus')&&!document.querySelector('#end-ov .fo-card.zoom');

/* refocus + CLAIM */
out.deckBefore=(typeof S!=='undefined'&&S.run&&S.run.fcards)?S.run.fcards.length:-1;
tap(document.querySelectorAll('#end-ov .fo-offer .fcv')[1]);await sleep(900);
out.claimTapped=tap(document.getElementById('foClaimBtn'));
await sleep(1400);
out.afterClaim={focusGone:!ov.classList.contains('fo-focus'),
 deckAfter:(S.run&&S.run.fcards)?S.run.fcards.length:-1,
 taken:!!document.querySelector('#end-ov .fo-wrap.taken'),
 filledSlots:document.querySelectorAll('#end-ov .fo-slot.filled').length};

/* deck tap -> read-only shelf focus */
tap(document.querySelector('#end-ov .fo-slot.filled .fcv'));await sleep(900);
out.deckFocus={cls:ov.classList.contains('fo-focus'),
 slotZoomed:!!document.querySelector('#end-ov .fo-slot.zoom'),
 noClaim:!document.getElementById('foClaimBtn'),
 panelVisible:vis(document.getElementById('foFocusPanel'))};
tap(document.getElementById('foFBack'));await sleep(700);
out.closeBtnCloses=!ov.classList.contains('fo-focus');

out.verdict=out.focus.cls&&out.focus.zoomed&&out.focus.scrimVisible&&out.focus.panelVisible
 &&out.focus.claimBtn&&out.focus.othersHidden&&out.focus.skipHidden&&!out.focus.sheetOpen
 &&out.scrimCloses&&out.claimTapped&&out.afterClaim.deckAfter===out.deckBefore+1
 &&out.afterClaim.taken&&out.deckFocus.slotZoomed&&out.deckFocus.noClaim
 &&out.closeBtnCloses&&out.clearance>0.5;
return out;
