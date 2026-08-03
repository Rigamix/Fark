# -*- coding: utf-8 -*-
"""P435b - the preserve restore moves AGAIN, and this time it is genuinely last.

P434 moved it below `G.kept=[]`. That fixed the data and the die stayed
invisible, because there is a SECOND clear further down the same function:
`clearRow('playerDiceRow')` empties #keptRow as well - deliberately, with a
comment saying every path that clears the throwing row must clear the kept line
too "or the scored dice outlive the turn".

So the restore was still upstream of something that wipes it. Same bug, one
level up, found the same way: by measuring the rendered surface and getting
0x0 with no children rather than by re-reading the diff.

THE RULE THIS ARRIVES AT: a restore into a fresh turn has to run after
EVERYTHING that clears, not merely after the first thing that clears. Being
"after the reset" was not the same as being last, and only a render check could
tell those apart.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

start = s.find(u"  /* PRESERVE PAYS OUT HERE, AFTER THE RESET, AND THE ORDER IS THE WHOLE FIX.")
assert start >= 0, 'preserve block not found'
end = s.find(u"\n  }\n", s.find(u"famLog('THE AMBER CRACKS", start))
assert end > start, 'preserve block end not found'
block = s[start:end + len(u"\n  }\n")]
s = s[:start] + s[end + len(u"\n  }\n"):]

block = block.replace(
  u"  /* PRESERVE PAYS OUT HERE, AFTER THE RESET, AND THE ORDER IS THE WHOLE FIX.\n"
  u"     This block used to sit four lines UPSTREAM of the reset above, so it wrote\n"
  u"     G.kept and G.numDice and then had both overwritten before the turn began -\n"
  u"     Preserve spent its charge, announced \"THE AMBER CRACKS\", and delivered\n"
  u"     nothing. Anything restored into a fresh turn has to land after the turn is\n"
  u"     cleared, not before. If the reset ever moves, this moves with it. */\n",
  u"  /* PRESERVE PAYS OUT HERE, LAST, AND THE POSITION IS THE WHOLE FIX.\n"
  u"     It has been wrong twice, upstream of a different wipe each time.\n"
  u"       First: four lines above `G.kept=[];G.numDice=matchDice.length`, so the\n"
  u"       data was overwritten before the turn began and Preserve announced\n"
  u"       \"THE AMBER CRACKS\" having delivered nothing.\n"
  u"       Then: above `clearRow('playerDiceRow')`, which empties #keptRow too -\n"
  u"       deliberately, see its comment - so the DATA survived and the minted die\n"
  u"       was wiped off the table. Right numbers, empty board.\n"
  u"     A RESTORE INTO A FRESH TURN MUST RUN AFTER EVERYTHING THAT CLEARS, not\n"
  u"     merely after the first thing that clears. \"After the reset\" was not the\n"
  u"     same as \"last\", and only checking the rendered row told them apart.\n"
  u"     Anything added below that clears the row belongs ABOVE this block. */\n")

ANCHOR = u"  clearRow('playerDiceRow');clearRow('oppDiceRow');refreshKeptTray();\n"
assert s.count(ANCHOR) == 1, 'clearRow anchor matched %d' % s.count(ANCHOR)
s = s.replace(ANCHOR, ANCHOR + block, 1)

assert s != orig, 'nothing changed'
# COUNT THE CODE, NOT THE PROSE. The first version of this assert counted
# "THE AMBER CRACKS" and fired - because the new comment QUOTES that string
# while explaining the bug. The check was wrong, not the edit. Count the
# famLog call itself.
assert s.count(u"famLog('THE AMBER CRACKS") == 1, 'preserve block duplicated'
assert s.index(ANCHOR) < s.index(u"PRESERVE PAYS OUT HERE"), 'restore is still above the clear'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P435b applied: restore now runs after every clear')
