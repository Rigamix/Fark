/* THE TAB + HIGH TABLE.
 * Tab: own it -> the room chip renders (reachability); take -> +250g,
 * owe 400; pay refuses while short; pay clears at 500g; retake then
 * force-settle broke -> a circle rubs out instead.
 * High Table: own it -> seat target +500 (G.target), and the win pot
 * pays floor(base*1.5)+buyIn (seat 0 persona is not hoard/triples). */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
S.run.fcards=[{id:'the_tab',tier:1,charges:1},{id:'high_table',tier:1,charges:0}];
S.run.gold=100;S.run.points=3;S.run._tabOwed=0;
try{save();}catch(e){}
/* the chip surface */
try{showScreen('gauntlet');}catch(e){}
await sleep(800);
const chipShown=(document.body.textContent||'').indexOf('the tab')>=0;
/* take */
famTabTake();
const afterTake={gold:S.run.gold,owed:S.run._tabOwed};
/* pay while short: 350 < 400 -> refuses */
famTabPay();
const shortPay={gold:S.run.gold,owed:S.run._tabOwed};
/* pay at 500 */
S.run.gold=500;famTabPay();
const paid={gold:S.run.gold,owed:S.run._tabOwed};
/* retake, then settle broke -> circle */
famTabTake();
S.run.gold=100;
const pts0=S.run.points;
_tabSettle();
const settled={gold:S.run.gold,owed:S.run._tabOwed,points:S.run.points,pts0:pts0};
/* HIGH TABLE: sit and win */
S.run.gold=100;
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000))return {err:'no match',chipShown,afterTake,shortPay,paid,settled};
await sleep(3000);
const targetRaised=G.target;
const htArmed=!!G._highTable;
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
G.pPts=(G.target||3300)-100;try{updHUD();}catch(e){}
const gold0=S.run.gold;
const hcap=!!(G._handicap||G._sealRule);/* the seat rolls sealed some nights - the baseline doubles */
const expectedPot=Math.floor(20*(hcap?2:1)*1.5)+10;
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll',targetRaised};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
tap(document.getElementById('btnBank'));
if(!await until(()=>G._endMatchFired,25000))return {err:'no win',targetRaised,htArmed};
await sleep(2500);
const potGain=S.run.gold-gold0;/* half-again on the seat baseline: floor(20*(hcap?2:1)*1.5)+10 */
return {chipShown,afterTake,shortPay,paid,settled,targetRaised,htArmed,potGain,hcap,expectedPot,
  verdicts:{
    chipReachable:chipShown,
    take250Owe400:afterTake.gold===350&&afterTake.owed===400,
    shortPayRefused:shortPay.gold===350&&shortPay.owed===400,
    payClears:paid.gold===100&&paid.owed===0,
    brokeSettleRubsCircle:settled.owed===0&&settled.gold===100&&settled.points===settled.pts0-1,
    targetPlus500:targetRaised===3300,
    potHalfAgain:potGain===expectedPot},
  verdict:chipShown&&afterTake.gold===350&&paid.owed===0&&settled.points===settled.pts0-1&&targetRaised===3300&&potGain===expectedPot};
