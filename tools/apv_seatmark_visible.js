/* IS THE DEAD .seat-mark ACTUALLY VISIBLE? Look, do not reason.
 *
 * The CSS at 3925-3940 carries Denis's own art direction for exactly the thing
 * ruling 3.12 asks for - a soft squircle under the seat, explicitly not a lane
 * stripe - and no JS has ever created one. Before proposing it as the surface,
 * the question is whether an element at z-index:1 is actually SEEN, because
 * this file's hardest-won lesson is that chip overlays are invisible under the
 * 3D canvas and were shipped that way for a long time.
 *
 * z1 (seat mark) < z3 (#dgCanvas) < z41 (#d3xCanvas, the dice). The table image
 * is beneath all of them. So the prediction is that it shows on the table and
 * the dice occlude it - which is precisely what the ruling wants. A prediction
 * is not a measurement, and neither is a DOM query: this exists to be
 * SCREENSHOTTED and looked at.
 *
 * Three lanes, three inks, so a single frame shows placement, occlusion and
 * the pulse's mid-animation state at once. Lane 2 is deliberately under a die.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};
const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};

const r = await FXH.rollAndSettle();
out.roll = {ok: r.ok, why: r.why};

const sc = document.getElementById('screen-match');
const tl = document.getElementById('throwLine');
if (!sc || !tl) return {err: 'no screen or throw line'};
/* NOT `S` AND NOT `T`. _fxh.js is eval'd into this same function scope, so a
   const named S puts the GAME's save-state global in the temporal dead zone and
   FXH.match's _getS() throws before the probe does anything - which is the trap
   the harness documents for G, hit here with the other global. Cost one run. */
const SR = sc.getBoundingClientRect(), TR = tl.getBoundingClientRect();

/* THE FORMULA, from the CSS layout rather than from any live die: die 13cqw,
   gap 3.8cqw, container query unit = #screen-match. Verified against measured
   seat rects [7,79,151,223,295,368] at w=56 on a 430px screen. */
const CQ = SR.width / 100;
const PITCH = 16.8 * CQ, SIZE = 13 * CQ;
const N = ((G.matchOppDice || []).length) || 6;
const laneCentre = (i) => ({
  x: (TR.left - SR.left) + TR.width / 2 + (i - (N - 1) / 2) * PITCH,
  y: (TR.top - SR.top) + TR.height / 2,
});

out.geometry = {screen: {w: Math.round(SR.width), h: Math.round(SR.height)},
                throwLine: {x: Math.round(TR.left), y: Math.round(TR.top),
                            w: Math.round(TR.width), h: Math.round(TR.height)},
                pitch: +PITCH.toFixed(2), size: +SIZE.toFixed(2), lanes: N,
                centres: [0, 1, 2, 3, 4, 5].map(i => {
                  const c = laneCentre(i); return [Math.round(c.x), Math.round(c.y)];
                })};

/* WHAT THE MEASURED SEATS SAY, so the formula is checked against the DOM in
   the same breath rather than trusted */
out.measuredSeats = [].slice.call(
  document.getElementById('playerDiceRow').children).map(e => {
    const b = e.getBoundingClientRect();
    return [Math.round(b.left - SR.left + b.width / 2), Math.round(b.top - SR.top + b.height / 2)];
  });

const INKS = {0: 'rgba(168,176,184,.55)',   /* fog   */
              2: 'rgba(168,136,192,.55)',   /* snare */
              4: 'rgba(176,148,112,.55)'};  /* snuff */
out.made = [];
Object.keys(INKS).forEach(k => {
  const i = +k, c = laneCentre(i);
  const el = document.createElement('div');
  el.className = 'seat-mark';
  el.style.left = c.x + 'px';
  el.style.top = c.y + 'px';
  el.style.width = SIZE + 'px';
  el.style.height = SIZE + 'px';
  el.style.setProperty('--sm-ink', INKS[k]);
  sc.appendChild(el);
  const b = el.getBoundingClientRect();
  out.made.push({lane: i, w: Math.round(b.width), h: Math.round(b.height),
                 x: Math.round(b.left - SR.left), y: Math.round(b.top - SR.top),
                 z: getComputedStyle(el).zIndex,
                 anim: getComputedStyle(el).animationName,
                 bg: getComputedStyle(el).backgroundImage.slice(0, 60)});
});

out.formulaMatchesTheDOM = out.measuredSeats.length === 6 &&
  out.geometry.centres.every((c, i) => Math.abs(c[0] - out.measuredSeats[i][0]) <= 1 &&
                                       Math.abs(c[1] - out.measuredSeats[i][1]) <= 1);
out.note = 'LOOK AT THE SCREENSHOT - the DOM says it exists, only the picture says it is seen';
await FXH.sleep(900);   /* let the pulse reach a visible point in its cycle */
return out;
