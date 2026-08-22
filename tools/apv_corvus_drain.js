const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchBossMatch==='function',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
S.run.tier=3;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match'};
await sleep(2500);
/* count drain events by watching gold, and roll events by the seam */
const golds=[];
const rolls=[];
const _ff=window.famFire;
window.famFire=function(seam,ev){if(seam==='roll')rolls.push(ev&&ev.rollNum);return _ff.apply(this,arguments);};
let last=S.run.gold;
const iv=setInterval(()=>{if(S.run.gold!==last){golds.push({from:last,to:S.run.gold});last=S.run.gold;}},30);
const Q=[1,1,5,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* ONE tap only - no retry, so the count is unambiguous */
const tapped=tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing',12000);
await sleep(900);
clearInterval(iv);
return {tapped,rollSeamFires:rolls,turnRollCount:G.turnRollCount,
  goldSteps:golds,totalRollCost:(G._tellState&&G._tellState.totalRollCost)||0,
  chip:(document.getElementById('arrearsVal')||{}).textContent,
  verdict:golds.length===1&&(G._tellState&&G._tellState.totalRollCost)===5};
