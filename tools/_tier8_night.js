window.__errs=[];
window.addEventListener('error',e=>{window.__errs.push('ERR: '+(e.message||'')+' @'+(e.lineno||''));});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
await until(()=>typeof showScreen==='function',20000);
_getS();
const res={};
for(const t of [7,8]){
  window.__errs.length=0;
  S.run.tier=t;S.run.gold=500;S.run.points=0;S.run.night=null;
  let threw=null;
  try{_ensureNight();}catch(e){threw='ensureNight: '+e.message;}
  try{showScreen('gauntlet');}catch(e){threw=(threw||'')+' showScreen: '+e.message;}
  await sleep(2200);
  const seats=(S.run.night&&S.run.night.roster)||[];
  res['tier'+t]={
    threw,
    buyInLookup:(typeof NIGHT_BUYINS!=='undefined')?NIGHT_BUYINS[t]:'?',
    tiersLen:(typeof TIERS!=='undefined')?TIERS.length:'?',
    seatCount:seats.length,
    artNames:seats.map(r=>r._art),
    seatPrices:(typeof _ptSeats!=='undefined'?_ptSeats:[]).map(s=>s&&s.price),
    seatNames:(typeof _ptSeats!=='undefined'?_ptSeats:[]).map(s=>s&&(s.art||s.name)),
    errs:window.__errs.slice(0,4),
  };
}
return res;
