/* CURSED TABLE (loss side) + HAIR OF THE DOG (the arm). Own both,
 * seal the seat, lose: TWO circles rub out (unsealed or unowned would
 * be one) and _hotdNext arms for the next match. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
S.run.fcards=[{id:'marked_table',tier:1,charges:0},{id:'hair_of_the_dog',tier:1,charges:0}];
S.run.points=5;S.run._hotdNext=false;
try{save();}catch(e){}
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
G._sealRule='last_call';/* the cursed seat's symmetric rule */
const Q=[];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
G.oPts=(G.target||2800)-100;try{updHUD();}catch(e){}
const pts0=S.run.points;
for(let cycle=0;cycle<6&&!G._endMatchFired;cycle++){
  [1,2,3,4,6,2].forEach(v=>Q.push(v));
  tap(document.getElementById('btnRoll'));
  if(!await until(()=>G.phase==='choosing'||G._endMatchFired,15000))break;
  if(G._endMatchFired)break;
  await sleep(500);
  const one=G.pool.find(d=>!d.committed&&d.val===1);
  if(one){tap(one.el);await sleep(300);}
  tap(document.getElementById('btnBank'));
  if(!await until(()=>G._endMatchFired||(G.phase==='idle'&&Q.length===0),90000))break;
  await sleep(1500);
}
if(!G._endMatchFired)return {err:'match never ended',oPts:G.oPts};
await sleep(2500);
const circlesGone=pts0-(S.run.points||0);
const hotdArmed=!!S.run._hotdNext;
const route=G&&G._endRoute?{win:G._endRoute.win,isHandicap:G._endRoute.isHandicap}:null;
return {circlesGone,hotdArmed,route,pts0,ptsNow:S.run.points,
  verdicts:{
    rivalWon:!!(route&&route.win===false),
    sealedLossRubsTwo:circlesGone===2,
    hotdArmedOnLoss:hotdArmed},
  verdict:!!(route&&route.win===false)&&circlesGone===2&&hotdArmed};
