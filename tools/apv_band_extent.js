/* How tall is the dice band, really - measured across a live throw.
 *
 * THE PROPOSAL is to size dgCanvas and stCanvas to the band the dice occupy
 * rather than to the whole match screen, which shrinks the mip chain with them
 * because _paintHalo sizes its scratch from cv. About 29MB on a dpr-3 phone for
 * one coordinate change.
 *
 * THE RISK IS CLIPPING, AND IT IS NOT WHERE IT LOOKS. A band taken from the
 * dice ROWS' rects would be right for settled dice and wrong during a throw:
 * these dice are DROPPED, so frame 0 is the peak and the mesh spends the first
 * part of every flight ABOVE the row it lands in. A mark clipped off the top of
 * the canvas for the first 300ms of every roll is exactly the kind of defect
 * that reads as "sometimes the glow flickers".
 *
 * So the extent is sampled from the HULLS - what is actually painted - across a
 * real roll and a real settle, and reported against the rows' own boxes. The
 * padding then comes from a measurement instead of from a guess, and the
 * headroom the dice actually use is a number rather than an adjective.
 *
 * THE GLOW REACHES PAST THE HULL TOO: soft 11 stretched by sy 1.24, plus the
 * line, plus G.clear. That is added on top of the measured extent rather than
 * hoped to be inside it.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

/* BOOT, AND RECORD HOW. FXH.match failed twice in a row with "match never
   became idle" while a bare _getS()+launchBossMatch() reached idle in 500ms in
   the same build - the difference between them is showScreen('gauntlet'). That
   is a harness question and this probe is not about it, so it tries the shared
   helper, falls back to the path measured to work, and reports which it used.
   A measurement blocked on an instrument's flake is a measurement not taken;
   a measurement that hides the flake is worse. */
const m = await FXH.match(1);
out.boot = {viaFXH: m.ok, why: m.why || null};
if (!m.ok) {
  try { _getS(); window._fkDiscardOk = true;
        S.run.tier = 1; S.run.gold = 500;
        try { delete S.pendingMatch; } catch (e) {}
        launchBossMatch(); } catch (e) { return {err: 'direct launch: ' + e.message}; }
  const ok = await FXH.until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 25000);
  if (ok == null) return Object.assign(out, {err: 'neither path reached idle'});
  await FXH.sleep(1200);
  out.boot.viaDirect = true;
}

const scEl = document.getElementById('screen-match');
const sc = scEl.getBoundingClientRect();
out.screen = {w: Math.round(sc.width), h: Math.round(sc.height)};

const rowBox = id => { const el = document.getElementById(id);
  if (!el) return null; const r = el.getBoundingClientRect();
  return {top: +(r.top - sc.top).toFixed(1), bottom: +(r.bottom - sc.top).toFixed(1),
          h: +r.height.toFixed(1)}; };
out.rows = {player: rowBox('playerDiceRow'), opp: rowBox('oppDiceRow'),
            keptTray: rowBox('keptTray'), keptRow: rowBox('keptRow')};

/* sample the painted extent: every visible match die's hull, right now */
const extent = () => {
  const ds = D3X.dice.filter(d => d.match && d.obj && d.obj.visible && d.chip);
  let top = 1e9, bot = -1e9, left = 1e9, right = -1e9, n = 0;
  ds.forEach(d => { const h = D3X._hullOf(d, sc, D3X.GLOW.grow); if (!h) return;
    n++;
    h.forEach(p => { if (p[1] < top) top = p[1]; if (p[1] > bot) bot = p[1];
                     if (p[0] < left) left = p[0]; if (p[0] > right) right = p[0]; }); });
  return n ? {top: +top.toFixed(1), bottom: +bot.toFixed(1),
              left: +left.toFixed(1), right: +right.toFixed(1), dice: n} : null;
};

const rolling = () => D3X.dice.filter(d => d.match && d.roll).length;
const samples = [];
const grab = tag => { const e = extent(); if (e) samples.push(Object.assign({tag,
  rolling: rolling()}, e)); };

/* GET TO THE DICE THE WAY EVERY OTHER PROBE DOES. match() returns at `idle`,
   which is before a single die has been dealt - the first version of this
   tapped btnRoll itself and sampled an empty table, reporting rows of zero
   height and no dice at all. */
const rs = await FXH.rollAndSettle();
out.rolled = {ok: rs.ok, why: rs.why, freeDice: rs.freeDice,
              reachedChoosing: rs.reachedChoosing, tapeDrained: rs.tapeDrained};
/* THE PART OF ok THIS PROBE NEEDS IS DICE, not the choosing phase. rollAndSettle
   reports ok only when the player can act, and it returned not-ok with
   freeDice 6 - the dice were on the table and had hulls, which is the entire
   requirement here. The full result is reported rather than discarded. */
if (!(rs.freeDice > 0)) return Object.assign(out, {err: 'no dice: ' + rs.why});
for (let i = 0; i < 4; i++) { grab('settled'); await FXH.sleep(120); }

/* THEN A REAL FLIGHT. _setDieVal goes through reDrawDieFace to D3.roll to
   _physQueue - P898 measured that chain at 1017 frame-ms of solved physics -
   so this is the same throw the game does, not a simulation of one. Tapping
   the roll button again would need a legal selection first, which is a
   different problem and not this measurement's. */
const free = G.pool.filter(d => !d.committed && !d._frozen && d.el);
if (free.length < 2) return Object.assign(out, {err: 'need two free dice'});
free.slice(0, 2).forEach(d => {
  try { _setDieVal(d, (typeof rollFaceExclude === 'function')
    ? rollFaceExclude(d.mat, d.val, d) : (d.val % 6) + 1); } catch (e) {}
});
const t0 = Date.now();
let sawFlight = false;
while (Date.now() - t0 < 12000) {
  grab('flight');
  if (rolling() > 0) sawFlight = true;
  await FXH.sleep(50);
  if (sawFlight && rolling() === 0) break;
}
await FXH.until(() => rolling() === 0, 15000);
for (let i = 0; i < 4; i++) { grab('settled'); await FXH.sleep(120); }

const flying = samples.filter(s => s.rolling > 0);
const still = samples.filter(s => s.rolling === 0);
const minOf = (a, k) => a.length ? Math.min.apply(null, a.map(s => s[k])) : null;
const maxOf = (a, k) => a.length ? Math.max.apply(null, a.map(s => s[k])) : null;
out.sampled = {total: samples.length, whileFlying: flying.length, settled: still.length};
out.extentFlying = flying.length ? {top: minOf(flying, 'top'), bottom: maxOf(flying, 'bottom'),
                                    left: minOf(flying, 'left'), right: maxOf(flying, 'right')} : null;
out.extentSettled = still.length ? {top: minOf(still, 'top'), bottom: maxOf(still, 'bottom'),
                                    left: minOf(still, 'left'), right: maxOf(still, 'right')} : null;
out.extentAll = {top: minOf(samples, 'top'), bottom: maxOf(samples, 'bottom'),
                 left: minOf(samples, 'left'), right: maxOf(samples, 'right')};

/* how far the glow itself reaches beyond a hull */
/* NOT `const G`. The page's G is a let, and a const of the same name anywhere
   in this probe's scope puts every G reference in the eval'd harness into its
   temporal dead zone - including `typeof G`, which throws instead of answering.
   That is what made FXH.match time out and report "match never became idle"
   through four runs. Never name a probe local after a page global. */
const GL = D3X.GLOW;
out.glowReach = {soft: GL.soft, sy: GL.sy, sx: GL.sx, line: GL.line,
                 clear: GL.clear,
                 estimateY: +(GL.soft * GL.sy + GL.line / 2 + GL.clear).toFixed(1),
                 estimateX: +(GL.soft * GL.sx + GL.line / 2 + GL.clear).toFixed(1)};

/* what a band would cost against what the full screen costs */
const dpr = Math.min(devicePixelRatio || 1, D3X.GLOW_DPR_MAX || 3);
const bandH = out.extentAll.bottom - out.extentAll.top + 2 * out.glowReach.estimateY;
out.saving = {
  dpr,
  fullScreenMB: +(sc.width * dpr * sc.height * dpr * 4 / 1048576).toFixed(2),
  bandMB: +(sc.width * dpr * bandH * dpr * 4 / 1048576).toFixed(2),
  bandHeight: +bandH.toFixed(1), screenHeight: +sc.height.toFixed(1),
  fractionOfScreen: +(bandH / sc.height).toFixed(3),
};

/* and the assertion Denis asked for, checked as it stands today */
const dg = document.getElementById('dgCanvas'), st = document.getElementById('stCanvas');
out.canvases = {dg: dg ? [dg.width, dg.height] : null,
                st: st ? [st.width, st.height] : null,
                sameSize: !!(dg && st && dg.width === st.width && dg.height === st.height)};

out.VERDICT = {
  thereWereDiceAtAll: out.sampled.total > 0 &&
                      !!out.extentSettled && out.extentSettled.bottom > 0,
  theProbeSawAFlight: out.sampled.whileFlying >= 3,
  theProbeSawASettle: out.sampled.settled >= 3,
  /* THE ONE THAT DECIDES THE PADDING: do the dice go above where they land? */
  diceRiseAboveTheirSettledTop: !!out.extentFlying && !!out.extentSettled &&
    out.extentFlying.top < out.extentSettled.top,
  /* and the band must actually be worth doing */
  theBandIsLessThanTheScreen: out.saving.fractionOfScreen < 0.8,
  itSavesRealMemory: out.saving.bandMB < out.saving.fullScreenMB * 0.8,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
