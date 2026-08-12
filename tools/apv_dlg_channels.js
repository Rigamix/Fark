/* WHERE DOES NPC DIALOGUE ACTUALLY LAND, AND HOW CLOSE TOGETHER?
 * SUITE: exclude   (a measurement, not an assertion — the numbers are the point)
 *
 * Denis, from play: "you have some lines (which I think are old dialogue lines)
 * appearing in the parchment box, and then the new lines appear as text the same
 * way the 'Patron is rolling' is" and "not every single action from the npc
 * needs a dialogue for it... It's fine to have silences sometimes."
 *
 * Two claims, so two measurements, and they must not share an instrument:
 *   CHANNEL  every string that reaches a player-visible text surface, tagged
 *            with WHICH surface. DLG.show writes the parchment box; setStatusMsg
 *            writes #statusMsg, the "RIVAL IS ROLLING…" line. A dialogue line in
 *            the second column is the bug.
 *   SPACING  the gap between consecutive parchment lines, and every trigger that
 *            was REFUSED and why. A system with no refusals is a system with no
 *            silences, whatever its comments say.
 *
 * WHY THE REFUSALS MATTER MORE THAN THE SHOWS. DLG.trigger already claims to
 * space lines out (prob gate + busyUntil+gap). If it does, the refusal log is
 * full and the shows are far apart, and item 6 is only the hesitation leak. If
 * the refusal log is empty, something is going around the gate — and the two
 * things that do, by construction, are triggerCard (bypasses both) and the
 * _priority whitelist (bypasses the spacing one). This tells them apart.
 *
 * CONTROL: a run must record at least one refusal AND at least one show, or the
 * wrap did not fire and the zeroes mean nothing.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };

const T0 = Date.now();
const log = [];      /* every visible string, with its surface */
const refused = [];  /* every trigger that chose silence, and why */

/* reach the gauntlet */
for (let a = 0; a < 3; a++) {
  tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break;
}
if (typeof launchSeat !== 'function') return { skip: 'launchSeat unreachable' };

/* ── the wraps. Installed BEFORE the match so MATCH_START is counted too. ── */
const realShow = DLG.show.bind(DLG);
DLG.show = function(text){ log.push({t: Date.now()-T0, ch: 'box', s: String(text).slice(0,70)}); return realShow(text); };

const realStatus = window.setStatusMsg;
window.setStatusMsg = function(m, c){
  if (m) log.push({t: Date.now()-T0, ch: 'status', s: String(m).slice(0,70)});
  return realStatus.apply(this, arguments);
};

/* trigger: record the decision, not just the outcome. Re-implements the two
   gates as READS so nothing is changed — the real trigger still makes the call. */
const asked = [];    /* every trigger, whatever came of it */
const realTrigger = DLG.trigger.bind(DLG);
DLG.trigger = function(cat){
  const now = Date.now(), before = log.length;
  const p = DLG.prob[cat] || 0.5;
  const priority = (cat==='MATCH_START'||cat==='REMATCH_START'||cat==='PLAYER_SIX_KIND'||cat==='OPP_WINS');
  const blocked = !priority && now < DLG.busyUntil + DLG.gap;
  const r = realTrigger(cat);
  asked.push(cat);
  if (log.length === before) refused.push({t: now-T0, cat, p, wouldBlock: blocked});
  else log[log.length-1].cat = cat;   /* so a shown line can be traced to its beat */
  return r;
};

/* THE SUSPECT. Before P632 this was `_dlgHesitate`, a private helper that
   called setStatusMsg and was invisible to every wrap above except as an
   unexplained line in the status column. It is now two ordinary DLG categories,
   so the trigger wrap sees it — which is itself the fix being verified.
   THE STALE-INSTRUMENT GUARD: if the old helper is still present, this probe is
   reading a build P632 never reached, and every number below is about the wrong
   file. Say so loudly rather than reporting a clean result. */
const staleBuild = (typeof window._dlgHesitate === 'function');
const HES = c => c === 'OPP_HESITATE_PUSH' || c === 'OPP_HESITATE_BANK';

const realCard = DLG.triggerCard.bind(DLG);
DLG.triggerCard = function(cid, isP){
  const now = Date.now(), before = log.length;
  const blocked = now < DLG.busyUntil + DLG.gap;   /* what trigger WOULD have said */
  const r = realCard(cid, isP);
  if (log.length > before) log[log.length-1].viaCard = true, log[log.length-1].wouldBlock = blocked;
  return r;
};

/* ── play ── */
try { G = null; } catch (e) {}
try { launchSeat(0); } catch (e) { return { err: 'launchSeat threw: ' + e }; }
if (!await until(() => typeof G !== 'undefined' && G && G.pCards !== undefined, 14000))
  return { err: 'match never started' };

/* A CRUDE AUTOPLAYER, and crude is fine: the player's SKILL is irrelevant to
   how dialogue is spaced. Ending the player turn fast is what matters, because
   the rival's turn is where the beats under test live. Bank whenever legal,
   otherwise take the first die that scores, otherwise roll.
   Selection goes through toggleDie on G.pool rather than through the DOM: the
   tap target is a hidden <i class="die-hit"> pad, and a first attempt that
   clicked the .die itself selected nothing and stalled the whole run. */
const btn = id => document.getElementById(id);
const on  = el => el && !el.classList.contains('disabled') && vis(el);
/* idle is a STUCK detector, not a turn timer. At 60 it was firing during a
   long rival turn — 14s of legitimately-nothing-to-do — and cutting the run at
   two rival turns, which is no sample at all. The deadline is the real bound. */
const DEADLINE = Date.now() + 260000;
let idle = 0, turns = 0;
while (Date.now() < DEADLINE && !(G && G._endMatchFired)) {
  await sleep(280);
  if (on(btn('btnBank'))) { tap(btn('btnBank')); turns++; idle = 0; continue; }
  if (G && G.phase === 'choosing' && G.pool) {
    let took = false;
    for (const d of G.pool.filter(x => !x.committed && !x.sel)) {
      try { toggleDie(d); } catch(e) { continue; }
      await sleep(70);
      if (on(btn('btnBank')) || on(btn('btnRoll'))) { took = true; break; }
      try { toggleDie(d); } catch(e) {}   /* that one did not score — put it back */
    }
    if (took) { idle = 0; continue; }
  }
  if (on(btn('btnRoll'))) { tap(btn('btnRoll')); idle = 0; continue; }
  if (++idle > 300) break;  /* ~84s with nothing actionable — genuinely stuck */
}

/* ── the two answers ── */
const box = log.filter(l => l.ch === 'box');
const gaps = box.slice(1).map((l, i) => l.t - box[i].t);
const statusLooksLikeDialogue = log.filter(l =>
  l.ch === 'status' && /[a-z]{3}.*[a-z]{3}/.test(l.s) && l.s !== l.s.toUpperCase());

return {
  arm: 'measure',
  ranFor: Math.round((Date.now()-T0)/1000) + 's',
  matchEnded: !!(G && G._endMatchFired),
  /* the autoplayer's own vital sign — zero banked turns means the run drove
     nothing and every number below is about an idle table, not a match */
  playerBanks: turns, oppTurns: (G && G.oTurns) || 0,

  /* CONTROL — a run with no shows or no refusals measured nothing, and a stale
     build means it measured the wrong file */
  control: { shows: box.length, refusals: refused.length,
             P632_APPLIED: !staleBuild, hesitateAsked: asked.filter(HES).length },

  /* THE BEAT UNDER TEST. asked = how often the rival's decision offered a pause;
     shown = how many actually spoke. shown should be a small fraction of asked,
     and every one of them must be in the box column. */
  hesitate: { asked: asked.filter(HES).length,
              shown: box.filter(l => HES(l.cat)).length,
              refused: refused.filter(r => HES(r.cat)).length,
              inStatusChannel: log.filter(l => l.ch === 'status' && HES(l.cat)).length },

  /* CHANNEL */
  boxLines: box.length,
  statusLines: log.filter(l => l.ch === 'status').length,
  dialogueInStatusChannel: statusLooksLikeDialogue.map(l => l.s),

  /* SPACING */
  gapsMs: gaps,
  minGapMs: gaps.length ? Math.min(...gaps) : null,
  medianGapMs: gaps.length ? gaps.slice().sort((a,b)=>a-b)[gaps.length>>1] : null,
  under3s: gaps.filter(g => g < 3000).length,
  bypassedGate: box.filter(l => l.viaCard && l.wouldBlock).map(l => l.s),
  refusedCats: refused.map(r => r.cat + (r.wouldBlock ? '(spaced)' : '(prob)')),

  timeline: log.map(l => l.t + ' ' + l.ch + (l.viaCard?'*':'') + (l.cat?' ['+l.cat+']':'') + ' | ' + l.s),
};
