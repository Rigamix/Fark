/* THE LADDER, KEYED BY GEAR BAND — the axis the constants actually consume.
 *
 * ladder_real.js reports by NIGHT. PWIN/BWIN are keyed by gear BAND, and those
 * are not the same axis: a player at night 6 sits at band 2 or band 3 depending
 * on what they bought, and which one is precisely what _runEconomySim is
 * modelling. Mapping a per-night result onto the constants would need an
 * assumption the model was supposed to supply — the same circle this work
 * spent a session climbing out of. So band is primary here and tier is
 * recorded per match as a secondary axis.
 *
 * IT MEASURES BOTH SEATS. ladder_real.js only ever calls launchBossMatch, so
 * every number it ever produced is a boss number. PWIN needs the patron seat,
 * which means a fresh night per match, since launchSeat consumes seats from a
 * roster.
 *
 * NO SECOND COPY OF THE RULE. `gearLevel` and `FAMS` are extracted from
 * _runEconomySim's own source and eval'd, not reimplemented here. A probe that
 * decides "band 2" by its own definition, while the model decides by another,
 * is two quantities sharing a name — the defect this session has found four
 * times. If extraction fails the probe REFUSES to run rather than falling back
 * to a copy, and it asserts each loadout's band before measuring it.
 *
 * THE POLICY IS IN EVERY LINE OF OUTPUT, and that is not decoration. Ruling #24
 * established that these ratios are explicitly NOT policy-invariant — the
 * silver:bone bust ratio sweeps 0.126 to 0.864 with push depth. PWIN[g] is a
 * single number per band with NO policy dimension, so whichever policy this
 * runs under is the policy those constants silently encode. Anything derived
 * from this output must carry the policy name with it.
 *
 * TIER IS DRAWN UNIFORMLY per match, and that choice is stated because it is a
 * denominator. Weighting tiers by the bands' real occupancy would be more
 * faithful to what PWIN[g] means — but occupancy is itself an output of the
 * model whose input we are trying to measure, so importing it would put the
 * circularity straight back. Uniform is neutral and the per-tier breakdown is
 * reported, so anyone who wants a weighted figure can form one afterwards with
 * their weighting visible. NOTE the sim-derived 0.443 for band 2 WAS
 * occupancy-weighted; comparing it to a flat mean here compares two different
 * quantities.
 *
 * Cell config: #lb=<band>,<seat>,<policy>,<n>     seat = patron | boss
 * Emits   LB;band;seat;policy;tier;i;win;pPts;oPts;secs
 * and     LB-CELL;band;seat;policy;n=..;wins=..;rate=..;wilson=..;byTier=..
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(100); }
  return false; };
const tap = el => { if (!el) return false;
  const r = el.getBoundingClientRect();
  const o = {bubbles: true, cancelable: true, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2};
  el.dispatchEvent(new PointerEvent('pointerdown', o));
  el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o)); return true; };

const H = (location.hash.match(/#lb=([^&]+)/) || [])[1] || '';
const [BRAW, SRAW, PRAW, NRAW] = H.split(',');
const band = +BRAW || 1, seat = (SRAW || 'boss'), polName = PRAW || 'carl', N = +NRAW || 10;
if (seat !== 'patron' && seat !== 'boss') return {err: 'seat must be patron|boss, got ' + seat};

if (!await until(() => typeof launchBossMatch === 'function' && typeof S !== 'undefined', 30000))
  return {err: 'no boot'};

/* the sim harness supplies the policies + legalKeeps - the REAL pair */
try {
  const src = await (await fetch('tools/sim_harness.js')).text();
  (0, eval)(src);
} catch (e) { return {err: 'harness load: ' + e.message}; }
if (!window.FSIM || !FSIM.POLICIES[polName]) return {err: 'no policy ' + polName};
const policy = FSIM.POLICIES[polName];

/* ── the band rule, taken from the model rather than restated ─────── */
let gearLevel = null, FAMS = null;
try {
  const src = _runEconomySim.toString();
  const gl = src.match(/function gearLevel\(fam\)\{[\s\S]*?\n  \}/);
  const fm = src.match(/var FAMS=\[[^\]]*\];/);
  if (!gl || !fm) throw new Error('could not locate gearLevel/FAMS in the model');
  (0, eval)('window.__lbFAMS = ' + fm[0].replace(/^var FAMS=/, '').replace(/;$/, '') + ';');
  (0, eval)('window.__lbGear = (' + gl[0].replace(/^function gearLevel/, 'function') + ');');
  gearLevel = window.__lbGear; FAMS = window.__lbFAMS;
} catch (e) { return {err: 'REFUSING TO RUN - could not extract the band rule from the model: ' + e.message}; }

/* one loadout per live band. Band 0 is unreachable by construction (`fam`
   always holds the starter draft's die), which is why there are three. */
const LOADOUTS = {
  1: ['amber', 'bone', 'bone', 'bone', 'iron', 'iron'],
  2: ['amber', 'silver', 'bone', 'bone', 'iron', 'iron'],
  3: ['jade', 'jade2', 'starstone', 'amber', 'bone', 'iron'],
};
const dice = LOADOUTS[band];
if (!dice) return {err: 'no loadout for band ' + band};
/* ASSERT the band rather than assume it - the whole point of borrowing the
   model's own rule is to be told when a loadout is not what it is labelled */
const famOf = d => d.filter(m => FAMS.indexOf(m) >= 0);
const actual = gearLevel(famOf(dice));
if (actual !== band)
  return {err: 'loadout for band ' + band + ' actually scores band ' + actual +
               ' (fam=' + famOf(dice).join('|') + ') - refusing to mislabel a cell'};
/* and the other two must NOT score this band, or the axis is not separated */
const others = Object.keys(LOADOUTS).filter(b => +b !== band)
  .map(b => ({b: +b, g: gearLevel(famOf(LOADOUTS[b]))}));
if (others.some(o => o.g === band))
  return {err: 'another loadout also scores band ' + band + ': ' + JSON.stringify(others)};

if (typeof _getS === 'function') _getS();
S.settings = S.settings || {}; S.settings.fastRival = true;
S.run._bossSeen = {drunkard:1, peasant:1, commoner:1, merchant:1, soldier:1, knight:1, noble:1, bishop:1};
setInterval(() => { try { if (typeof G !== 'undefined' && G && (G.phase === 'opp' || G._oppTurnActive)) G._ffMult = 0.05; } catch (e) {} }, 150);

/* A BATCH MUST COME BACK. The first version of this ran a whole 130-match cell
   in one invocation; the connection died at an unknown point and the entire
   cell was lost, with nothing on disk to say whether it had reached match 20 or
   match 129. Cells are now assembled from small batches by the runner, and this
   is the belt to that braces: past the budget the loop stops and reports what it
   has, so an invocation always yields data instead of a maybe. */
const BUDGET_MIN = +((location.hash.match(/budget=(\d+)/) || [])[1]) || 25;
const DEADLINE = Date.now() + BUDGET_MIN * 60000;

const SUB_REFUSE = 0.05;/* P937: above this fraction of substituted decisions the cell refuses */
let wins = 0, done = 0, stalls = 0, budgetStopped = 0;
/* P936: how often a persona's own code was silently replaced by the
   harness's fallback. Both fallbacks stay - a stalled cell is worse than a
   substituted keep - but a run that substituted is a run about a different
   policy than the one every output line names, so it says so. */
let subBank = 0, subKeep = 0, subBankErr = null, subKeepErr = null, decisions = 0;
const byTier = {};
const LOG = [];
const say = t => { LOG.push(t); try { console.log(t); } catch (e) {} };
say('LB-START;band=' + band + ';seat=' + seat + ';policy=' + polName +
    ';n=' + N + ';dice=' + dice.join('|') + ';famScored=' + actual);

for (let m = 0; m < N; m++) {
  if (Date.now() > DEADLINE) {
    budgetStopped = 1;
    say('LB-BUDGET;band=' + band + ';seat=' + seat + ';stopped=' + m + '/' + N);
    break;
  }
  const t0 = Date.now();
  /* TIER UNIFORM per match - see the header. Recorded, so the curve survives. */
  const tier = Math.floor(Math.random() * 8);
  let okStart = false;
  for (let a = 0; a < 3 && !okStart; a++) {
    try { delete S.pendingMatch; } catch (e) {}
    window._fkDiscardOk = true;
    S.run.tier = tier;
    S.run.dice = dice.slice();
    if (seat === 'patron') {
      /* a fresh night every match: launchSeat consumes seats from the roster,
         so without this the second match has nothing to play */
      try { S.run.night = null; } catch (e) {}
      try { launchPatronMatch(); } catch (e) {}
    } else {
      try { launchBossMatch(); } catch (e) {}
    }
    okStart = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle' &&
      !G._endMatchFired && (G.pTurns || 0) === 0, 15000);
    if (!okStart) await sleep(1800);
  }
  if (!okStart) { stalls++; say('LB;' + band + ';' + seat + ';' + polName + ';' + tier + ';' + m + ';stall-start'); continue; }
  await sleep(400);
  G.pF = [];/* bare gear convention, stated - no family cards, no enchants */
  const state = {};
  let guard = Date.now() + 240000, dead = false;
  while (!G._endMatchFired) {
    if (Date.now() > guard) { dead = true; break; }
    if (G.phase === 'idle' && !G._oppTurnActive) { tap(document.getElementById('btnRoll')); await sleep(300); }
    const got = await until(() => G._endMatchFired ||
      (G.phase === 'choosing' && (G.pool || []).some(d => !d.committed && d.el && d.el.onclick)), 12000);
    if (G._endMatchFired) break;
    if (!got) { if (Date.now() > guard) { dead = true; break; } continue; }
    await sleep(120);
    const free = G.pool.filter(d => !d.committed && !d._frozen);
    const keeps = FSIM.legalKeeps(free);
    if (!keeps.length) { await sleep(400); continue; }
    /* P936: A SUBSTITUTED KEEP IS RECORDED. policy.keep throwing used to fall
       through to "the last legal keep" in silence, so a persona that failed on
       some state was measured as a different one - under its own name, in every
       line of output. The fallback stays (a stalled cell is worse) but the cell
       now reports how often it fired. */
    decisions++;
    let sel = null;
    try { sel = policy.keep(free, {keeps: keeps, G: G, state: state, rolls: G.turnRollCount || 0}); }
    catch (e) { subKeepErr = subKeepErr || String(e && e.message || e); }
    if (!sel || !sel.length) { subKeep++; sel = keeps[keeps.length - 1].sel; }
    for (const d of sel) { if (d.el && !d.sel) tap(d.el); await sleep(60); }
    await sleep(180);
    state.oppTotal = G.oPts;
    /* P936: FROM THE ONE DEFINITION, not a second one. This used to read
       `(G.turnNum||1) >= (G.turnCap||10)`, which is wrong twice: the capped
       resource is pTurns, not turnNum (P917 - turnNum increments at the
       handover and read 10 on patron matches whose cap is 8), so it told every
       persona "last turn" before it was; and it dropped the rival-reached-
       target clause that sim_harness has. Four persona bankAt bodies branch on
       this, so the personas were playing a different endgame here than in the
       sim, on a value both call by the same name. */
    state.lastTurn = FSIM.lastTurnFlag(G, G.pTurns || 0, G.turnCap || 0);
    /* P936: AND A SUBSTITUTED BANK RULE IS RECORDED. This used to silently
       become "bank at 300" whenever a persona's bankAt threw - a policy
       substitution invisible in the output, on a run whose every line names the
       policy it believes it measured. */
    let bank = false;
    try { bank = policy.bankAt({turnPts: G.turnPts || 0, diceLeft: free.length - sel.length,
      rolls: G.turnRollCount || 0, state: state, G: G}); }
    catch (e) { subBank++; subBankErr = subBankErr || String(e && e.message || e);
                /* P937: THE FALLBACK BANKS A WON MATCH. `turnPts>=300` alone
                   changed TWO things when it fired - the threshold, and the
                   willingness to bank a match already won. Every persona opens
                   its bankAt with `pPts+turnPts>=target -> true` (mkPolicy's
                   default at 888 and each named persona), except Randy, whose
                   comment says randomness at every exposed decision is the
                   point. A substituted turn should be a different threshold, not
                   a turn that throws the match away. */
                bank = ((G.pPts || 0) + (G.turnPts || 0) >= (G.target || Infinity))
                       || (G.turnPts || 0) >= 300; }
    tap(document.getElementById(bank ? 'btnBank' : 'btnRoll'));
    await sleep(250);
  }
  if (dead) { stalls++;
    try { say('LB-STALL;' + band + ';' + seat + ';' + tier + ';' + m + ';phase=' + G.phase +
      ';turn=' + G.turnNum + ';pPts=' + G.pPts + ';oPts=' + G.oPts); } catch (e) {}
    continue; }
  const win = G.pPts > G.oPts ? 1 : 0;
  wins += win; done++;
  byTier[tier] = byTier[tier] || {n: 0, w: 0};
  byTier[tier].n++; byTier[tier].w += win;
  say('LB;' + band + ';' + seat + ';' + polName + ';' + tier + ';' + m + ';' +
      (win ? 'win' : 'loss') + ';' + G.pPts + ';' + G.oPts + ';' + Math.round((Date.now() - t0) / 1000));
  await until(() => !G || !G._oppTurnActive, 8000);
  await sleep(2500);
}

const rate = done ? (wins / done) : 0;
const z = 1.96;
const ph = done ? ((rate + z * z / (2 * done)) / (1 + z * z / done)) : 0;
const hw = done ? (z * Math.sqrt(rate * (1 - rate) / done + z * z / (4 * done * done)) / (1 + z * z / done)) : 0;
/* P940: THE INTERVAL IS NOT SYMMETRIC ABOUT THE OBSERVED RATE, and reporting a
   bare half-width invited exactly that reading. Wilson recentres: 3/14 is a
   rate of 21.4% but an interval of [7.6, 47.6] centred on 27.6. Quoting
   "21.4% +/- 20" implies [1.4, 41.4] - wrong at both ends, and wrong in the
   direction that matters, since 0.443 sits inside the true interval and
   outside the naive one. Bounds are returned and logged; the centre and
   half-width stay beside them so nothing is lost. */
const lo = Math.max(0, ph - hw), hi = Math.min(1, ph + hw);
const tierStr = Object.keys(byTier).sort().map(t =>
  t + ':' + byTier[t].w + '/' + byTier[t].n).join(' ');
say('LB-CELL;band=' + band + ';seat=' + seat + ';policy=' + polName +
    ';n=' + done + ';wins=' + wins + ';rate=' + (rate * 100).toFixed(1) +
    ';wilson=[' + (lo * 100).toFixed(1) + ',' + (hi * 100).toFixed(1) + ']' +
    ';stalls=' + stalls + ';subBank=' + subBank + ';subKeep=' + subKeep + ';byTier=' + tierStr);
return {band, seat, policy: polName, asked: N, n: done, wins,
        /* P936: a nonzero substitution count means this cell did not measure
           the policy it names. Reported, not hidden in a log line. */
        subBank, subKeep, subBankErr, subKeepErr, decisions,
        subRate: decisions ? +((subBank + subKeep) / decisions).toFixed(4) : 0,
        /* P937: A COUNT GETS READ ONCE AND THEN IGNORED - the cap-run filter
           taught that, by being a reported field the first band table was
           printed straight over. So this REFUSES. Above SUB_REFUSE of its
           decisions, the cell did not measure the policy every one of its
           output lines names, and it returns a refusal instead of a win rate.
           The line is a judgement: 2% is incidental, 90% is a different policy,
           and 5% is where a persona failing once every twenty decisions stops
           being incidental. subRate is reported either way so a different line
           can be drawn afterwards without re-running. */
        refusal: (decisions && (subBank + subKeep) / decisions > SUB_REFUSE)
          ? ('the harness substituted its own keep/bank on ' +
             Math.round(100 * (subBank + subKeep) / decisions) + '% of ' + decisions +
             ' decisions (bank ' + subBank + ', keep ' + subKeep + '; first errors: ' +
             (subBankErr || '-') + ' / ' + (subKeepErr || '-') +
             ') - this cell did not measure ' + polName)
          : null,
        policyRanUnsubstituted: subBank === 0 && subKeep === 0,
        rate: +(rate * 100).toFixed(1),
        wilsonLo: +(lo * 100).toFixed(1), wilsonHi: +(hi * 100).toFixed(1),
        wilsonCentre: +(ph * 100).toFixed(1), wilsonHalfWidth: +(hw * 100).toFixed(1),
        stalls, budgetStopped, byTier, dice, log: LOG};
