const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(40);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
try{delete S.pendingMatch;}catch(e){}
try{if(S.run&&S.run.night){S.run.night.seatsPlayed=S.run.night.roster.map(()=>false);S.run.night.results=S.run.night.roster.map(()=>null);}}catch(e){}
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match'};
await sleep(2500);
/* stamp when the row settles, and when the bust visual lands */
let tSettle=null,tBust=null;
const _bi=window._bustImpact;
window._bustImpact=function(){tBust=performance.now();return _bi.apply(this,arguments);};
const Q=[2,3,4,6,2,3];/* dead roll: no 1s, no 5s, no triple */
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const t0=performance.now();
tap(document.getElementById('btnRoll'));
/* poll the settle test the game itself uses */
const iv=setInterval(()=>{try{if(tSettle===null&&typeof _rowSettled==='function'&&_rowSettled('#playerDiceRow')&&(G.turnRollCount||0)>0)tSettle=performance.now();}catch(e){}},20);
await until(()=>tBust!==null,25000);
clearInterval(iv);
await sleep(300);
return {rollToSettleMs:tSettle?Math.round(tSettle-t0):null,
  settleToBustMs:(tSettle&&tBust)?Math.round(tBust-tSettle):null,
  rollToBustMs:tBust?Math.round(tBust-t0):null,
  note:'pre-P857 this was ~880ms settle->bust (260+600+20)'};
