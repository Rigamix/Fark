/* P862 - the D18 question, re-asked in the world section 2 created.
 *
 * WHY THIS REPLACES apv_frozen_reachable's PREMISE. That probe asked whether
 * Sacrifice could destroy a frozen die, and answered "the question does not
 * arise": _frozen has two writers, both inside the legacy player-active
 * layer, and that layer was unreachable - its headline verdict is literally
 * `wholeLegacyActiveLayerIsDead: true`. Section 2 makes the layer reachable
 * again. frozen_die IS Brutus's Grip now, won from his spoils and equipped in
 * the boss slot, so a player can freeze a die for the first time and every
 * interaction that was safe only because nobody could get there is live.
 *
 * A verdict of "dead" that stops being true is worse than no verdict: it is
 * reassurance pointing at a world that has moved. So the claim is re-asked
 * against the mechanism rather than the reachability.
 *
 * THE ANSWER, read off the source before driving it, is that the filter at
 * CFX.sacrifice._targets() now carries `!d._frozen` - so the defect D18
 * described was fixed at some point after that probe was written, and the
 * fix is what is load-bearing now. This drives it.
 *
 * ON EQUIPPING DIRECTLY: acquisition is NOT faked here, it is tested
 * elsewhere - apv_boss_card_spoils walks the whole win/tile/TAKE path for all
 * eight cards. This probe is about an interaction GIVEN possession, and it
 * writes S.run.cards[0] with exactly the statement famSpoilsPick uses.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};

if(!await until(()=>typeof launchBossMatch==='function',20000))return {err:'no boot'};
_getS();window._fkDiscardOk=true;
const out={};

/* the layer is reachable at all - the premise that changed */
try{
  const grip=CARDS.filter(c=>c.id==='frozen_die')[0];
  out.card={id:grip&&grip.id,name:grip&&grip.name,npc:grip&&grip.npc,uses:grip&&grip.maxUses};
  out.layerIsReachableNow=!!(grip&&grip.npc);
}catch(e){out.cardErr=String(e);}

S.run.tier=4;S.run.gold=500;
S.run.cards=['frozen_die',null,null,null];   /* the line famSpoilsPick uses */
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match'};
await sleep(2200);

out.inHand=!!(G.pCards&&G.pCards.indexOf('frozen_die')>=0);
/* sampled at BOTH moments on purpose. frozen_die is in _GLINT_NEEDS_SELECTION,
   so the gate is legitimately shut until a die is selected - reading it once,
   early, records a `false` sitting next to a PASS and invites the next reader
   to think the gate is broken. */
out.gateBeforeAnyRoll=(typeof canActivateCard==='function')?canActivateCard('frozen_die'):null;

/* every face scores, so nothing busts mid-measurement */
const Q=[];for(let i=0;i<24;i++)Q.push(i%2?5:1);
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);

for(let i=0;i<3;i++){if(G.phase==='idle'){tap(document.getElementById('btnRoll'));break;}await sleep(400);}
await until(()=>G.phase==='choosing',12000);
await sleep(800);

/* select a die, then arm the freeze and tap it - the card's own flow */
const d0=(G.pool||[]).find(x=>!x.committed&&(x.val===1||x.val===5));
if(d0&&d0.el)tap(d0.el);
await sleep(400);
out.gateAfterSelection=(typeof canActivateCard==='function')?canActivateCard('frozen_die'):null;
try{activateCard('frozen_die');}catch(e){out.activateThrew=String(e).slice(0,90);}
await sleep(600);
const target=(G.pool||[]).find(x=>!x.committed);
if(target&&target.el)tap(target.el);
await sleep(700);

const frozen=(G.pool||[]).filter(x=>x._frozen);
out.frozenCount=frozen.length;
out.frozenLanes=frozen.map(x=>x.lane);

/* THE QUESTION */
let targets=[];
try{targets=CFX.sacrifice._targets();}catch(e){out.targetsThrew=String(e).slice(0,90);}
out.sacrificeTargets=targets.length;
out.sacrificeWouldTakeFrozen=targets.some(t=>t._frozen);
/* the control: Sacrifice can see SOMETHING, or "it would not take a frozen
   die" is true of an empty list and means nothing */
out.sacrificeCanSeeAnything=targets.length>0;

out.VERDICT={
  layerIsReachableNow: out.layerIsReachableNow===true,
  gripReachesTheHand: out.inHand===true,
  gateOpensOnceADieIsSelected: out.gateAfterSelection===true,
  freezeActuallyHappened: out.frozenCount>0,
  sacrificeCanSeeAnything: out.sacrificeCanSeeAnything===true,
  sacrificeExcludesTheFrozenDie: out.sacrificeWouldTakeFrozen===false,
};
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
return out;
