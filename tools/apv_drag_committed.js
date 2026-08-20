/* P835: a committed die sits OUT of the vagabond drag. Commit the 1,
 * start a drag on a free die, move it across, commit the drag - the
 * committed die must keep its pool index, its lane and its seat pair
 * (matchDice[lane]===mat), while the free dice genuinely permute. */
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
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
/* commit the 1 by keep+reroll (committed:true stays in the pool) */
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
[5,2,3,4,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===2,20000))return {err:'no roll 2'};
await sleep(900);
/* wait for the PHYSICS rest (apv_p702 pattern) - _vgRowInfo needs d.phys */
await until(()=>window.D3X&&D3X.dice.filter(d=>d.match&&d.phys).length>=6,9000);
await sleep(800);
const committedDie=G.pool.find(d=>d.committed);
if(!committedDie)return {err:'no committed die'};
const cIdxBefore=G.pool.indexOf(committedDie);
const cLaneBefore=committedDie.lane;
const cMatBefore=committedDie.mat;
const freeBefore=G.pool.filter(d=>!d.committed).map(d=>({v:d.val,lane:d.lane}));
/* start a drag on a free die (bypass the vagabond-material gate; the
   census/commit path is the unit under test) */
const dragMe=G.pool.filter(d=>!d.committed)[0];
_startVagabondDrag(dragMe.el);
await sleep(150);
const st=window._vgDragState;
if(!st){const info=_vgRowInfo();return {err:'drag did not start',d3xDice:(window.D3X&&D3X.dice||[]).filter(d=>d.match).length,info:info?{n:info.dice.length}:null,dragMeConn:!!(dragMe.el&&dragMe.el.isConnected)};}
const censusSize=st.order.length;
const committedInCensus=st.order.some(d=>d.chip===committedDie.el);
/* carry it to the far end and commit */
st.to=st.order.length-1;
_commitVagabondDrag();
await sleep(400);
const cIdxAfter=G.pool.indexOf(committedDie);
const cLaneAfter=committedDie.lane;
const seatPairHolds=G.matchDice[committedDie.lane]===cMatBefore;
const freeAfter=G.pool.filter(d=>!d.committed).map(d=>({v:d.val,lane:d.lane}));
const freeOrderChanged=JSON.stringify(freeAfter.map(f=>f.v))!==JSON.stringify(freeBefore.map(f=>f.v));
/* every die's seat pair must hold after the permute */
const allPairsHold=G.pool.every(d=>G.matchDice[d.lane]===d.mat||d.mat===undefined);
return {censusSize,committedInCensus,cIdxBefore,cIdxAfter,cLaneBefore,cLaneAfter,
  freeBefore:freeBefore.map(f=>f.v),freeAfter:freeAfter.map(f=>f.v),
  freeOrderChanged,seatPairHolds,allPairsHold,
  verdicts:{
    committedExcludedFromCensus:!committedInCensus&&censusSize===freeBefore.length,
    committedKeepsPoolIndex:cIdxAfter===cIdxBefore,
    committedKeepsLane:cLaneAfter===cLaneBefore,
    committedSeatPairHolds:seatPairHolds,
    freeDiceActuallyPermute:freeOrderChanged,
    everySeatPairHolds:allPairsHold},
  verdict:!committedInCensus&&cIdxAfter===cIdxBefore&&cLaneAfter===cLaneBefore
    &&seatPairHolds&&freeOrderChanged&&allPairsHold};
