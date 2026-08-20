/* 1d FOG, adversarial: fog their lane 0, script their deal so lane 0
 * holds the BEST scorer (a 1) and lane 1 a lesser one (a 5). A seeing
 * chooser keeps the 1; a fog-blinded one cannot see it and keeps the 5.
 * Kept lanes are the falsifiable observable. */
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
const Q1=[1,2,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q1.length?Q1.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no choosing'};
await sleep(500);
/* fog their lane 0 */
_lmArm('_fog',0,1);
const fogState=G._fog?JSON.parse(JSON.stringify(G._fog)):null;
const one=(G.pool||[]).find(d=>!d.committed&&d.val===1);
if(!one)return {err:'no 1'};
tap(one.el);
await sleep(300);
/* their deal: lane0=1 (fogged, best), lane1=5 (visible scorer), rest dead */
const SEQ=[1,5,2,2,3,3];
const draws=[];
const realF=window.rollFace;
window.rollFace=function(m){
  const v=(draws.length<SEQ.length)?SEQ[draws.length]:realF(m);
  draws.push(v);return v;
};
tap(document.getElementById('btnBank'));
if(!await until(()=>(G.oppDice||[]).length>=6,20000))return {err:'no opp deal'};
/* wait for their keep decision - kept flags mutate in the roll resolution */
if(!await until(()=>(G.oppDice||[]).some(d=>d.kept)||(G._oppHeld||[]).length>0,20000))
  return {err:'no keeps',vals:(G.oppDice||[]).map(d=>d.val)};
await sleep(600);
window.rollFace=realF;
const keptLanes=[].concat(
  (G.oppDice||[]).filter(d=>d.kept).map(d=>d.lane),
  (G._oppHeld||[]).map(d=>d.lane));
const dealt=(G.oppDice||[]).map(d=>({lane:d.lane,val:d.val}));
return {fog:fogState,dealt:dealt,keptLanes:keptLanes,fogAfter:G._fog||null,
  verdicts:{
    laneZeroWasOne:!!dealt.find(d=>d.lane===0&&d.val===1),
    fogBlindsIt:keptLanes.indexOf(0)<0,
    keepsTheVisibleFive:keptLanes.indexOf(1)>=0
  },
  verdict:keptLanes.indexOf(0)<0&&keptLanes.indexOf(1)>=0};
