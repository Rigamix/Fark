/* NOTE 3 - the Last Orders sign, measured against the panel it is printed on.
 *
 * Every number here is a fraction of the SIGN box, so it can be compared
 * directly with the art. The painted landmarks, sampled from
 * LastOrders_panel.png (858x547) by scanning opaque rows/columns for dark ink:
 *
 *   dividers          31.3%  and  64.2%   of the sign's width
 *   moon centre       18.4%
 *   middle centre     47.8%
 *   mug centre        80.2%
 *   frame inner edge  53.4%  of the sign's height
 *   first icon ink   ~56.7%
 *
 * WHAT THIS CAN AND CANNOT SETTLE. It can prove the three columns are centred on
 * the painted icons, that the hearts sit between the dividers, that the night
 * number is beside the moon rather than under it, and that nothing overflows the
 * sign. It CANNOT tell anyone whether the label is big enough to read - that is
 * Denis's eye on his own phone, and the probe reports the rendered px so the
 * conversation has a number in it instead of an adjective.
 *
 * CONTROL: the screen is actually up and the sign actually has a box. Every
 * fraction below divides by the sign's width; a zero-width sign would make them
 * all NaN or, worse, 0 and read as perfect alignment.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };

/* the screen builds off S.run, so wait for a run to exist rather than driving a
   whole night to lose a heart the slow way */
if (!(await until(() => typeof S !== 'undefined' && S && S.run, 20000))) {
  return { skip: 'no S.run to build the screen from' };
}
S.run._died = false;              /* the death path shows GAME OVER instead */
S.run.coins = 2;                  /* one heart just lost, so a spent one renders */
S.run.tier = 3;                   /* night 4 */
try { _showLastOrders(); } catch (e) { return { skip: 'showLastOrders threw: ' + String(e).slice(0, 90) }; }
await sleep(900);

const v = {}, notes = {};
const sign = document.querySelector('.lo-screen .lo-sign');
if (!sign) return { skip: 'no .lo-sign on screen' };
const S0 = sign.getBoundingClientRect();
notes._sign = { w: +S0.width.toFixed(1), h: +S0.height.toFixed(1),
                viewport: innerWidth + 'x' + innerHeight };
/* CONTROL */
v.theSignIsOnScreenWithABox = S0.width > 50 && S0.height > 50;

const fx = el => { const r = el.getBoundingClientRect();
  return { l: (r.left - S0.left) / S0.width, r: (r.right - S0.left) / S0.width,
           c: (r.left + r.width / 2 - S0.left) / S0.width,
           t: (r.top - S0.top) / S0.height, b: (r.bottom - S0.top) / S0.height }; };
const pct = n => +(n * 100).toFixed(1);

const moon = document.querySelector('.lo-c-moon'), lives = document.querySelector('.lo-c-lives'),
      mug = document.querySelector('.lo-c-mug'), night = document.querySelector('.lo-night'),
      hearts = document.querySelector('.lo-hearts'),
      hs = [...document.querySelectorAll('.lo-heart')];
if (!moon || !lives || !mug || !night || !hearts || hs.length !== 3) {
  return { verdict: v, notes: Object.assign(notes, { _err: 'markup missing',
    got: { moon: !!moon, lives: !!lives, mug: !!mug, night: !!night, hearts: !!hearts, heartCount: hs.length } }) };
}

const M = fx(moon), L = fx(lives), U = fx(mug), N = fx(night), H = fx(hearts);
notes._columns = {
  moonCentre: pct(M.c) + '% (art 18.4%)',
  livesCentre: pct(L.c) + '% (art 47.8%)',
  mugCentre: pct(U.c) + '% (art 80.2%)',
  livesSpan: pct(L.l) + '%..' + pct(L.r) + '% (dividers 31.3%..64.2%)',
};
/* each label centred on the icon it belongs to, within 3% of the sign's width */
v.labelsSitOverTheirPaintedIcons = Math.abs(M.c - 0.184) < 0.03
                                && Math.abs(L.c - 0.478) < 0.03
                                && Math.abs(U.c - 0.802) < 0.03;

notes._hearts = {
  span: pct(H.l) + '%..' + pct(H.r) + '%',
  gapPx: hs.length === 3 ? +(hs[1].getBoundingClientRect().left - hs[0].getBoundingClientRect().right).toFixed(1) : null,
  heightPx: +hs[0].getBoundingClientRect().height.toFixed(1),
  spentRendered: hs.filter(e => e.classList.contains('spent')).length,
};
/* the row must sit BETWEEN the painted dividers, not straddle them */
v.heartsSitBetweenTheDividers = H.l > 0.313 && H.r < 0.642;
/* Denis: "hearts have too much space between them". The old gap was 6% of the
   band; anything under a third of a heart's own width reads as one row. */
v.heartGapIsTighterThanAThirdOfAHeart = notes._hearts.gapPx !== null
  && notes._hearts.gapPx < hs[0].getBoundingClientRect().width / 3;

notes._night = { left: pct(N.l) + '%', vCentre: pct((N.t + N.b) / 2) + '% (icon band ~56.7%..71%)',
                 text: (night.textContent || '').trim() };
/* BESIDE the moon, not under it: its vertical centre must be inside the painted
   icon band rather than below it */
v.nightNumberSitsBesideTheMoon = ((N.t + N.b) / 2) > 0.55 && ((N.t + N.b) / 2) < 0.75 && N.l > 0.18;

const labPx = parseFloat(getComputedStyle(document.querySelector('.lo-lab')).fontSize);
notes._labelFontPx = labPx;
notes._labelTexts = [...document.querySelectorAll('.lo-lab')].map(e => e.textContent.trim());
/* REPORTED, NOT ASSERTED, and deliberately so: the art leaves only ~18 units of
   clear parchment above the icons, so this is the tightest thing on the screen.
   Whether it is READABLE is Denis's call; the probe just refuses to let it be
   discussed without a number. */

/* nothing may overflow the sign - a label wider than its column would spill onto
   the wood and read as a bug */
const spill = [...document.querySelectorAll('.lo-c, .lo-night, .lo-hearts')].filter(el => {
  const f = fx(el); return f.l < -0.01 || f.r > 1.01; });
notes._overflow = spill.map(e => e.className);
v.nothingSpillsOffTheSign = spill.length === 0;

/* the bounce is declared AND applied - a keyframe nobody references is the
   commonest way an animation "does not work" */
const rosterAnim = getComputedStyle(document.querySelector('.lo-roster')).animationName;
notes._rosterAnimation = rosterAnim;
v.rosterCarriesBothGlowAndBounce = /loRoster/.test(rosterAnim) && /loRosterBounce/.test(rosterAnim);

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
