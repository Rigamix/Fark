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
    /* P920: THE BUST IS COUNTED WHERE IT HAPPENS, and endPTurn is the control.
       The old count inferred a bust from a scoreless `choosing` phase, which a
       farkle never produces - the game runs doBust and hands over, so the wait
       below timed out and the turn went uncounted. Measured: 1, 2 and 0 real
       busts across three matches, all three reported as zero.
       endPTurn is wrapped BESIDE it and is not decoration. Every player turn
       ends there, bank or bust, so its count must equal pTurns; without that a
       zero from the bust wrap cannot be told apart from a wrap sitting off the
       path the game calls, which is exactly how the first zero survived three
       matches. A bust count is only readable when bustHookOnPath is true. */
    let bustsInferred = 0, endPTurnsSeen = 0, bustJustFired = false;
    /* P921: ONE ENTRY PER COMPLETED TURN, IN ORDER - points banked, or 0 for a
       bust. bankAmounts holds the banked turns in order and the busts used to be
       appended as zeros at the END, so a busted turn 2 and a busted turn 9 were
       indistinguishable and "resample turn i from turn i's own bag" was not
       computable. That matters because the exchangeability check on a reach
       resample has to separate two failure modes with OPPOSITE signs -
       heterogeneity by position makes the resample run hot, coupling across
       positions makes the observed run hot - and a single ratio cannot, because
       both can be present and cancel.
       RECORDED AT endPTurn, NOT AT doBust: amber eats a bust and the turn
       CONTINUES, so a zero pushed at every doBust would invent a turn that never
       ended. doBust spends _bustImmuneTurn on entry, so the wrap has to read the
       flag BEFORE delegating - that is the only moment at which "will this bust
       actually end the turn" can be answered. */
    const turnSeq = [];
    const _origBust = window.doBust, _origEndPT = window.endPTurn;
    const bustHooked = typeof _origBust === 'function' && typeof _origEndPT === 'function';
    if (bustHooked) {
      window.doBust = function () {
        busts++; bustJustFired = true;
        return _origBust.apply(this, arguments);
      };
      window.endPTurn = function () {
        endPTurnsSeen++;
        /* P921b: THE GAME'S OWN NUMBER, read at the game's own moment. endPTurn's
           first statement is `var _pTurnPts=(G.turnPts||0)` under a comment that
           says "A bust is a turn worth ZERO, not no turn - it happened and it
           produced a value", and that records the measurement: of TEN endPTurn
           call sites, seven clear turnPts first - the five bust paths plus
           steal_low_bank and block_low_bank - and the normal bank routes via
           handleYield, which never touches turnPts.
           The harness modelled two of those ten. Reconstructing the value from
           bank taps and bust events would have recorded 0 for amber's `!_amOK`
           bank-out, where the bust is eaten and the player banks anyway without
           the driver ever tapping bank. Reading the field covers every path by
           construction instead of by enumeration. */
        try { turnSeq.push(G ? (G.turnPts || 0) : 0); } catch (e) { turnSeq.push(0); }
        return _origEndPT.apply(this, arguments);
      };
    }
    const unhook = function () {
      if (!bustHooked) return;
      window.doBust = _origBust; window.endPTurn = _origEndPT;
    };
    /* P914: EVERY BANK AMOUNT, because the envelope question is per TURN and
       not per match. TURN_CAP_PATRON is 8 and TURN_CAP_BOSS is 10, and the
       comment at 12715 is load-bearing: "bank AND bust both count", so the
       resource is eight ATTEMPTS. A match total divided by banks would miss
       the busted turns entirely and overstate the yield. */
    const bankAmounts = [];

    while (!G._endMatchFired) {
      if (Date.now() > deadline) { stalled = 'deadline at phase=' + G.phase; break; }
      if (G.phase === 'idle' && !G._oppTurnActive) {
        tap(document.getElementById('btnRoll')); rolls++; await sleep(260);
      }
      /* P920: A BUSTED TURN ENDS THIS WAIT. It used to run the full twelve
         seconds and return null, because a farkle never reaches a choosing
         phase - twelve seconds of nothing per bust, which over a ladder is
         hours. The wrap knows the moment it happens. */
      bustJustFired = false;
      const got = await until(() => G._endMatchFired || bustJustFired ||
        (G.phase === 'choosing' &&
         (G.pool || []).some(d => !d.committed && d.el && d.el.onclick)), 12000);
      if (G._endMatchFired) break;
      if (bustJustFired) {
        /* let the handover land before the loop looks for the next roll */
        const turnWas = G.turnNum;
        await until(() => G._endMatchFired || G.turnNum !== turnWas ||
                          G.phase === 'idle', 12000);
        continue;
      }
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
        /* P920: THE OLD INFERENCE, KEPT AND RENAMED. It is not the bust count
           any more - the event is - but a disagreement between the two is the
           signature of the UI shape changing under the harness, which is worth
           seeing rather than silently repairing. */
        bustsInferred++;
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

      if (doBank) { banks++; bankAmounts.push(turn); }
      tap(document.getElementById(doBank ? 'btnBank' : 'btnRoll'));
      await sleep(230);
    }

    /* P912: LET THE END-ROUTE LAND BEFORE ANYONE STARTS ANOTHER MATCH.
       launchBossMatch calls showScreen('match', ...) inside a setTimeout of
       80ms, so a caller that launches the instant _endMatchFired goes true is
       racing the navigation the finished match is about to do - and the loser
       is the new match, which is exactly the screen-gauntlet-with-G-null the
       boss path kept returning.
       Waits for the ACTIVE SCREEN TO STOP CHANGING rather than for a duration:
       two consecutive reads the same, with a bounded give-up so a game that
       never settles costs one match and not the run. */
    const screensNow = () => {
      try { return [].slice.call(document.querySelectorAll('.screen.active'))
        .map(function (e) { return e.id; }).join(','); } catch (e) { return '?'; }
    };
    /* MEASURED, and the first version of this waited for the wrong thing. It
       stopped as soon as two consecutive reads matched - but immediately after
       _endMatchFired the screen is still screen-match and momentarily STABLE,
       so it returned in 358ms, the caller launched, and the end-route then
       navigated to the gauntlet on top of the new match. Stability is not the
       signal; DEPARTURE is. Wait for the match screen to go, then for whatever
       replaces it to hold still. */
    let prevScreens = null, settleMs = null, leftMatch = false;
    const settleT0 = Date.now();
    while (Date.now() - settleT0 < 12000) {
      const now = screensNow();
      if (!leftMatch) {
        if (now.indexOf('screen-match') < 0) { leftMatch = true; prevScreens = now; }
      } else if (now === prevScreens) { settleMs = Date.now() - settleT0; break; }
      else prevScreens = now;
      await sleep(300);
    }

    unhook();
    const pPts = (G && G.pPts) || 0, oPts = (G && G.oPts) || 0;
    /* read once - four fields below compare against it and a re-read between
       them would let them disagree about the same match */
    const _pT = (function () { try { return G ? (G.pTurns || 0) : null; }
                               catch (e) { return null; } })();
    return {
      settledOn: prevScreens, settleMs, leftMatchScreen: leftMatch,
      ok: !stalled, stalled, policy: policy.key, target,
      pPts, oPts, win: pPts > oPts ? 1 : 0,
      busts, banks, rolls, keeps, bankAmounts,
      /* P920: THE CHECK THAT WAS COMPUTABLE ALL ALONG. A player turn ends in
         exactly one of a bank or a bust, so banks + busts === pTurns. Nine
         banks and nine pTurns with a bust among them is impossible, and the
         driver returned that triple three times without anyone able to see it,
         because the identity was never written down. bustsDerived comes from a
         DOM-tap counter and a game field; busts comes from a wrap on the game's
         own event. They share nothing but the game, so their agreement is
         evidence rather than an echo. */
      bustsInferred, endPTurnsSeen, bustHooked,
      /* P921: the ordered per-turn record. Its length must equal pTurns - the
         same identity P920 asserts from the other side - or a resample built on
         it is drawing from a sample with holes. */
      turnSeq, turnSeqComplete: (_pT != null) && turnSeq.length === _pT,
      turnSeqBusts: turnSeq.filter(function (x) { return x === 0; }).length,
      bustHookOnPath: bustHooked && _pT != null && endPTurnsSeen === _pT,
      bustsDerived: (_pT != null) ? _pT - banks : null,
      bustCountsAgree: (_pT != null) ? (_pT - banks) === busts : null,
      turnsAddUp: (_pT != null) ? (banks + busts) === _pT : null,
      /* pTurns, NOT turnNum. 36870: "a completed player turn (bank or bust)" -
         which is exactly what TURN_CAP counts, per its own comment at 12715.
         turnNum increments at the handover to the rival (36848) and came back
         as 10 on patron matches whose cap is 8, which is what made the first
         envelope run's per-turn arithmetic untrustworthy. */
      /* P917: WHY IT ENDED, and what added turns past the cap. The cap is soft -
         starstone grants a turn (24867/36945), the trailing player always gets
         a final answer turn, and a dead-even match takes another round. An
         envelope that does not separate those is measuring a longer match than
         it claims. _endReason is set at the cap branch itself, so it is read
         rather than inferred. */
      endReason: (function(){ try { return G ? (G._endReason || null) : null; } catch(e){ return null; } })(),
      finalAnswerUsed: (function(){ try { return G ? !!G._finalAnswerUsed : null; } catch(e){ return null; } })(),
      extraTurnsLeft: (function(){ try { return G ? (G._extraTurn || 0) : null; } catch(e){ return null; } })(),
      pTurns: _pT,
      turnNum: (function(){ try { return G ? G.turnNum : null; } catch(e){ return null; } })(),
      turnCap: (function(){ try { return G ? G.turnCap : null; } catch(e){ return null; } })(),
      hitTheCap: (function(){ try { return !!(G && G.turnCap && _pT != null && _pT >= G.turnCap); }
                              catch(e){ return null; } })(),
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
    /* A MATCH ENDS TWO WAYS, and only one of them is "somebody reached the
       target". TURN_CAP_PATRON is 8 and TURN_CAP_BOSS is 10, so a tier whose
       target sits outside the policy's envelope ends on the CAP - normally,
       every time, by arithmetic. This used to refuse those: measured, a hard
       cell match ended 6250 against 9500 and was scored a failure.
       Not widened - widening a threshold to fit a real result is how the last
       two gates went wrong. Asked instead: reached, or capped, are both
       complete. Neither being true is the only broken case. */
    const reached = res.winnerOverTarget >= 0.8 && res.winnerOverTarget <= 2.5;
    if (!reached && !res.hitTheCap)
      return {ok: false, why: 'the match ended without reaching the target (' +
        Math.max(res.pPts, res.oPts) + ' against ' + res.target +
        ') and without hitting the turn cap' +
        (res.pTurns != null ? ' (player turn ' + res.pTurns + ' of ' +
          res.turnCap + ')' : '') + ' - so it ended for neither legitimate reason'};
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

  /* THE OUTCOME CHECK, on the axis the score gate cannot see - and A PAIR, for
     the same reason the per-match score floor was thrown out. An absolute band
     on one tier is that shape again: 2 of 10 is both a limping driver and a
     genuinely hard cell, so its lower edge can refuse a real finding, and a
     brutal band-2 boss cell is exactly what the ladder exists to discover.
     Two tiers, and the win rate must not RISE. Say that precisely, because
     the loose version is worse than useless: what the code below tests is
     `hw >= ew` refused, which is "the outcome did not rise, and the easy cell
     cleared the floor" - NOT "the outcome falls". At ten matches a cell, two
     wins against zero is a difference of two events with heavily overlapping
     intervals, and a flat driver produces that pairing routinely.
     SO A PASS IS NOT EVIDENCE ABOUT DIFFICULTY, and nobody should later cite a
     2-then-0 as if it were. Same scope note as the other pair: this catches a
     driver that does not play, not one that plays slightly wrong. A smoke
     test, not calibration. */
  const WIN_N = 10;
  function sanityWinRate(easy, hard) {
    const clean = a => (a || []).filter(r => r && !r.err && !r.stalled);
    const e = clean(easy), h = clean(hard);
    if (e.length < WIN_N || h.length < WIN_N) return {ok: false,
      why: 'need ' + WIN_N + ' completed matches in each cell; got ' + e.length +
           ' easy and ' + h.length + ' hard. A win rate over fewer is not this ' +
           'check'};
    const ew = e.filter(r => r.win).length, hw = h.filter(r => r.win).length;
    /* THE FLOOR ON THE EASY TIER IS ONE, and one is the most it can honestly
       be. One win proves the driver can win. Zero is indistinguishable from
       broken - and at zero wins everywhere, "the driver does not play" and "the
       game is several times harder than the design target" become the same
       observation, which no gate can separate. A floor of two or three would
       refuse exactly the finding the ladder exists to produce, which is the
       trap the absolute band fell into one level up. So: easy 1 / hard 0
       PASSES, deliberately. */
    if (ew === 0) return {ok: false, easyWins: ew, hardWins: hw,
      why: 'zero wins in ' + e.length + ' at the EASY tier. A driver that never ' +
           'wins where it should is not playing - the run this replaces went 0 ' +
           'from 8 while scoring a quarter of the target'};
    if (ew === e.length && hw === h.length) return {ok: false, easyWins: ew,
      hardWins: hw, why: 'won every match at both tiers, which is not a game'};
    /* and the tell: a working player wins LESS as the match gets harder */
    if (hw >= ew) return {ok: false, easyWins: ew, hardWins: hw,
      why: ew + ' wins at the easy tier and ' + hw + ' at the hard one - the ' +
           'outcome did not fall. Flat against difficulty is the same defect as ' +
           'flat against target, and a ladder on top of it would be measuring ' +
           'something other than difficulty. Fix the driver, not the gate.'};
    return {ok: true, easyWins: ew, hardWins: hw, n: e.length};
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
          TARGET_SPREAD, TOTAL_SPREAD, WIN_N, RELOAD_PER_MATCH};
})();
