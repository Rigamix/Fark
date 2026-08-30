const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
await until(()=>typeof showScreen==='function',20000);
_getS();
S.run.tier=3;S.run.gold=500;S.run.points=0;S.run.night=null;
try{_ensureNight();}catch(e){}
showScreen('gauntlet');
await sleep(2500);
const out={seatNames:(typeof _ptSeats!=='undefined'?_ptSeats:[]).map(s=>({name:s.name,word:s.word,trait:s.trait,persona:s.pat&&s.pat.persona}))};
/* the seat tiles as rendered */
out.tileText=[...document.querySelectorAll('#ptRoom *')].map(e=>e.childElementCount?null:(e.textContent||'').trim())
  .filter(t=>t&&t.length>1).slice(0,40);
/* open a seat peek */
const seat=document.querySelector('#ptRoom [onclick*="_ptSeat"],#ptRoom [class*="seat"]');
if(seat){const r=seat.getBoundingClientRect();const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  seat.dispatchEvent(new PointerEvent('pointerdown',o));seat.dispatchEvent(new PointerEvent('pointerup',o));seat.dispatchEvent(new MouseEvent('click',o));}
await sleep(1500);
out.afterTap=(document.body.innerText||'').replace(/\s+/g,' ').trim().slice(0,400);
return out;
