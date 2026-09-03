# -*- coding: utf-8 -*-
u"""P931 (brief 3.9): silver to 120g, stock 3 - both fields, and saved runs too.

RULED by Denis 2026-09-03: "make it cheap for now." Measured at 14 matches per
arm, silver's match total is indistinguishable from iron's - difference -0.8%,
95% CI [-29%, +28%] - so 1.5x iron is excluded and every point in the interval
prices silver NEAR iron. Fair value is 0.71-1.28x iron's 100g, i.e. 71-128g.

THE BRIEF'S STARTING POINT IS ONE PATCH STALE. 3.9 says "from 580g"; the file
already reads 320, cut by P892. The ruling's destination is unchanged.

120g SITS NEAR THE TOP OF THE MEASURED BAND ON PURPOSE - the benefit of the
doubt goes to end-game defensive value, which the unreachable-target harness is
blind to BY CONSTRUCTION: it removes the target so the cap is the only way a
match ends, which is exactly the situation in which a defensive die would earn
its keep. It collides with neither iron at 100 nor flint at 150.

AND THE STOCK MOVES WITH IT, because stock 1 is the SECOND place "silver is
premium" is written down. Repricing alone ships a 120g die carrying jade's
scarcity. Stock 3 puts it beside lead and amber, where a cheap utility die
belongs. One fact, two homes - the same defect class as the rest of this work.

A SAVED RUN WOULD HAVE KEPT STOCK 1. _initDiceStock copies DICE_STORE's stock
into S.run.diceStock at run start, so an in-progress run freezes the old value
and the array edit never reaches it. The file already has this exact migration
for starstone ("was set-bonus stock 1, now flat-bonus stock 3"), which is both
the precedent and the proof that changing the array alone is not enough. Silver
gets the same treatment, guarded the same way so a player who has already SPENT
stock is not handed more.

NOT DONE, AND SAID OUT LOUD: the store's order. Its comment claims it "stays
cheap->expensive" and it does not - flint 150 sits before iron 100, amber 180
after lead 200 - so the claim was already false before silver moved. Display
order is a design call, not a bug fix, so it is flagged rather than changed.
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


sub(u"""  {mat:'silver',   price:320, stock:1, label:'Silver'},/* P892: was 580 */""",
    u"""  /* P931 (brief 3.9, ruled by Denis 2026-09-03): 320 -> 120, stock 1 -> 3.
     P892 had already cut 580 -> 320; the brief's "from 580" is a patch stale.
     THIS NUMBER IS A PLACEHOLDER AND THE INSTRUMENT THAT PRODUCED IT IS BLIND
     TO ONE THING. Measured at 14 matches per arm: silver's match total is
     indistinguishable from iron's, -0.8% with a 95% CI of [-29%, +28%], so 1.5x
     iron is excluded and every point in that interval prices silver near iron.
     Fair value 0.71-1.28x iron's 100g = 71-128g; 120 sits near the top of it,
     because the harness that measured it removes the target so the turn cap is
     the only way a match can end - and that is exactly the situation where a
     DEFENSIVE die would earn its keep. "Silver is for surviving the last turn
     of a close match" is not disproved by this; it is unasked. Testing it needs
     reachable-target matches at a high tier.
     So what is established is "not a premium die at any price above iron's".
     What is NOT established is silver's identity. Do not read 120 as a settled
     valuation.
     THE STOCK IS PART OF THE SAME FACT. A stock of 1 is the second place
     "premium" is written down, and repricing alone would ship a cheap die
     carrying jade's scarcity. 3 puts it beside lead and amber. */
  {mat:'silver',   price:120, stock:3, label:'Silver'},""",
    '1 the price and stock')

sub(u"""    if(S.run.diceStock&&typeof S.run.diceStock.starstone==='number'&&S.run.diceStock.starstone<3){
      S.run.diceStock.starstone=3;
    }""",
    u"""    if(S.run.diceStock&&typeof S.run.diceStock.starstone==='number'&&S.run.diceStock.starstone<3){
      S.run.diceStock.starstone=3;
    }
    /* P931: the same migration for Silver (brief 3.9 - was 320/stock 1, now
       120/stock 3). _initDiceStock copies DICE_STORE's stock into
       S.run.diceStock at run start, so an in-progress run froze the old value
       and the array edit alone would never reach it. Guarded the same way as
       starstone above: only RAISED to the new default, so a player who has
       already spent stock this run is not handed more. */
    if(S.run.diceStock&&typeof S.run.diceStock.silver==='number'&&S.run.diceStock.silver<3){
      S.run.diceStock.silver=3;
    }""",
    '2 the saved-run migration')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# BOTH FIELDS MOVED, which is the whole ruling
if code.count("{mat:'silver',   price:120, stock:3, label:'Silver'}") != 1:
    sys.exit('the silver row is not price 120 / stock 3 exactly once (nothing written)')
if "price:320" in code or "price:580" in code:
    sys.exit('an old silver price survives (nothing written)')
# the neighbours it must not collide with are untouched
for row, why in ((u"{mat:'iron',     price:100, stock:4, label:'Iron'}", 'iron'),
                 (u"{mat:'flint',    price:150, stock:3, label:'Flint'}", 'flint')):
    if code.count(row) != 1:
        sys.exit('%s was disturbed (nothing written)' % why)
# and 120 collides with neither
_prices = [int(m.group(1)) for m in re.finditer(r"\{mat:'\w+',\s*price:(\d+),", code)]
if _prices.count(120) != 1:
    sys.exit('120 is not unique among store prices (nothing written)')
# THE MIGRATION EXISTS AND MIRRORS ITS PRECEDENT - raise-only, same guard shape
if code.count('S.run.diceStock.silver=3') != 1:
    sys.exit('the saved-run migration is not present exactly once (nothing written)')
if code.count('S.run.diceStock.silver<3') != 1:
    sys.exit('the migration is not guarded as raise-only (nothing written)')
if code.count('S.run.diceStock.starstone=3') != 1:
    sys.exit('the starstone migration it copies was disturbed (nothing written)')
# and the array stock the migration targets actually says 3
_m = re.search(r"\{mat:'silver',\s*price:120,\s*stock:(\d+)", code)
if not _m or _m.group(1) != '3':
    sys.exit('the migration target does not match the array stock (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
