# -*- coding: utf-8 -*-
u"""P914: the outcome gate says what it actually tests, and stops failing a
match that ended on the turn cap.

THE JUSTIFICATION WAS OVERSTATED. The gate refuses when hw >= ew, so what it
tests is "the outcome DID NOT RISE, and the easy cell cleared the floor" - not
"the outcome falls". At ten matches a cell, two wins against zero is a
difference of two events with heavily overlapping intervals, and a flat driver
produces that pairing routinely. The gate's purpose survives intact - it catches
a driver that does not play - but written down as a fall, somebody will later
cite 2-then-0 as evidence about difficulty. It isn't.

AND sanity() FAILED A LEGITIMATE MATCH, found by it firing. It required
winnerOverTarget between 0.8 and 2.5 - "somebody reached the target" - and the
first hard match ended 6250 against a target of 9500. Nobody reached it, because
A MATCH CAN END ON THE TURN CAP: TURN_CAP_PATRON is 8 and TURN_CAP_BOSS is 10,
and at a tier whose target is out of the policy's envelope, ending on the cap is
the NORMAL outcome rather than a broken one.

The fix is not to widen the band, which would have been the third time this
session a threshold got loosened to make a real result fit. It is to ask why the
match ended: a target reached OR a cap hit are both complete matches, and
neither is evidence of a broken driver. Only a match that ended for neither
reason is.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', 'fark_driver.js')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (s.count(old), label))
    s = s.replace(old, new)
    edits.append(label)


sub(u"""    if (!(res.winnerOverTarget >= 0.8 && res.winnerOverTarget <= 2.5))
      return {ok: false, why: 'nobody reached the target: winner had ' +
        Math.max(res.pPts, res.oPts) + ' against ' + res.target};""",
    u"""    /* A MATCH ENDS TWO WAYS, and only one of them is "somebody reached the
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
        (res.turnsUsed != null ? ' (turn ' + res.turnsUsed + ' of ' +
          res.turnCap + ')' : '') + ' - so it ended for neither legitimate reason'};""",
    '1 a capped match is a complete match')

sub(u"""     Two tiers, and the win rate must FALL. Flatness is the tell for the outcome
     the way it is for the score.
     SAME SCOPE NOTE AS THE OTHER PAIR: at ten matches a cell the variance is
     large, so this catches a driver that does not play, not one that plays
     slightly wrong. A pass is a smoke test, not calibration. */""",
    u"""     Two tiers, and the win rate must not RISE. Say that precisely, because
     the loose version is worse than useless: what the code below tests is
     `hw >= ew` refused, which is "the outcome did not rise, and the easy cell
     cleared the floor" - NOT "the outcome falls". At ten matches a cell, two
     wins against zero is a difference of two events with heavily overlapping
     intervals, and a flat driver produces that pairing routinely.
     SO A PASS IS NOT EVIDENCE ABOUT DIFFICULTY, and nobody should later cite a
     2-then-0 as if it were. Same scope note as the other pair: this catches a
     driver that does not play, not one that plays slightly wrong. A smoke
     test, not calibration. */""",
    '2 the gate states what it tests')

code = s
if 'res.hitTheCap' not in code:
    sys.exit('the cap ending is not accepted (nothing written)')
if 'the outcome did not rise' not in code:
    sys.exit('the gate still claims a fall (nothing written)')
if 'must FALL' in code:
    sys.exit('the overstated wording survives (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
