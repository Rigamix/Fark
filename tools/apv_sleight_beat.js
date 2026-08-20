/* P830: sleight's beat + face honesty, driven. Arm sleight, bank, and
 * during the rival's first roll: (1) the .card-reroll glow appears on
 * their dice AFTER the row settles (the land-pause-reroll order);
 * (2) after the reckoning, every rival die's MESH stamp equals its
 * scored value (the stale-face fix - chip._trueVal===d.val); (3) the
 * player's armed sleight card wears the armed look. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(80);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
G.pF=[{id:'sleight',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(500);
famUse(0);
await sleep(300);
const armed=!!G._famSleight;
const cardArmed=!!document.querySelector('#famRowP .fcv.armed');
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
/* their deal: batch 1-6 the deal, 7-12 the settle-reroll */
const realRF=window.rollFace;
const RQ=[2,3,4,6,6,2, 1,5,1,5,2,3];
window.rollFace=m=>RQ.length?RQ.shift():realRF(m);
tap(document.getElementById('btnBank'));
/* the ORDER: the glow must appear only after the row exists and settles */
if(!await until(()=>(G.oppDice||[]).length>=6,30000))return {err:'no deal'};
const dealVals=(G.oppDice||[]).map(d=>d.val);
const glowSeen=await until(()=>(G.oppDice||[]).some(d=>d.el&&d.el.classList.contains('card-reroll')),15000);
const valsAtGlow=(G.oppDice||[]).map(d=>d.val);
/* mesh honesty read AT the beat - the row is live here (post-reckoning it clears, and an empty sample proves nothing) */
await sleep(250);
const liveDice=(G.oppDice||[]).filter(d=>d.el);
const stampsLive=liveDice.map(d=>({v:d.val,t:d.el._trueVal}));
const honestLive=liveDice.length>=4&&liveDice.every(d=>d.el._trueVal===d.val);
/* after the reckoning: mesh honesty + the reroll batch is what they hold */
await sleep(2500);

const rerolled=valsAtGlow.join(',')!==dealVals.join(',')||RQ.length<=0;
return {armed,cardArmed,dealVals,valsAtGlow,glowSeen,honest:honestLive,stamps:stampsLive,sample:liveDice.length,
  spent:!G._famSleight,rqLeft:RQ.length,
  verdicts:{
    armShowsOnCard:cardArmed,
    glowAfterSettle:glowSeen,
    valuesSwitchedAtTheBeat:rerolled,
    meshStampsHonest:honestLive,
    armConsumed:!G._famSleight},
  verdict:cardArmed&&glowSeen&&honestLive&&!G._famSleight};
