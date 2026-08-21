/* P847/P848: Gambler's Eye through the MAIN roll path.
 * Leg 1 (P847): the ENTRY disarms a pending arm atomically; the GE
 *   roll fires the roll seam with the main path's payload.
 * Leg 2 (P848 headline): a GE reroll into a DEAD table fires the
 *   deadRoll seam and fool's gold rescues - before the fall-through,
 *   the branch called _delayedDoBust directly and the player busted
 *   holding a live rescue charge.
 * Leg 3 (P848): the visibly-differs rule survives the fall-through -
 *   every rerolled lane differs from the face it replaced. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
const seamEvents=[];
const _ff=window.famFire;
window.famFire=function(seam,ev){if(seam==='roll'||seam==='deadRoll')seamEvents.push({seam,ev:JSON.parse(JSON.stringify(ev||{}))});return _ff.apply(this,arguments);};
const Q=[];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const QX=[];
const realRFE=window.rollFaceExclude;
window.rollFaceExclude=(m,x,d)=>QX.length?QX.shift():realRFE(m,x,d);
const freshTurn=async q=>{
  let ok=false;
  for(let a=0;a<5&&!ok;a++){
    if(a>0){try{showScreen('gauntlet');}catch(e){}await sleep(700);}
    try{delete S.pendingMatch;}catch(e){}
    try{if(S.run&&S.run.night){S.run.night.seatsPlayed[0]=false;S.run.night.results[0]=null;}}catch(e){}
    window._fkDiscardOk=true;
    try{launchSeat(0);}catch(e){}
    ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle'
      &&(G.pool||[]).length===0&&(G.pTurns||0)===0,9000);
    if(!ok)await sleep(1200);
  }
  if(!ok)return false;
  await sleep(2000);
  Q.length=0;q.forEach(v=>Q.push(v));
  let rolled=false;
  for(let r=0;r<3&&!rolled;r++){
    tap(document.getElementById('btnRoll'));
    rolled=await until(()=>G.phase==='choosing',6000);
  }
  if(!rolled)return false;
  await sleep(450);return true;};
const R={};

/* ── Leg 1: entry disarm + the roll seam through the main path ── */
if(!await freshTurn([1,1,5,2,3,4]))return {err:'no turn 1'};
const st={id:'steady_hand',fam:'iron',kind:'active',tier:2,charges:3,state:{}};
G.pF=[st];CFX.steady_hand.use(st,'p');await sleep(250);
const armedBefore={flag:!!G._steadyArmed,
  rings:document.querySelectorAll('#playerDiceRow .break-target').length};
G.activeCardState=G.activeCardState||{usedCards:{}};
G.activeCardState.usedCards['gamblers_eye']=1;G.oCards=[];
activateCard('gamblers_eye');await sleep(400);
const atEntry={flag:!!G._steadyArmed,
  rings:document.querySelectorAll('#playerDiceRow .break-target').length,
  mode:G.phase==='gamblers_eye'};
const ones=(G.pool||[]).filter(d=>!d.committed&&d.val===1).slice(0,2);
ones.forEach(d=>tap(d.el));await sleep(300);
const heldLanes=ones.map(d=>d.lane);
const oldVals={};(G.pool||[]).forEach(d=>{if(!d.committed&&!heldLanes.includes(d.lane))oldVals[d.lane]=d.val;});
const rcBefore=G.turnRollCount||0;
const evBefore=seamEvents.length;
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing',15000);await sleep(600);
const geRollEvents=seamEvents.slice(evBefore).filter(e=>e.seam==='roll');
/* leg 3 data: every rerolled lane differs from its old face */
let differs=true,rerolled=0;
(G.pool||[]).forEach(d=>{if(oldVals[d.lane]!==undefined){rerolled++;if(d.val===oldVals[d.lane])differs=false;}});
const frozenSurvived=(G.pool||[]).filter(d=>d._frozen).length;
R.leg1={armedBefore,atEntry,rcBefore,rcAfter:G.turnRollCount,geRollEvents,
  rerolled,differs,frozenSurvived};

/* ── Leg 2: GE reroll into a DEAD table -> deadRoll seam -> rescue ── */
if(!await freshTurn([1,1,5,2,3,4]))return {err:'no turn 2',R};
const fg={id:'fools_gold_f',fam:'fools_gold',kind:'active',tier:2,charges:2,state:{}};
G.pF=[fg];
G.activeCardState.usedCards['gamblers_eye']=1;G.oCards=[];
activateCard('gamblers_eye');await sleep(350);
/* hold the 2 and 3 (non-scorers); force the other four dead: with the
   held 2+3 the table is {2,3}+{2,3,4,6}: no 1/5, no triple */
const two=(G.pool||[]).find(d=>!d.committed&&d.val===2);
const three=(G.pool||[]).find(d=>!d.committed&&d.val===3);
tap(two.el);await sleep(150);tap(three.el);await sleep(300);
QX.length=0;[2,3,4,6].forEach(v=>QX.push(v));
/* fool's gold's rescue reroll goes through _rollD -> the queue: feed scorers */
Q.length=0;[1,1,1,5,5,5].forEach(v=>Q.push(v));
const chargesBefore=fg.charges;
const evBefore2=seamEvents.length;
tap(document.getElementById('btnRoll'));
/* the dead check fires at settle; fool's gold rescues into choosing */
const rescued=await until(()=>fg.charges<chargesBefore&&G.phase==='choosing',20000);
await sleep(500);
const deadEvents=seamEvents.slice(evBefore2).filter(e=>e.seam==='deadRoll');
R.leg2={rescued,chargesBefore,chargesAfter:fg.charges,
  deadRollFired:deadEvents.length>0,
  turnAlive:G.phase==='choosing'&&!G._endMatchFired};

return {R,verdicts:{
  entryDisarms:R.leg1.armedBefore.flag&&R.leg1.armedBefore.rings>0&&!R.leg1.atEntry.flag&&R.leg1.atEntry.rings===0,
  modeEntered:R.leg1.atEntry.mode,
  seamFired:R.leg1.geRollEvents.length===1&&R.leg1.geRollEvents[0].ev.actor==='p'&&R.leg1.geRollEvents[0].ev.rollNum===R.leg1.rcBefore+1,
  holdsSurvive:R.leg1.frozenSurvived===2,
  visiblyDiffers:R.leg1.rerolled>=3&&R.leg1.differs,
  deadRollReachesFoolsGold:R.leg2.deadRollFired&&R.leg2.rescued&&R.leg2.turnAlive},
  verdict:R.leg1.armedBefore.flag&&!R.leg1.atEntry.flag&&R.leg1.atEntry.rings===0&&R.leg1.atEntry.mode
    &&R.leg1.geRollEvents.length===1&&R.leg1.geRollEvents[0].ev.rollNum===R.leg1.rcBefore+1
    &&R.leg1.frozenSurvived===2&&R.leg1.differs
    &&R.leg2.deadRollFired&&R.leg2.rescued&&R.leg2.turnAlive};
