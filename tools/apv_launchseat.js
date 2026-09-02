/* Can the game run consecutive matches? launchSeat, not the DOM.
 *
 * The two earlier attempts hunted for `.seat-row` elements to tap and found
 * none at any timing, because .seat-row was dead CSS - deleted in P909. The
 * gauntlet's seats are .ptcard and their handler is
 * `sit.onclick=function(){_ptOpen=false;launchSeat(st.i);}` (21526), so
 * launchSeat(seatIdx) is not a shortcut past the player's path: it IS the
 * player's path with the click removed.
 *
 * WHAT IT DECIDES. If the game chains matches, the ladder keeps ~15 per browser
 * and stays near six hours. If it cannot, it is one boot per match and the same
 * 480 matches cost about ninety minutes more. Building the slow version to
 * avoid a question answerable in one run would be the wrong trade.
 *
 * READING launchSeat's OWN GUARDS rather than guessing at them: it returns
 * silently when the seat is already spent, when the index is out of range, and
 * defers to resumeMatch when S.pendingMatch is set unless _fkDiscardOk is true.
 * All three are handled here, and a silent return is reported as such rather
 * than as a timeout.
 *
 * A NIGHT HAS FOUR SEATS, so four consecutive matches is the whole of what one
 * night can answer. The fifth round asks the harder question - whether a NEW
 * night arrives - because eight nights in a session is what a real player does.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
eval(await (await fetch('/tools/fark_driver.js')).text());
const out = {rounds: []};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const night = () => { try { return S.run && S.run.night ? S.run.night : null; }
                      catch (e) { return null; } };
const played = () => { const n = night(); return n ? (n.seatsPlayed || []).slice() : null; };
const nextSeat = () => { const p = played(); if (!p) return -1;
                         for (let i = 0; i < p.length; i++) if (!p[i]) return i;
                         return -1; };
const gLive = () => { try { return typeof G !== 'undefined' && G &&
  G.phase === 'idle' && !G._endMatchFired && (G.pTurns || 0) === 0; }
  catch (e) { return false; } };

/* start from a clean night the game made for itself */
try { _getS(); window._fkDiscardOk = true; } catch (e) {}
try { S.run = _freshRun(); } catch (e) {}
try { S.run.night = null; } catch (e) {}
try { _ensureNight(); } catch (e) { out.ensureNightThrew = e.message; }
out.nightAtStart = {exists: !!night(),
                    seats: night() ? night().roster.length : 0,
                    played: played(), tier: night() ? night().tier : null};
if (!night()) return Object.assign(out, {err: '_ensureNight made no night'});

let nightsUsed = 1;
for (let round = 1; round <= 6; round++) {
  let idx = nextSeat();
  let newNight = false;
  if (idx < 0) {
    /* the night is spent - can the game produce another? that is the question
       a four-seat night cannot answer on its own */
    try { S.run.night = null; _ensureNight(); } catch (e) {}
    nightsUsed++;
    newNight = true;
    idx = nextSeat();
  }
  if (idx < 0) { out.rounds.push({round, err: 'no seat available and no new night'});
                 break; }

  const t0 = Date.now();
  window._fkDiscardOk = true;
  try { delete S.pendingMatch; } catch (e) {}
  let threw = null;
  try { launchSeat(idx); } catch (e) { threw = e.message; }
  const started = await FDRV.until(gLive, 20000);
  if (started == null) {
    out.rounds.push({round, seat: idx, newNight, threw,
      err: 'seat did not start',
      /* a SILENT return is not a timeout, and launchSeat has three of them */
      spentAlready: (played() || [])[idx] === true,
      gIsNull: (function(){ try { return typeof G === 'undefined' || !G; }
                            catch(e){ return 'threw'; } })(),
      screens: [].slice.call(document.querySelectorAll('.screen.active'))
        .map(e => e.id)});
    break;
  }
  const res = await FDRV.playMatch({policy: 'bank300', timeoutMs: 200000,
                                    alreadyStarted: true});
  out.rounds.push({round, seat: idx, newNight, startedMs: started,
    matchMs: Date.now() - t0,
    result: res && res.err ? {err: res.err}
      : {target: res.target, pPts: res.pPts, oPts: res.oPts, win: res.win,
         banks: res.banks, busts: res.busts, stalled: res.stalled},
    playedAfter: played()});
  if (res && res.err) break;
  await FDRV.sleep(400);
}

const good = out.rounds.filter(r => r.result && !r.result.err && !r.result.stalled);
out.summary = {
  rounds: out.rounds.length,
  completed: good.length,
  nightsUsed,
  medianMatchMs: good.length
    ? good.map(r => r.matchMs).sort((a, b) => a - b)[Math.floor(good.length / 2)]
    : null,
  firstFailure: (out.rounds.filter(r => r.err || (r.result && r.result.err))[0] || null),
};
/* what it costs either way, so the runner decision is arithmetic not taste */
out.runnerCost = {
  matchesNeeded: 480,
  chainedHours: out.summary.medianMatchMs
    ? +((480 * out.summary.medianMatchMs) / 3600000 / 2).toFixed(2) : null,
  bootPerMatchHours: out.summary.medianMatchMs
    ? +((480 * (out.summary.medianMatchMs + 11000)) / 3600000 / 2).toFixed(2) : null,
  note: 'two browsers at the shoot.js cap; boot measured at roughly 11s',
};

out.VERDICT = {
  aNightExists: !!out.nightAtStart.exists && out.nightAtStart.seats > 0,
  /* THE QUESTION: four seats of one night, back to back */
  fourConsecutiveMatches: out.summary.completed >= 4,
  /* and the harder one - eight nights in a session is what a player does */
  aSecondNightArrived: out.rounds.some(r => r.newNight && r.startedMs != null),
  nothingStalled: !out.rounds.some(r => r.result && r.result.stalled),
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
