/* P846 SWEEP: every enrolled mutator driven individually, through the
 * door the player uses. The contract per leg is TWO-SIDED now:
 *   - a leg that MUTATED must have fired the R1 void (hook counter +
 *     ghosts 0 + promise null);
 *   - a leg that REFUNDED (no target) must NOT have voided - the
 *     promise survives a card that did nothing (the P846 over-void
 *     fix; the old roster hook voided at dispatch regardless).
 * The verdict asserts both sides on every leg - not a tolerance band.
 * Each CARDS id also carries its obtainability class (live vs
 * retired: dep flag / _removedCards), so the headline number can't
 * count retired content as live coverage. */
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
const _ftc=window.famTableChanged;let ftcN=0;
window.famTableChanged=function(){ftcN++;return _ftc.apply(this,arguments);};
const gz=()=>(window._pkGhosts||[]).filter(g=>g.isConnected).length;
/* a leg that busts hands the seat to the rival - keep their turn fast */
setInterval(()=>{try{if(typeof G!=='undefined'&&G&&(G.phase==='opp'||G._oppTurnActive))G._ffMult=0.05;}catch(e){}},150);
const Q=[];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
window._ftDiag=null;
const freshTurn=async q=>{
  let ok=false;
  for(let a=0;a<5&&!ok;a++){
    /* leave the match screen first - a relaunch on top of a live match
       screen is the measured stall; the seat hub is the clean door */
    if(a>0){try{showScreen('gauntlet');}catch(e){}await sleep(700);}
    try{delete S.pendingMatch;}catch(e){}
    try{if(S.run&&S.run.night){S.run.night.seatsPlayed[0]=false;S.run.night.results[0]=null;}}catch(e){}
    window._fkDiscardOk=true;
    try{launchSeat(0);}catch(e){}
    ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle'
      &&(G.pool||[]).length===0&&(G.pTurns||0)===0,9000);
    if(!ok)await sleep(1200);
  }
  if(!ok){
    try{window._ftDiag={phase:typeof G!=='undefined'&&G?G.phase:null,
      pool:typeof G!=='undefined'&&G?(G.pool||[]).length:null,
      pTurns:typeof G!=='undefined'&&G?G.pTurns:null,
      gold:S.run&&S.run.gold,hearts:S.run&&S.run.hearts,
      seats:S.run&&S.run.night&&JSON.stringify(S.run.night.seatsPlayed),
      screens:[...document.querySelectorAll('[id^=screen-]')].filter(e=>getComputedStyle(e).display!=='none').map(e=>e.id),
      modal:(document.querySelector('.gbx-box')||{}).textContent||null};}catch(e){window._ftDiag={diagErr:String(e)};}
    return false;}
  await sleep(2000);
  if(q){Q.length=0;q.forEach(v=>Q.push(v));
    /* the roll tap can be EATEN right after a relaunch (the standing
       trap) - re-tap; handleRoll's phase gate makes extras no-ops */
    let rolled=false;
    for(let r=0;r<3&&!rolled;r++){
      tap(document.getElementById('btnRoll'));
      rolled=await until(()=>G.phase==='choosing',6000);
    }
    if(!rolled)return false;
    await sleep(450);}
  return true;};
const armStar=async()=>{
  const sg={id:'stargazer',fam:'starstone',kind:'active',tier:3,charges:3,state:{}};
  G.pF=[sg];CFX.stargazer.use(sg,'p');await sleep(200);
  return gz()>0&&!!G._famPeekVals;};
const R={};
/* record: mutated legs need hookFired+void; refunded legs need intact */
const record=(id,pre,expectMutation,extra)=>{
  const fired=ftcN>pre,ghosts=gz(),peek=!!G._famPeekVals;
  R[id]=Object.assign({hookFired:fired,ghostsAfter:ghosts,peekAfter:peek,
    expectMutation,
    pass:expectMutation?(fired&&ghosts===0&&!peek):(!fired&&ghosts>0&&peek)},extra||{});};

/* ── FAM layer ── */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const sc={id:'sacrifice',fam:'obsidian',kind:'active',tier:2,charges:3,state:{}};
  G.pF.push(sc);const pre=ftcN;CFX.sacrifice.use(sc,'p');await sleep(1200);
  record('fam:sacrifice',pre,true);}
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const kg={id:'powder_keg',fam:'flint',kind:'active',tier:2,charges:3,state:{}};
  G.pF.push(kg);const pre=ftcN;CFX.powder_keg.use(kg,'p');await sleep(800);
  record('fam:powder_keg',pre,true);}
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const en={id:'encore',fam:'flint',kind:'active',tier:2,charges:3,state:{}};
  G.pF.push(en);const pre=ftcN;CFX.encore.use(en,'p');await sleep(800);
  record('fam:encore',pre,true);}
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const st={id:'steady_hand',fam:'iron',kind:'active',tier:2,charges:3,state:{}};
  G.pF.push(st);CFX.steady_hand.use(st,'p');await sleep(200);
  const d=(G.pool||[]).find(x=>!x.committed);const pre=ftcN;
  if(d&&d.el&&d.el.onclick)d.el.onclick();
  await sleep(400);record('fam:steady_hand_tap',pre,true);}
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const tm={id:'transmute',fam:'jade',kind:'active',tier:2,charges:3,state:{}};
  G.pF.push(tm);CFX.transmute.use(tm,'p');await sleep(200);
  const d=(G.pool||[]).find(x=>!x.committed);
  if(d&&d.el&&d.el.onclick)d.el.onclick();
  await sleep(200);const pre=ftcN;_transPick(3);await sleep(300);
  record('fam:transmute_pick',pre,true);}
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const pre=ftcN;
  const lane=(G.pool||[]).find(d=>!d.committed).lane;
  try{_removeDieAt(lane);}catch(e){R._rdErr=String(e);}
  await sleep(300);record('fam:_removeDieAt',pre,true);}

/* quicksilver - the enchant no card list could cover (P846) */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const d=(G.pool||[]).find(x=>!x.committed);
  d.ench={t:'quicksilver'};
  const pre=ftcN;famQuicksilver();await sleep(400);
  record('ench:quicksilver',pre,true);}

/* seven_dice - ARM: dispatch paints rings, the TAP mutates (P845b) */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  G.activeCardState=G.activeCardState||{usedCards:{}};
  G.activeCardState.usedCards['seven_dice']=1;G.oCards=[];
  const gate7=canActivateCard('seven_dice');
  activateCard('seven_dice');await sleep(250);
  const rings7=document.querySelectorAll('#playerDiceRow .break-target').length;
  const d7=(G.pool||[]).find(x=>!x.committed);const pre=ftcN;
  if(d7&&d7.el&&d7.el.onclick)d7.el.onclick();
  await sleep(400);
  record('card:seven_dice_tap',pre,true,{gate7,rings7,armSurvivedDispatch:rings7>0,obtain:'live'});}

/* gamblers_eye - LIVE. P848: the roll falls through to the MAIN path,
   so the void moment is the ENTRY (P847's guard) - pre is captured
   before activateCard. The reroll itself is a real roll now (seams,
   physics, deadRoll all inherited - apv_ge_edges drives those). */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  G.activeCardState=G.activeCardState||{usedCards:{}};
  G.activeCardState.usedCards['gamblers_eye']=1;G.oCards=[];
  const gateGE=canActivateCard('gamblers_eye');
  const pre=ftcN;
  activateCard('gamblers_eye');await sleep(300);
  const inMode=G.phase==='gamblers_eye';
  /* hold the two 1s, reroll the rest through the real roll */
  const ones=(G.pool||[]).filter(d=>!d.committed&&d.val===1).slice(0,2);
  ones.forEach(d=>tap(d.el));await sleep(300);
  tap(document.getElementById('btnRoll'));
  await until(()=>G.phase==='choosing',15000);await sleep(700);
  record('card:gamblers_eye',pre,true,{gateGE,inMode,
    frozenHolds:(G.pool||[]).filter(d=>d._frozen).length,obtain:'live'});}

/* flask REFUND - the over-void fix: a no-op card must NOT eat the
   promise. All free dice forced scoring (1s/5s) -> flask refunds. */
if(await freshTurn([1,1,5,1,5,5])&&await armStar()){
  G.activeCardState=G.activeCardState||{usedCards:{}};
  G.activeCardState.usedCards['grogs_flask']=1;G.oCards=[];
  const pre=ftcN;activateCard('grogs_flask');await sleep(700);
  record('card:grogs_flask_REFUND',pre,false,{obtain:'live'});}

/* ── CARDS layer through the real dispatch, obtainability labeled ──
   live: drafted or boss-reward, reachable in a current run.
   retired: dep:true; five also stripped from old saves by
   _removedCards, old_bones survives old saves. Driven anyway - old
   content in an old save must still void honestly. */
const MUTATORS=[
  ['grogs_flask','live'],['finnicks_palm','live'],['vanishing_act','live'],
  ['frozen_die','live'],['double_down','live'],['coin_flip','live'],
  ['the_nudge','live'],['alchemists_chisel','live'],['twinning_charm','live'],
  ['old_bones','retired-save-reachable'],
  ['brutus_fist','retired'],['ambrose_grace','retired'],['wild_die','retired'],
  ['alchemist_touch','retired'],['double_down_die','retired']];
const SELECT_FIRST=['frozen_die','coin_flip','the_nudge','twinning_charm',
  'double_down_die','alchemist_touch','vanishing_act','alchemists_chisel'];
/* wild_die is NOT selection-prepped: its handler targets UNSELECTED
   non-scoring dice and mutates behind a face-picker tap (second stage) */
for(const [id,obtain] of MUTATORS){
  const cd=(typeof CARDS!=='undefined'?CARDS:[]).find(c=>c.id===id);
  const timing=cd?cd.timing:'?';
  const atChoosing=String(timing).split('|').includes('choosing');
  if(!await freshTurn(atChoosing?[1,1,5,2,3,4]:null)){R['card:'+id]={err:'no turn',obtain};continue;}
  let armed=false;
  if(atChoosing)armed=await armStar();
  G.activeCardState=G.activeCardState||{usedCards:{}};
  G.activeCardState.usedCards[id]=1;
  G.oCards=[];
  if(atChoosing&&SELECT_FIRST.includes(id)){
    const d=(G.pool||[]).find(x=>!x.committed&&x.val!==1&&x.val!==5)||(G.pool||[]).find(x=>!x.committed);
    if(d)tap(d.el);await sleep(250);
    if(id==='twinning_charm'){const d2=(G.pool||[]).find(x=>!x.committed&&!x.sel);
      if(d2)tap(d2.el);await sleep(250);}
    if(id==='alchemists_chisel'){/* needs two selected, DIFFERENT mats -
      seat-0 loadouts can be uniform, so force a silver second die */
      const first=(G.pool||[]).find(x=>x.sel);
      let d2=(G.pool||[]).find(x=>!x.committed&&!x.sel&&first&&x.mat!==first.mat);
      if(!d2){d2=(G.pool||[]).find(x=>!x.committed&&!x.sel);
        if(d2){d2.mat='silver';try{if(G.matchDice&&d2.lane<G.matchDice.length)G.matchDice[d2.lane]='silver';}catch(e){}}}
      if(d2)tap(d2.el);await sleep(250);}}
  if(id==='double_down'){
    const one=(G.pool||[]).find(d=>!d.committed&&d.val===1);
    if(one)tap(one.el);await sleep(300);
    Q.push(5,2,3,4,6);
    let rolled2=false;
    for(let r=0;r<3&&!rolled2;r++){
      tap(document.getElementById('btnRoll'));
      rolled2=await until(()=>G.phase==='choosing',6000);}
    await sleep(400);
    armed=await armStar();}
  const gate=canActivateCard(id);
  const pre=ftcN;let aErr=null;
  try{activateCard(id);}catch(e){aErr=String(e);}
  if(id==='wild_die'){/* second stage: the face picker holds the mutation */
    await sleep(300);tap(document.querySelector('.wdp-btn'));}
  await sleep(id==='finnicks_palm'?1200:(id==='double_down'?1500:500));
  record('card:'+id,pre,true,{timing,gate,armed,aErr,obtain});
}
/* ── verdict: BOTH sides asserted on EVERY leg ── */
const legs=Object.keys(R).filter(k=>k.includes(':'));
const failed=legs.filter(k=>R[k].err||!R[k].pass);
const live=legs.filter(k=>!R[k].obtain||R[k].obtain==='live');
const retired=legs.filter(k=>R[k].obtain&&R[k].obtain!=='live');
return {R,firstStallDiag:window._ftDiag,
  summary:{legs:legs.length,liveLegs:live.length,retiredLegs:retired.length,
  failed:failed.map(k=>({leg:k,detail:R[k]}))},
  verdict:legs.length>=25&&failed.length===0};
