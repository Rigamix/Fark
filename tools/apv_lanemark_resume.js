/* P947 CROSSES THE SAVE, SO THE PROBE CROSSES THE SAVE.
 *
 * Denis's rule, earned by P945: its 9/9 probe verified arming and refusal and
 * never entered runOppTurn, which is exactly where the re-key had left a
 * ReferenceError that killed every rival turn. A probe has to cross the same
 * span the patch does. P947 spans arm -> snapshot -> resume -> FIRE, so this
 * drives all four rather than reading S.pendingMatch and calling it done.
 *
 * THE CONTROL THAT MATTERS. "The mark is back after a resume" passes on a
 * version that restores it with its ORIGINAL turn stamp - and that version is
 * strictly worse than dropping the mark, because oppTurnCount restarts at 0 so
 * the mark never comes due, is never swept, and holds its lane against
 * _lmArm's refusal for the rest of the match. Presence is therefore not the
 * test. The tests are: it comes DUE, it FIRES, and its lane can be re-armed
 * afterwards.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};
const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const _ff = setInterval(() => {
  try { if (typeof G !== 'undefined' && G) G._ffMult = 0.05; } catch (e) {}
}, 150);

/* ── 1. ARM, on a turn count that is deliberately NOT zero, so a restore
       that keeps the original stamp is distinguishable from one that
       rebases. With oppTurnCount 0 both produce turn:1 and the probe
       could not tell the fix from the bug. ─────────────────────────── */
try { G._laneMark = {}; G.oppTurnCount = 4; } catch (e) {}
const armed = _lmArm('_snuff', 2, 1);
out.arm = {armed, stampedTurn: (_lmMap()[2] || {}).turn, oppTurnCount: G.oppTurnCount};

/* ── 2. SNAPSHOT through the game's own writer ────────────────────── */
try { saveMatchState(); } catch (e) { out.saveErr = e.message; }
const snap = (S && S.pendingMatch) || null;
/* A DEEP COPY, TAKEN NOW. Reading the live object at the end of the run is how
   the aliasing defect first showed - the snapshot's mark had been mutated by
   play - but it is also a probe that cannot tell "saved wrong" from "saved
   right then corrupted". Both are recorded separately. */
const snapAtSave = snap && snap._laneMark
  ? JSON.parse(JSON.stringify(snap._laneMark)) : null;
out.snapshot = {
  exists: !!snap,
  carriesLaneMark: !!(snap && snap._laneMark),
  markAtSaveTime: snapAtSave ? snapAtSave[2] : null,
};

/* ── 3. RESUME through the game's own path ────────────────────────── */
const prevG = (typeof G !== 'undefined') ? G : null;
try { window._fkDiscardOk = false; resumeMatch(); } catch (e) { out.resumeErr = e.message; }
const live = await FXH.until(() => typeof G !== 'undefined' && G && G !== prevG &&
  G.phase === 'idle' && !G._endMatchFired, 30000);
out.resumedMs = live;
if (live == null) return Object.assign(out, {err: 'the resume never came up',
                                             predicate: FXH.until.lastError});

const back = _lmMap()[2] || null;
out.afterResume = {
  present: !!(back && back.live), type: back && back.t, lane: back && back.lane,
  turn: back && back.turn, turnsLeft: back && back.turns,
  oppTurnCount: G.oppTurnCount,
  /* THE WHOLE POINT: due-ness is turn === oppTurnCount, so a mark restored
     with its old stamp of 5 against a restarted count of 0 is inert */
  wouldComeDueNextRivalTurn: !!(back && back.turn === (G.oppTurnCount || 0) + 1),
  rawStampWouldHaveBeen: out.arm.stampedTurn,
};

/* ── 4. AND IT FIRES. The span's far end. ─────────────────────────── */
const r = await FXH.rollAndSettle();
out.roll = {ok: r.ok, why: r.why};
try {
  ((G && G.pool) || []).filter(d => !d.committed).forEach(d => {
    if ((d.val === 1 || d.val === 5) && d.el) FXH.tap(d.el);
  });
} catch (e) {}
try { endPTurn(); } catch (e) {}
const dealt = await FXH.until(() => (G.oppDice || []).length > 0 &&
  (document.getElementById('oppDiceRow') || {children: []}).children.length > 0, 120000);
out.dealtMs = dealt;
out.fired = dealt == null ? null : {
  seats: (G.oppDice || []).map(d => (d && d.lane !== undefined) ? d.lane : null),
  published: ((G._oSnuffLanes) || []).slice(),
  markStillLive: !!((_lmMap()[2] || {}).live),
};
/* a spent mark frees its spot - the other half of the rebase being right */
out.laneReArms = out.fired ? _lmArm('_fog', 2, 1) : null;
/* re-read the SAME snapshot object the resume was handed, after a mark has
   fired against it */
out.snapshotAfterPlay = (snap && snap._laneMark) ? snap._laneMark[2] : null;
try { clearInterval(_ff); } catch (e) {}

out.VERDICT = {
  theMarkArmed: out.arm.armed === true && out.arm.stampedTurn === 5,
  theSnapshotCarriesIt: out.snapshot.carriesLaneMark === true &&
    !!(out.snapshot.markAtSaveTime && out.snapshot.markAtSaveTime.t === '_snuff'),
  /* THE SNAPSHOT WAS SAVED IN ITS LIVE STATE, not already spent */
  theSnapshotIsTheArmedMark: !!(out.snapshot.markAtSaveTime &&
    out.snapshot.markAtSaveTime.live === true &&
    out.snapshot.markAtSaveTime.turn === 5),
  /* AND PLAY DID NOT WRITE BACK INTO IT. The restore must copy, not alias:
     the first version handed S.pendingMatch's own object to G, so _lmSpend
     mutated the save when the mark fired. */
  theRestoreDidNotAliasTheSave: out.snapshotAfterPlay
    ? (out.snapshotAfterPlay.live === true && out.snapshotAfterPlay.turn === 5)
    : null,
  theResumeCameUp: live != null,
  theMarkSurvives: out.afterResume.present === true &&
                   out.afterResume.type === '_snuff' && out.afterResume.lane === 2,
  /* PRESENCE IS NOT THE TEST - a plain carry passes that and is worse than
     dropping the mark. The stamp must have been rebased. */
  theStampWasRebased: out.afterResume.wouldComeDueNextRivalTurn === true &&
                      out.afterResume.turn !== out.arm.stampedTurn,
  /* THE FAR END OF THE SPAN */
  reachedTheRivalTurn: dealt != null,
  itActuallyFired: !!(out.fired && out.fired.published.indexOf(2) >= 0),
  theSnuffedSeatIsGone: !!(out.fired && out.fired.seats.indexOf(2) < 0),
  theLaneIsFreeAfterwards: out.laneReArms === true,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
