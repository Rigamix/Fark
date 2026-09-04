/* THE CONTROL, written against the OLD API so it can run on the pre-P945 build.
 *
 * apv_lane_rekey.js cannot be the control: it calls _lmMap/_lmLive/_lmDueList,
 * which do not exist before the re-key, so it dies at the first line and returns
 * nothing. A probe that cannot execute on the old build is not evidence that the
 * old build was wrong - it is evidence of nothing at all.
 *
 * This uses only what both builds have: _lmArm, and reading the keys directly.
 * On the OLD build both assertions below must FAIL; on the new one the keys are
 * gone entirely, which is itself the proof the shape changed.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};
const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

out.era = {
  hasOldKeys: ('_fog' in G) || ('_snuff' in G) || ('_snare' in G) ||
              (typeof _lmMap !== 'function'),
  hasNewMap: typeof _lmMap === 'function',
};

/* ── two fogs on two lanes ─────────────────────────────────────────── */
try { G._fog = null; G._snuff = null; G._snare = null; G._laneMark = {}; } catch (e) {}
try { G.oppTurnCount = 0; } catch (e) {}
_lmArm('_fog', 2, 1);
_lmArm('_fog', 4, 1);
out.twoFogs = {
  oldKeyLane: (G._fog && G._fog.lane !== undefined) ? G._fog.lane : null,
  /* on the old build the first fog is simply gone - one key, overwritten */
  bothSurvive: (typeof _lmLive === 'function')
    ? _lmLive('_fog').length === 2
    : false,
};

/* ── fog and snuff on ONE lane ─────────────────────────────────────── */
try { G._fog = null; G._snuff = null; G._snare = null; G._laneMark = {}; } catch (e) {}
const r1 = _lmArm('_fog', 3, 1);
const r2 = _lmArm('_snuff', 3, 1);
out.oneLane = {
  armReturnedSomething: r2 !== undefined,
  secondRefused: r2 === false,
  /* THE FORBIDDEN STATE: two live marks on one lane */
  bothLiveOnLaneThree: !!(G._fog && G._fog.live && G._fog.lane === 3 &&
                          G._snuff && G._snuff.live && G._snuff.lane === 3),
};

out.VERDICT = {
  /* on the OLD build these are the two defects, so both read TRUE there */
  theFirstFogWasOverwritten: out.twoFogs.bothSurvive === false,
  twoMarksSharedOneLane: out.oneLane.bothLiveOnLaneThree === true,
  armGaveNoRefusal: out.oneLane.armReturnedSomething === false,
};
return out;
