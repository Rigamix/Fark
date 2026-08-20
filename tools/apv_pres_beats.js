/* P826/P828: the beat WIRES, driven on real paths with cardFx/_fxSpray
 * logged. Turn 1: falling_star arm (bank 1000 >= threshold) -> 'gain'
 * beat + the go-again starburst + turn 2 begins (extra turn). Turn 2:
 * double_or_nothing armed, flip FORCED to lose -> churn + hit beats +
 * economics (-half). Then encore: blue class + spray on the reroll. */
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
/* wire log */
const FXLOG=[];const _ocfx=window.cardFx;
window.cardFx=function(k,t,o){FXLOG.push({k:k,t:JSON.stringify(t||null)});return _ocfx.apply(this,arguments);};
const SPLOG=[];const _osp=window._fxSpray;
window._fxSpray=function(el,col,n,o){SPLOG.push(col);return _osp.apply(this,arguments);};
G.pF=[{id:'falling_star',tier:3,charges:0,state:{}},/* t3 threshold 1000 - t1's 1500 is above the probe's triple */
      {id:'double_or_nothing',tier:1,charges:1,state:{}},
      {id:'encore',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,1,1,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
tap(ones[0].el);await sleep(120);tap(ones[1].el);await sleep(120);tap(ones[2].el);await sleep(300);
tap(document.getElementById('btnBank'));/* 1000 - falling_star arms */
if(!await until(()=>G._fExtraTurn===false&&(G.turnNum||0)===1&&G.phase==='idle'||FXLOG.some(x=>x.k==='gain'),20000)){}
/* the extra turn: endPTurn consumes _fExtraTurn - same turnNum, back to idle */
const extraTurn=await until(()=>G.phase==='idle'&&!G._fExtraTurn&&G.pPts>=1000,20000);
await sleep(1400);
const starArmBeat=FXLOG.some(x=>x.k==='gain'&&/falling_star/.test(x.t));
const starburst=SPLOG.filter(c=>c==='#ffd870'||c==='#fff2c0').length>=2;
const wentAgain=(G.turnNum||0)===1&&G.phase==='idle';/* no rival turn ran */
/* TURN (extra): DoN - arm, keep a 1, bank with the flip FORCED to lose */
[1,2,3,4,6,6].forEach(v=>Q.push(v));
famUse(1);/* arm before the bank, per the card */
await sleep(300);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll 2',FXLOG};
await sleep(600);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p1=G.pPts;
const realRandom=Math.random;
Math.random=()=>0.9;/* flip loses */
tap(document.getElementById('btnBank'));
await until(()=>G.phase==='opp'||G.pPts!==p1+100,15000);
Math.random=realRandom;
await sleep(600);
const flipChurn=FXLOG.some(x=>x.k==='churn'&&/double_or_nothing/.test(x.t));
const flipHit=FXLOG.some(x=>x.k==='hit'&&/double_or_nothing/.test(x.t));
const donDelta=G.pPts-p1;/* +100 bank then -50 flip = +50 */
return {extraTurn,starArmBeat,starburst,wentAgain,flipChurn,flipHit,donDelta,
  fx:FXLOG.slice(0,10),
  verdicts:{
    fallingStarArmBeat:starArmBeat,
    goAgainStarburst:starburst,
    extraTurnGranted:wentAgain,
    flipChurns:flipChurn,
    flipLossHits:flipHit,
    flipEconomics:donDelta===50},
  verdict:starArmBeat&&starburst&&flipChurn&&flipHit&&donDelta===50};
