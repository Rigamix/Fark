/* P851: "and the ability to play them" — the DRIVEN half. A real
 * patron seat, a real hand, a real rival turn: does the patron
 * actually fire a family card? Three legs, one per decider the NPC
 * levers use (score-gap based), asserting famUse(idx,'o') reached the
 * card and the effect landed. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
/* record every NPC card play at the dispatcher */
const plays=[];
const _fu=window.famUse;
window.famUse=function(i,actor){
  let id=null;try{const L=(actor==='o')?(G&&G.oF):(G&&G.pF);id=L&&L[i]&&L[i].id;}catch(e){}
  const before=(()=>{try{const L=(actor==='o')?G.oF:G.pF;return L&&L[i]?L[i].charges:null;}catch(e){return null;}})();
  const r=_fu.apply(this,arguments);
  if(actor==='o'){let after=null;try{const L=G.oF;after=L&&L[i]?L[i].charges:null;}catch(e){}
    plays.push({id,before,after,spent:before!=null&&after!=null&&after<before});}
  return r;};
const R={};
const runLeg=async(name,hand,setup)=>{
  let ok=false;
  for(let a=0;a<5&&!ok;a++){
    if(a>0){try{showScreen('gauntlet');}catch(e){}await sleep(700);}
    try{delete S.pendingMatch;}catch(e){}
    S.run.tier=5;/* night 6: full personas, 3-card hands */
    delete S.run.night;
    try{_ensureNight();}catch(e){}
    /* give seat 0 the hand under test */
    try{S.run.night.roster[0].fcards=hand.slice();
      S.run.night.seatsPlayed=S.run.night.roster.map(()=>false);
      S.run.night.results=S.run.night.roster.map(()=>null);}catch(e){}
    window._fkDiscardOk=true;
    try{launchSeat(0);}catch(e){}
    ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle'&&(G.pool||[]).length===0,9000);
    if(!ok)await sleep(1200);
  }
  if(!ok){R[name]={err:'no match'};return;}
  await sleep(2200);
  const dealt=(G.oF||[]).map(c=>c&&c.id);
  setup();
  const n0=plays.length;
  /* hand the turn over: roll, keep a scorer, bank -> the rival plays */
  const Q=[1,1,5,2,3,4];
  const realE=window._enchRollM;
  window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
  let rolled=false;
  for(let r=0;r<3&&!rolled;r++){tap(document.getElementById('btnRoll'));rolled=await until(()=>G.phase==='choosing',6000);}
  if(!rolled){R[name]={err:'no roll',dealt};return;}
  await sleep(400);
  const one=(G.pool||[]).find(d=>!d.committed&&d.val===1);
  if(one)tap(one.el);
  await sleep(300);
  tap(document.getElementById('btnBank'));
  /* speed the rival turn and wait for it to finish */
  const iv=setInterval(()=>{try{if(G&&(G.phase==='opp'||G._oppTurnActive))G._ffMult=0.05;}catch(e){}},120);
  await until(()=>plays.length>n0,25000);
  await sleep(1500);
  clearInterval(iv);
  R[name]={dealt,played:plays.slice(n0),
    fired:plays.slice(n0).length>0,
    spent:plays.slice(n0).some(p=>p.spent)};
};
/* leg A: double_or_nothing — its lever wants the player 1000+ ahead */
await runLeg('doubleOrNothing',
  [{id:'double_or_nothing',tier:1,charges:1,state:{}},{id:'slow_cook',tier:1},{id:'retort',tier:1}],
  ()=>{G.pPts=2000;G.oPts=200;try{updHUD();}catch(e){}});
/* leg B: sleight — lever wants the player 800+ ahead */
await runLeg('sleight',
  [{id:'sleight',tier:1,charges:1,state:{}},{id:'bloom',tier:1},{id:'pickpocket',tier:1}],
  ()=>{G.pPts=1800;G.oPts=200;G._oSleight=false;try{updHUD();}catch(e){}});
/* leg C: a full 3-card hand straight from the generator, untouched */
let genHand=null;
try{const p=generatePatron(5,null);genHand=(p.fcards||[]).map(c=>Object.assign({charges:1,state:{}},c));}catch(e){}
if(genHand&&genHand.length)await runLeg('generatedHand',genHand,()=>{G.pPts=2400;G.oPts=200;try{updHUD();}catch(e){}});
return {R,
  verdicts:{
    donFired:!!(R.doubleOrNothing&&R.doubleOrNothing.fired),
    sleightFired:!!(R.sleight&&R.sleight.fired),
    generatedHandSize:genHand?genHand.length:0,
    generatedHandNoDead:!!(R.generatedHand&&!R.generatedHand.err)},
  verdict:!!(R.doubleOrNothing&&R.doubleOrNothing.fired&&R.sleight&&R.sleight.fired&&genHand&&genHand.length===3)};
