/* dice_harness.js — measure the dice throw without rendering a single frame.
 *
 * `D3X._physSolve(slotX, values, obstacles, limitX)` is a pure function of its
 * arguments plus Math.random(): it runs the whole throw and returns the tape.
 * So a throw can be run hundreds of times in a fraction of a second, with no
 * canvas, no rAF and no match in progress — which is the only way to say
 * anything honest about behaviour that varies every time.
 *
 * Paste into the console (or inject it) and call:
 *     dice.baseline()            // 200 throws, the numbers that matter
 *     dice.trials(200,{n:3})     // a 3-dice reroll
 *     dice.trials(200,{obst:[-1.5]})   // with a kept die pinned at x=-1.5
 *     dice.worst(200)            // the ugliest throw it can find, in detail
 *
 * WHAT IS MEASURED, and why each one is here:
 *   slide      how far the tidy passes MOVE a die from where the sim stopped
 *              it, in die-widths. This is Denis's "dice slide and magnetically
 *              go into a cleaner layout". Drive it to zero.
 *   reorder    how often a die is handed a different die's landing x because
 *              the final pass re-sorts by loadout order. Any value above 0
 *              means the throw's outcome was overruled.
 *   offEdge    dice whose resting centre is outside the on-screen bound.
 *   minGap     closest approach between neighbouring resting centres; below
 *              1.0 die-width they are visibly touching or overlapping.
 *   drift      distance from a die's own slot centre — what the invisible
 *              circular slot is supposed to cap.
 *   steps      solver frames used; 700 is the cap, and hitting it means the
 *              throw never settled.
 */
(function (g) {
  var DEF_SLOTS = [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5];

  function pct(a, p) {
    if (!a.length) return 0;
    var s = a.slice().sort(function (x, y) { return x - y; });
    return s[Math.min(s.length - 1, Math.floor(p * s.length))];
  }
  function mean(a) { return a.length ? a.reduce(function (s, v) { return s + v; }, 0) / a.length : 0; }
  function r2(v) { return Math.round(v * 100) / 100; }

  /* one throw, measured */
  function once(opt) {
    opt = opt || {};
    var n = opt.n || 6;
    var slots = (opt.slots || DEF_SLOTS).slice(0, n);
    var vals = opt.vals || slots.map(function () { return 1 + Math.floor(Math.random() * 6); });
    /* An obstacle is a die already resting on this table: _physSolve builds a
       mass-0 box at {x,y,z} and reads o.q for its yaw. Passing bare numbers
       made every target NaN - the harness's own bug, caught on its first run
       against kept dice. `kept:[x,...]` is the shorthand. */
    var obst = opt.obst || (opt.kept || []).map(function (x) {
      return { x: x, y: 0.48, z: 0, q: null };
    });
    var limitX = opt.limitX === undefined ? 3.1 : opt.limitX;

    var sol = D3X._physSolve(slots, vals, obst, limitX);
    var d = sol.dbg;
    if (!d) throw new Error('no dbg on the solve — is this build patched?');

    var slide = d.slide.map(Math.abs);
    /* a die was REORDERED if the x it was handed is not the x it landed at,
       beyond what the separation pass alone would do: the final pass assigns
       the sorted landing positions by loadout order, so a die that crossed a
       neighbour gets a completely different one */
    var landedOrder = d.landed.map(function (x, i) { return [x, i]; })
      .sort(function (a, b) { return a[0] - b[0]; }).map(function (p) { return p[1]; });
    var slotOrder = slots.map(function (x, i) { return [x, i]; })
      .sort(function (a, b) { return a[0] - b[0]; }).map(function (p) { return p[1]; });
    var reorder = 0;
    for (var i = 0; i < n; i++) if (landedOrder[i] !== slotOrder[i]) reorder++;

    var edge = limitX + 0.55;
    var offEdge = d.want.filter(function (x) { return Math.abs(x) > edge + 1e-6; }).length;

    var xs = d.want.slice().sort(function (a, b) { return a - b; });
    var minGap = Infinity;
    for (var j = 1; j < xs.length; j++) minGap = Math.min(minGap, xs[j] - xs[j - 1]);
    if (!isFinite(minGap)) minGap = 0;

    var drift = d.want.map(function (x, k) { return Math.abs(x - slots[k]); });

    var bad = d.want.filter(function (v) { return !isFinite(v); }).length;
    if (bad) throw new Error('solver returned ' + bad + ' non-finite target x - that is a real defect, not a metric');
    /* how many times a die was pushed back by its own slot wall. This is
       "as if they bounce on invisible walls repeatedly" as a number. */
    var hits = d.penHits || [];
    return {
      penHitsMax: hits.length ? Math.max.apply(null, hits) : 0,
      penHitsTotal: hits.reduce(function (a, b) { return a + b; }, 0),
      steps: sol.steps, frames: sol.frames.length,
      maxSlide: Math.max.apply(null, slide), meanSlide: mean(slide),
      reorder: reorder, offEdge: offEdge, minGap: minGap,
      maxDrift: Math.max.apply(null, drift),
      landed: d.landed, want: d.want, slots: slots, vals: vals
    };
  }

  function trials(n, opt) {
    n = n || 200;
    var runs = [], t0 = performance.now();
    for (var i = 0; i < n; i++) runs.push(once(opt));
    var ms = performance.now() - t0;
    var f = function (k) { return runs.map(function (r) { return r[k]; }); };
    return {
      throws: n, msPerThrow: r2(ms / n),
      slide_max: r2(Math.max.apply(null, f('maxSlide'))),
      slide_p50: r2(pct(f('maxSlide'), 0.5)),
      slide_p95: r2(pct(f('maxSlide'), 0.95)),
      reordered_throws: f('reorder').filter(function (v) { return v > 0; }).length,
      reordered_dice_total: f('reorder').reduce(function (a, b) { return a + b; }, 0),
      offEdge_throws: f('offEdge').filter(function (v) { return v > 0; }).length,
      minGap_worst: r2(Math.min.apply(null, f('minGap'))),
      minGap_p05: r2(pct(f('minGap'), 0.05)),
      drift_max: r2(Math.max.apply(null, f('maxDrift'))),
      drift_p95: r2(pct(f('maxDrift'), 0.95)),
      penHits_worstDie: Math.max.apply(null, f('penHitsMax')),
      penHits_perThrow_p50: pct(f('penHitsTotal'), 0.5),
      penHits_perThrow_p95: pct(f('penHitsTotal'), 0.95),
      steps_max: Math.max.apply(null, f('steps')),
      steps_p95: pct(f('steps'), 0.95),
      hitCap: f('steps').filter(function (v) { return v >= 700; }).length
    };
  }

  /* the single ugliest throw in n, with the per-die detail */
  function worst(n, opt) {
    n = n || 200;
    var bad = null;
    for (var i = 0; i < n; i++) {
      var r = once(opt);
      if (!bad || r.maxSlide > bad.maxSlide) bad = r;
    }
    return {
      maxSlide: r2(bad.maxSlide), reorder: bad.reorder, steps: bad.steps,
      perDie: bad.slots.map(function (s, i) {
        return { slot: s, landedAt: r2(bad.landed[i]), movedTo: r2(bad.want[i]),
                 slid: r2(bad.want[i] - bad.landed[i]) };
      })
    };
  }

  function baseline() {
    return {
      six: trials(200),
      three: trials(200, { n: 3, slots: [-1.5, -0.5, 0.5] }),
      one: trials(200, { n: 1, slots: [0] }),
      withKept: trials(200, { kept: [-2.2, 2.2] }),
      narrow: trials(200, { limitX: 2.0 })
    };
  }

  g.dice = { once: once, trials: trials, worst: worst, baseline: baseline, SLOTS: DEF_SLOTS };
})(window);
