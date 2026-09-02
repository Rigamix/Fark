/* THE DRIVER — one player, three requirements, built once.
 *
 * WHY IT REPLACES THE LADDER'S OWN LOOP. That loop used `carl`, an archetype
 * from agents2.js, against constants derived from _runBalanceSim's three
 * threshold policies. The number it produced would have been precise, confident
 * and about a different quantity. It also stalled four times in twelve at
 * phase=choosing, and scored ~2000 whatever the tier's target was.
 *
 * REQUIREMENT 1 — THE RIGHT POLICIES, AND NOT A SECOND COPY OF THEM. Both
 * halves are EXTRACTED from _runBalanceSim's own source and eval'd: the POLICIES
 * literal, and playerTurn's bank function body. A driver that restates a rule
 * the model owns is two quantities sharing a name, which is the defect this
 * project has found five times. If extraction fails it REFUSES to run.
 *
 * REQUIREMENT 2 — THE SAME KEEP. The sim's comment is explicit: "The player
 * side keeps its policy-driven maximal keep", which is `r.used` from
 * scoreRoll(vals,[],0,{},mats) - every scoring die, scored bare with no cards.
 * scoreRoll is a live function, so the driver calls it rather than reproducing
 * it, and taps exactly the dice its mask names.
 *
 * REQUIREMENT 3 — THE TARGET CHECK, INSIDE THE DRIVER. A working player's total
 * scales with the match it is in: a higher target means a longer match means
 * more banked. The broken run scored ~2000 at tier 0 and ~2000 at tier 7, and
 * that was visible in its FIRST ROW. So the first completed match is measured
 * against its own target and the driver refuses to continue below the floor -
 * before six hours are spent, not after.
 *
 * AND THE STALLS. Four in twelve sat at phase=choosing until a 240s guard.
 * `legalKeeps` returning nothing is not something to wait out: it means the
 * roll scored zero, which is a BUST. The driver detects it from scoreRoll
 * directly, waits for the turn to advance rather than for the guard, and counts
 * it - a busted turn is part of the game, not a failure of the harness.
 */
window.FDRV = (function () {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  async function until(fn, ms) {
    const t0 = Date.now();
    let threw = 0, tries = 0, last = null;
    while (Date.now() - t0 < ms) {
      tries++;
      try { if (fn()) { until.lastError = null; return Date.now() - t0; } }
      catch (e) { threw++; last = (e && e.message) || String(e); }
      await sleep(80);
    }
    until.lastError = (tries && threw === tries)
      ? 'the predicate threw on all ' + tries + ' attempts: ' + last : null;
    return null;
  }
  const tap = el => {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    const o = {bubbles: true, cancelable: true,
               clientX: r.left + r.width / 2, clientY: r.top + r.height / 2};
    el.dispatchEvent(new PointerEvent('pointerdown', o));
    el.dispatchEvent(new PointerEvent('pointerup', o));
    el.dispatchEvent(new MouseEvent('click', o));
    return true;
  };

  /* ── the rules, taken from the model ───────────────────────────── */
  let POLICIES = null, bankRule = null, extractWhy = null;
  try {
    const src = _runBalanceSim.toString();
    const pm = src.match(/var POLICIES=cfg\.policies\|\|(\[[\s\S]*?\]);/);
    if (!pm) throw new Error('could not find the POLICIES literal');
    POLICIES = (0, eval)('(' + pm[1] + ')');
    /* playerTurn's bankFn, body and all - the three-clause rule PWIN was
       derived against, not a paraphrase of it */
    const bm = src.match(
      /function playerTurn\(gear,policy,[^)]*\)\{[\s\S]*?function\(turn,diceLeft\)\{([\s\S]*?)\},myTotal/);
    if (!bm) throw new Error('could not find playerTurn\'s bank function');
    bankRule = (0, eval)('(function(policy,turn,diceLeft){' + bm[1] + '})');
  } catch (e) { extractWhy = e.message; }

  const policyByKey = k => (POLICIES || []).filter(p => p.key === k)[0] || null;
  const targetOf = () => {
    try { return (G && (G.target || (G.rung && G.rung.target))) || 1500; }
    catch (e) { return 1500; }
  };

  /* ── one match ─────────────────────────────────────────────────── */
  async function playMatch(opt) {
    opt = opt || {};
    if (extractWhy) return {err: 'REFUSING TO RUN - ' + extractWhy};
    const policy = (typeof opt.policy === 'object' && opt.policy)
      || policyByKey(opt.policy || 'bank500');
    if (!policy) return {err: 'no policy ' + opt.policy};
    const deadline = Date.now() + (opt.timeoutMs || 240000);

    /* PLAY A MATCH SOMEBODY ELSE STARTED. The launch and the play are separate
       jobs, and a caller measuring how the GAME gets from one match to the next
       needs the second without the first. */
    if (opt.alreadyStarted) {
      const live = await until(() => { try { return typeof G !== 'undefined' && G &&
        G.phase === 'idle' && !G._endMatchFired; } catch (e) { return false; } }, 15000);
      if (live == null) return {err: 'alreadyStarted, but no live match'};
    } else {
    /* start it. A FRESH RUN EVERY TIME, which is what the game does at 11273.
       Without it the third match never launched - bank300 won, bank500 lost,
       and losing a boss match ends the run, so `hot` had nothing to play. And
       independence is the property a ladder is made of: matches that inherit
       each other's run are not samples of the same thing. */
    try { if (typeof _freshRun === 'function') S.run = _freshRun(); } catch (e) {}
    try { delete S.pendingMatch; } catch (e) {}
    window._fkDiscardOk = true;
    if (opt.tier != null) S.run.tier = opt.tier;
    if (opt.dice) S.run.dice = opt.dice.slice();
    S.run._bossSeen = {drunkard:1, peasant:1, commoner:1, merchant:1,
                       soldier:1, knight:1, noble:1, bishop:1};
    /* A FRESH NIGHT FOR BOTH SEATS, measured. After the first match the run
       carries a night whose roster is a consumed set of PATRON seats, and
       launchBossMatch has no boss in it - so it shows the gauntlet and leaves
       G null, which is what "match never started" was. _freshRun() alone did
       not cover this: it makes a run, and the run makes a patron night.
       Nulling the night is also what makes matches independent, which is the
       property a ladder is made of. */
    try { S.run.night = null; } catch (e) {}
    if (opt.seat === 'patron') { try { launchPatronMatch(); } catch (e) {} }
    else { try { launchBossMatch(); } catch (e) {} }
    const started = await until(() => typeof G !== 'undefined' && G &&
      G.phase === 'idle' && !G._endMatchFired && (G.pTurns || 0) === 0, 20000);
    if (started == null) {
      /* REPORT WHAT IT SAW. "never started" cost a diagnostic run before it
         gave up the screen it was actually sitting on. */
      let phase = null; try { phase = (typeof G !== 'undefined' && G) ? G.phase : null; }
      catch (e) { phase = 'G unreadable: ' + ((e && e.message) || e); }
      return {err: 'match never started', predicate: until.lastError, phase: phase,
              gIsNull: (function(){ try { return typeof G === 'undefined' || !G; }
                                    catch(e){ return 'threw'; } })(),
              activeScreens: [].slice.call(document.querySelectorAll('.screen.active'))
                .map(function(e){ return e.id; })};
    }
    }
    await sleep(300);
    try { G.pF = []; } catch (e) {}   /* bare gear: no family cards, no enchants */

    const target = targetOf();
    let busts = 0, banks = 0, rolls = 0, keeps = 0, stalled = null;

    while (!G._endMatchFired) {
      if (Date.now() > deadline) { stalled = 'deadline at phase=' + G.phase; break; }
      if (G.phase === 'idle' && !G._oppTurnActive) {
        tap(document.getElementById('btnRoll')); rolls++; await sleep(260);
      }
      const got = await until(() => G._endMatchFired ||
        (G.phase === 'choosing' &&
         (G.pool || []).some(d => !d.committed && d.el && d.el.onclick)), 12000);
      if (G._endMatchFired) break;
      if (got == null) continue;
      await sleep(110);

      const free = G.pool.filter(d => !d.committed && !d._frozen);
      if (!free.length) { await sleep(250); continue; }
      const vals = free.map(d => d.val), mats = free.map(d => d.mat);
      let r = null;
      try { r = scoreRoll(vals, [], 0, {}, mats); } catch (e) {}

      /* A ZERO IS A BUST, NOT SOMETHING TO WAIT OUT. This is where the old
         loop sat until its guard: no legal keep, so it slept and retried on a
         table that could never change. */
      if (!r || !r.total || r.total <= 0) {
        busts++;
        const turnWas = G.turnNum;
        await until(() => G._endMatchFired || G.turnNum !== turnWas ||
                          G.phase === 'idle', 12000);
        continue;
      }

      /* the sim's keep: every scoring die, by its own mask */
      const sel = [];
      for (let i = 0; i < free.length; i++) if (r.used && r.used[i]) sel.push(free[i]);
      if (!sel.length) { await sleep(250); continue; }
      for (const d of sel) { if (d.el && !d.sel) tap(d.el); await sleep(45); }
      keeps++;
      await sleep(150);

      const turn = (G.turnPts || 0) + r.total;
      const hot = sel.length >= free.length;          /* all dice scored */
      const diceLeft = hot ? 6 : (free.length - sel.length);
      const oppDone = (G.oPts || 0) >= target;        /* last licks */

      let doBank;
      if ((G.pPts || 0) + turn >= target) doBank = true;
      else if (oppDone) doBank = ((G.pPts || 0) + turn) > (G.oPts || 0);
      else if (hot && policy.pushHot && turn < 3000) doBank = false;
      else doBank = !!bankRule(policy, turn, diceLeft);

      if (doBank) banks++;
      tap(document.getElementById(doBank ? 'btnBank' : 'btnRoll'));
      await sleep(230);
    }

    const pPts = (G && G.pPts) || 0, oPts = (G && G.oPts) || 0;
    return {
      ok: !stalled, stalled, policy: policy.key, target,
      pPts, oPts, win: pPts > oPts ? 1 : 0,
      busts, banks, rolls, keeps,
      pOverTarget: target ? +(pPts / target).toFixed(3) : null,
      winnerOverTarget: target ? +(Math.max(pPts, oPts) / target).toFixed(3) : null,
    };
  }

  /* ── the gates ─────────────────────────────────────────────────── */

  /* PER MATCH: structural only. A performance bar here refuses a match the
     player simply lost - measured, bank500 scored 2900 of 7200 while the rival
     overshot to 8850, which is a result and not a broken driver. What a match
     must show is that it RAN: somebody reached the target, and the player
     banked at least once. A driver that never banks is broken; a driver that
     banks and loses is a driver. */
  function sanity(res) {
    if (!res || res.err) return {ok: false, why: (res && res.err) || 'no result'};
    if (res.stalled) return {ok: false, why: 'the match stalled: ' + res.stalled};
    if (!(res.banks > 0)) return {ok: false,
      why: 'the player banked nothing in a completed match - it is not playing'};
    if (!(res.winnerOverTarget >= 0.8 && res.winnerOverTarget <= 2.5))
      return {ok: false, why: 'nobody reached the target: winner had ' +
        Math.max(res.pPts, res.oPts) + ' against ' + res.target};
    return {ok: true, pOverTarget: res.pOverTarget};
  }

  /* THE ONE THAT PROTECTS A SIX-HOUR RUN, and it needs two matches because the
     defect is a failure to SCALE. The broken ladder scored ~2000 whatever it
     was asked for: 3400 against a 3800 target (a respectable 89%) and 3550
     against 12500. A floor on one match passes the first and would have to be
     set so high it refuses honest losses. Two targets a factor apart, and the
     totals have to move with them. */
  /* WHAT THIS CATCHES AND WHAT IT DOES NOT, because a pass will be read as
     more than it is. 2.5x targets against 1.5x totals catches NOT PLAYING THE
     GAME - a score that is flat against the match it is in. It does not catch
     playing it slightly wrong: a driver scaling at 1.6x passes here while being
     meaningfully off. At n=2, where the variance is enormous, that is the right
     trade - but a pass is a smoke test, NOT CALIBRATION, and nothing downstream
     should treat it as evidence that the driver plays well. It is evidence that
     the driver plays. */
  const TARGET_SPREAD = 2.5, TOTAL_SPREAD = 1.5;
  function sanityScale(lowRes, highRes) {
    const a = sanity(lowRes), b = sanity(highRes);
    if (!a.ok) return {ok: false, why: 'low-tier match: ' + a.why};
    if (!b.ok) return {ok: false, why: 'high-tier match: ' + b.why};
    const tRatio = highRes.target / lowRes.target;
    if (tRatio < TARGET_SPREAD) return {ok: false,
      why: 'the two tiers are only ' + tRatio.toFixed(2) + 'x apart in target; ' +
           'pick tiers at least ' + TARGET_SPREAD + 'x apart or this proves nothing'};
    const pRatio = lowRes.pPts ? (highRes.pPts / lowRes.pPts) : 0;
    if (pRatio < TOTAL_SPREAD) return {ok: false,
      why: 'the player scored ' + lowRes.pPts + ' against a target of ' +
           lowRes.target + ' and ' + highRes.pPts + ' against ' + highRes.target +
           ' - the target moved ' + tRatio.toFixed(1) + 'x and the total moved ' +
           pRatio.toFixed(2) + 'x. A player whose score does not scale with the ' +
           'match is not playing it, and a ladder on top of this would be ' +
           'precise and about a different quantity. Fix the driver, not the gate.'};
    return {ok: true, targetRatio: +tRatio.toFixed(2), totalRatio: +pRatio.toFixed(2)};
  }

  /* THE OUTCOME CHECK, on the axis the pair test cannot see. Scoring that
     scales correctly and winning 0% or 100% are both broken, and the score
     gate would pass either. Ten matches at one tier before six hours are
     committed; two to eight wins. That band is deliberately wide - this is a
     smoke test for a broken driver, not a measurement of difficulty, and a
     narrow one would refuse real results. The original run's 0 from 8 fails it
     immediately, with no argument about luck required. */
  const WIN_MIN = 2, WIN_MAX = 8, WIN_N = 10;
  function sanityWinRate(results) {
    const done = (results || []).filter(r => r && !r.err && !r.stalled);
    if (done.length < WIN_N) return {ok: false,
      why: 'only ' + done.length + ' of ' + WIN_N + ' matches completed; a win ' +
           'rate over fewer is not the check this is'};
    const wins = done.filter(r => r.win).length;
    if (wins < WIN_MIN || wins > WIN_MAX) return {ok: false, wins, n: done.length,
      why: wins + ' wins in ' + done.length + '. Anything outside ' + WIN_MIN +
           '-' + WIN_MAX + ' at one tier is a driver that is not playing, not a ' +
           'difficulty finding - the run this replaces went 0 from 8 while ' +
           'scoring a quarter of the target. Fix the driver, not the band.'};
    return {ok: true, wins, n: done.length};
  }

  /* ONE MATCH PER PAGE, and the runner enforces it rather than this file.
     Independence is the property a ladder is made of, and a reloaded page gives
     it by construction instead of by argument about what state was carried. The
     cost is a boot per match - about ten seconds against a seventy-second match
     - and one thing it hides: whether the GAME can run consecutive matches.
     That is left open rather than closed. launchSeat(seatIdx) at 45740 is the
     gauntlet's own entry and S.run.night.seatsPlayed says which remain; two
     attempts to reach it by tapping DOM found no .seat-row at all, which is a
     fact about my selector or my timing and not yet about the game. */
  const RELOAD_PER_MATCH = true;

  return {POLICIES, bankRule, policyByKey, playMatch, sanity, sanityScale,
          sanityWinRate, targetOf, extractWhy, until, sleep, tap,
          TARGET_SPREAD, TOTAL_SPREAD, WIN_MIN, WIN_MAX, WIN_N,
          RELOAD_PER_MATCH};
})();
