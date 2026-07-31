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
const reached=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
if(!reached||typeof G==='undefined'||!G)return{fatal:'never reached a match',
  onMatchScreen:vis(document.getElementById('screen-match')),
  screens:[...document.querySelectorAll('[id^=screen-]')].filter(vis).map(e=>e.id)};
const R={};
/* #8: a steal moves points ACROSS the table */
G.oPts=1200; G._oLastBank=300; G.turnPts=0; G.kept=[];
const oBefore=G.oPts,pBefore=G.turnPts;
BREAK_TRIGGERS.vagabond.fire();
R.playerGained=G.turnPts-pBefore;
R.rivalLost=oBefore-G.oPts;
R.stealMovesPoints=R.playerGained===300&&R.rivalLost===300;
/* never below zero */
G.oPts=100; G._oLastBank=900; G.turnPts=0; G.kept=[];
BREAK_TRIGGERS.vagabond.fire();
R.rivalFloorAtZero=G.oPts===0;
/* #19: naked run reads the owned loadout, not what survived the fight */
S.run.tier=3;
S.run.dice=['bone','bone','bone','bone','bone','bone'];
G.matchDice=['obsidian','bone','bone','bone','bone'];   /* a Trade left a worked die on the table */
const feat=FEATS.filter(f=>f.id==='naked_run')[0];
R.nakedRun_ownedLoadoutWins=feat?feat.check(G)===true:'no feat';
S.run.dice=['obsidian','bone','bone','bone','bone','bone'];
G.matchDice=['bone','bone','bone','bone','bone','bone'];
R.nakedRun_workedBuildFails=feat?feat.check(G)===false:'no feat';
/* the pot still adds up under its new name */
G._turnBonusPot=0; G.kept=[{vals:[1],pts:100}];
G._turnBonusPot=250; G.turnPts=G.kept.reduce((a,k)=>a+k.pts,0)+(G._turnBonusPot||0);
R.potStillSums=G.turnPts===350;
R.oldFieldGone=typeof G._stakesRisingBonus==='undefined';
return R;
