/* TRADE through the real icon-keep: brand lane 0, keep the branded 1
 * (with a 5) by ROLLING - the swap must land: matchDice[0] and
 * matchOppDice[0] exchange, the ledger records it, the die repaints
 * to the rival's material, and the brand leaves the lane. */
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
G.pF=[];try{famRenderRow();}catch(e){}
const mine0=G.matchDice[0],theirs0=G.matchOppDice[0];
const Q=[1,5,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
G._enchArr=[{t:'trade',face:1},null,null,null,null,null];
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const branded=G.pool.find(d=>d.lane===0&&d.val===1);
if(!branded||!branded.ench)return {err:'no brand'};
tap(branded.el);await sleep(150);
tap(G.pool.find(d=>!d.committed&&d.val===5).el);await sleep(300);
[1,2,3,4].forEach(v=>Q.push(v));/* keep rolling - the match continues */
tap(document.getElementById('btnRoll'));
if(!await until(()=>(G._tradeSwaps||[]).length>0,10000))return {err:'no swap',md0:G.matchDice[0]};
await sleep(800);
const swap=(G._tradeSwaps||[])[0];
const laneDie=G.pool.find(d=>d.lane===0);
return {mine0,theirs0,md0:G.matchDice[0],od0:G.matchOppDice[0],
  swap:swap?{lane:swap.lane,mine:swap.mine,theirs:swap.theirs}:null,
  laneMatNow:laneDie?laneDie.mat:null,enchGone:!(G._enchArr&&G._enchArr[0]),
  verdicts:{
    swapped:G.matchDice[0]===theirs0&&G.matchOppDice[0]===mine0,
    ledgered:!!(swap&&swap.mine===mine0&&swap.theirs===theirs0),
    repainted:!laneDie||laneDie.mat===theirs0,
    brandLeftWithDie:!(G._enchArr&&G._enchArr[0])},
  verdict:G.matchDice[0]===theirs0&&G.matchOppDice[0]===mine0&&!!swap&&!(G._enchArr&&G._enchArr[0])};
