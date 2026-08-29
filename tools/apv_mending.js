/* P861 - THE MENDING, driven on both seats.
 *
 * The brief is explicit that a badge working in one direction only is the
 * Steeped defect, so "it works" is two claims, not one, and they are tested
 * against different machinery: the player's gate lives in setBtns/handleBank
 * and reads G.turnRollCount; the rival's lives in oppShouldBank and reads
 * G._oRollNum.
 *
 * THE CONTROL IS THE POINT OF THE RIVAL LEG. "the rival banked after 2+ rolls"
 * is worth nothing if the rival never banks after one roll anyway - that is a
 * uniform series, not a measurement. So the same decision is put to
 * oppShouldBank with the rule OFF and with it ON, on inputs chosen so the
 * off-case answers TRUE. If the control does not answer true, the leg reports
 * that it proved nothing rather than reporting a pass.
 */
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
const out={};

/* ══ LEG A: her rule, against the player ══════════════════════════════ */
S.run.tier=1;S.run.gold=500;S.run.sleeve=null;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match'};
await sleep(2000);

out.tellIsMending=!!(G._tell&&G._tell.id==='mending');
out.ruleActiveP=_ruleActive('mending','p');
out.badgeShows=(document.getElementById('mendVal')||{}).textContent;

/* every face scores, so nothing here can bust and confound the reading */
const Q=[];for(let i=0;i<40;i++)Q.push(i%2?5:1);
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);

const bankBtn=()=>document.getElementById('btnBank');
const selectOneScoring=()=>{
  const d=(G.pool||[]).find(x=>!x.committed&&!x.sel&&(x.val===1||x.val===5));
  if(d&&d.el)tap(d.el);return !!d;
};

for(let i=0;i<3;i++){if(G.phase==='idle'){tap(document.getElementById('btnRoll'));break;}await sleep(400);}
await until(()=>G.phase==='choosing',12000);
await sleep(700);
out.rollsAfterFirst=G.turnRollCount;
out.selectedA=selectOneScoring();
await sleep(400);

const gA=_mendGate();
out.afterOneRoll={
  count:gA.count,need:gA.need,blocked:gA.blocked,
  bankDisabled:bankBtn().classList.contains('disabled'),
  bankHeld:bankBtn().classList.contains('mend-held'),
  badge:(document.getElementById('mendVal')||{}).textContent,
};
/* the backstop, not just the button: call the handler the button would call */
const ptsBefore=G.pPts;
try{handleBank();}catch(e){out.bankThrewA=String(e);}
await sleep(500);
out.afterOneRoll.bankRefused=(G.pPts===ptsBefore);
out.afterOneRoll.stillPlayerTurn=(G.phase!=='opp');

/* second roll clears the floor */
for(let i=0;i<3;i++){if(G.phase==='choosing'||G.phase==='idle'){tap(document.getElementById('btnRoll'));break;}await sleep(400);}
await until(()=>G.turnRollCount>=2,12000);
await sleep(700);
out.selectedB=selectOneScoring();
await sleep(400);
const gB=_mendGate();
out.afterTwoRolls={
  count:gB.count,need:gB.need,blocked:gB.blocked,
  bankDisabled:bankBtn().classList.contains('disabled'),
  bankHeld:bankBtn().classList.contains('mend-held'),
  badge:(document.getElementById('mendVal')||{}).textContent,
};
const pts2=G.pPts;
try{handleBank();}catch(e){out.bankThrewB=String(e);}
await sleep(900);
out.afterTwoRolls.bankAccepted=(G.pPts>pts2);

/* ══ LEG B: worn by the player, against the rival ═════════════════════ */
/* oppShouldBank is asked the SAME question twice, rule off then rule on, on
   an input the off-case answers TRUE for (a bank big enough to trip the
   "3000+ : ALWAYS bank" branch). A control that answers false would make the
   on-case unfalsifiable. */
const RUNG=RUNGS.find(r=>r.key==='commoner')||RUNGS[2];
const ask=()=>oppShouldBank(RUNG,3200,4,3000,3000,20000);

G._sleeve=null;G._tell=null;G._sealRule=null;G._oRollNum=1;
out.controlBanksOnRollOne=ask();

G._sleeve='mending';G._oRollNum=1;
out.withMendingRollOne=ask();
G._oRollNum=2;
out.withMendingRollTwo=ask();
/* the escape hatch: no dice left means the rule may not demand a roll */
G._oRollNum=1;
out.withMendingNoDiceLeft=oppShouldBank(RUNG,3200,0,3000,3000,20000);

out.legBProvedSomething=(out.controlBanksOnRollOne===true);

/* ══ verdicts ════════════════════════════════════════════════════════ */
out.VERDICT={
  A_ruleIsHers:            out.tellIsMending&&out.ruleActiveP===true,
  A_heldAfterOneRoll:      out.afterOneRoll.blocked===true&&out.afterOneRoll.bankDisabled===true
                           &&out.afterOneRoll.bankHeld===true,
  A_handlerRefused:        out.afterOneRoll.bankRefused===true&&out.afterOneRoll.stillPlayerTurn===true,
  A_releasedAfterTwo:      out.afterTwoRolls.blocked===false&&out.afterTwoRolls.bankHeld===false
                           &&out.afterTwoRolls.bankAccepted===true,
  A_badgeCounts:           out.afterOneRoll.badge==='1/2'&&out.afterTwoRolls.badge==='2/2',
  B_controlIsMeaningful:   out.legBProvedSomething===true,
  B_rivalHeldOnRollOne:    out.withMendingRollOne===false,
  B_rivalFreedOnRollTwo:   out.withMendingRollTwo===true,
  B_noSoftLockWithNoDice:  out.withMendingNoDiceLeft===true,
};
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
return out;
