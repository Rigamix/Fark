# -*- coding: utf-8 -*-
"""P466 - the second-shape pass, and the bug the measurement found.

RULED: continue the table with the group that did not fit BANK_FX's
amount-in/amount-out shape. Reading them shows that group is not one shape
either, so this takes the two that genuinely share arithmetic and says plainly
why the other three do not.

  steal_pct        Math.ceil(a*pct) on BOTH sides. Real shared formula, and a
                   ceil changed to floor on one side only would be invisible.
  periodic_drain   Math.max(0, pool-amount) on BOTH sides. The CLAMP is the
                   valuable part: lose it on one side and only that side's
                   score can go negative.

  steal_low_bank   the "formula" is take all of it. A row whose body is
  block_low_bank   `return a` or `return 0` is ceremony, and the player
                   expresses zeroing by ABORTING the bank (_bankAborted,
                   _turnScoreClear, early return) while the rival zeroes a
                   running local and continues. Not the same expression.
  challenge        two genuinely different algorithms - see below.

THE BUG. challenge's rival branch double-charges:

    var penalty=Math.min(eff.penalty,G.oPts+pts);
    pts=Math.max(0,pts-penalty);
    G.oPts=Math.max(0,G.oPts-Math.max(0,penalty-(eff.penalty-penalty)));

`penalty-(eff.penalty-penalty)` is `2*penalty - eff.penalty`, which collapses to
`penalty` whenever they can afford it - so the pool pays the FULL penalty after
the bank has already paid it. Computed, not reasoned:

    pool 1000, bank 200, penalty 500  ->  loses 700
    pool 1000, bank 600, penalty 500  ->  loses 1000
    pool 1000, bank 500, penalty 500  ->  loses 1000

The player's mirror loses exactly 500 every time. AND THE CODE'S OWN MESSAGE
SAYS `LOST 500` WHILE TAKING UP TO 1000 - the announcement is the intent, which
is what makes this a bug rather than a deliberate boss handicap.

Fixed to take exactly the penalty, bank first, capped at what they hold - which
is what the player's side does and what the card claims.

THIS MAKES BOSSES SLIGHTLY STRONGER, since they stop being over-charged. That is
a balance consequence of fixing arithmetic, not a design change, but it is worth
knowing before the next difficulty pass.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── the two rows that genuinely share arithmetic ──
ANCH = u"var BANK_FX={"
assert s.count(ANCH) == 1, 'BANK_FX matched %d' % s.count(ANCH)
s = s.replace(ANCH, u"""/* BANK_TAKE / SCORE_DRAIN - the second shape. These do not fit BANK_FX because
   they are not amount-in/amount-out: one computes how much MOVES between pools,
   the other rewrites a score pool and never touches the bank.
   Only the two mechanics with a real shared formula are here. steal_low_bank and
   block_low_bank take all of it or none of it - a row returning `a` or `0` is
   ceremony - and the player expresses zeroing by aborting the whole bank while
   the rival zeroes a running local, which is not the same expression. */
var BANK_TAKE={
  steal_pct: function(a,e){return Math.ceil(a*(e.pct||0));}
};
var SCORE_DRAIN={
  /* the Math.max(0,...) clamp is the point: lose it on one side only and just
     that side's score can go negative. */
  periodic_drain: function(pool,e){return Math.max(0,pool-(e.amount||0));}
};

""" + ANCH)

def one(old, new, label):
    global s
    assert s.count(old) == 1, '%s matched %d' % (label, s.count(old))
    s = s.replace(old, new)

one(u"var steal=Math.ceil(total*eff.pct);total-=steal;G.oPts+=steal;",
    u"var steal=BANK_TAKE.steal_pct(total,eff);total-=steal;G.oPts+=steal;", 'P steal_pct')
one(u"var steal=Math.ceil(pts*eff.pct);pts-=steal;G.pPts+=steal;",
    u"var steal=BANK_TAKE.steal_pct(pts,eff);pts-=steal;G.pPts+=steal;", 'R steal_pct')
one(u"G.pPts=Math.max(0,G.pPts-npc.effect.amount);",
    u"G.pPts=SCORE_DRAIN.periodic_drain(G.pPts,npc.effect);", 'P drain')
one(u"G.oPts=Math.max(0,G.oPts-npc.effect.amount);",
    u"G.oPts=SCORE_DRAIN.periodic_drain(G.oPts,npc.effect);", 'R drain')

# ── the challenge double-charge ──
BAD = (u"pts=Math.max(0,pts-penalty);"
       u"G.oPts=Math.max(0,G.oPts-Math.max(0,penalty-(eff.penalty-penalty)));")
assert s.count(BAD) == 1, 'challenge rival branch matched %d' % s.count(BAD)
s = s.replace(BAD, u"""/* THE BANK PAYS FIRST, THEN THE POOL, AND THE TOTAL IS EXACTLY `penalty`.
               What was here computed the pool's share as penalty-(eff.penalty-penalty),
               i.e. 2*penalty-eff.penalty, which collapses to the FULL penalty
               whenever they could afford it - so the pool paid it again after
               the bank already had. pool 1000 / bank 600 / penalty 500 cost
               them 1000. The player's mirror loses exactly 500, and this
               branch's own message says LOST 500 while taking twice that. */
            var _chFromBank=Math.min(pts,penalty);
            pts=Math.max(0,pts-_chFromBank);
            G.oPts=Math.max(0,G.oPts-(penalty-_chFromBank));""")

assert s != orig, 'nothing changed'
assert s.count('var BANK_TAKE={') == 1 and s.count('var SCORE_DRAIN={') == 1
assert s.count('BANK_TAKE.steal_pct(') == 2, 'steal_pct wired %d times' % s.count('BANK_TAKE.steal_pct(')
assert s.count('SCORE_DRAIN.periodic_drain(') == 2
assert s.count('_chFromBank') == 3

import re
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
for gone in [u"Math.ceil(total*eff.pct)", u"Math.ceil(pts*eff.pct)",
             u"penalty-(eff.penalty-penalty)",
             u"G.pPts=Math.max(0,G.pPts-npc.effect.amount);"]:
    assert gone not in body, 'old code still live: %s' % gone
# BANK_FX is untouched by this pass
assert body.count('BANK_FX.') == 8, 'BANK_FX call count moved: %d' % body.count('BANK_FX.')
# the three deliberately excluded stay exactly as they were
for keep in ['steal_low_bank', 'block_low_bank']:
    assert ("mechanic==='%s'" % keep) in body
    assert ('BANK_TAKE.' + keep) not in s and ('BANK_FX.' + keep) not in s

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P466 applied: BANK_TAKE + SCORE_DRAIN (2 rows, 4 sites) + challenge double-charge fixed')
