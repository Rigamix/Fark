/* FOR KEEPS, the LOSS half: seed an amber, arm the chip, rival preset
 * one bank from target; keep yielding minimal player turns until the
 * rival crosses. Gate on G._endMatchFired (the earlier end-ov text
 * gate passed on a pre-populated hidden element). Their pick must
 * take the amber; a bone backfills to six. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
S.run._fkArmed=true;
S.run.dice=['amber','bone','bone','bone','bone','bone'];
try{save();}catch(e){}
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
if(!G._forKeeps)return {err:'not armed'};
const Q=[];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
G.oPts=(G.target||2800)-100;try{updHUD();}catch(e){}
for(let cycle=0;cycle<6&&!G._endMatchFired;cycle++){
  [1,2,3,4,6,2].forEach(v=>Q.push(v));
  tap(document.getElementById('btnRoll'));
  if(!await until(()=>G.phase==='choosing'||G._endMatchFired,15000))break;
  if(G._endMatchFired)break;
  await sleep(500);
  const one=G.pool.find(d=>!d.committed&&d.val===1);
  if(one){tap(one.el);await sleep(300);}
  tap(document.getElementById('btnBank'));
  /* rival turn runs; either the match ends or we come back to idle */
  if(!await until(()=>G._endMatchFired||(G.phase==='idle'&&Q.length===0),90000))break;
  await sleep(1500);
}
if(!G._endMatchFired)return {err:'match never ended',oPts:G.oPts,pPts:G.pPts};
await sleep(2500);
const diceNow=(S.run.dice||[]).slice();
const amberGone=diceNow.indexOf('amber')<0;
const stillSix=diceNow.length===6;
const allBone=diceNow.every(m=>m==='bone');
const route=G&&G._endRoute?{win:G._endRoute.win,isBoss:G._endRoute.isBoss,isHandicap:G._endRoute.isHandicap,fk:G._endRoute._forKeeps,fkLost:G._endRoute._fkLost}:null;
return {diceNow:diceNow,amberGone:amberGone,stillSix:stillSix,route:route,
  verdicts:{
    rivalWon:!!(route&&route.win===false),
    bestDieTaken:amberGone,
    boneBackfilled:stillSix&&allBone},
  verdict:!!(route&&route.win===false)&&amberGone&&stillSix&&allBone};
