/* SUITE: exclude. A1a PRESERVE REPRO - three questions, one run:
 * 1. CAPTURE: which die does the picker take when a 5-group precedes a
 *    1-group? (suspect: first-match, no player choice, no 1-over-5 pref)
 * 2. PAYOUT: does a {val:1} record come back as a 1 with points, one die
 *    short, through the REAL endPTurn -> opp turn -> startPTurn cycle?
 * 3. SNAPSHOT: what does the post-payout boundary claim famPreserve is?
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(70);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
const out={};
tap(document.getElementById('hsBtnBottom'));await sleep(2000);
await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
tap(document.querySelector('.nrdie'));await sleep(1200);
tap(document.getElementById('nrTakeBtn'));await sleep(2400);
await until(()=>typeof launchSeat==='function'&&S&&S.run,9000);
_getS();try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
out.ready=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);
if(!out.ready)return out;
const logs=[];const _fl=window.famLog;window.famLog=function(m){logs.push(String(m));try{return _fl.apply(this,arguments);}catch(e){}};

/* ---- Q1: the picker, 5-group first ---- */
G.kept=[
 {vals:[5],mat:'bone',pts:50,dice:[{val:5,mat:'bone',ench:null,lane:0}]},
 {vals:[1],mat:'iron',pts:100,dice:[{val:1,mat:'iron',ench:null,lane:3}]}
];
const inst={id:'preserve',tier:1,charges:1,state:{}};
G.pF=[inst];
out.q1_used=CFX.preserve.use(inst);
out.q1_record=G._famPreserve?{...G._famPreserve}:null;   /* expect val 5: first match, no choice */
out.q1_announce=logs.slice(-1)[0]||null;

/* ---- Q1b: 1-group first ---- */
G._famPreserve=null;
G.kept=[
 {vals:[1],mat:'iron',pts:100,dice:[{val:1,mat:'iron',ench:null,lane:3}]},
 {vals:[5],mat:'bone',pts:50,dice:[{val:5,mat:'bone',ench:null,lane:0}]}
];
out.q1b_used=CFX.preserve.use(inst);
out.q1b_record=G._famPreserve?{...G._famPreserve}:null;  /* expect val 1 */

/* ---- Q2: the real cycle with a {val:1,lane:3} record pending ---- */
G._famPreserve={val:1,mat:'iron',ench:null,lane:3,pts:100,crack:0};
G._famPreserveAtTurnStart=null;
G.kept=[];G.turnPts=0;
const turnBefore=G.turnNum;
logs.length=0;
handleYield();                                            /* the real bank */
out.q2_banked=await until(()=>G&&G.phase!=='opp'&&G.turnNum>turnBefore,45000);
if(out.q2_banked){
  await sleep(600);
  const kr=document.getElementById('keptRow');
  const chips=kr?[...kr.querySelectorAll('.die')]:[];
  out.q2={
    announces:logs.filter(m=>/AMBER|PRESERV/i.test(m)),
    keptVals:(G.kept||[]).map(k=>k.vals),
    turnPts:G.turnPts,
    numDice:G.numDice,
    mintedVals:chips.map(c=>c._trueVal),
    mintedMats:chips.map(c=>c._trueMat),
    liveRecord:G._famPreserve,
    atTurnStart:G._famPreserveAtTurnStart?{val:G._famPreserveAtTurnStart.val}:null,
    pvLane:G._pvLane
  };
  /* ---- Q3: what would a save RIGHT NOW claim? (the resume replay contract) */
  out.q3_snapshotWouldCarry=(G._famPreserveAtTurnStart!==undefined&&G._famPreserveAtTurnStart!==null)
    ?{src:'atTurnStart',val:G._famPreserveAtTurnStart.val}
    :(G._famPreserve?{src:'live',val:G._famPreserve.val}:null);
}
/* ---- Q4: WHO renders the minted die and what face does each layer think it shows ---- */
if(out.q2_banked){
  const kr=document.getElementById('keptRow');
  const host=kr?kr.querySelector('.die'):null;
  if(host){
    const dx=(window.D3X&&D3X.dice||[]).find(d=>d.chip===host||d.chip===host.parentElement);
    const e3=host._d3;
    out.q4={
      fk3d:document.documentElement.classList.contains('fk3d'),
      hostClasses:host.className,
      wrapDataMat:host.parentElement&&host.parentElement.getAttribute&&host.parentElement.getAttribute('data-mat'),
      trueVal:host._trueVal,trueMat:host._trueMat,still:host._d3Still,
      adopted:!!dx,
      dxMatch:dx?dx.match:null,
      dxOwned:e3?!!e3._d3xOwned:null,
      dxObjVisible:dx&&dx.obj?dx.obj.visible:null,
      dxQuat:dx&&dx.obj?dx.obj.quaternion.toArray().map(x=>+x.toFixed(3)):null,
      d3state:e3?{result:e3.result,pitch:e3.pitch,yaw:e3.yaw,tilt:e3.tilt,turn:e3.turn,spin:e3.spin,
        slotVis:e3.slot?getComputedStyle(e3.slot).visibility+'/'+getComputedStyle(e3.slot).display:null}:null,
      isoQ1:(window.D3X&&D3X._isoQ)?D3X._isoQ(1,D3X.TILT_MATCH).toArray().map(x=>+x.toFixed(3)):null,
      isoQ5:(window.D3X&&D3X._isoQ)?D3X._isoQ(5,D3X.TILT_MATCH).toArray().map(x=>+x.toFixed(3)):null
    };
  }
}
out.verdict={
  pickerTakesFirstMatchNotThe1: out.q1_record&&out.q1_record.val===5,
  captureRight_q1b: out.q1b_record&&out.q1b_record.val===1,
  payoutVal: out.q2&&out.q2.keptVals.length?out.q2.keptVals[0][0]:null,
  payoutPts: out.q2?out.q2.turnPts:null,
  dieShort: out.q2?out.q2.numDice:null
};
return out;
