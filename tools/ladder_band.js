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

let wins = 0, done = 0, stalls = 0;
const byTier = {};
const LOG = [];
const say = t => { LOG.push(t); try { console.log(t); } catch (e) {} };
say('LB-START;band=' + band + ';seat=' + seat + ';policy=' + polName +
    ';n=' + N + ';dice=' + dice.join('|') + ';famScored=' + actual);

for (let m = 0; m < N; m++) {
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
    let sel = null;
    try { sel = policy.keep(free, {keeps: keeps, G: G, state: state, rolls: G.turnRollCount || 0}); } catch (e) {}
    if (!sel || !sel.length) sel = keeps[keeps.length - 1].sel;
    for (const d of sel) { if (d.el && !d.sel) tap(d.el); await sleep(60); }
    await sleep(180);
    state.oppTotal = G.oPts; state.lastTurn = (G.turnNum || 1) >= (G.turnCap || 10);
    let bank = false;
    try { bank = policy.bankAt({turnPts: G.turnPts || 0, diceLeft: free.length - sel.length,
      rolls: G.turnRollCount || 0, state: state, G: G}); } catch (e) { bank = (G.turnPts || 0) >= 300; }
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
const tierStr = Object.keys(byTier).sort().map(t =>
  t + ':' + byTier[t].w + '/' + byTier[t].n).join(' ');
say('LB-CELL;band=' + band + ';seat=' + seat + ';policy=' + polName +
    ';n=' + done + ';wins=' + wins + ';rate=' + (rate * 100).toFixed(1) +
    ';wilson=' + (ph * 100).toFixed(1) + '±' + (hw * 100).toFixed(1) +
    ';stalls=' + stalls + ';byTier=' + tierStr);
return {band, seat, policy: polName, n: done, wins,
        rate: +(rate * 100).toFixed(1), wilsonHalfWidth: +(hw * 100).toFixed(1),
        stalls, byTier, dice, log: LOG};
