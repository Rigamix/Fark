/* IS THERE A BUST DIVERGENCE AT ALL? Deep sample, one tier per run.
 *
 * The reported "model busts 1.6-6.7x more at seven of eight nights" did not
 * survive Wilson intervals on its own samples: five of eight cells have the
 * model rate INSIDE the real 95% interval, and CORVUS and WHISPER each rested
 * on a SINGLE bust event. Two mechanism hunts (release-singles, bust-saves)
 * were built to explain a target that was mostly never established.
 *
 * This settles whether a question exists before any more hunting. Only the
 * three nights still outside their interval are worth the wall-clock:
 *   CORVUS  real 1/48  = 0.021 [0.004, 0.109]  model 0.140
 *   BRUTUS  real 5/48  = 0.104 [0.045, 0.222]  model 0.300
 *   WHISPER real 1/22  = 0.045 [0.008, 0.218]  model 0.220
 *
 * SIZE: 300 turns. At a true rate of 0.02 that is ~6 busts, interval roughly
 * [0.009, 0.043] - which excludes 0.14. At a true 0.14 the interval is about
 * [0.10, 0.19]. Either way the model rate lands clearly inside or outside.
 *
 * TIMING IS NOT TOUCHED beyond two shipped settings. fastRival multiplies
 * _oppDelay by 0.4 with a 40ms floor and its own comment says it changes no
 * scoring or banking decision; reducedMotion only skips particle emission and
 * adds a CSS class. The dice physics tape that _afterOppSettle waits on is
 * left alone deliberately - shortening it could change RNG consumption or the
 * number of rolls, which is exactly the quantity being measured.
 *
 * Standing instrument lessons, all three kept: read G.oTurns / G.oPts rather
 * than hooking a lexically-bound function; check _oppTurnActive BEFORE calling
 * runOppTurn, never after; never relaunch over a live turn, because finOpp
 * clears the active flag and then hits a ghost-timer guard sitting BEFORE
 * G.oTurns++, so an orphaned turn really ran but never registered.
 *
 * NO CONTROL ARM HERE, and that is deliberate rather than an omission: this
 * run is not testing a mechanism, it is measuring one rate per tier. Finnick
 * is already established at 58/149 = 0.389 against the model's 0.390, which
 * is the control for the question this feeds.
 */
const TIER = __TIER__;
const NAMES = {3: 'CORVUS', 4: 'BRUTUS', 6: 'WHISPER'};
const LOADOUT = {3: ['silver','jade','jade','bone','bone','bone'],
                 4: ['silver','jade','jade','jade','bone','bone'],
                 6: ['silver','jade','jade','starstone','jade2','bone']};
const PRATE = {3: 541, 4: 679, 6: 536};
const TARGET_TURNS = 300, MAX_MATCHES = 60, TURNS_PER = 12;

const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof launchBossMatch !== 'function') return { error: 'game globals missing' };
try { S.settings = S.settings || {}; S.settings.fastRival = true; S.settings.reducedMotion = true; } catch (e) {}

let turns = 0, busts = 0, matches = 0, stalled = 0, pts = 0;
const perMatch = [];

for (let m = 0; m < MAX_MATCHES && turns < TARGET_TURNS; m++) {
  await until(() => typeof G === 'undefined' || !G || !G._oppTurnActive, 8000);
  await sleep(140);
  try {
    _getS();
    S.run = S.run || {};
    S.run.tier = TIER;
    S.run.dice = LOADOUT[TIER].slice();
    S.run.cards = S.run.cards || [];
    launchBossMatch();
  } catch (e) { break; }
  if (!(await until(() => typeof G !== 'undefined' && G && G.rung && G.matchOppDice, 9000))) break;
  matches++;
  await sleep(280);

  let mt = 0, mb = 0;
  for (let i = 0; i < TURNS_PER && turns < TARGET_TURNS; i++) {
    if (G._oppTurnActive) break;
    const t0 = (G.oTurns || 0), p0 = (G.oPts || 0);
    try { runOppTurn(); } catch (e) { break; }
    if (!(await until(() => G && (G.oTurns || 0) > t0, 20000))) { stalled++; break; }
    turns++; mt++;
    const gained = (G.oPts || 0) - p0;
    pts += gained;
    if (gained <= 0) { busts++; mb++; }
    try {
      G.pPts = (G.pPts || 0) + PRATE[TIER];
      if (G._endMatchFired || G.oPts >= (G.target || 1e9) || G.pPts >= (G.target || 1e9)) break;
    } catch (e) { break; }
    await sleep(80);
  }
  perMatch.push([mt, mb]);
}

/* Wilson 95%, computed here so the answer arrives with its own interval
   rather than a bare rate that invites the same mistake again */
function wilson(k, n) {
  if (!n) return [0, 1];
  const z = 1.96, p = k / n, d = 1 + z * z / n;
  const c = p + z * z / (2 * n);
  const s = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n));
  return [+((c - s) / d).toFixed(4), +((c + s) / d).toFixed(4)];
}
const ci = wilson(busts, turns);
const MODEL = {3: 0.140, 4: 0.300, 6: 0.220};
return { tier: TIER, boss: NAMES[TIER], matches: matches, turns: turns, busts: busts,
         stalled: stalled,
         bustRate: turns ? +(busts / turns).toFixed(4) : null,
         ci95: ci, modelRate: MODEL[TIER],
         modelInsideInterval: MODEL[TIER] >= ci[0] && MODEL[TIER] <= ci[1],
         ptsPerTurn: turns ? Math.round(pts / turns) : null,
         perMatch: perMatch };
