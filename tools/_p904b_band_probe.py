# -*- coding: utf-8 -*-
u"""P904b: the band probe gets to the dice the way every other probe does.

It called FXH.match and then tapped the roll button itself. match() returns when
the match reaches `idle`, which is BEFORE any dice are dealt - the rows measured
zero height and the sampler collected nothing at all. rollAndSettle is the
helper that exists for this and every other probe uses it.

Then the flight is driven by _setDieVal on two dice, which P898 measured going
through reDrawDieFace to D3.roll to _physQueue - a real physics throw of 1017
frame-ms. Tapping the roll button a second time would need a legal selection
first, which is a different thing to get right and nothing to do with this
measurement.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', 'apv_band_extent.js')
s = io.open(P, encoding='utf-8', newline='').read()

OLD = u"""/* a real roll, sampled densely through the flight - a settled-only reading
   would miss the whole of the drop, which is the case this exists to catch */
const btn = document.getElementById('btnRoll');
if (!btn) return Object.assign(out, {err: 'no roll button'});
grab('before');
FXH.tap(btn);
const t0 = Date.now();
while (Date.now() - t0 < 9000) { grab('flight'); await FXH.sleep(60);
  if (rolling() === 0 && Date.now() - t0 > 1500) break; }
await FXH.until(() => rolling() === 0, 15000);
for (let i = 0; i < 5; i++) { grab('settled'); await FXH.sleep(120); }"""

NEW = u"""/* GET TO THE DICE THE WAY EVERY OTHER PROBE DOES. match() returns at `idle`,
   which is before a single die has been dealt - the first version of this
   tapped btnRoll itself and sampled an empty table, reporting rows of zero
   height and no dice at all. */
const rs = await FXH.rollAndSettle();
out.rolled = {ok: rs.ok, why: rs.why, freeDice: rs.freeDice};
if (!rs.ok) return Object.assign(out, {err: 'never got to the dice: ' + rs.why});
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
for (let i = 0; i < 4; i++) { grab('settled'); await FXH.sleep(120); }"""

if s.count(OLD) != 1:
    sys.exit('ANCHOR x%d (nothing written)' % s.count(OLD))
s = s.replace(OLD, NEW)

# the verdict must also require that dice were actually there
OLD2 = u"""  theProbeSawAFlight: out.sampled.whileFlying >= 3,
  theProbeSawASettle: out.sampled.settled >= 3,"""
NEW2 = u"""  thereWereDiceAtAll: out.sampled.total > 0 &&
                      !!out.extentSettled && out.extentSettled.bottom > 0,
  theProbeSawAFlight: out.sampled.whileFlying >= 3,
  theProbeSawASettle: out.sampled.settled >= 3,"""
if s.count(OLD2) != 1:
    sys.exit('ANCHOR2 x%d (nothing written)' % s.count(OLD2))
s = s.replace(OLD2, NEW2)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: the band probe uses rollAndSettle and drives a real flight')
