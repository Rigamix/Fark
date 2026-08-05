# -*- coding: utf-8 -*-
u"""P468 - BUST_FX: the two true bust-path mirrors, defaults in one place.

RULED: ship gain_pts and punish_busts, the two of seven that survived reading as
real mirrors. The other five were a query beside a dispatch (single1_bonus,
single5_bonus, bust_bank_half), two deliberately different designs
(bust_survive), or an off-by-one needing a ruling (bust_immune_turns).

THE DUPLICATION HERE IS LITERAL, WHICH MAKES IT WORTH REMOVING. Each mechanic
has exactly ONE card, and the boss-side fallbacks are that card's real values
typed a second time:

  gain_pts       the_nightshift  amount:500                  boss falls back ||500
  punish_busts   judgment_npc    threshold:2, penalty:1500   boss falls back ||2, ||1500

(An earlier draft of this file named mabels_pinch and never_saw_a_robe. Those
came from a grep taking the nearest PRECEDING `id:` in a text window, which is
the previous card's - the same read-a-proxy-as-the-target mistake, on card
attribution this time. The probe reads NPC_CARDS directly and corrected it. The
numbers were right throughout; only the names were wrong.)

So the same three numbers live in the card definition AND in two `||` defaults,
while the PLAYER side has no defaults at all. Change the card and the fallbacks
go stale silently; remove a field and the player's side reads undefined.

One row per mechanic, both seats calling it - the same shape and the same fix as
gain_when_ahead in P465.

AND THE BOSS'S MESSAGE USES THE ROW TOO. It printed
`(_obNpc.effect.penalty||1500)` beside a deduction computed from the same
expression - correct today, and exactly the pattern that let challenge announce
500 while taking 1000. If a number is printed next to a deduction it reads from
the same source as the deduction.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

ANCH = u"var BANK_TAKE={"
assert s.count(ANCH) == 1, 'BANK_TAKE matched %d' % s.count(ANCH)
s = s.replace(ANCH, u"""/* BUST_FX - the bust path's two real mirrors. Each mechanic has exactly one
   card, and the boss side used to repeat that card's numbers as `||` fallbacks
   while the player side had none. The defaults live here now, so both seats
   read the same source and the card stays the only other place they appear. */
var BUST_FX={
  gain_pts:{amount:function(e){return (e&&e.amount)||500;}},
  punish_busts:{threshold:function(e){return (e&&e.threshold)||2;},
                penalty:function(e){return (e&&e.penalty)||1500;}}
};

""" + ANCH)

def one(old, new, label):
    global s
    assert s.count(old) == 1, '%s matched %d' % (label, s.count(old))
    s = s.replace(old, new)

# ── gain_pts, both seats ──
one(u"G.oPts+=eff.amount;", u"G.oPts+=BUST_FX.gain_pts.amount(eff);", 'P gain_pts')
one(u"G.pPts+=(_obNpc.effect.amount||500);",
    u"G.pPts+=BUST_FX.gain_pts.amount(_obNpc.effect);", 'O gain_pts')

# the boss's gain_pts MESSAGE repeats the same expression - caught by the
# old-form assert, which is the whole reason it is written as a list of exact
# strings rather than a count. A message reading its number from a second copy
# of the expression is the challenge pattern in miniature.
one(u"triggerCard(cid,_obNpc.name+' +'+(_obNpc.effect.amount||500),true);",
    u"triggerCard(cid,_obNpc.name+' +'+BUST_FX.gain_pts.amount(_obNpc.effect),true);",
    'O gain_pts message')

# ── punish_busts: threshold in the condition, penalty in the body ──
one(u"G.npcCardState.playerBustCount>=eff.threshold",
    u"G.npcCardState.playerBustCount>=BUST_FX.punish_busts.threshold(eff)", 'P threshold')
one(u"G.pPts=Math.max(0,G.pPts-eff.penalty);",
    u"G.pPts=Math.max(0,G.pPts-BUST_FX.punish_busts.penalty(eff));", 'P penalty')
one(u"G.npcCardState.oppBustCount>=(_obNpc.effect.threshold||2)",
    u"G.npcCardState.oppBustCount>=BUST_FX.punish_busts.threshold(_obNpc.effect)", 'O threshold')
one(u"G.oPts=Math.max(0,G.oPts-(_obNpc.effect.penalty||1500));",
    u"G.oPts=Math.max(0,G.oPts-BUST_FX.punish_busts.penalty(_obNpc.effect));", 'O penalty')
# the message must read from the same source as the deduction
one(u"triggerCard(cid,_obNpc.name+' −'+(_obNpc.effect.penalty||1500),true);",
    u"triggerCard(cid,_obNpc.name+' −'+BUST_FX.punish_busts.penalty(_obNpc.effect),true);",
    'O message')
# and the player's message likewise
one(u"_pendingBustTriggers.push({cid:cid,msg:npc.name+' −'+eff.penalty+'!'});",
    u"_pendingBustTriggers.push({cid:cid,msg:npc.name+' −'+BUST_FX.punish_busts.penalty(eff)+'!'});",
    'P message')

assert s != orig, 'nothing changed'
assert s.count('var BUST_FX={') == 1
assert s.count('BUST_FX.gain_pts.amount(') == 3, 'gain_pts wired %d' % s.count('BUST_FX.gain_pts.amount(')
assert s.count('BUST_FX.punish_busts.threshold(') == 2
assert s.count('BUST_FX.punish_busts.penalty(') == 4   # 2 deductions + 2 messages

import re
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
for gone in [u"_obNpc.effect.amount||500", u"_obNpc.effect.threshold||2",
             u"_obNpc.effect.penalty||1500", u"G.pPts-eff.penalty",
             u"G.oPts+=eff.amount;"]:
    assert gone not in body, 'old form still live: %s' % gone
# the five NOT shipped stay untouched - three were never pairs, one is two
# designs on purpose, one needs a ruling
for keep in ['bust_survive', 'bust_immune_turns', 'bust_bank_half',
             'single1_bonus', 'single5_bonus']:
    assert ("mechanic==='%s'" % keep) in body, '%s vanished' % keep
    assert ('BUST_FX.' + keep) not in s, '%s was not meant to move' % keep
# earlier tables undisturbed
assert body.count('BANK_FX.') == 8 and body.count('BANK_TAKE.steal_pct(') == 2

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P468 applied: BUST_FX, 2 mechanics, 8 call sites, defaults in one place')
