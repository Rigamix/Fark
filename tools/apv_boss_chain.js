/* Do BOSS matches chain? The one thing P911 could not answer.
 *
 * P911 measured six consecutive matches over two nights, all of them PATRON
 * seats via launchSeat. The ladder needs boss cells too, and launchBossMatch is
 * the entry that kept returning screen-gauntlet with G null.
 *
 * THE CANDIDATE IS A RACE, read off the source rather than guessed: launchBossMatch
 * does not touch the night at all - it reads TIERS[S.run.tier].boss and calls
 * showScreen('match', ...) inside a setTimeout of 80ms. So a caller that
 * launches the instant _endMatchFired goes true is racing the navigation the
 * FINISHED match is about to do, and the loser is the new match. First launch
 * wins because nothing is behind it; the second gets overwritten. That is
 * exactly the symptom.
 *
 * SO IT IS TESTED BOTH WAYS IN ONE RUN. Three boss matches with the driver's
 * new settle - waiting for the active screen to stop changing before returning
 * - and three with it disabled. If the race is the cause, the settled arm
 * chains and the unsettled one fails on match two, which is a difference the
 * run produces rather than an argument I make.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
eval(await (await fetch('/tools/fark_driver.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const gLive = () => { try { return typeof G !== 'undefined' && G &&
  G.phase === 'idle' && !G._endMatchFired && (G.pTurns || 0) === 0; }
  catch (e) { return false; } };
const screens = () => { try { return [].slice.call(
  document.querySelectorAll('.screen.active')).map(e => e.id).join(','); }
  catch (e) { return '?'; } };

async function chain(n, settle) {
  const rows = [];
  try { _getS(); window._fkDiscardOk = true; S.run = _freshRun(); S.run.tier = 2; }
  catch (e) { return [{err: 'setup: ' + e.message}]; }
  for (let i = 0; i < n; i++) {
    window._fkDiscardOk = true;
    try { delete S.pendingMatch; } catch (e) {}
    const before = screens();
    let threw = null;
    try { launchBossMatch(); } catch (e) { threw = e.message; }
    const started = await FDRV.until(gLive, 20000);
    if (started == null) {
      rows.push({i, err: 'did not start', threw, before, after: screens(),
                 gIsNull: (function(){ try { return typeof G === 'undefined' || !G; }
                                       catch(e){ return 'threw'; } })()});
      break;
    }
    const r = await FDRV.playMatch({policy: 'bank500', timeoutMs: 200000,
                                    alreadyStarted: true});
    rows.push({i, startedMs: started, before,
               settledOn: r && r.settledOn, settleMs: r && r.settleMs,
               result: r && r.err ? {err: r.err}
                 : {target: r.target, pPts: r.pPts, oPts: r.oPts, win: r.win}});
    if (r && r.err) break;
    /* the unsettled arm launches immediately, which is the race */
    if (!settle) await FDRV.sleep(0);
  }
  return rows;
}

/* WITH the settle, which the driver now does inside playMatch */
out.settled = await chain(3, true);

/* WITHOUT it: neutralise the settle by making the screen read constant, so the
   loop exits on its first comparison and returns immediately. Same code path,
   no waiting - which isolates the wait rather than a different code path. */
const realQSA = document.querySelectorAll.bind(document);
document.querySelectorAll = function (sel) {
  if (sel === '.screen.active') return [];      /* always the same reading */
  return realQSA(sel);
};
out.unsettled = await chain(3, false);
document.querySelectorAll = realQSA;

const ok = rows => rows.filter(r => r && !r.err && r.result && !r.result.err).length;
out.summary = {settledCompleted: ok(out.settled), unsettledCompleted: ok(out.unsettled)};

out.VERDICT = {
  bossMatchesChainWithTheSettle: out.summary.settledCompleted === 3,
  /* the finding either way: if BOTH arms chain, the race was not the cause and
     the earlier failures need another explanation */
  theSettleIsWhatMadeTheDifference:
    out.summary.settledCompleted > out.summary.unsettledCompleted,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
