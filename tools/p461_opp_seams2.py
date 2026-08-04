# -*- coding: utf-8 -*-
"""P461 - the opponent's `bust` and `bankBonus` seams.

RULED: these two ship now - same clean-gate shape as roll and turnStart, no
open question left. commit needs its own scoping pass (10 genuinely different
re-scorings); deadRoll and rivalTurn are design questions, not build tasks.

WHY THESE TWO ARE GATES AND commit IS NOT, measured rather than felt:

  bust       `_oppBustOut()` is a NAMED inner function with 4 call sites, and
             every bust exit funnels through it. One call inside it covers all
             four. It first measured as a 9-site DECISION - four of those nine
             are this function's definition, its call, a comment and a counter.
             Reading them is what moved it.
  bankBonus  ONE canonical site: `G.oPts+=pts;_npcActuallyBanked=true`. The
             rival's bank landing, with every card and badge adjustment to
             `pts` already applied.

RAISED AT THE TOP OF _oppBustOut, BEFORE the Aegis branch. Aegis can hand half
the bank back, which means a hook reading oPts after it would see a bust that
partly did not happen. The seam is "the rival busted", not "the rival busted
and here is what survived" - the same distinction that made Preserve's restore
belong after _turnTableClear rather than inside it.

AND bankBonus GOES AFTER `_npcActuallyBanked=true`, not before: a hook asking
"did the rival actually bank" must see the flag it is about. Same reason
turnStart and roll went after their counters.

NEITHER UNGATES A CARD. Every CFX hook still tests _fxMine and still returns
early for an opponent. This raises the moments; deciding which cards should
fire for a boss is the parked work, and keeping those two apart is the whole
point of the seams-before-personality direction.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

BUST = u"      function _oppBustOut(){"
assert s.count(BUST) == 1, '_oppBustOut matched %d' % s.count(BUST)
s = s.replace(BUST, BUST + u"""
        /* THE OPPONENT'S bust SEAM. At the TOP, before Aegis - Aegis can hand
           half the bank back, and a hook reading oPts after it would see a
           bust that partly did not happen. The seam is "the rival busted",
           not "and here is what survived".
           Every bust exit funnels through this function, so one call covers
           all four of its call sites. */
        try{famFire('bust',{actor:'o'});}catch(e){}""")

BB = u"      else{G.oPts+=pts;_npcActuallyBanked=true;"
assert s.count(BB) == 1, 'bankBonus site matched %d' % s.count(BB)
s = s.replace(BB, BB + u"""famFire('bankBonus',{actor:'o',amt:pts});""")

assert s != orig, 'nothing changed'
assert s.count("famFire('bust',{actor:'o'})") == 1
assert s.count("famFire('bankBonus',{actor:'o'") == 1
# the player's own raises are untouched
assert s.count("famFire('bust',{actor:'p'") == 1
assert s.count("famFire('bankBonus',{actor:'p'") == 1
# and the two already shipped are still there
assert s.count("famFire('turnStart',{actor:'o'})") == 1
assert s.count("famFire('roll',{actor:'o'})") == 1
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P461 applied: opponent bust + bankBonus seams raised (4 of 8 now)')
