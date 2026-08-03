/* PRESERVE — does the die actually arrive?
 *
 * Before P434 this spent its charge, printed "THE AMBER CRACKS — A 1 ALREADY
 * KEPT", and delivered nothing: the restore ran four lines UPSTREAM of
 * startPTurn's reset, so `G.kept=[]` and `G.numDice=matchDice.length` wiped it
 * before the turn began. The player was told it worked.
 *
 * Three things are asserted, because the clobber was hiding the other two:
 *   THE DIE ARRIVES      — G.kept holds it when the turn starts.
 *   IT KEEPS ITS MATERIAL — the old consumer hardcoded mat:'bone', so a
 *                           preserved amber or jade die was silently downgraded
 *                           and the family trait the player paid for vanished.
 *   THE COST IS REAL     — numDice is one BELOW the loadout, not a hardcoded 5.
 *                           A player already down a die to Break would have got
 *                           five back and paid nothing.
 *
 * Driven through the real consumer on a live match rather than by calling the
 * card: what broke was startPTurn's ordering, and only startPTurn can show it. */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = { bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2 };
  el.dispatchEvent(new PointerEvent('pointerdown', o)); el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o)); return true; };

const out = { notes: [] };

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
const _atMatch = await until(() => vis(document.getElementById('screen-match')), 9000);
const _idle    = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 14000);

/* THE PRECONDITION HAS TO HOLD, AND UNTIL() RETURNS FALSE RATHER THAN THROWING.
   Ignoring that return value made this probe flap: standalone it passes every
   time, inside the full suite it intermittently reported dieArrived,
   materialKept, pointsCarried and playerCanSeeIt all false - which reads as
   "Preserve is broken" and is not what happened.
   The tell was the one check that still PASSED. stashConsumed true means
   G._famPreserve really was set and really was consumed; the die was placed and
   then something wiped G.kept afterwards. That is the signature of startPTurn
   being called here while the match was still initialising, so init's own turn
   start ran second and cleared the tray - a race the probe creates, not a fault
   in the feature.
   So: if the match is not idle, DECLINE. "I could not run" is a different fact
   from "the game is wrong", and a probe that reports the second when it means
   the first is worse than no probe - it spends someone's afternoon. */
if (!_atMatch || !_idle || typeof G === 'undefined' || !G) {
  return { skip: 'setup did not reach an idle match (atMatch=' + _atMatch
                 + ' idle=' + _idle + ' phase=' + (typeof G !== 'undefined' && G ? G.phase : 'no G')
                 + ') - not a Preserve result either way' };
}

out.loadoutSize = (G.matchDice || []).length;

/* AMBER ON PURPOSE, not bone. Bone would pass a consumer that still hardcoded
   the material, which is exactly the fault being tested. */
G._famPreserve = { val: 1, mat: 'amber', pts: 100, crack: 0 };
out.stashed = JSON.parse(JSON.stringify(G._famPreserve));

startPTurn();
await sleep(200);

out.keptAfter  = JSON.parse(JSON.stringify(G.kept || []));
out.numDice    = G.numDice;
out.turnPts    = G.turnPts;
out.stashAfter = G._famPreserve;

/* DATA IS NOT PIXELS. G.kept holding the entry is not the player seeing it -
   the same gap as every other check today. Give the tray a beat to paint, then
   look at what actually rendered. */
await sleep(1200);
/* #keptTray is the 2D FALLBACK. refreshKeptTray returns early when the page
   carries .fk3d, and #keptRow under the 3D layer is the live surface. Checking
   the tray on a 3D build measures a element that is correctly empty - the same
   wrong-surface mistake as reading an authored rule instead of the CSSOM. */
out.is3D = document.documentElement.classList.contains('fk3d');
const tray = document.getElementById(out.is3D ? 'keptRow' : 'keptTray');
out.traySurface = out.is3D ? 'keptRow (3D)' : 'keptTray (2D)';
const chips = tray ? [...tray.querySelectorAll('.die,.kept-die,img,canvas')].filter(vis) : [];
out.tray = tray ? (function(){ const r = tray.getBoundingClientRect(), cs = getComputedStyle(tray);
  return { w: Math.round(r.width), h: Math.round(r.height), display: cs.display,
           opacity: cs.opacity, text: (tray.textContent || '').trim().slice(0, 40) }; })() : null;
out.trayChips = chips.length;
out.trayVisible = !!(out.tray && out.tray.display !== 'none' && +out.tray.opacity > 0.05
                     && out.tray.w > 1 && out.tray.h > 1);

/* Does it appear once the turn is actually played? The tray may legitimately
   be hidden at phase 'idle' and paint on the first roll - that is a different
   fact from "never shown", and calling it a bug without checking would be the
   same jump-to-conclusion this session keeps catching. */
let rolled = false;
for (let a2 = 0; a2 < 3 && !rolled; a2++) {
  const rb = [...document.querySelectorAll('button,div')]
    .filter(e => vis(e) && /^ROLL$/i.test((e.textContent || '').trim()))[0];
  if (rb) tap(rb);
  rolled = await until(() => [...document.querySelectorAll('.die')].filter(vis).length >= 3, 12000);
  if (!rolled) await sleep(1000);
}
await sleep(2200);
out.afterRoll = (function(){ const t = document.getElementById(out.is3D ? 'keptRow' : 'keptTray');
  if (!t) return null; const r = t.getBoundingClientRect(), cs = getComputedStyle(t);
  const c = [...t.querySelectorAll('.die,.kept-die,img,canvas')].filter(vis);
  return { w: Math.round(r.width), h: Math.round(r.height), display: cs.display,
           chips: c.length, text: (t.textContent || '').trim().slice(0, 40) }; })();
out.keptStillThere = JSON.parse(JSON.stringify(G.kept || []));

const k = (G.kept || [])[0] || null;
out.verdict = {
  dieArrived:        !!k && (k.vals || []).indexOf(1) >= 0,
  materialKept:      !!k && k.mat === 'amber',
  pointsCarried:     !!k && k.pts === 100 && G.turnPts === 100,
  costsADie:         G.numDice === Math.max(1, out.loadoutSize - 1),
  stashConsumed:     G._famPreserve === null,
  /* the half the data assertions cannot see */
  playerCanSeeIt:    out.trayVisible === true && out.trayChips > 0
};
return out;
