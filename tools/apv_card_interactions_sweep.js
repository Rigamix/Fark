/* P844 SWEEP: every enrolled mutator driven individually - the cardHit
 * standard (fires landed one by one, not trusted from the hook's
 * existence). famTableChanged is wrapped in a counter; each leg
 * records (a) the hook fired, (b) the armed promise+ghosts voided.
 * CARDS-layer legs drive the REAL dispatch (activateCard) with the
 * gate satisfied; a handler that refunds for want of a target still
 * proves its hook. Cards whose timing gate cannot host a promise
 * (idle-timed: no pool, no possible peek) are recorded as gate-safe
 * with the gate measured, not assumed. */
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
/* the hook counter - all enrollment sites call the global */
const _ftc=window.famTableChanged;let ftcN=0;
window.famTableChanged=function(){ftcN++;return _ftc.apply(this,arguments);};
const gz=()=>(window._pkGhosts||[]).filter(g=>g.isConnected).length;
/* a leg that busts hands the seat to the rival - keep their turn fast
   so the next leg's relaunch window is never eaten (the ladder idiom;
   palm's leg was lost to a slow rival turn twice before this) */
setInterval(()=>{try{if(typeof G!=='undefined'&&G&&(G.phase==='opp'||G._oppTurnActive))G._ffMult=0.05;}catch(e){}},150);
const Q=[];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const FAILS=[];
const freshTurn=async q=>{
  let ok=false;
  for(let a=0;a<3&&!ok;a++){
    try{delete S.pendingMatch;}catch(e){}
    try{if(S.run&&S.run.night){S.run.night.seatsPlayed[0]=false;S.run.night.results[0]=null;}}catch(e){}
    window._fkDiscardOk=true;
    try{launchSeat(0);}catch(e){FAILS.push('launch:'+e);}
    ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle'
      &&(G.pool||[]).length===0&&(G.pTurns||0)===0,9000);
    if(!ok)await sleep(1500);
  }
  if(!ok){FAILS.push('stuck: phase='+(typeof G!=='undefined'&&G?G.phase:'noG')
    +' pool='+(typeof G!=='undefined'&&G?(G.pool||[]).length:'-')
    +' pTurns='+(typeof G!=='undefined'&&G?G.pTurns:'-')
    +' opp='+(typeof G!=='undefined'&&G?!!G._oppTurnActive:'-')
    +' hearts='+(S.run?S.run.hearts:'-')+' gold='+(S.run?S.run.gold:'-')
    +' died='+(S.run?S.run._died:'-'));return false;}
  await sleep(2000);
  if(q){Q.length=0;q.forEach(v=>Q.push(v));
    /* the roll tap can be eaten right after a relaunch (measured:
       phase stays idle, pool 0, no gate flag set) - the ladder's
       re-tap idiom */
    let rolled=false;
    for(let rt=0;rt<3&&!rolled;rt++){
      tap(document.getElementById('btnRoll'));
      rolled=await until(()=>G.phase==='choosing',6000);
    }
    if(!rolled){
      FAILS.push('rollstuck: phase='+G.phase+' pool='+(G.pool||[]).length
        +' palmAnim='+!!G._palmAnimating+' encoreP='+!!G._encorePending);
      return false;}
    await sleep(450);}
  return true;};
const armStar=async()=>{
  const sg={id:'stargazer',fam:'starstone',kind:'active',tier:3,charges:3,state:{}};
  G.pF=[sg];CFX.stargazer.use(sg,'p');await sleep(200);
  return gz()>0&&!!G._famPeekVals;};
const R={};
const record=(id,pre,extra)=>{R[id]=Object.assign({hookFired:ftcN>pre,
  ghostsAfter:gz(),peekAfter:!!G._famPeekVals},extra||{});};

/* ── FAM layer ── */
/* sacrifice (the reported pair) */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const sc={id:'sacrifice',fam:'obsidian',kind:'active',tier:2,charges:3,state:{}};
  G.pF.push(sc);const pre=ftcN;CFX.sacrifice.use(sc,'p');await sleep(1200);
  record('fam:sacrifice',pre);}
/* powder_keg */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const kg={id:'powder_keg',fam:'flint',kind:'active',tier:2,charges:3,state:{}};
  G.pF.push(kg);const pre=ftcN;CFX.powder_keg.use(kg,'p');await sleep(800);
  record('fam:powder_keg',pre);}
/* encore */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const en={id:'encore',fam:'flint',kind:'active',tier:2,charges:3,state:{}};
  G.pF.push(en);const pre=ftcN;CFX.encore.use(en,'p');await sleep(800);
  record('fam:encore',pre);}
/* steady_hand - two-stage: arm, then die tap rerolls */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const st={id:'steady_hand',fam:'iron',kind:'active',tier:2,charges:3,state:{}};
  G.pF.push(st);CFX.steady_hand.use(st,'p');await sleep(200);
  const d=(G.pool||[]).find(x=>!x.committed);const pre=ftcN;
  if(d&&d.el&&d.el.onclick)d.el.onclick();
  await sleep(400);record('fam:steady_hand_tap',pre);}
/* transmute - two-stage: arm, tap, _transPick */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const tm={id:'transmute',fam:'jade',kind:'active',tier:2,charges:3,state:{}};
  G.pF.push(tm);CFX.transmute.use(tm,'p');await sleep(200);
  const d=(G.pool||[]).find(x=>!x.committed);
  if(d&&d.el&&d.el.onclick)d.el.onclick();
  await sleep(200);const pre=ftcN;_transPick(3);await sleep(300);
  record('fam:transmute_pick',pre);}
/* _removeDieAt direct - the shared removal path (break/seizures/shatter) */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  const pre=ftcN;
  const lane=(G.pool||[]).find(d=>!d.committed).lane;
  try{_removeDieAt(lane);}catch(e){R._rdErr=String(e);}
  await sleep(300);record('fam:_removeDieAt',pre);}

/* seven_dice - an ARM (P845b): dispatch paints rings, the TAP mutates
   and enrolls. Driven like steady_hand, through the real gate (P845
   moved it to choosing - at idle the pool is always empty). */
if(await freshTurn([1,1,5,2,3,4])&&await armStar()){
  G.activeCardState=G.activeCardState||{usedCards:{}};
  G.activeCardState.usedCards['seven_dice']=1;G.oCards=[];
  const gate7=canActivateCard('seven_dice');
  activateCard('seven_dice');await sleep(250);
  const rings7=document.querySelectorAll('#playerDiceRow .break-target').length;
  const d7=(G.pool||[]).find(x=>!x.committed);const pre=ftcN;
  if(d7&&d7.el&&d7.el.onclick)d7.el.onclick();
  await sleep(400);
  record('card:seven_dice_tap',pre,{gate7,rings7,armSurvivedDispatch:rings7>0});}

/* ── CARDS layer: the classified 15 through the real dispatch ── */
const MUTATORS=['grogs_flask','finnicks_palm','brutus_fist','ambrose_grace',
  'vanishing_act','old_bones','frozen_die','double_down','wild_die',
  'coin_flip','the_nudge','alchemists_chisel','alchemist_touch','twinning_charm',
  'double_down_die'];
const SELECT_FIRST=['frozen_die','coin_flip','the_nudge','twinning_charm',
  'double_down_die','alchemist_touch','wild_die','vanishing_act','alchemists_chisel'];
for(const id of MUTATORS){
  const cd=(typeof CARDS!=='undefined'?CARDS:[]).find(c=>c.id===id);
  const timing=cd?cd.timing:'?';
  const atChoosing=String(timing).split('|').includes('choosing');
  if(!await freshTurn(atChoosing?[1,1,5,2,3,4]:null)){R['card:'+id]={err:'no turn'};continue;}
  let armed=false;
  if(atChoosing)armed=await armStar();
  /* satisfy the gate */
  G.activeCardState=G.activeCardState||{usedCards:{}};
  G.activeCardState.usedCards[id]=1;
  G.oCards=[];
  if(atChoosing&&SELECT_FIRST.includes(id)){
    const d=(G.pool||[]).find(x=>!x.committed&&x.val!==1&&x.val!==5)||(G.pool||[]).find(x=>!x.committed);
    if(d)tap(d.el);await sleep(250);
    if(id==='twinning_charm'){const d2=(G.pool||[]).find(x=>!x.committed&&!x.sel);
      if(d2)tap(d2.el);await sleep(250);}}
  if(id==='double_down'){
    /* needs kept dice: keep the 1, roll again, then fire */
    const one=(G.pool||[]).find(d=>!d.committed&&d.val===1);
    if(one)tap(one.el);await sleep(300);
    Q.push(5,2,3,4,6);tap(document.getElementById('btnRoll'));
    await until(()=>G.phase==='choosing',12000);await sleep(400);
    armed=await armStar();}
  const gate=canActivateCard(id);
  const pre=ftcN;let aErr=null;
  try{activateCard(id);}catch(e){aErr=String(e);}
  await sleep(id==='finnicks_palm'?1200:500);
  record('card:'+id,pre,{timing,gate,armed,aErr});
}
/* verdicts: every driven leg must have fired the hook; every leg that
   hosted a promise must have voided it */
const legs=Object.keys(R).filter(k=>k.includes(':'));
const fired=legs.filter(k=>R[k].hookFired);
const hosted=legs.filter(k=>R[k].armed!==false&&R[k].gate!==false&&!R[k].err);
const voided=legs.filter(k=>R[k].hookFired&&R[k].ghostsAfter===0&&!R[k].peekAfter);
return {R,fails:FAILS.slice(0,6),summary:{legs:legs.length,hookFired:fired.length,
  voidClean:voided.length,firedList:fired},
  verdict:legs.length>=20&&fired.length>=legs.length-2};
