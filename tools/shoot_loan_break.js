/* BRIEF 4b: "the player's OWN die returns to that lane IMMEDIATELY. The player
 * stays at 6 dice for the rest of the match. The cost of breaking a borrowed die
 * is exactly the cost of breaking any die - one die gone for the match - never
 * inflated to a whole seat." Plus: the dead die is match-scoped, not run-scoped. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(1900);
const p=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(p){tap(p);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
_getS();
/* give the stash something worth lending */
S.run.diceInv=['obsidian','starstone']; S.run.dieEnchInv=[null,null]; save();
const invBefore=(S.run.diceInv||[]).slice();
const lent=CFX.fair_trade.use({});
if(!lent)return{skipped:'fair trade use() refused'};
const ft={...G._fairTrade};
const dice0=(G.matchDice||[]).slice(), num0=G.numDice;
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing'||G.phase==='idle',14000);
await until(()=>!(D3X.dice||[]).some(d=>d.roll),12000);
await sleep(500);
/* break the die sitting in the loaned lane */
const victim=(G.pool||[]).filter(d=>!d.committed&&d.lane===ft.lane)[0];
if(!victim)return{skipped:'loaned lane not live this roll',ftLane:ft.lane,
  lanes:(G.pool||[]).map(d=>d.lane)};
G._breakArmed=true;
try{_breakDie(victim);}catch(e){return{err:String(e)}}
await sleep(400);
_getS();
return {
  lentLane:ft.lane, ownDie:ft.was, borrowedDie:ft.borrowed,
  STAYS_AT_SIX: G.matchDice.length===dice0.length && G.numDice===num0,
  matchDiceLen:G.matchDice.length, numDice:G.numDice, wasLen:dice0.length, wasNum:num0,
  OWN_DIE_BACK_IN_LANE: G.matchDice[ft.lane]===ft.was,
  laneNowHolds:G.matchDice[ft.lane],
  BORROWED_DEAD_THIS_MATCH: (G._ftDead||[]).indexOf(ft.borrowed)>=0,
  STASH_NOT_SPLICED: (S.run.diceInv||[]).length===invBefore.length,
  stashNow:(S.run.diceInv||[]).slice(),
  LOAN_CLEARED: !G._fairTrade,
  CANNOT_RELEND_DEAD: (function(){try{
    G._fairTrade=null; const before=(G._ftDead||[]).slice();
    const ok=CFX.fair_trade.use({});
    const took=G._fairTrade?G._fairTrade.borrowed:null;
    return !(took&&before.indexOf(took)>=0);
  }catch(e){return 'err:'+e}})()
};
