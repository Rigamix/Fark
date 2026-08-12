/* CAN THE PLAYER DRAG THE CARD THEY ACTUALLY HOLD?
 * SUITE: exclude
 *
 * The card is taken through the draft's own famApplyPick - NOT by seeding a
 * loadout array - because seeding is exactly how P615's verification proved a
 * gesture on cards the player never has. If this probe supplies the input, it
 * cannot tell you the game supplies it.
 *
 * ?tap=1 is the control: 4px of travel, under the threshold, must NOT play the
 * card. If a twitch plays it, the drag arm is only measuring that any pointer
 * sequence fires.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!vis(el)) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
for(let a=0;a<3;a++){ tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if(await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }
if (typeof launchSeat !== 'function') return { skip: 'launchSeat unreachable' };

/* an ACTIVE card with a use handler, chosen the way the draft would */
_getS();
const playable = FAM_CARDS.filter(c => c.kind === 'active' && CFX[c.id] && CFX[c.id].use);
if (!playable.length) return { err: 'no active family card with a use handler' };
famApplyPick({ id: playable[0].id, tier: 1 });

try { G = null; } catch (e) {}
launchSeat(0);
if (!await until(() => typeof G !== 'undefined' && G && G.pF && G.pF.length, 14000))
  return { err: 'match never started or hand empty' };
await sleep(2400);
{ let last=null, stable=0;
  for (let i=0;i<60 && stable<3;i++){ const c=document.querySelector('#famRowP .fcv');
    const r=c?Math.round(c.getBoundingClientRect().top):null;
    stable=(r!==null&&r===last)?stable+1:0; last=r; await sleep(80); } }

const card = document.querySelector('#famRowP .fcv');
if (!card) return { err: 'no family card rendered' };
const r0 = card.getBoundingClientRect();
const from = { x: r0.left + r0.width/2, y: r0.top + r0.height/2 };
const TAP = /(?:\?|&)tap=1/.test(location.search);
const lift = TAP ? 4 : Math.max(120, (r0.top + r0.height/2) - _famThresholdY() + 40);
const to = { x: from.x, y: from.y - lift };

/* CHARGES ARE THE WRONG SIGNAL for a card that needs a target. famUse only
   decrements when fx.use() returns truthy, and a card like Transmute returns
   falsy because it is now WAITING for the player to tap a die - which is the
   card working, not failing. So the direct question is asked instead: was the
   card's own use handler reached at all. */
let useCalls = 0;
{ const id = card.dataset.cid, fx = CFX[id];
  if (fx && fx.use) { const real = fx.use.bind(fx);
    fx.use = function(){ useCalls++; return real.apply(this, arguments); }; } }

/* AND famUse ITSELF, because fx.use sitting at zero has two meanings: the
   drag never reached famUse, or famUse reached its own guards and refused.
   Those are opposite verdicts on this patch - the second is the GAME working
   (Transmute needs a rolled die and there is none before the first roll), the
   first is the gesture still broken. Counting both tells them apart. */
let famUseCalls = 0, famUseArg = null;
{ const realFamUse = famUse;
  window.famUse = function(i){ famUseCalls++; famUseArg = i; return realFamUse.apply(this, arguments); }; }

const out = { arm: TAP ? 'tap-control' : 'drag',
  cardId: card.dataset.cid, boundHandler: !!card._famDrag,
  chargesBefore: G.pF[0].charges,
  thresholdY: +_famThresholdY().toFixed(1),
  cardCentreY: +(r0.top + r0.height/2).toFixed(1),
  topmostAtCentre: (() => { const el = document.elementFromPoint(from.x, from.y);
    return el ? el.tagName.toLowerCase() + (el.className && typeof el.className==='string'
      ? '.' + el.className.split(' ')[0] : '') : null; })() };

function touch(type,x,y){ const t=new Touch({identifier:1,target:card,clientX:x,clientY:y});
  return new TouchEvent(type,{bubbles:true,cancelable:true,
    touches:type==='touchend'?[]:[t],targetTouches:type==='touchend'?[]:[t],changedTouches:[t]}); }

card.dispatchEvent(touch('touchstart', from.x, from.y));
await sleep(40);
for (let i=1;i<=8;i++){ document.dispatchEvent(touch('touchmove', from.x, from.y + (to.y-from.y)*i/8)); await sleep(30); }
out.draggingClass = card.classList.contains('fcv-drag');
out.armedClass = card.classList.contains('armed');
const rMid = card.getBoundingClientRect();
out.liftedCentreY = +(rMid.top + rMid.height/2).toFixed(1);
document.dispatchEvent(touch('touchend', to.x, to.y));
await sleep(900);

out.chargesAfter = (G.pF && G.pF[0]) ? G.pF[0].charges : null;
out.useHandlerCalls = useCalls;
out.famUseCalls = famUseCalls; out.famUseArg = famUseArg;
out.canUseNow = (() => { try { const inst=G.pF[0], fx=CFX[inst.id];
  return fx && fx.canUse ? !!fx.canUse(inst) : 'no canUse guard'; } catch(e){ return 'threw'; } })();
out.played = useCalls > 0;
out.chargeSpent = out.chargesAfter !== out.chargesBefore;
out.control = { handlerBound: out.boundHandler, cardWasTopmost: /fcv|img/.test(out.topmostAtCentre||''),
                tapMustNotPlay: TAP ? (useCalls === 0) : 'n/a' };
return out;
