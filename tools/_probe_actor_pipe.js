/* SUITE: exclude. P761/P762: the actor pipe, both seats, real seams.
 *
 * Player side must be UNCHANGED (regression), rival side must run the
 * SAME hooks through famFire's own routing - no direct effect calls,
 * the events go through the bus exactly as the seams raise them.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const out={};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
await until(()=>document.getElementById('screen-gauntlet'),8000);
launchSeat(0);
if(!await until(()=>G&&G.phase,12000))return {err:'no match'};
await until(()=>window.D3X&&D3X.mount,12000);
/* the match-start startPTurn clears BOTH rows moments after launch - an
   out-of-band rival turn started inside that window loses its held die
   to a wipe that, in the real lifecycle, only runs when the turn passes
   back. Let the opening player turn settle first. */
await sleep(3500);

const inst=(id,tier)=>({id:id,tier:tier||1,charges:2,state:{}});

/* ── 1. slow_cook, rival-owned, through the bus ── */
G.pF=[];G.oF=[inst('slow_cook')];
famFire('roll',{actor:'o',rollNum:3});
famFire('roll',{actor:'o',rollNum:4});
const scAcc=G.oF[0].state.acc||0;
const scDelta=famFire('bankBonus',{actor:'o',amt:100,total:100});
out.slowCook={acc:scAcc,delta:scDelta,drained:(G.oF[0].state.acc||0)===0};

/* player regression: same card, player-owned, player seams */
G.pF=[inst('slow_cook')];G.oF=[];
G.turnRollCount=3;
famFire('roll',{actor:'p'});
const scpAcc=G.pF[0].state.acc||0;
const scpDelta=famFire('bankBonus',{actor:'p',total:100});
out.slowCookPlayer={acc:scpAcc,delta:scpDelta};

/* ── 2. pickpocket, rival-owned: lifts from the PLAYER ── */
G.pF=[];G.oF=[inst('pickpocket')];
G.pPts=1000;G.oPts=500;
famFire('bank',{actor:'o',amt:300});
out.pickpocket={pPts:G.pPts,oPts:G.oPts,lifted:G.pPts<1000&&G.oPts>500};
/* and player-owned still lifts from the rival */
G.pF=[inst('pickpocket')];G.oF=[];
G.pPts=1000;G.oPts=500;
famFire('bank',{actor:'p',amt:300});
out.pickpocketPlayer={pPts:G.pPts,oPts:G.oPts,lifted:G.oPts<500&&G.pPts>1000};

/* ── 3. double_or_nothing: armed through famUse('o'), resolved at bank ── */
G.pF=[];G.oF=[inst('double_or_nothing')];
out.dblArm={canBefore:CFX.double_or_nothing.canUse(G.oF[0],'o')};
famUse(0,'o');
out.dblArm.armed=!!G.oF[0].state.armed;
out.dblArm.charge=G.oF[0].charges;
G.oPts=1000;const _o0=G.oPts;
famFire('bank',{actor:'o',amt:400});
out.dblArm.moved=G.oPts!==_o0;/* doubled or lost - either proves the flip ran */
out.dblArm.disarmed=!G.oF[0].state.armed;

/* ── 4. preserve, end to end: capture at their bank, REAL return next turn ── */
G.pF=[];G.oF=[inst('preserve')];
G._ovDie=null;
G.oppDice=[{val:1,mat:'amber',ench:null,lane:2,kept:true}];
famUse(0,'o');
out.preserve={captured:G._ovDie?JSON.parse(JSON.stringify(G._ovDie)):null,
  charge:G.oF[0].charges};
if(!G._ovDie)return Object.assign(out,{err:'preserve capture failed'});
/* their REAL next turn: the die must come back held in lane 2 */
G.oPts=0;G.pPts=0;
try{runOppTurn();}catch(e){return Object.assign(out,{err:'runOppTurn threw: '+e.message});}
await until(()=>((G._oppHeld||[]).some(d=>d.lane===2&&d.val===1))||G._ovDie===null,15000);
await sleep(2500);
const held=(G._oppHeld||[]).filter(d=>d.lane===2&&d.val===1)[0];
out.preserveReturn={
  consumed:G._ovDie===null,
  held:!!held,
  mat:held?held.mat:null,
  elLive:!!(held&&held.el&&held.el.isConnected),
  laneAvoided:!(G.oppDice||[]).some(d=>d.lane===2),
};
/* the amber shell on the actual 3D die */
let shell=false;
try{
  if(held&&window.D3X){
    const dd=D3X.dice.find(q=>q.chip===held.el);
    shell=!!(dd&&dd.obj&&dd.obj.getObjectByName('fkAmber'));
  }
}catch(e){}
out.preserveReturn.amber=shell;
/* let the turn finish so nothing leaks into verdicts */
await until(()=>G.oPts>0||((G._oppHeld||[]).length===0&&(G.oppDice||[]).length===0),45000);

out.verdicts={
  slowCookRival:out.slowCook.acc>0&&out.slowCook.delta===out.slowCook.acc&&out.slowCook.drained,
  slowCookPlayer:out.slowCookPlayer.acc>0&&out.slowCookPlayer.delta===out.slowCookPlayer.acc,
  pickpocketBoth:out.pickpocket.lifted&&out.pickpocketPlayer.lifted,
  dblFlip:out.dblArm.canBefore&&out.dblArm.armed&&out.dblArm.charge===1&&out.dblArm.moved&&out.dblArm.disarmed,
  preserveCapture:!!out.preserve.captured&&out.preserve.captured.mat==='amber'&&out.preserve.charge===1,
  preserveReturn:out.preserveReturn.consumed&&out.preserveReturn.held&&out.preserveReturn.mat==='amber'
    &&out.preserveReturn.elLive&&out.preserveReturn.laneAvoided,
};
out.verdict=Object.values(out.verdicts).every(v=>v);
return out;
