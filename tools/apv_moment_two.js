/* P884 - moment 2, the branded face lands (FX brief step 6).
 *
 * THE ASSERTION IS SET EQUALITY, not a count I predicted. The probe brands
 * several lanes and forces values, but whether a given face actually lands is
 * the roll's business, so "exactly one beat" would be a claim about my setup
 * rather than about the wiring. What the hook promises is narrower and
 * checkable: a beat fires for EXACTLY the dice _dieIsIcon is true of. That
 * holds however the dice fall, and it fails the moment the hook drifts from
 * the canonical predicate - which is the whole reason the predicate is
 * canonical.
 *
 * The setup still has to produce a mixed hand, or set equality is vacuous:
 * both sides empty passes. So the run is gated on at least one live icon AND
 * at least one branded die that is not one.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why};

/* ── brand the hand before the roll ─────────────────────────────────
   lane 0 tithe on 1 - meant to land.  lane 1 tithe on 6 - meant not to.
   lane 2 snuff on 1 with a fog already on lane 2, so it is REFUSED even if
   its face comes up: the one case where a live face must stay silent. */
G._castEnch = [];
G._enchArr = [{t:'tithe',face:1},{t:'tithe',face:6},{t:'snuff',face:1},
              null,null,null];
_lmArm('_fog', 2, 1, null);
out.setup = {fogLane: G._fog && G._fog.lane, fogLive: !!(G._fog && G._fog.live)};

/* ── witness the beat, and what ink it was handed ───────────────────── */
const BEATS = [];
const realLanded = FKFX.landed;
FKFX.landed = function (el, ink) {
  BEATS.push({el: el, ink: ink});
  return realLanded.apply(this, arguments);
};

/* P887: DRIVE THE FRAMES. _physPose only runs for a die the frame decided to
   DRAW, and headless renders at ~1fps, so every previous run of this probe
   settled through the WATCHDOG - the exit players do not take. Spinning
   D3X.frame() while the tape plays makes _physPose the exit, which is the only
   way to exercise it here at all. */
D3X._landedVia.physPose = 0; D3X._landedVia.watchdog = 0;
const beatTimes = [];
const realLandedT = FKFX.landed;
FKFX.landed = function () { beatTimes.push(performance.now()); return realLandedT.apply(this, arguments); };
const spin = setInterval(() => { try { D3X.frame(); } catch (e) {} }, 8);
const r = await FXH.rollAndSettle({vals: [1, 5, 1, 5, 1, 5]});
clearInterval(spin);
FKFX.landed = realLandedT;
out.exits = Object.assign({}, D3X._landedVia);
out.beatSpacing = beatTimes.length > 1
  ? beatTimes.slice(1).map((t, i) => +(t - beatTimes[i]).toFixed(1)) : [];
out.gotToTheDice = {ok: r.ok, why: r.why, freeDice: r.freeDice};
FKFX.landed = realLanded;
if (!r.ok) return Object.assign(out, {err: 'never got to the dice: ' + r.why});

/* ── what the hand actually turned out to be ────────────────────────── */
const pool = (G.pool || []);
out.hand = pool.map(d => ({
  lane: _laneOf(d), val: d.val,
  ench: d.ench ? d.ench.t : null, face: d.ench ? d.ench.face : null,
  live: d.ench ? _iconLive(d) : false,
  refused: d.ench ? _iconRefused(d) : false,
  isIcon: _dieIsIcon(d),
}));

const predicateSet = pool.filter(d => _dieIsIcon(d)).map(d => d.el);
const beatSet = BEATS.map(b => b.el);
const same = predicateSet.length === beatSet.length &&
             predicateSet.every(el => beatSet.indexOf(el) >= 0);

out.beats = {
  n: BEATS.length,
  inks: BEATS.map(b => b.ink),
  lanes: BEATS.map(b => {const d = pool.filter(x => x.el === b.el)[0];
                        return d ? _laneOf(d) : null;}),
};
out.predicate = {
  liveIcons: predicateSet.length,
  brandedButNotIcons: pool.filter(d => d.ench && !_dieIsIcon(d)).length,
  refusedPresent: pool.some(d => d.ench && _iconRefused(d)),
};

/* the ink must be the brand's own, from ENCH_ICONS - not a colour picked here */
out.inkMatches = BEATS.every(b => {
  const d = pool.filter(x => x.el === b.el)[0];
  return d && d.ench && ENCH_ICONS[d.ench.t] && b.ink === ENCH_ICONS[d.ench.t].ink;
});

out.VERDICT = {
  /* the run has to be a mixed hand or set equality proves nothing */
  handHasALiveIcon:        out.predicate.liveIcons > 0,
  handHasABrandThatIsNot:  out.predicate.brandedButNotIcons > 0,
  /* the claim */
  beatsMatchThePredicate:  same === true,
  /* these two are VACUOUS on an empty beat set - "every beat wore its ink"
     and "no beat for a refused brand" both pass when nothing fired at all,
     which is how the first run of this probe reported two green verdicts on a
     hook that had never run. Gated on a beat existing. */
  everyBeatWoreItsBrandInk: out.beats.n > 0 && out.inkMatches === true,
  /* the refusal case specifically - it is the one a naive hook gets wrong */
  refusalWasInPlay:        out.predicate.refusedPresent === true,
  /* P887: which exit fired. Before the counters nothing could tell, and the
     exit players actually take had never been exercised by any probe. */
  aBeatCameThroughAnExit: (out.exits.physPose + out.exits.watchdog) > 0,
  thePhysPoseExitCanFire: out.exits.physPose > 0,
  noBeatForARefusedBrand:  out.beats.n > 0 &&
                           !pool.some(d => d.ench && _iconRefused(d) &&
                                           beatSet.indexOf(d.el) >= 0),
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
return out;
