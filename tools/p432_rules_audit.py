# -*- coding: utf-8 -*-
"""P432 - the rules audit, and marking a trap.

THE BACKLOG ITEM'S PREMISE WAS WRONG, and measuring it is what showed that.
It read: "the rules screen is the only teaching surface and it teaches six
things the code doesn't do." Measured:

  THE LIVE SHEET IS ACCURATE. _gbSettings('rules') - reached from the home
  screen's book icon - makes 14 scoring claims. All 14 were checked by RUNNING
  scoreSelection against the hands they describe, not by reading the scorer.
  14 of 14 match, including every doubling step (four 2s = 400, five = 800,
  six = 1,600, four 1s = 2,000).

  THE SIX WRONG CLAIMS ARE IN A SCREEN NOBODY CAN OPEN. #rulesOverlay - four
  tabs, Play/Scoring/Dice/Gauntlet - has exactly one entry point: a .menu-btn
  in the static markup of #screen-menu, measured NOT VISIBLE because the home
  screen is rendered over it now. Same shape as #screen-bossreward, which has
  no entry point either.

So nothing player-facing is wrong. The real gap is the opposite of the one
filed: teaching is MISSING, not incorrect. The reachable sheet covers scoring
and nothing else, while the master brief asks for a "scoring & your dice"
sheet.

THIS PATCH ONLY MARKS THE TRAP. Eight tabs of authored copy carrying at least
six stale claims, one onclick away from being live, is a hazard - and deleting
authored content is not a call to make in passing. Both go to Denis.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u'<div class="rules-overlay" id="rulesOverlay" onclick="if(event.target===this)closeRules()">'
NEW = (u'<!-- UNREACHABLE, AND STALE. DO NOT WIRE THIS UP WITHOUT READING IT FIRST.\n'
       u'     Its only entry point is the RULES .menu-btn below in this same static\n'
       u'     markup, and that button is not visible - the home screen renders over\n'
       u'     it. Measured, not assumed. Same shape as #screen-bossreward.\n'
       u'     AT LEAST SIX OF ITS CLAIMS ARE NOW FALSE, and they are false in the\n'
       u'     most expensive way: confidently, in the voice of the game.\n'
       u'       "Losing to a patron costs nothing"  - it costs a seat for the night.\n'
       u'       "Patron win - 5g + 5g per tier"     - not what the payout computes.\n'
       u'       "Equip up to 3 cards ... more with renown perks" - the perk ladder\n'
       u'                                             is deleted; renown is gone.\n'
       u'       "Vanguard, Anchor, Bookends, ..."   - Anchor and Bookends collapsed\n'
       u'                                             INTO Vanguard.\n'
       u'       "Renown, which is permanent"        - deleted, master brief section 8.\n'
       u'       "Last Call - target score drops"    - that is the HANDICAP; the badge\n'
       u'                                             rule of the same name voids a\n'
       u'                                             bank under 800. One name, two\n'
       u'                                             rules, and this teaches one.\n'
       u'     The LIVE sheet is _gbSettings(\'rules\'), reached from the book icon on\n'
       u'     the home screen. Its 14 scoring claims were verified by running\n'
       u'     scoreSelection against each hand: 14 of 14 correct.\n'
       u'     The master brief also rules AGAINST reviving this: "the pause menu is\n'
       u'     the ONLY rules-reference surface ... there is no innkeep\'s book\n'
       u'     screen; do not rebuild one." -->\n'
       + OLD)

n = s.count(OLD)
assert n == 1, 'overlay anchor matched %d times (want 1)' % n
s = s.replace(OLD, NEW)

assert s != orig, 'nothing changed'
assert u'UNREACHABLE, AND STALE' in s
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P432 applied: dead rules overlay marked')
