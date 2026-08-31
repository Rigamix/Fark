# -*- coding: utf-8 -*-
u"""P892: the pity metric measures a population its own survival gate excludes,
band 0 is unreachable and comes out, and Silver's price comes down.

THE PITY METRIC IS BACKWARDS, NOT INSENSITIVE. agg.noBuyByN3 increments inside
the night loop, after `if(dead)break;`, so only a run that survived night 3 can
contribute. The output then divides by RUNS - every run, including the ones
that died on night 1. Survivor numerator, whole-population denominator.

And the two failure modes are the SAME failure. A run that cannot afford a 180g
amber on 100 starting gold is a run that also loses its seats and dies before
night 3. So the numerator empties exactly when pity is most severe: the metric
is quietest at the moment it should be loudest. That is why it reads 0% under
every input including all-zero win rates - not insensitivity to the constants,
but a quantity measured against the wrong population. The same shape as the
bustsPerMatch zero, which also passed at full strength while measuring
something its own gate had already excluded.

The fix is a denominator built from the population the numerator is drawn from,
counted at the test rather than inferred. agg.alive[2] would still be wrong: it
counts runs that STARTED night 3, and the test runs after night 3's match and
shop, so a run that died in that match is in that denominator and can never be
in the numerator.

pG2byN3 and pG3byN6 are deliberately NOT changed. They are joint probabilities
- "what fraction of ALL runs reach G2 by night 3" - and a run that died did not
reach it, so RUNS is the right denominator there. Saying so, because the next
reader will otherwise fix them by analogy.

BAND 0 IS DELETED RATHER THAN NOTED. `fam` is seeded with one family die from
the starter draft and never shrinks, so gearLevel cannot return 0 and PWIN[0] /
BWIN[0] are never read - proven twice, by a 40,000-run occupancy census and by
moving PWIN[0] between 0.0 and 1.0 with no effect on runsWon. A dead row in a
four-entry table invites somebody to tune a number that does nothing, which is
how spawnBankPop survived. Deleting the rows alone would risk a silent NaN if
band 0 ever became reachable, so gearLevel's own dead branch is where the
invariant is stated and floored.

SILVER 580 -> 320, in all three places it is written. Two measurements point the
same way. In play, two silver beat two 100g irons by 0.8-1.3pp - inside noise -
so a 580g die buys what 200g of iron buys. And PWIN[2] was overstated by ~18pp
in exactly the band silver occupies, so the corrected economy makes 580g HARDER
to reach than the old model implied. Overpriced on both counts.

320 rather than 200, and the reasoning is on the record so it can be argued
with: silver carries a real consistency premium that a fixed-policy win-rate
delta under-captures - its per-turn bust rate is roughly a third of bone's -
and an archived ruling measured that advantage MONOTONE IN PUSH DEPTH, running
from 0.126 to 0.864 across seventeen policy cells. A player who adapts their
policy realises more of it than a fixed bank500 comparison can show. 320 also
puts it where a no-effect statistical die belongs on this ladder: above amber's
180 and below the effect-carrying family dice at 500 and up. Silver at 580 sat
ABOVE obsidian while having `effect:null`, which is the part that is hard to
defend at any push depth.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. the pity denominator ─────────────────────────────────────────
sub(u"""  var agg={g2ByN3:0,g3ByN6:0,noBuyByN3:0,dead:0,won:0,""",
    u"""  /* P892: reachedN3 is the pity metric's DENOMINATOR, counted at the test.
     noBuyByN3 can only increment for a run that survived to the night-3 shop,
     and the old output divided it by RUNS - a survivor numerator over the
     whole population. Worse, the two failure modes coincide: a run that
     cannot afford a 180g amber on 100 gold is a run that also loses its seats
     and dies before night 3, so the numerator empties exactly when pity is
     most severe. alive[2] would still be wrong - it counts runs that STARTED
     night 3, and this test runs after night 3's match. */
  var agg={g2ByN3:0,g3ByN6:0,noBuyByN3:0,reachedN3:0,dead:0,won:0,""",
    '1 the denominator counter')

sub(u"""      if(night===3){if(gearLevel(fam)>=2)g2Stamp=true;if(!boughtEver)agg.noBuyByN3++;}""",
    u"""      if(night===3){agg.reachedN3++;if(gearLevel(fam)>=2)g2Stamp=true;if(!boughtEver)agg.noBuyByN3++;}""",
    '2 counted at the test')

sub(u"""    pityNoBuyByN3:Math.round(100*agg.noBuyByN3/RUNS),""",
    u"""    /* P892: OF THE RUNS THAT GOT THERE, not of all runs - see reachedN3.
       pityBase is reported beside it so the denominator is never in doubt.
       pG2byN3 and pG3byN6 above are deliberately left over RUNS: they are
       JOINT probabilities - what fraction of all runs reach G2 by night 3 -
       and a run that died did not reach it. Do not "fix" them by analogy. */
    pityNoBuyByN3:agg.reachedN3?Math.round(100*agg.noBuyByN3/agg.reachedN3):0,
    pityBase:agg.reachedN3,""",
    '3 the corrected output')

# ── 2. band 0 comes out ─────────────────────────────────────────────
sub(u"""  var PWIN=cfg.pwin||{0:0.48,1:0.55,2:0.62,3:0.68};
  var BWIN=cfg.bwin||{0:0.30,1:0.45,2:0.55,3:0.62};""",
    u"""  /* P892: BAND 0 IS GONE. `fam` is seeded with one family die by the starter
     draft and never shrinks, so gearLevel cannot return 0 and these rows were
     never read - proven by a 40,000-run occupancy census and by moving the
     old PWIN[0] between 0.0 and 1.0 with no effect on runsWon. A dead row in
     a four-entry table invites tuning a number that does nothing.
     STALE, NOT CONTAMINATED, and dated: git log -S on each literal returns
     only its birth commit, and that file predates the silver bust-save defect
     by 91 minutes. But 1,140 commits of tuning later, PWIN[2] measures 0.443
     against the 0.62 below - ~18pp overstated, and the band silver lives in.
     Left as-is pending the real-engine ladder, which is the only measurement
     that is not this model. */
  var PWIN=cfg.pwin||{1:0.55,2:0.62,3:0.68};
  var BWIN=cfg.bwin||{1:0.45,2:0.55,3:0.62};""",
    '4 band 0 deleted from the literals')

sub(u"""    if(fam.length>=1)return 1;
    return 0;""",
    u"""    /* P892: the floor is 1, not 0. `fam` always holds the starter draft's
       die, so this branch is unreachable - and it is where the invariant
       belongs, because deleting PWIN[0] would otherwise turn a future
       reachable band 0 into an undefined win rate, which reads as "the
       player loses every seat" rather than as an error. */
    return 1;""",
    '5 the dead branch floors at band 1')

# ── 3. Silver's price, in all three places ──────────────────────────
sub(u"""  {mat:'silver',   price:580, stock:1, label:'Silver'},""",
    u"""  {mat:'silver',   price:320, stock:1, label:'Silver'},/* P892: was 580 */""",
    '6 the shop price')

sub(u"""  {id:'silver',name:'SILVER',icon:'\U0001f518',cost:580,""",
    u"""  /* P892: 580 -> 320. Measured, two silver beat two 100g irons by 0.8-1.3pp,
     inside noise - a 580g die buying what 200g of iron buys - and the economy
     model's win rate for the band silver occupies was overstated by ~18pp, so
     580 was harder to reach than intended as well. 320 keeps the consistency
     premium (its per-turn bust rate is about a third of bone's, and that
     advantage grows the deeper a player pushes) while putting a die with
     effect:null below the effect-carrying family dice rather than above
     obsidian. */
  {id:'silver',name:'SILVER',icon:'\U0001f518',cost:320,""",
    '7 the die cost')

sub(u"""  var FAM_PRICE={amber:180,obsidian:500,silver:580,starstone:700,vagabond:700,jade:750,jade2:1800};""",
    u"""  /* P892: silver 580 -> 320 here too. Three places hold this price - the
     shop row, the die def and this table - and they have to move together. */
  var FAM_PRICE={amber:180,obsidian:500,silver:320,starstone:700,vagabond:700,jade:750,jade2:1800};""",
    '8 the economy model price')

# ── post-asserts, against code with comments stripped ───────────────
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
if 'agg.noBuyByN3/RUNS' in code:
    sys.exit('pity still divides by RUNS (nothing written)')
if code.count('agg.reachedN3++') != 1:
    sys.exit('the denominator is not counted exactly once (nothing written)')
if '0:0.48' in code or '0:0.30' in code:
    sys.exit('a band-0 constant survives (nothing written)')
# the joint metrics must be UNCHANGED - do not fix by analogy
for keep in ('agg.g2ByN3/RUNS', 'agg.g3ByN6/RUNS'):
    if keep not in code:
        sys.exit('%s was changed and should not have been (nothing written)' % keep)
# the price moved in all three places and nowhere kept the old one
if re.search(r"silver[^\n]{0,40}580", code) or re.search(r"580[^\n]{0,40}silver", code):
    sys.exit('a silver 580 survives in code (nothing written)')
if len(re.findall(r'320', code)) < 3:
    sys.exit('the new price is not written in three places (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
