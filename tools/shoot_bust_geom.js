/* For each card on screen: the card box, the bust's box, its natural size, and
 * how much of the bust is being cut off on each side by object-fit:cover. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(2500);
_getS();
const WANT=['Nix','Dunstan','Osgood','Twill'];
(S.run.night.roster||[]).forEach((p,i)=>{if(WANT[i])p._art=WANT[i];});
save();showScreen('gauntlet');await sleep(1800);
const out=[];
document.querySelectorAll('.ptcard').forEach(card=>{
  const im=card.querySelector('.lwho'); if(!im) return;
  const c=card.getBoundingClientRect(), b=im.getBoundingClientRect();
  const nw=im.naturalWidth, nh=im.naturalHeight;
  if(!nw) return;
  /* cover: scale = max(boxW/nw, boxH/nh) */
  const sc=Math.max(b.width/nw, b.height/nh);
  const drawnW=nw*sc, drawnH=nh*sc;
  out.push({
    art:(im.getAttribute('src')||'').split('/').pop().replace('_opt.webp',''),
    natural:[nw,nh],
    boxPctOfCard:{top:+(100*(b.top-c.top)/c.height).toFixed(1),
                  height:+(100*b.height/c.height).toFixed(1)},
    cutOffTopPx:+Math.max(0,(drawnH-b.height)*0).toFixed(1),      /* pos 0% => no top cut */
    cutOffBottomPx:+Math.max(0,drawnH-b.height).toFixed(1),
    cutOffSidesPx:+Math.max(0,drawnW-b.width).toFixed(1),
    boxPx:[+b.width.toFixed(0),+b.height.toFixed(0)],
    drawnPx:[+drawnW.toFixed(0),+drawnH.toFixed(0)]
  });
});
return {cardPx:(()=>{const c=document.querySelector('.ptcard').getBoundingClientRect();
  return [+c.width.toFixed(0),+c.height.toFixed(0)];})(), busts:out};
