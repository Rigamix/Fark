# -*- coding: utf-8 -*-
u"""P912: the driver waits for the previous match's end-route to land before
starting the next one.

THE BOSS-CHAINING FAILURE HAS A CANDIDATE, and it is a race rather than state.
launchBossMatch does not touch the night at all - it reads TIERS[S.run.tier].boss
and calls showScreen('match', ...) inside a setTimeout of 80ms. So three
theories about run state (a dead run, a stale night, an unseen boss) were all
looking in the wrong place: the run was fine, the night was irrelevant, and what
the failure showed was screen-gauntlet with G null.

Which is what it looks like when the PREVIOUS match's end-route navigates to the
gauntlet AFTER the next launch's 80ms timeout has already put us on the match
screen. First launch wins the race because nothing is behind it; the second one
gets overwritten.

SO THE DRIVER SETTLES BEFORE IT RETURNS. After _endMatchFired it waits for the
active screen to stop changing - two consecutive reads the same, or a bounded
give-up - so a caller that immediately starts another match is not racing a
navigation that has not happened yet. That is cheaper and more honest than
sleeping a fixed guess: it waits for the thing rather than for a duration.

STATED AS A HYPOTHESIS, NOT A FIX. launchSeat chaining already worked six for
six without this, so nothing here is known to have been broken by the race -
only that the race exists and the boss path is where it would bite. The test is
three consecutive BOSS matches, which is the one thing P911 could not answer,
and it is what the ladder's boss cells need.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', 'fark_driver.js')
s = io.open(P, encoding='utf-8', newline='').read()

OLD = u"""    const pPts = (G && G.pPts) || 0, oPts = (G && G.oPts) || 0;
    return {"""
NEW = u"""    /* P912: LET THE END-ROUTE LAND BEFORE ANYONE STARTS ANOTHER MATCH.
       launchBossMatch calls showScreen('match', ...) inside a setTimeout of
       80ms, so a caller that launches the instant _endMatchFired goes true is
       racing the navigation the finished match is about to do - and the loser
       is the new match, which is exactly the screen-gauntlet-with-G-null the
       boss path kept returning.
       Waits for the ACTIVE SCREEN TO STOP CHANGING rather than for a duration:
       two consecutive reads the same, with a bounded give-up so a game that
       never settles costs one match and not the run. */
    const screensNow = () => {
      try { return [].slice.call(document.querySelectorAll('.screen.active'))
        .map(function (e) { return e.id; }).join(','); } catch (e) { return '?'; }
    };
    let prevScreens = null, settleMs = null;
    const settleT0 = Date.now();
    while (Date.now() - settleT0 < 8000) {
      const now = screensNow();
      if (now === prevScreens) { settleMs = Date.now() - settleT0; break; }
      prevScreens = now;
      await sleep(350);
    }

    const pPts = (G && G.pPts) || 0, oPts = (G && G.oPts) || 0;
    return {
      settledOn: prevScreens, settleMs,"""

if s.count(OLD) != 1:
    sys.exit('ANCHOR x%d (nothing written)' % s.count(OLD))
s = s.replace(OLD, NEW)

code = s
if code.count('P912: LET THE END-ROUTE LAND') != 1:
    sys.exit('the settle is not present exactly once (nothing written)')
if 'settledOn' not in code or 'settleMs' not in code:
    sys.exit('the settle does not report what it settled on (nothing written)')
# it must run AFTER the match loop, not inside it
if code.index('P912: LET THE END-ROUTE LAND') < code.index('while (!G._endMatchFired)'):
    sys.exit('the settle runs before the match loop (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: the driver settles before returning')
