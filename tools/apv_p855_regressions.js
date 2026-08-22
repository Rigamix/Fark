/* P855: a leg per regression, plus the Short Fuse ruling on BOTH seats.
 * A — THE LEAK, driven as the exact failure: sacrifice on one turn ->
 *     bust into a save (which banks half and clears the shared pot) ->
 *     a clean winning bank on a later turn must NOT be refused.
 * B — pickpocket reads ONE number: the record, the fallback and the
 *     rival-turn site all resolve to .15, no literal left.
 * C — short_fuse tiers: gate 3/2/2, multiplier 2/2/3, burn absolute,
 *     read from the card's own data on the PLAYER seat...
 * D — ...and on the RIVAL seat, where ev.me is their instance. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof FAM_CARDS!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
const R={};

/* ── B: one number, three readers ── */
const ppRec=(_tellById('pickpocket')||{}).chance;
const srcAll=document.documentElement.outerHTML;
R.pickpocket={record:ppRec,
  literalSurvives:/Math\.random\(\)<0\.3&&left>1/.test(srcAll),
  descSays15:/15% chance I palm/.test(srcAll)};

/* ── C/D: short_fuse data + both-seat tier reads ── */
const sf=FAM_CARDS.find(c=>c.id==='short_fuse');
R.shortFuseData={p:sf&&sf.p,lit:sf&&sf.lit,
  texts:(sf&&sf.text||[]).map(t=>/SECOND|TRIPLE|third/.test(t))};
/* drive CFX.short_fuse.commit directly per tier per owner - ev.me is
   the acting seat's instance, which is the whole question */
const drive=(tier,owner,rc)=>{
  let mul=1;
  const ev={mine:true,owner,me:{tier,state:{}},mul:m=>{mul=m;},add:()=>{}};
  if(owner==='p')G.turnRollCount=rc; else G._oRollNum=rc;
  try{CFX.short_fuse.commit(ev);}catch(e){return {err:String(e)};}
  return {mul,lit:!!ev.me.state.lit};
};

/* ── A: the leak, as the real sequence ── */
let ok=false;
for(let a=0;a<5&&!ok;a++){
  if(a>0){try{showScreen('gauntlet');}catch(e){}await sleep(700);}
  try{delete S.pendingMatch;}catch(e){}
  try{if(S.run&&S.run.night){S.run.night.seatsPlayed=S.run.night.roster.map(()=>false);
    S.run.night.results=S.run.night.roster.map(()=>null);}}catch(e){}
  window._fkDiscardOk=true;
  try{launchSeat(0);}catch(e){}
  ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle'&&(G.pool||[]).length===0,9000);
  if(!ok)await sleep(1200);
}
if(!ok)return {R,err:'no match'};
await sleep(2200);
/* tier reads, now that G exists */
R.shortFuse={
  p_t1_roll2:drive(1,'p',2), p_t1_roll3:drive(1,'p',3),
  p_t2_roll2:drive(2,'p',2), p_t3_roll2:drive(3,'p',2),
  o_t1_roll2:drive(1,'o',2), o_t2_roll2:drive(2,'o',2), o_t3_roll2:drive(3,'o',2)};
const roll=async q=>{const Q=q.slice();const realE=window._enchRollM;
  window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
  let r0=false;
  for(let r=0;r<3&&!r0;r++){tap(document.getElementById('btnRoll'));r0=await until(()=>G.phase==='choosing'||G.phase==='opp'||G._endMatchFired,9000);}
  return r0;};
/* turn A: sacrifice, then FORCE a bust with a save armed */
if(!await roll([1,5,2,3,4,6]))return {R,err:'no roll'};
await sleep(500);
const sc={id:'sacrifice',fam:'obsidian',kind:'active',tier:1,charges:3,state:{}};
G.pF=[sc];
CFX.sacrifice.use(sc,'p');
await sleep(1300);
R.leak={sacPotArmed:G._sacPot||0};
/* arm Thick Skin's save so the bust banks half and clears the pot */
G.activeCardState=G.activeCardState||{usedCards:{}};
G.activeCardState.stitchActive=true;/* Mabel's Stitch save path */
const potBefore=G._turnBonusPot||0;
/* force a dead table -> bust */
(G.pool||[]).filter(d=>!d.committed).forEach(d=>{d.val=2;try{reDrawDieFace(d);}catch(e){}});
await roll([2,3,4,6,2,3]);
await sleep(2500);
R.leak.sacPotAfterBustSave=G._sacPot||0;
R.leak.potAfterBustSave=G._turnBonusPot||0;
R.leak.potBefore=potBefore;
/* now a CLEAN winning bank on a later turn must be allowed */
const iv=setInterval(()=>{try{if(G&&(G.phase==='opp'||G._oppTurnActive))G._ffMult=0.05;}catch(e){}},120);
await until(()=>G.phase==='idle'&&!G._oppTurnActive,45000);
await sleep(800);
if(!G._endMatchFired){
  G.pPts=(G.target||2800)-300;try{updHUD();}catch(e){}
  if(await roll([1,1,1,2,3,4])){
    await sleep(500);
    const ones=(G.pool||[]).filter(d=>!d.committed&&d.val===1).slice(0,3);
    for(const d of ones){tap(d.el);await sleep(120);}
    await sleep(300);
    tap(document.getElementById('btnBank'));
    await until(()=>G._endMatchFired,20000);
    await sleep(1200);
  }
}
clearInterval(iv);
R.leak.cleanWinAllowed=!!G._endMatchFired;
R.leak.finalPhase=G.phase;
return {R,verdicts:{
  pickpocketOneNumber:R.pickpocket.record===0.15&&!R.pickpocket.literalSurvives,
  fuseDataPresent:JSON.stringify(R.shortFuseData.p)==='[2,2,3]'&&JSON.stringify(R.shortFuseData.lit)==='[3,2,2]',
  fuseTierIGate3:R.shortFuse.p_t1_roll2.mul===1&&R.shortFuse.p_t1_roll3.mul===2,
  fuseTierIIGate2:R.shortFuse.p_t2_roll2.mul===2,
  fuseTierIIITriple:R.shortFuse.p_t3_roll2.mul===3,
  fuseRivalSeatScales:R.shortFuse.o_t1_roll2.mul===1&&R.shortFuse.o_t2_roll2.mul===2&&R.shortFuse.o_t3_roll2.mul===3,
  sacPotClearedByBustSave:R.leak.sacPotAfterBustSave===0,
  staleTallyDoesNotRefuseAWin:R.leak.cleanWinAllowed},
  verdict:R.pickpocket.record===0.15&&!R.pickpocket.literalSurvives
    &&R.shortFuse.p_t1_roll2.mul===1&&R.shortFuse.p_t2_roll2.mul===2&&R.shortFuse.p_t3_roll2.mul===3
    &&R.shortFuse.o_t2_roll2.mul===2&&R.shortFuse.o_t3_roll2.mul===3
    &&R.leak.sacPotAfterBustSave===0&&R.leak.cleanWinAllowed};
