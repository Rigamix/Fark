/* WHAT ARE THE ~8% OF TURNS THE DEEP PROBE THREW AWAY?
 *
 * The three deep bust-rate runs dropped 7-9% of attempted turns as "stalled" -
 * G.oTurns never ticked within 20s. That is the one systematic hole in all
 * three numbers, and it must be classified before any of them sizes a fix.
 *
 * TWO CANDIDATE MECHANISMS, opposite in effect, and I am not choosing between
 * them by reading:
 *
 *   A. MATCH-ENDING TURNS. finOpp clears _oppTurnActive and THEN hits
 *      `if(G!==_matchG||!G||G._endMatchFired)return`, which sits BEFORE the
 *      G.oTurns++. A rival turn that reaches target sets _endMatchFired, so
 *      the turn really happened but never registered. Those are HIGH-SCORING
 *      turns - dropping them removes non-busts and INFLATES the measured bust
 *      rate, meaning the real rate is even lower and the gap even wider.
 *
 *   B. GENUINE HANGS / SLOW PLAYBACK. A turn that simply outlived the 20s
 *      window. Long turns carry more rolls and so more bust exposure -
 *      dropping them DEPRESSES the measured bust rate.
 *
 * I asserted B in a summary without checking. Both widen the gap, but they are
 * different mechanisms and only one is real. This measures which.
 *
 * METHOD: run turns exactly as the deep probe does, and on every stall record
 * the state that distinguishes the two - _endMatchFired, the oPts delta (did
 * the turn actually score?), whether _oppTurnActive is still set (still
 * running vs finished-but-unregistered), and how long it took. A stalled turn
 * that scored points with _endMatchFired set is mechanism A. One still active
 * at timeout with no points is mechanism B.
 *
 * The 20s window is also widened to 45s here: if most "stalls" resolve given
 * more time, they were never stalls, and the deep numbers need re-running with
 * a longer window rather than reinterpreting.
 */
const TIER = 3;                       // CORVUS - 29 stalls of ~325 attempts
const LOADOUT = ['silver','jade','jade','bone','bone','bone'];
const PRATE = 541;
const MATCHES = 14, TURNS_PER = 12, WINDOW = 45000;

const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof launchBossMatch !== 'function') return { error: 'game globals missing' };
try { S.settings = S.settings || {}; S.settings.fastRival = true; S.settings.reducedMotion = true; } catch (e) {}

let turns = 0, busts = 0, stalls = 0, lateResolves = 0;
const stallRows = [], durations = [];

for (let m = 0; m < MATCHES; m++) {
  await until(() => typeof G === 'undefined' || !G || !G._oppTurnActive, 8000);
  await sleep(140);
  try {
    _getS();
    S.run = S.run || {};
    S.run.tier = TIER;
    S.run.dice = LOADOUT.slice();
    S.run.cards = S.run.cards || [];
    launchBossMatch();
  } catch (e) { break; }
  if (!(await until(() => typeof G !== 'undefined' && G && G.rung && G.matchOppDice, 9000))) break;
  await sleep(280);

  for (let i = 0; i < TURNS_PER; i++) {
    if (G._oppTurnActive) break;
    const t0 = (G.oTurns || 0), p0 = (G.oPts || 0), started = Date.now();
    try { runOppTurn(); } catch (e) { break; }

    /* the deep probe's window, then a longer one - the difference tells us
       whether these were stalls at all */
    let ok = await until(() => G && (G.oTurns || 0) > t0, 20000);
    let late = false;
    if (!ok) {
      ok = await until(() => G && (G.oTurns || 0) > t0, WINDOW - 20000);
      if (ok) { late = true; lateResolves++; }
    }
    const dur = Date.now() - started;

    if (!ok) {
      stalls++;
      stallRows.push({
        endMatchFired: !!(G && G._endMatchFired),
        stillActive: !!(G && G._oppTurnActive),
        ptsDelta: (G ? (G.oPts || 0) : 0) - p0,
        oTurnsMoved: (G ? (G.oTurns || 0) : 0) - t0,
        ms: dur
      });
      break;                      /* match state is unknown after a stall */
    }

    turns++;
    durations.push(dur);
    if ((G.oPts || 0) - p0 <= 0) busts++;
    if (late) stallRows.push({ lateResolve: true, ms: dur,
                               ptsDelta: (G.oPts || 0) - p0 });
    try {
      G.pPts = (G.pPts || 0) + PRATE;
      if (G._endMatchFired || G.oPts >= (G.target || 1e9) || G.pPts >= (G.target || 1e9)) break;
    } catch (e) { break; }
    await sleep(80);
  }
}

const A = stallRows.filter(r => !r.lateResolve && r.endMatchFired).length;
const B = stallRows.filter(r => !r.lateResolve && !r.endMatchFired && r.stillActive).length;
const other = stallRows.filter(r => !r.lateResolve).length - A - B;
durations.sort((a, b) => a - b);
return {
  tier: TIER, completedTurns: turns, busts: busts,
  bustRate: turns ? +(busts / turns).toFixed(4) : null,
  stalls: stalls, lateResolvesAt45s: lateResolves,
  mechanismA_matchEnded: A,
  mechanismB_stillRunning: B,
  unclassified: other,
  scoredBeforeStalling: stallRows.filter(r => !r.lateResolve && r.ptsDelta > 0).length,
  medianTurnMs: durations.length ? durations[Math.floor(durations.length / 2)] : null,
  maxTurnMs: durations.length ? durations[durations.length - 1] : null,
  stallRows: stallRows
};
