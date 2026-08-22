/* IS THE CARDS-TABLE LAYER REACHABLE? The question P846 retracted §1c
 * on and never actually asked. Static evidence says no (every writer
 * to S.run.cards sits behind showScreen('draft') / showScreen(
 * 'bossreward') - neither name is ever passed - or #endDraftSlots,
 * which is read 9 times and created 0, or S.renownPerks.legend, which
 * _getS wipes and nothing sets). This DRIVES it: win a patron match
 * and a boss match, record every screen the game opens, and read
 * S.run.cards after each payout. */
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
/* record every screen the game opens, for the whole probe */
const screens=[];
const _ss=window.showScreen;
window.showScreen=function(name,data){screens.push(name);return _ss.apply(this,arguments);};
/* and every write to S.run.cards */
const cardWrites=[];
const R={};
const snapCards=()=>JSON.parse(JSON.stringify(S.run.cards||[]));
R.cardsAtStart=snapCards();
const winOnce=async(label,boss)=>{
  let ok=false;
  for(let a=0;a<5&&!ok;a++){
    if(a>0){try{_ss('gauntlet');}catch(e){}await sleep(700);}
    try{delete S.pendingMatch;}catch(e){}
    try{if(S.run&&S.run.night){S.run.night.seatsPlayed=S.run.night.roster.map(()=>false);
      S.run.night.results=S.run.night.roster.map(()=>null);}}catch(e){}
    window._fkDiscardOk=true;
    try{boss?launchBossMatch():launchSeat(0);}catch(e){}
    ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle'&&(G.pool||[]).length===0,9000);
    if(!ok)await sleep(1200);
  }
  if(!ok){R[label]={err:'no match'};return;}
  await sleep(2200);
  const before=snapCards();
  const nS=screens.length;
  /* force the win */
  G.pPts=(G.target||2800)-500;
  try{updHUD();}catch(e){}
  const Q=[1,1,1,2,3,4];
  const realE=window._enchRollM;
  window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
  let rolled=false;
  for(let r=0;r<3&&!rolled;r++){tap(document.getElementById('btnRoll'));rolled=await until(()=>G.phase==='choosing',6000);}
  if(!rolled){R[label]={err:'no roll'};return;}
  await sleep(500);
  const ones=(G.pool||[]).filter(d=>!d.committed&&d.val===1).slice(0,3);
  for(const d of ones){tap(d.el);await sleep(120);}
  await sleep(300);
  tap(document.getElementById('btnBank'));
  await until(()=>G._endMatchFired,20000);
  await sleep(3500);/* let the payout screens run */
  R[label]={won:!!G._endMatchFired,
    screensOpened:screens.slice(nS),
    cardsBefore:before,cardsAfter:snapCards(),
    fcardsAfter:(S.run.fcards||[]).map(c=>c.id+'-T'+c.tier),
    changed:JSON.stringify(before)!==JSON.stringify(snapCards())};
};
await winOnce('patronWin',false);
await winOnce('bossWin',true);
/* the static claims, re-checked at runtime */
const evidence={
  bossrewardEverOpened:screens.indexOf('bossreward')>=0,
  draftEverOpened:screens.indexOf('draft')>=0,
  endDraftSlotsExists:!!document.getElementById('endDraftSlots'),
  renownPerks:JSON.parse(JSON.stringify(S.renownPerks||{})),
  legendPerk:!!(S.renownPerks&&S.renownPerks.legend),
  allScreensSeen:[...new Set(screens)]};
return {R,evidence,
  verdict:{
    cardsLayerEverFilled:(S.run.cards||[]).filter(Boolean).length>0,
    familyLayerFilled:(S.run.fcards||[]).length>0,
    conclusion:((S.run.cards||[]).filter(Boolean).length>0)
      ?'CARDS layer IS reachable'
      :'CARDS layer NOT reachable through any driven payout'}};
