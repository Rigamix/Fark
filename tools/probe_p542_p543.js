/* P542 and P543, each with the control that could fail.

   P542. The bug was canUse saying yes where use() said no. So the check is not
   "does it refuse" - it is "do the two AGREE", in both directions. A fix that
   simply made canUse always false would silence the dead button and break the
   card, and would pass any test that only looked at the silent states.

   P543. The bug was the tap flourish scoring a die the engine scores as 0. The
   control is a selection holding an icon die ALONGSIDE real scoring dice: that
   must still flourish. A fix that suppressed the flourish whenever an icon is
   present would close the bug and break every mixed keep. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(!CFX||!CFX.fair_trade)return{error:'fair_trade missing'};
if(typeof CFX.fair_trade._pick!=='function')return{error:'P542 not applied - no _pick'};

_getS(); S.run=S.run||{}; S.run.tier=2; S.run.gold=400;
S.run.dice=['bone','bone','bone','bone','bone','bone'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);

/* the P542 arm rewrites G.matchDice to construct states, so stash the real
   board and put it back before rolling - the first run of this probe left a
   three-seat board behind and the roll never produced a pool, which reads as
   a broken probe rather than a broken fix. */
const _realDice=(G.matchDice||[]).slice(), _realNum=G.numDice, _realDead=(G._ftDead||[]).slice();
/* ---- P542: the gate and the action must agree, state by state ---------- */
const ft=[];
function tryState(name,seats,stash,dead){
  G._fairTrade=null; G.phase='idle'; G.turnRollCount=0;
  G.matchDice=seats.slice(); G._ftDead=(dead||[]).slice();
  S.run.diceInv=stash.slice();
  const gate=!!CFX.fair_trade.canUse({});
  const before=G.matchDice.join(',');
  const acted=!!CFX.fair_trade.use({});
  ft.push({name,gate,acted,agree:gate===acted,changed:G.matchDice.join(',')!==before});
}
tryState('empty stash',            ['bone','bone','bone'], []);
tryState('relic in stash (cost 0)',['bone','bone','bone'], ['grogs_tooth']);
tryState('lucky in stash (cost 0)',['bone','bone','bone'], ['lucky']);
tryState('spare bone in stash',    ['bone','bone','bone'], ['bone']);
tryState('seats silver, stash iron',['silver','silver','silver'], ['iron']);
tryState('exact tie iron/iron',    ['iron','iron','iron'], ['iron']);
tryState('iron over bone (works)', ['bone','bone','bone'], ['iron']);
tryState('jade2 over bone (works)',['bone','bone','bone'], ['jade2']);
tryState('only stash die is dead', ['bone','bone','bone'], ['iron'], ['iron']);
const disagree=ft.filter(r=>!r.agree);
const stillWorks=ft.filter(r=>r.name.indexOf('(works)')>=0);

/* ---- P543: the flourish must follow the preview ------------------------ */
G._fairTrade=null; G.matchDice=_realDice.slice(); G.numDice=_realNum;
G._ftDead=_realDead.slice(); S.run.diceInv=[];
try{startPTurn();}catch(e){}
await sleep(300);
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=4,8000)))return{error:'no pool'};
await sleep(600);

function tapScore(sel){
  /* the exact expression the patched toggleDie now evaluates */
  const rest=_splitIcons(sel).rest;
  const ctx=_pCrowsForScore()||{}; ctx._bookendsEligible=_bookendsEligible(sel);
  return rest.length?scoreSelection(rest.map(x=>x.val),effectiveCards(),
    G.kept.reduce((a,k)=>a+k.pts,0),ctx,rest.map(x=>x.mat),
    rest.map(x=>x.ench||null)):0;
}
function rawScore(sel){
  const ctx=_pCrowsForScore()||{}; ctx._bookendsEligible=_bookendsEligible(sel);
  return scoreSelection(sel.map(x=>x.val),effectiveCards(),
    G.kept.reduce((a,k)=>a+k.pts,0),ctx,sel.map(x=>x.mat));
}
const one=G.pool[0], five=G.pool[1];
one.val=1; five.val=5; one.committed=false; five.committed=false;
one.ench={t:'tithe',face:1};                 /* an icon die showing a 1 */
five.ench=null;
const brandedAlone={raw:rawScore([one]), tap:tapScore([one])};
const mixed={raw:rawScore([one,five]), tap:tapScore([one,five])};
one.ench=null;
const plainOne={raw:rawScore([one]), tap:tapScore([one])};

return {
  P542:{rows:ft, disagreements:disagree.map(r=>r.name),
        stillWorks:stillWorks.map(r=>({n:r.name,acted:r.acted,changed:r.changed}))},
  P543:{brandedAlone, mixed, plainOne},
  verdict:
    disagree.length ? 'FAIL - gate and action still disagree on: '+disagree.map(r=>r.name).join('; ')
    : stillWorks.some(r=>!r.acted||!r.changed) ? 'FAIL - a trade that used to work no longer fires'
    : brandedAlone.raw<=0 ? 'INCONCLUSIVE - the branded 1 did not score under the OLD maths, so there was nothing to suppress'
    : brandedAlone.tap!==0 ? 'FAIL - the branded 1 still flourishes ('+brandedAlone.tap+')'
    : mixed.tap<=0 ? 'FAIL - a mixed keep lost its flourish, which is the control case'
    : plainOne.tap<=0 ? 'FAIL - an ordinary 1 lost its flourish'
    : 'PASS - gate and action agree on all '+ft.length+' states, working trades still fire, the branded 1 no longer flourishes ('
      +brandedAlone.raw+' -> 0) and a mixed keep still does ('+mixed.tap+')'
};
