/* Is the tell badge VISIBLE, or merely present? Run for Mabel (the new rule)
   and Brutus (drill_order, untouched) so a null result can be attributed. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof launchBossMatch==='function',20000))return {err:'no boot'};
_getS();window._fkDiscardOk=true;
const look=async(tier,label)=>{
  S.run.tier=tier;S.run.gold=500;S.run.sleeve=null;
  try{delete S.pendingMatch;}catch(e){}
  try{showScreen('gauntlet');}catch(e){}
  launchBossMatch();
  await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
  await sleep(2600);
  const b=document.getElementById('tellBadge');
  if(!b)return {label,tell:G&&G._tell&&G._tell.id,badge:'NO ELEMENT'};
  /* POLL, do not sample. A single reading of a fading-in element measures the
     clock, not the badge - both rules came back 0 on some runs and 1 on
     others, which is a race in the instrument, not a difference between them.
     "Does it ever become visible" is the claim; this waits for the answer. */
  const t0=Date.now();let peak=0;
  while(Date.now()-t0<6000){peak=Math.max(peak,parseFloat(getComputedStyle(b).opacity)||0);
    if(peak>=1)break;await sleep(150);}
  const r=b.getBoundingClientRect(),cs=getComputedStyle(b);
  return {label,tell:G._tell&&G._tell.id,
    parent:b.parentElement&&(b.parentElement.id||b.parentElement.className),
    rect:{x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)},
    display:cs.display,visibility:cs.visibility,opacity:cs.opacity,peakOpacity:peak,zIndex:cs.zIndex,
    inViewport:r.width>0&&r.height>0&&r.bottom>0&&r.top<innerHeight,
    text:(b.textContent||'').replace(/\s+/g,' ').trim().slice(0,60)};
};
/* ORDER REVERSED. The first reading was Mabel-then-Brutus and only Mabel came
   back opacity:0 - which is equally consistent with "the new rule's badge does
   not fade in" and with "the FIRST match after boot has not finished its
   entrance by 2600ms". Swapping the order separates them: if the opacity:0
   follows the SLOT rather than the RULE, it is the clock, not the badge. */
const brutus=await look(4,'BRUTUS/drill_order');
const mabel=await look(1,'MABEL/mending');
return {mabel,brutus,
  sameShape:(mabel.inViewport===brutus.inViewport)};
