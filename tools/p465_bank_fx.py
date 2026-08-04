# -*- coding: utf-8 -*-
"""P465 - BANK_FX: the mirror pair's arithmetic in one table.

RULED: build the table over handleBank + finOpp, the nine mechanics that appear
on both sides. Measured first (docs/MIRROR_DIFF.md): all nine are the same rule
seen from two seats, so this is consolidation and not a ruling.

WHAT GOES IN THE TABLE, AND WHAT DELIBERATELY DOES NOT.

The RULE is shared. The PRESENTATION is not, and forcing it together would be
inventing a merge rather than finding one - the player accumulates a bonusMsg
string, the rival calls spawnPop and a delayed DLG.triggerCard. Those are two
genuinely different surfaces that happen to fire at the same moment.

The GUARDS are also not shared: each side keeps its own once-flag because they
must fire once PER SEAT, not once between them.

So the table takes THE ARITHMETIC - which is exactly where drift costs, because
a number changed on one side and not the other is invisible until someone plays
both seats and compares.

FOUR ROWS THIS PASS, not nine. steal_pct, steal_low_bank and block_low_bank MOVE
points between pools rather than only adjusting the amount, so their row needs a
second return value; periodic_drain does not touch the banked amount at all; and
challenge has to express WHEN its terms are read (frozen at declaration for the
player, live for the rival) which no arithmetic-only row can carry. Those four
are a second shape and get their own pass rather than being bent into this one.

ONE APPROVED BEHAVIOUR CHANGE, and it is the point rather than a side effect:

  gain_when_ahead   the player defends with (eff.amount||500), the rival used
                    npc.effect.amount BARE. One row carries the default, so both
                    seats inherit it. No-op today - corvus_writ is the only card
                    with the mechanic and it defines amount:500 - and it removes
                    a NaN the day a second card omits it.

  flat_bonus        same shape, smaller: the rival's `pts+=eff.amount` becomes
                    `+(e.amount||0)`. The player's condition already required
                    amount>0; the rival's did not.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── the table, declared above handleBank ──
ANCH = u"function handleBank("
assert s.count(ANCH) == 1, 'handleBank def matched %d' % s.count(ANCH)
s = s.replace(ANCH, u"""/* BANK_FX - the arithmetic shared by handleBank (the player's bank) and finOpp
   (the rival's). Measured as the same rule on both sides before this was
   written; see docs/MIRROR_DIFF.md.
   Each row takes the amount being banked and the effect def, and returns the
   new amount. Nothing here touches score pools, messages or guards - those
   differ per seat on purpose and stay at the call sites.
   The defaults live HERE so both seats inherit them: the player had
   (eff.amount||500) for gain_when_ahead and the rival had none. */
var BANK_FX={
  flat_bonus:        function(a,e){return a+(e.amount||0);},
  double_first_bank: function(a,e){return a*2;},
  halve_first_bank:  function(a,e){return a-Math.floor(a/2);},
  gain_when_ahead:   function(a,e){return a+(e.amount||500);}
};

""" + ANCH)

def one(old, new, label):
    global s
    assert s.count(old) == 1, '%s matched %d' % (label, s.count(old))
    s = s.replace(old, new)

# ── flat_bonus ──
one(u"total+=eff.amount;", u"total=BANK_FX.flat_bonus(total,eff);", 'P flat')
one(u"pts+=eff.amount;",   u"pts=BANK_FX.flat_bonus(pts,eff);",     'R flat')

# ── halve_first_bank: `half` is reused in the message, so derive it ──
one(u"var half=Math.floor(total/2);total-=half;",
    u"var half=total-BANK_FX.halve_first_bank(total,eff);total-=half;", 'P half')
one(u"var half=Math.floor(pts/2);pts-=half;",
    u"var half=pts-BANK_FX.halve_first_bank(pts,eff);pts-=half;", 'R half')

# ── gain_when_ahead: the rival gains the player's default ──
one(u"total+=(eff.amount||500);", u"total=BANK_FX.gain_when_ahead(total,eff);", 'P gwa')
one(u"pts+=npc.effect.amount;",   u"pts=BANK_FX.gain_when_ahead(pts,npc.effect);", 'R gwa')

# ── double_first_bank: `total*=2;` is not unique, so scope by its neighbour ──
one(u"var _mtBefore=total;total*=2;",
    u"var _mtBefore=total;total=BANK_FX.double_first_bank(total,eff);", 'P dbl')

i = s.index(u"var _mtBonus=pts;")
seg = s[i:i + 220]
assert seg.count(u"pts*=2;") == 1, 'R dbl: %d occurrences near anchor' % seg.count(u"pts*=2;")
s = s[:i] + seg.replace(u"pts*=2;", u"pts=BANK_FX.double_first_bank(pts,eff);") + s[i + 220:]

assert s != orig, 'nothing changed'
assert s.count('var BANK_FX={') == 1
# eight call sites, four rows, both seats each
for row, n in [('flat_bonus', 2), ('double_first_bank', 2),
               ('halve_first_bank', 2), ('gain_when_ahead', 2)]:
    assert s.count('BANK_FX.' + row + '(') == n, \
        '%s called %d times, expected %d' % (row, s.count('BANK_FX.' + row + '('), n)
# the old arithmetic is gone from executable code, not merely from sight
import re
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
for gone in [u"total+=eff.amount;", u"pts+=eff.amount;", u"total+=(eff.amount||500);",
             u"pts+=npc.effect.amount;", u"var half=Math.floor(total/2);total-=half;",
             u"var half=Math.floor(pts/2);pts-=half;"]:
    assert gone not in body, 'old arithmetic still live: %s' % gone
# the four NOT in this pass must be untouched
for later in ['steal_pct', 'steal_low_bank', 'block_low_bank', 'periodic_drain']:
    assert ("mechanic==='%s'" % later) in body, '%s should not have moved' % later
    assert ('BANK_FX.' + later) not in s, '%s was not meant to be in this pass' % later

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P465 applied: BANK_FX, 4 rows, 8 call sites across both seats')
