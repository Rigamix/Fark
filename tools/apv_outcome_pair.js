/* The last gate before six hours: ten matches at an easy tier, ten at a hard
 * one, and the win rate must fall.
 *
 * WHY A PAIR RATHER THAN A BAND. An absolute band on one tier refuses a
 * genuinely hard cell, which is exactly what the ladder exists to discover -
 * the same trap the per-match score floor fell into. Flatness is the tell.
 *
 * THE TIER KNOB IS S.run.tier, read off _ensureNight rather than guessed: it
 * rebuilds the night whenever night.tier !== S.run.tier, so setting the tier is
 * enough and nulling the night is only needed when a night's four seats are
 * spent. If the two cells came back at the same target the pair test would be
 * flat BY CONSTRUCTION and would prove nothing, so both targets are reported
 * and asserted apart.
 *
 * MATCHES ARE CHAINED VIA launchSeat, which P911 measured at six in a row over
 * two nights with no failures. Each match starts from a seat the night has not
 * spent - launchSeat enforces that itself, returning silently on a spent one -
 * so independence holds without a reload.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
eval(await (await fetch('/tools/fark_driver.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const night = () => { try { return (S.run && S.run.night) || null; } catch (e) { return null; } };
const nextSeat = () => { const n = night(); if (!n) return -1;
  const p = n.seatsPlayed || [];
  for (let i = 0; i < p.length; i++) if (!p[i]) return i;
  return -1; };
const gLive = () => { try { return typeof G !== 'undefined' && G &&
  G.phase === 'idle' && !G._endMatchFired && (G.pTurns || 0) === 0; }
  catch (e) { return false; } };

async function playCell(tier, n, policy) {
  const results = [];
  try { _getS(); window._fkDiscardOk = true; } catch (e) {}
  try { S.run = _freshRun(); S.run.tier = tier; S.run.night = null; _ensureNight(); }
  catch (e) { return {err: 'cell setup: ' + e.message, results}; }
  for (let i = 0; i < n; i++) {
    let idx = nextSeat();
    if (idx < 0) { try { S.run.night = null; _ensureNight(); } catch (e) {}
                   idx = nextSeat(); }
    if (idx < 0) { results.push({err: 'no seat and no new night'}); break; }
    window._fkDiscardOk = true;
    try { delete S.pendingMatch; } catch (e) {}
    try { launchSeat(idx); } catch (e) { results.push({err: 'launchSeat: ' + e.message}); break; }
    const started = await FDRV.until(gLive, 20000);
    if (started == null) { results.push({err: 'seat did not start', seat: idx}); break; }
    const r = await FDRV.playMatch({policy, timeoutMs: 220000, alreadyStarted: true});
    results.push(r);
    if (r && r.err) break;
    await FDRV.sleep(300);
  }
  return {results};
}

const POLICY = 'bank500';
const easy = await playCell(0, 10, POLICY);
out.easy = {tier: 0, err: easy.err || null,
            targets: easy.results.map(r => r && r.target).filter(Boolean),
            wins: easy.results.filter(r => r && r.win).length,
            completed: easy.results.filter(r => r && !r.err && !r.stalled).length,
            scores: easy.results.map(r => r && !r.err ? [r.pPts, r.oPts] : r && r.err)};
const hard = await playCell(7, 10, POLICY);
out.hard = {tier: 7, err: hard.err || null,
            targets: hard.results.map(r => r && r.target).filter(Boolean),
            wins: hard.results.filter(r => r && r.win).length,
            completed: hard.results.filter(r => r && !r.err && !r.stalled).length,
            scores: hard.results.map(r => r && !r.err ? [r.pPts, r.oPts] : r && r.err)};

const med = a => a.length ? a.slice().sort((x, y) => x - y)[Math.floor(a.length / 2)] : null;
out.targets = {easy: med(out.easy.targets), hard: med(out.hard.targets)};
out.targets.ratio = (out.targets.easy && out.targets.hard)
  ? +(out.targets.hard / out.targets.easy).toFixed(2) : null;

out.outcomeGate = FDRV.sanityWinRate(easy.results, hard.results);
/* and the score gate on the same data - one representative match a cell */
const pick = rs => rs.filter(r => r && !r.err && !r.stalled)[0] || null;
const eR = pick(easy.results), hR = pick(hard.results);
out.scoreGate = (eR && hR) ? FDRV.sanityScale(eR, hR) : {ok: false, why: 'no pair'};

out.VERDICT = {
  /* the cells have to be genuinely different, or the pair proves nothing */
  theTiersDiffer: !!out.targets.ratio && out.targets.ratio >= FDRV.TARGET_SPREAD,
  bothCellsCompleted: out.easy.completed === 10 && out.hard.completed === 10,
  nothingStalled: !easy.results.concat(hard.results).some(r => r && r.stalled),
  /* THE GATE */
  theOutcomeGatePasses: out.outcomeGate.ok === true,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
