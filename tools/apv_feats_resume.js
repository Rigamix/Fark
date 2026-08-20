/* P843: feat accumulators survive a mid-match save/resume. Drives the
 * REAL pipeline: saveMatchState -> the localStorage JSON boundary ->
 * resumeMatch -> the featState restore loop. Leg 2: a pre-P843
 * snapshot (no featState) resumes clean with fresh zeroes. Leg 3: a
 * driven win proves restored progress feeds evaluateFeats
 * (slow_boiled from a restored 7-roll max, long_road from a restored
 * deficit). */
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
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
/* leg 1: distinctive values on every carried field - numbers, booleans,
   and a legit zero/false to prove presence-not-truthiness */
const SET={_featMaxRolls:7,_featBloom:true,_featWardSaves:2,_featMaxBank:1900,
  _featJade:true,_featSticky:3,_featBusts:1,_featShatterBanked:true,
  _featStarChain:2,_featOmenTrue:1,_featMaxDeficit:1234,_forKeeps:true};
Object.keys(SET).forEach(k=>{G[k]=SET[k];});
saveMatchState();
const snapHasFeat=!!(S.pendingMatch&&S.pendingMatch.featState);
if(!snapHasFeat)return {err:'no featState in snapshot'};
/* the real serialization boundary */
const disk=JSON.parse(localStorage.getItem('gambit4_proto')||'{}');
const onDisk=disk.pendingMatch&&disk.pendingMatch.featState;
const diskOk=!!onDisk&&onDisk._featMaxRolls===7&&onDisk._forKeeps===true&&onDisk._featMaxDeficit===1234;
S.pendingMatch=disk.pendingMatch;
const G1=G;
resumeMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G!==G1&&G.phase==='idle',14000))return {err:'no resume 1',diskOk};
await sleep(2500);
const restored={};let allRestored=true;
Object.keys(SET).forEach(k=>{restored[k]=G[k];if(G[k]!==SET[k])allRestored=false;});
/* leg 2: a pre-P843 snapshot resumes clean */
saveMatchState();
const old=JSON.parse(JSON.stringify(S.pendingMatch));
delete old.featState;
S.pendingMatch=old;
const G2=G;
resumeMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G!==G2&&G.phase==='idle',14000))return {err:'no resume 2',diskOk,restored};
await sleep(2500);
const oldSnapClean=(G._featMaxRolls||0)===0&&(G._featMaxDeficit||0)===0&&!G._forKeeps;
/* leg 3: restored progress feeds evaluateFeats on a driven win */
G._featMaxRolls=7;G._featMaxDeficit=9999;
S.run._featsThisRun=0;S.run.feats={};
G.pPts=(G.target||2800)-900;try{updHUD();}catch(e){}
const Q=[1,1,1,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll',diskOk,restored,oldSnapClean};
await sleep(600);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
tap(ones[0].el);await sleep(120);tap(ones[1].el);await sleep(120);tap(ones[2].el);await sleep(300);
tap(document.getElementById('btnBank'));
if(!await until(()=>G._endMatchFired,20000))return {err:'no win',diskOk,restored,oldSnapClean};
await sleep(1500);
const feats=Object.keys(S.run.feats||{});
return {diskOk,restored,allRestored,oldSnapClean,feats,
  verdicts:{
    featStateOnDisk:diskOk,
    twelveFieldsRestored:allRestored,
    preP843SnapshotClean:oldSnapClean,
    restoredProgressAwards:feats.indexOf('slow_boiled')>=0&&feats.indexOf('long_road')>=0},
  verdict:diskOk&&allRestored&&oldSnapClean
    &&feats.indexOf('slow_boiled')>=0&&feats.indexOf('long_road')>=0};
