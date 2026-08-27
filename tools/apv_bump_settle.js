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
/* give the rival grogs_bump and get past its turn gate */
G.oCards=['grogs_bump'];
G.npcCardState=G.npcCardState||{usedOnce:{}};
G.npcCardState.usedOnce={};
G.turnNum=3;
let tSettle=null,tSwap=null;
const _tc=window.triggerCard;
window.triggerCard=function(cid,txt){if(cid==='grogs_bump'&&tSwap===null)tSwap=performance.now();return _tc.apply(this,arguments);};
const Q=[1,1,5,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const t0=performance.now();
tap(document.getElementById('btnRoll'));
const iv=setInterval(()=>{try{if(tSettle===null&&_rowSettled('#playerDiceRow')&&(G.turnRollCount||0)>0)tSettle=performance.now();}catch(e){}},20);
await until(()=>tSwap!==null,25000);
clearInterval(iv);
await sleep(400);
return {rollToSettleMs:tSettle?Math.round(tSettle-t0):null,
  rollToSwapMs:tSwap?Math.round(tSwap-t0):null,
  settleToSwapMs:(tSettle&&tSwap)?Math.round(tSwap-tSettle):null,
  swapAfterSettle:!!(tSettle&&tSwap&&tSwap>=tSettle),
  verdict:!!(tSettle&&tSwap&&tSwap>=tSettle)};
