/* WHERE DOES THE BUST LAND IN THE FRAME, in rendered pixels.
 * The alpha pass already showed the PNGs have zero transparent headroom, so
 * whatever pushes the characters down is geometry, not art. This reads the
 * live cards: the frame, the image box, and - the part that actually decides
 * it - which axis object-fit:cover binds on for each bust, because that is
 * what sets how much of the image is cropped and where. */
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
tap(document.getElementById('nrTakeBtn'));await sleep(2200);
await until(()=>[...document.querySelectorAll('.ptcard')].filter(vis).length>0,9000);
await sleep(900);

const out={cards:[]};
const cards=[...document.querySelectorAll('.ptcard')].filter(vis);
out.n=cards.length;

for(const c of cards){
  const img=c.querySelector('.lwho');
  if(!img)continue;
  const cr=c.getBoundingClientRect(), ir=img.getBoundingClientRect();
  const cs=getComputedStyle(img);
  const iw=img.naturalWidth, ih=img.naturalHeight;
  /* which axis does cover bind on? scale is the LARGER of the two ratios */
  const sx=ir.width/iw, sy=ir.height/ih, s=Math.max(sx,sy);
  const drawnW=iw*s, drawnH=ih*s;
  /* object-position 50% 0%: centred horizontally, TOP-aligned vertically */
  const overflowY=drawnH-ir.height;
  /* so where does the character's own top edge sit, as a % of the card */
  const contentTop=ir.top;                       /* alpha headroom is 0 */
  const contentBot=ir.top+drawnH;                /* may run past the box */
  out.cards.push({
    who:(c.querySelector('.cname')||{}).textContent||img.getAttribute('src').split('/').pop(),
    natural:iw+'x'+ih, ar:+(iw/ih).toFixed(3),
    boxTopPctOfCard:  +(100*(ir.top-cr.top)/cr.height).toFixed(2),
    boxHeightPctOfCard:+(100*ir.height/cr.height).toFixed(2),
    boxAr:            +(ir.width/ir.height).toFixed(3),
    coverBindsOn:     sy>sx?'height':'width',
    overflowYpx:      +overflowY.toFixed(1),
    /* the visible head top, and the visible foot, as % of the card */
    headTopPctOfCard: +(100*(contentTop-cr.top)/cr.height).toFixed(2),
    footPctOfCard:    +(100*(contentBot-cr.top)/cr.height).toFixed(2),
    objectFit:cs.objectFit, objectPosition:cs.objectPosition
  });
}

/* the frame's own window: where the banner starts covering the bust */
const f=cards[0]&&cards[0].querySelector('.lfront .lffg');
if(f){
  const fr=f.getBoundingClientRect(),cr=cards[0].getBoundingClientRect();
  out.frame={topPct:+(100*(fr.top-cr.top)/cr.height).toFixed(2),
             heightPct:+(100*fr.height/cr.height).toFixed(2)};
}
const nm=cards[0]&&cards[0].querySelector('.cname');
if(nm){const nr=nm.getBoundingClientRect(),cr=cards[0].getBoundingClientRect();
  out.nameBandTopPctOfCard=+(100*(nr.top-cr.top)/cr.height).toFixed(2);}
out.cardAr=cards[0]?+(cards[0].getBoundingClientRect().width/cards[0].getBoundingClientRect().height).toFixed(3):null;
return out;
