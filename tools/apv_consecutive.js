/* Can the GAME run consecutive matches, or is it my driver's sequencing?
 *
 * WHY THIS RUNS BEFORE THE RELOAD GOES IN. Reloading between matches is the
 * right answer for a ladder - independence by construction - but it makes this
 * question permanently unmeasurable through that path, and a real player plays
 * eight nights in a session. My read is that the failure is a "you did not
 * advance the night" error rather than a leak, because the diagnostic showed
 * the run HAD advanced: tier 1 to tier 2, a fresh roster, gold 500 to 100. But
 * probably is not measured.
 *
 * SO IT DRIVES THE PLAYER'S PATH, NOT MINE. After a match the game returns to
 * the gauntlet, where the next seat is CHOSEN. calling launchBossMatch() again
 * skips that, which is why it landed on screen-gauntlet with G null. This taps
 * whatever the gauntlet offers and reports what happens, five times over.
 *
 * IT CONCLUDES NOTHING IT DID NOT SEE. Every round records the screen, whether
 * G exists, what was tappable and what was tapped - so a failure says which
 * step stopped rather than that something did.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
eval(await (await fetch('/tools/fark_driver.js')).text());
const out = {rounds: []};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const seatCandidates = () => {
  const g = document.getElementById('screen-gauntlet');
  if (!g) return [];
  return [].slice.call(g.querySelectorAll(
    '.seat-row,.seat,.gauntlet-seat,[data-seat],button,.btn'))
    .filter(e => {
      const r = e.getBoundingClientRect();
      return r.width > 20 && r.height > 12 &&
             getComputedStyle(e).display !== 'none' &&
             !e.classList.contains('spent') && !e.disabled;
    });
};
const state = () => {
  let gOk = false; try { gOk = typeof G !== 'undefined' && !!G; } catch (e) {}
  return {
    screens: [].slice.call(document.querySelectorAll('.screen.active')).map(e => e.id),
    gExists: gOk,
    phase: (function(){ try { return (typeof G!=='undefined'&&G)?G.phase:null; }
                        catch(e){ return 'unreadable'; } })(),
    seats: seatCandidates().length,
    seatLabels: seatCandidates().slice(0, 6)
      .map(e => (e.className || '') + '|' + (e.textContent || '').trim().slice(0, 22)),
    night: (function(){ try { return S.run && S.run.night
      ? {seatsPlayed: S.run.night.seatsPlayed, tier: S.run.night.tier} : null; }
      catch(e){ return null; } })(),
    gold: (function(){ try { return S.run ? S.run.gold : null; } catch(e){ return null; } })(),
  };
};

/* match 1 through the driver, then the game's own path for the rest */
const first = await FDRV.playMatch({policy: 'bank300', tier: 2, seat: 'boss',
                                    timeoutMs: 150000});
out.rounds.push({n: 1, how: 'driver launch',
                 result: first && first.err ? {err: first.err}
                   : {pPts: first.pPts, oPts: first.oPts, win: first.win},
                 after: state()});

for (let n = 2; n <= 5; n++) {
  /* WAIT FOR THE GAUNTLET TO EXIST BEFORE READING IT. The first version looked
     while the game was still on screen-match at phase=opp and found nothing
     tappable - which said something about my timing, not about the game. The
     seats are .seat-row elements rendered when the screen comes up. */
  await FDRV.until(() => {
    const g = document.getElementById('screen-gauntlet');
    return g && g.classList.contains('active') &&
           g.querySelectorAll('.seat-row').length > 0;
  }, 20000);
  const before = state();
  let tapped = null, why = null;
  const seats = seatCandidates();
  if (!seats.length) { why = 'nothing tappable on the gauntlet'; }
  else {
    /* prefer something that reads like a seat over a generic button */
    const pick = seats.filter(e => /seat/i.test(e.className))[0] || seats[0];
    tapped = (pick.className || '') + '|' + (pick.textContent || '').trim().slice(0, 22);
    FDRV.tap(pick);
  }
  const started = await FDRV.until(() => {
    try { return typeof G !== 'undefined' && G && G.phase === 'idle' &&
                 !G._endMatchFired && (G.pTurns || 0) === 0; } catch (e) { return false; }
  }, 15000);
  const after = state();
  out.rounds.push({n, how: 'gauntlet tap', before, tapped, why,
                   startedMs: started, after});
  if (started == null) break;
  /* play it out with the driver's loop by calling the match body only - the
     driver's own launch is what we are avoiding here, so drive the turns by
     hand through the same helpers */
  const res = await FDRV.playMatch({policy: 'bank300', tier: 2, seat: 'boss',
                                    timeoutMs: 150000, alreadyStarted: true});
  out.rounds[out.rounds.length - 1].result = res && res.err
    ? {err: res.err} : {pPts: res.pPts, oPts: res.oPts, win: res.win};
  if (res && res.err) break;
}

out.summary = {
  rounds: out.rounds.length,
  startedViaGauntlet: out.rounds.filter(r => r.how === 'gauntlet tap' &&
                                             r.startedMs != null).length,
  attemptedViaGauntlet: out.rounds.filter(r => r.how === 'gauntlet tap').length,
};
out.VERDICT = {
  theFirstMatchRan: !out.rounds[0].result.err,
  theGauntletOffersSomething: out.rounds.length > 1 &&
    out.rounds[1].before && out.rounds[1].before.seats > 0,
  /* the finding either way - this is the number that decides whether reload is
     covering a driver problem or a game one */
  consecutiveMatchesStart: out.summary.attemptedViaGauntlet > 0 &&
    out.summary.startedViaGauntlet === out.summary.attemptedViaGauntlet,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
