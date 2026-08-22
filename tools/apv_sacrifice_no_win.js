const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
try{delete S.pendingMatch;}catch(e){}
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match'};
await sleep(2500);
const R={};
const roll=async q=>{const Q=q.slice();const realE=window._enchRollM;
  window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
  tap(document.getElementById('btnRoll'));
  return await until(()=>G.phase==='choosing',12000);};
/* LEG 1: sacrifice would cross the line -> banks but must NOT end it */
if(!await roll([1,5,2,3,4,6]))return {err:'no roll'};
await sleep(500);
const sc={id:'sacrifice',fam:'obsidian',kind:'active',tier:1,charges:3,state:{}};
G.pF=[sc];
G.pPts=(G.target||2800)-300;/* the 1 (100) alone will NOT cross; +800 sac would */
try{updHUD();}catch(e){}
CFX.sacrifice.use(sc,'p');
await sleep(1400);
R.sacPot=G._sacPot||0;
const one=(G.pool||[]).find(d=>!d.committed&&d.val===1);
if(one)tap(one.el);
await sleep(400);
const pts0=G.pPts,target=G.target;
tap(document.getElementById('btnBank'));
await sleep(3000);
R.leg1={ptsBefore:pts0,target,ptsAfter:G.pPts,
  credited:G.pPts>pts0,overTarget:G.pPts>=target,
  matchEnded:!!G._endMatchFired,phase:G.phase,
  sacPotAfter:G._sacPot||0};
/* LEG 2: a CLEAN total still wins (no sacrifice this turn) */
if(!R.leg1.matchEnded){
  await until(()=>G.phase==='idle'&&!G._oppTurnActive,45000);
  const iv=setInterval(()=>{try{if(G&&(G.phase==='opp'||G._oppTurnActive))G._ffMult=0.05;}catch(e){}},120);
  await sleep(800);
  if(await roll([1,1,1,2,3,4])){
    await sleep(500);
    const ones=(G.pool||[]).filter(d=>!d.committed&&d.val===1).slice(0,3);
    for(const d of ones){tap(d.el);await sleep(120);}
    await sleep(300);
    tap(document.getElementById('btnBank'));
    await until(()=>G._endMatchFired,20000);
    await sleep(1200);
  }
  clearInterval(iv);
  R.leg2={matchEnded:!!G._endMatchFired,pts:G.pPts};
}
return {R,verdict:!!(R.leg1&&R.leg1.credited&&R.leg1.overTarget&&!R.leg1.matchEnded
  &&R.leg2&&R.leg2.matchEnded)};
