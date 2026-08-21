/* P847: (1) GE's ENTRY disarms a pending arm (steady flag + rings die
 * at activation, not at the roll); (2) the GE reroll fires the roll
 * seam with the main path's payload shape; (3) the refund path still
 * voids/disarms NOTHING. */
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
const rollEvents=[];
const _ff=window.famFire;
window.famFire=function(seam,ev){if(seam==='roll')rollEvents.push(JSON.parse(JSON.stringify(ev||{})));return _ff.apply(this,arguments);};
const Q=[1,1,5,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(2200);
let rolled=false;
for(let r=0;r<3&&!rolled;r++){tap(document.getElementById('btnRoll'));rolled=await until(()=>G.phase==='choosing',6000);}
if(!rolled)return {err:'no roll'};
await sleep(450);
/* arm steady hand: rings + flag */
const st={id:'steady_hand',fam:'iron',kind:'active',tier:2,charges:3,state:{}};
G.pF=[st];CFX.steady_hand.use(st,'p');await sleep(250);
const armedBefore={flag:!!G._steadyArmed,
  rings:document.querySelectorAll('#playerDiceRow .break-target').length};
/* enter GE mode through the gate */
G.activeCardState=G.activeCardState||{usedCards:{}};
G.activeCardState.usedCards['gamblers_eye']=1;G.oCards=[];
activateCard('gamblers_eye');await sleep(400);
const atEntry={flag:!!G._steadyArmed,
  rings:document.querySelectorAll('#playerDiceRow .break-target').length,
  mode:G.phase==='gamblers_eye'};
/* hold the two 1s, roll: the seam must fire with rollNum=count+1 */
const ones=(G.pool||[]).filter(d=>!d.committed&&d.val===1).slice(0,2);
ones.forEach(d=>tap(d.el));await sleep(300);
const rcBefore=G.turnRollCount||0;
const evBefore=rollEvents.length;
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing',10000);await sleep(500);
const geRoll=rollEvents.slice(evBefore);
/* refund path: fresh mode attempt with 1 free die must void nothing */
/* (all but one die committed is hard to stage; assert on a fresh match
   turn instead: activate with <=1 free) - skipped here; the sweep's
   flask REFUND leg carries the refund contract. */
return {armedBefore,atEntry,rcBefore,rcAfter:G.turnRollCount,
  geRollEvents:geRoll,
  verdicts:{
    entryDisarms:armedBefore.flag&&armedBefore.rings>0&&!atEntry.flag&&atEntry.rings===0,
    modeEntered:atEntry.mode,
    seamFired:geRoll.length===1&&geRoll[0].actor==='p'&&geRoll[0].rollNum===rcBefore+1},
  verdict:armedBefore.flag&&!atEntry.flag&&atEntry.rings===0&&atEntry.mode
    &&geRoll.length===1&&geRoll[0].rollNum===rcBefore+1};
