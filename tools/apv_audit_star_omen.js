/* ILL OMEN, both outcomes. Leg A: declare, bank, FORCE the rival's
 * bust (rollFace queue all-dead) -> player takes 800, rival bleeds
 * up to 800 of their preset 1000. Leg B: fresh instance, rival banks
 * normally -> they gain 400. Dead wire: neither purse moves. */
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
G.pF=[{id:'ill_omen',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
G.oPts=1000;try{updHUD();}catch(e){}
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* the rival deals through rollFace: first turn ALL DEAD -> bust */
const realRF=window.rollFace;
let RQ=[2,2,3,3,4,6];
window.rollFace=m=>RQ.length?RQ.shift():realRF(m);
/* declare from idle, then take the turn */
const OW=[];const _oio=CFX.ill_omen.rivalTurn;
CFX.ill_omen.rivalTurn=function(ev){const b={p:G.pPts,o:G.oPts};const r=_oio.apply(this,arguments);if(ev.mine)OW.push({pts:ev.pts,dp:G.pPts-b.p,dO:G.oPts-b.o});return r;};
famUse(0);
await sleep(250);
if(!G._famIllOmen)return {err:'no declare'};
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(500);
const one=G.pool.find(d=>!d.committed&&d.val===1);
tap(one.el);await sleep(300);
const p0=G.pPts,o0=G.oPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank'};
const pAfterBank=G.pPts;
/* rival turn: forced bust -> omen lands */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2'};
await sleep(2000);
const omenTake=G.pPts-pAfterBank;
const oAfterOmen=G.oPts;
const consumed=!G._famIllOmen;
/* LEG B: fresh instance, rival banks normally (real RNG) */
G.pF=[{id:'ill_omen',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
famUse(0);
await sleep(250);
if(!G._famIllOmen)return {err:'no declare B',omenTake};
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B'};
await sleep(500);
const oneB=G.pool.find(d=>!d.committed&&d.val===1);
tap(oneB.el);await sleep(300);
const p1=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p1,15000))return {err:'no bank B',omenTake};
/* the rival's turn with real RNG; track their score to know they
   banked (pts>0). If they happen to bust, the run is inconclusive
   for leg B - report it honestly. */
const oB0=G.oPts;
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=3,90000))return {err:'no turn 3',omenTake};
await sleep(2000);
const oGain=G.oPts-oB0;
/* their gain = their own bank + the 400 miss bonus; the bonus is
   provable if gain-400 is a plausible bank (>=0) AND the omen record
   is consumed. A busted rival makes gain 800-oh wait, a bust would
   PAY leg A again: gain would be -??; detect via oGain<0 */
const consumedB=!G._famIllOmen;
const hitA=OW[0]||{},hitB=OW[1]||{};
return {omenTake:omenTake,o0:o0,oAfterOmen:oAfterOmen,consumed:consumed,
  oGain:oGain,consumedB:consumedB,OW:OW,
  verdicts:{
    omenLandsTakes800:hitA.dp===800&&hitA.dO===-800&&hitA.pts<=0,
    declarationConsumed:consumed,
    missGives400:hitB.dp===0&&hitB.dO===400&&hitB.pts>0,
    missConsumed:consumedB},
  verdict:hitA.dp===800&&hitA.dO===-800&&consumed&&hitB.dO===400&&consumedB};
