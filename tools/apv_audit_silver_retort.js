/* RETORT, both promised triggers. Text: "When you bust OR are hit by
 * an opponent card, they lose 400."
 * Leg A (bust): preset oPts 1000, bust on purpose -> oPts must drop
 * to 600 through the bust seam.
 * Leg B (hit): arm the NPC hex (a real opponent-card hit consumed by
 * startPTurn) -> if the second trigger is wired, oPts drops again;
 * grep says no wire exists, this DRIVES that claim. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
G.pF=[{id:'retort',tier:1,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
G.oPts=1000;try{updHUD();}catch(e){}
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll 1'};
await sleep(500);
/* keep the 1, then roll the remaining five into a DEAD table -> bust */
const one=G.pool.find(d=>!d.committed&&d.val===1);
tap(one.el);await sleep(300);
[2,2,3,3,4].forEach(v=>Q.push(v));
const o0=G.oPts;
tap(document.getElementById('btnRoll'));
/* the rival's own bank RAISES oPts moments after the bust seam pays,
   so track the MINIMUM through the transition - retort's 400 is the
   only subtractor in play */
let minO=o0;
const tPoll=setInterval(()=>{try{if(G.oPts<minO)minO=G.oPts;}catch(e){}},50);
if(!await until(()=>G.phase==='opp'||(G.turnNum||0)>=2,25000)){clearInterval(tPoll);return {err:'no bust',phase:G.phase};}
/* LEG B: the rival turn runs; before OUR next turn starts, arm the
   hex so startPTurn consumes it - a real opponent-card hit */
G._npcHexArmed=true;
const RH=[];const _orc=CFX.retort.cardHit;
CFX.retort.cardHit=function(ev){const before=G.oPts;const r=_orc.apply(this,arguments);RH.push({src:ev.src,actor:ev.actor,owner:ev.owner,mine:ev.mine,before:before,after:G.oPts});return r;};
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000)){clearInterval(tPoll);return {err:'no turn 2'};}
clearInterval(tPoll);
const oAfterBust=minO;
const bustPaid=(o0-minO);
await sleep(2000);
const hexLanded=(G.numDice<(G.matchDice||[]).length);/* hex took a die */
const hit=RH.find(h=>h.src==='whispers_hex'&&h.mine);
const hitPaid=hit?(hit.before-hit.after):0;
return {o0:o0,oAfterBust:oAfterBust,bustPaid:bustPaid,hexLanded:hexLanded,
  numDice:G.numDice,hitPaid:hitPaid,RH:RH,
  verdicts:{
    bustTriggerPays400:bustPaid===400,
    hexActuallyHit:hexLanded,
    hitTriggerPays:hitPaid>0},
  verdict:bustPaid===400};
