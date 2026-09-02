# -*- coding: utf-8 -*-
u"""P908: the gate's scope is written where the gate is, and the outcome check
it cannot see is added beside it.

WHAT THE PAIR TEST CATCHES, AND WHAT IT DOES NOT. Targets 2.5x apart, totals
must move 1.5x. That catches "not playing the game" - a driver that scores the
same whatever it is asked for. It does NOT catch "playing it slightly wrong": a
driver scaling at 1.6x passes while being meaningfully off. At n=2, where the
variance is enormous, that is the correct trade - but it means A PASS IS NOT
CALIBRATION, and somebody will eventually read it as one. So the limit is
stated at the function rather than in a message nobody will find.

AND THE CHECK THE PAIR TEST CANNOT SEE. Scaling correctly and winning 0% or
100% are both broken, and the outcome is a different axis from the score.
Ten matches at one tier before six hours are committed: expect somewhere between
two and eight wins. Twelve minutes, and 0/8 fails it immediately without any
argument about luck - which is exactly what the original run needed and did not
have. It is deliberately wide: this is a smoke test for a broken driver, not a
measurement of difficulty, and a narrow band here would refuse real results.

THE RELOAD, and what it costs. Reloading the page between matches is the right
answer for a ladder - independence by construction rather than by argument - so
the runner does one match per shoot.js invocation. The cost is a boot per match,
about ten seconds against a seventy-second match, and it is recorded here
because it also makes one thing permanently unmeasurable through that path:
whether the GAME can run consecutive matches. That question is left open with
its lead rather than closed by a workaround - launchSeat(seatIdx) at 45740 is
the entry the gauntlet uses, and S.run.night.seatsPlayed is the array that says
which seats remain. Two attempts to reach it by tapping DOM found no .seat-row
elements at all, which is a fact about my selector or my timing and not yet a
fact about the game.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', 'fark_driver.js')
s = io.open(P, encoding='utf-8', newline='').read()


def sub(old, new, label):
    global s
    if s.count(old) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (s.count(old), label))
    s = s.replace(old, new)
    print('  ' + label)


sub(u"""  const TARGET_SPREAD = 2.5, TOTAL_SPREAD = 1.5;
  function sanityScale(lowRes, highRes) {""",
    u"""  /* WHAT THIS CATCHES AND WHAT IT DOES NOT, because a pass will be read as
     more than it is. 2.5x targets against 1.5x totals catches NOT PLAYING THE
     GAME - a score that is flat against the match it is in. It does not catch
     playing it slightly wrong: a driver scaling at 1.6x passes here while being
     meaningfully off. At n=2, where the variance is enormous, that is the right
     trade - but a pass is a smoke test, NOT CALIBRATION, and nothing downstream
     should treat it as evidence that the driver plays well. It is evidence that
     the driver plays. */
  const TARGET_SPREAD = 2.5, TOTAL_SPREAD = 1.5;
  function sanityScale(lowRes, highRes) {""",
    '1 the pair test states its scope')

sub(u"""  return {POLICIES, bankRule, policyByKey, playMatch, sanity, sanityScale,
          targetOf, extractWhy, until, sleep, tap,
          TARGET_SPREAD, TOTAL_SPREAD};""",
    u"""  /* THE OUTCOME CHECK, on the axis the pair test cannot see. Scoring that
     scales correctly and winning 0% or 100% are both broken, and the score
     gate would pass either. Ten matches at one tier before six hours are
     committed; two to eight wins. That band is deliberately wide - this is a
     smoke test for a broken driver, not a measurement of difficulty, and a
     narrow one would refuse real results. The original run's 0 from 8 fails it
     immediately, with no argument about luck required. */
  const WIN_MIN = 2, WIN_MAX = 8, WIN_N = 10;
  function sanityWinRate(results) {
    const done = (results || []).filter(r => r && !r.err && !r.stalled);
    if (done.length < WIN_N) return {ok: false,
      why: 'only ' + done.length + ' of ' + WIN_N + ' matches completed; a win ' +
           'rate over fewer is not the check this is'};
    const wins = done.filter(r => r.win).length;
    if (wins < WIN_MIN || wins > WIN_MAX) return {ok: false, wins, n: done.length,
      why: wins + ' wins in ' + done.length + '. Anything outside ' + WIN_MIN +
           '-' + WIN_MAX + ' at one tier is a driver that is not playing, not a ' +
           'difficulty finding - the run this replaces went 0 from 8 while ' +
           'scoring a quarter of the target. Fix the driver, not the band.'};
    return {ok: true, wins, n: done.length};
  }

  /* ONE MATCH PER PAGE, and the runner enforces it rather than this file.
     Independence is the property a ladder is made of, and a reloaded page gives
     it by construction instead of by argument about what state was carried. The
     cost is a boot per match - about ten seconds against a seventy-second match
     - and one thing it hides: whether the GAME can run consecutive matches.
     That is left open rather than closed. launchSeat(seatIdx) at 45740 is the
     gauntlet's own entry and S.run.night.seatsPlayed says which remain; two
     attempts to reach it by tapping DOM found no .seat-row at all, which is a
     fact about my selector or my timing and not yet about the game. */
  const RELOAD_PER_MATCH = true;

  return {POLICIES, bankRule, policyByKey, playMatch, sanity, sanityScale,
          sanityWinRate, targetOf, extractWhy, until, sleep, tap,
          TARGET_SPREAD, TOTAL_SPREAD, WIN_MIN, WIN_MAX, WIN_N,
          RELOAD_PER_MATCH};""",
    '2 the outcome check and the reload note')

code = s
if 'sanityWinRate' not in code or code.count('function sanityWinRate') != 1:
    sys.exit('the outcome check is not defined exactly once (nothing written)')
if 'A PASS IS NOT' not in code and 'NOT CALIBRATION' not in code:
    sys.exit('the pair test does not state its scope (nothing written)')
if code.count('RELOAD_PER_MATCH') != 2:
    sys.exit('the reload note is not declared and exported (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done')
