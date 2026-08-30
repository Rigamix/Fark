const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
await until(()=>typeof showScreen==='function',20000);
_getS();
S.run.tier=3;S.run.gold=500;S.run.points=0;S.run.night=null;S.run._artPersona={};
try{_ensureNight();}catch(e){}
showScreen('gauntlet');
await sleep(2000);
/* pick the seat with the LONGEST surname so the fit is tested at its worst */
let best=null,bestLen=-1;
for(const st of (_ptSeats||[])){
  _ptOpenPanel(st);await sleep(50);
  const t=(document.getElementById('ptvName').textContent||'').trim();
  if(t.length>bestLen){bestLen=t.length;best=st;}
}
_ptOpenPanel(best);
await sleep(1400);
const el=document.getElementById('ptvName');
const r=el.getBoundingClientRect();
return {shown:(el.textContent||'').trim(),persona:best.pat&&best.pat.persona,word:best.word,
  nameBox:{x:Math.round(r.x),w:Math.round(r.width)},viewport:innerWidth,
  overflows:r.right>innerWidth+1||r.left<-1};
