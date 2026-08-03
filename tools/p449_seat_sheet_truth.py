# -*- coding: utf-8 -*-
"""P449 - the seat sheet tells the truth about the match you are about to play.

The seat sheet is the DECISION POINT: buy-in, pot, target, and what a cursed
seat pays and costs. Three things on it were wrong.

1. "lose 1" WAS HARDCODED, AND I BROKE IT MYSELF IN P447. Cursed Table now
   costs TWO circles on a loss, not one - that was the Bet Law fix. The seat
   sheet still promised one. A card whose whole point is that it cuts both ways
   was still advertising the old one-sided deal at the moment the player commits
   to it. Mine, same session, four patches earlier.

2. THE TARGET IS SHORT BY 500 WHENEVER HIGH TABLE IS OWNED, and this one
   predates me. _gbPeek reads n.roster[i] and shows patron.target; launchSeat
   then does `patron.target += 500` for High Table - AFTER the sheet is gone.
   So the number the player chooses against is not the number they play against.
   Display-only fix here: the roster object is NOT mutated, because launchSeat
   still has to do that and adding it twice would raise the target by 1000.

   This is High Table's answer to "the stake stays visible": it does not need a
   status chip. It needs the number it already changes to be right where the
   player reads it.

3. A DEAD `circ` VARIABLE. `var circ=(famOwnTier('marked_table')>0)?'THREE
   circles':'2 circles';` is assigned and never read - the block below it went
   to a different phrasing and left the computation behind.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. the cursed line tells the truth about BOTH sides ──
OLD = (u"    +(sealed?' · cursed: win '+((famOwnTier('marked_table')>0)?'3':'2')"
       u"+' circles / lose 1':'')+'</div>';")
assert s.count(OLD) == 1, 'cursed line matched %d' % s.count(OLD)
s = s.replace(OLD,
  u"""    /* BOTH NUMBERS READ THE CARD. `lose 1` used to be hardcoded, and P447
       made it a lie: Cursed Table now costs TWO circles on a loss, which is
       the Bet Law fix that stopped it being pure upside. Advertising the old
       one-sided deal at the moment the player commits is the worst place for
       it to be wrong. */
    +(sealed?' · cursed: win '+((famOwnTier('marked_table')>0)?'3':'2')
      +' circles / lose '+((famOwnTier('marked_table')>0)?'2':'1'):'')+'</div>';""")

# ── 2. the target shown is the target played ──
OLD_T = (u"    +'<div class=\"gbx-box sub\" style=\"flex:1;height:40px\">target '"
         u"+(pat.target||0).toLocaleString()+'</div>'")
assert s.count(OLD_T) == 1, 'target line matched %d' % s.count(OLD_T)
s = s.replace(OLD_T,
  u"""    /* HIGH TABLE'S +500 IS APPLIED IN launchSeat, AFTER this sheet closes,
       so the target here was the one the player would NOT be playing against.
       Shown, not applied: the roster object stays untouched because launchSeat
       still mutates it, and doing both would raise the target by 1000. */
    +'<div class="gbx-box sub" style="flex:1;height:40px">target '
      +((pat.target||0)+((famOwnTier('high_table')>0)?500:0)).toLocaleString()
      +((famOwnTier('high_table')>0)?' <span style="opacity:.7">+500 high table</span>':'')
      +'</div>'""")

# ── 3. the dead variable ──
OLD_C = u"    var circ=(famOwnTier('marked_table')>0)?'THREE circles':'2 circles';\n"
assert s.count(OLD_C) == 1, 'dead circ matched %d' % s.count(OLD_C)
s = s.replace(OLD_C, u"")

assert s != orig, 'nothing changed'
assert u"circles / lose 1':'')" not in s, 'the hardcoded lose count survives'
assert s.count(u"famOwnTier('high_table')>0)?500:0") == 1
# the dead var is gone and nothing referenced it
import re
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert u"'THREE circles'" not in code, 'the dead phrasing survives'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P449 applied: cursed loss count, high table target, dead var removed')
