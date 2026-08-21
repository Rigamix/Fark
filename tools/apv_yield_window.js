/* RULING 1 GATE (Denis): before building a real reroll behind
 * timing:'yielding', measure whether a tapping human can fire it.
 * Drives a REAL bank, samples the window at 50ms, and reports: how
 * long canActivateCard('crown_authority') is actually true, whether
 * the card is on screen and draggable in that window, and what (if
 * anything) signals the window is open. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
/* the card in slot 0, the real boss-reward route */
S.run.cards=S.run.cards||[];S.run.cards[0]='crown_authority';
try{save();}catch(e){}
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match'};
await sleep(2500);
const seeded=(G.pCards||[]).indexOf('crown_authority')>=0;
const usesSeeded=!!(G.activeCardState&&G.activeCardState.usedCards&&G.activeCardState.usedCards['crown_authority']);
/* roll, keep a scorer, bank -> the yielding window opens */
const Q=[1,1,5,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
let rolled=false;
for(let r=0;r<3&&!rolled;r++){tap(document.getElementById('btnRoll'));rolled=await until(()=>G.phase==='choosing',6000);}
if(!rolled)return {err:'no roll',seeded,usesSeeded};
await sleep(500);
const one=(G.pool||[]).find(d=>!d.committed&&d.val===1);
if(one)tap(one.el);
await sleep(400);
/* sample across the bank -> yield transition */
const samples=[];
const t0=Date.now();
tap(document.getElementById('btnBank'));
let sawYield=false,yieldStart=0,yieldEnd=0;
for(let i=0;i<120;i++){/* 6s at 50ms */
  const ph=G?G.phase:null;
  let can=false;try{can=canActivateCard('crown_authority');}catch(e){}
  /* the renderer's OWN markup: .mcard inside #playerCards, toggling
     card-ready / card-dormant (an earlier draft of this probe guessed
     .mcard-active + a 'glint' class and measured a false negative) */
  const bar=document.getElementById('playerCards');
  const cardEl=bar?bar.querySelector('.mcard[data-cid="crown_authority"]'):null;
  const cr=cardEl?cardEl.getBoundingClientRect():null;
  const onScreen=!!(cr&&cr.width>1&&cr.height>1&&cr.bottom>0&&cr.top<innerHeight);
  if(ph==='yielding'&&!sawYield){sawYield=true;yieldStart=Date.now();}
  if(sawYield&&ph==='yielding')yieldEnd=Date.now();
  samples.push({t:Date.now()-t0,ph,can,onScreen,
    glint:cardEl?cardEl.classList.contains('card-ready'):null,
    dormant:cardEl?cardEl.classList.contains('card-dormant'):null});
  if(sawYield&&ph!=='yielding'&&Date.now()-yieldStart>100)break;
  await sleep(50);
}
const canSamples=samples.filter(s=>s.can);
const canMs=canSamples.length?(canSamples[canSamples.length-1].t-canSamples[0].t):0;
const yieldMs=sawYield?(yieldEnd-yieldStart):0;
/* what signals the window? buttons + any status text */
const rollBtn=document.getElementById('btnRoll'),bankBtn=document.getElementById('btnBank');
return {seeded,usesSeeded,
  window:{yieldMs,canActivateMs:canMs,
    canWhileOnScreen:canSamples.filter(s=>s.onScreen).length,
    everCan:canSamples.length>0,
    everGlint:samples.some(s=>s.glint)},
  signals:{rollDisabled:rollBtn?rollBtn.classList.contains('disabled'):null,
    bankDisabled:bankBtn?bankBtn.classList.contains('disabled'):null,
    statusText:(document.getElementById('statusMsg')||{}).textContent||''},
  firstCan:canSamples[0]||null,lastCan:canSamples[canSamples.length-1]||null,
  phases:[...new Set(samples.map(s=>s.ph))],
  verdict:{
    windowExists:sawYield,
    humanReachable:canMs>=400&&canSamples.some(s=>s.onScreen),
    signalled:samples.some(s=>s.glint)}};
