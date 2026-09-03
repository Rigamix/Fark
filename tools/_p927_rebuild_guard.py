# -*- coding: utf-8 -*-
u"""P927: the comment that has failed three times becomes a check.

THE HISTORY. startPTurn rebuilds the hand with
`G.kept=[];G.numDice=G.matchDice?G.matchDice.length:6;`, and anything that sets
numDice ABOVE that line is silently discarded. This has now bitten three times:

  Preserve, twice - its own comment records both. "First: four lines above
  `G.kept=[];G.numDice=matchDice.length`, so the data was overwritten before the
  turn began and Preserve announced 'THE AMBER CRACKS' having delivered nothing."
  Then again, above clearRow, which wiped the minted die off the table.

  Tar Pit, P923 - spent its charge, logged "YOU ROLL 5", and the player rolled
  six.

Each time the repair was to move one block and write a longer comment. A comment
that has failed three times is not a weak comment, it is the wrong instrument:
it requires the next author to read a paragraph forty lines away and recognise
that they are in its domain. The rule is mechanical, so it can be a check.

WHAT IT DOES. startPTurn stamps numDice on entry; the rebuild compares before
overwriting. If they differ, something between the two set it and is about to
lose it - which is the bug, every time, with no legitimate case. The count lands
on G._ndDiscarded so a probe can assert on it, and a console warning names the
value and the history so whoever hits it does not have to rediscover P923.

IT DOES NOT CHANGE BEHAVIOUR. The rebuild still overwrites; this only makes the
overwrite audible. Silencing it correctly means moving the offending block below
the rebuild, which is where Whisper's Hex has always been and why the Hex has
always worked.
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


sub(u"""function startPTurn(){
  /* P875: a fresh turn earns a fresh nag.""",
    u"""function startPTurn(){
  /* P927: STAMPED ON ENTRY so the rebuild below can tell "left over from last
     turn" - which is fine and is what the rebuild is for - from "set during
     THIS startPTurn, above the rebuild" - which is the bug that has now hit
     three times. See the check beside the rebuild. */
  try{if(G)G._ndAtTurnTop=G.numDice;}catch(e){}
  /* P875: a fresh turn earns a fresh nag.""",
    '1 the entry stamp')

sub(u"""  G.phase='idle';G.turnPts=0;G.kept=[];G.numDice=G.matchDice?G.matchDice.length:6;""",
    u"""  G.phase='idle';G.turnPts=0;G.kept=[];
  /* P927: THE THRICE-FAILED COMMENT, MADE A CHECK. Anything that sets numDice
     between the top of startPTurn and this line is about to be discarded, and
     there is no legitimate case - a dice-count effect belongs BELOW here, where
     Whisper's Hex has always been and which is the entire reason the Hex has
     always worked. Preserve was caught by this shape twice and Tar Pit once
     (P923: charge spent, log reading "TAR PIT - YOU ROLL 5", six dice rolled).
     Three failures of a comment means the rule wanted a mechanism. */
  try{
    if(G&&G._ndAtTurnTop!==undefined&&G.numDice!==G._ndAtTurnTop){
      G._ndDiscarded=(G._ndDiscarded||0)+1;
      G._ndDiscardedVal=G.numDice;
      if(window.console&&console.warn)console.warn(
        '[fark P927] numDice was set to '+G.numDice+' above the turn rebuild '+
        '(was '+G._ndAtTurnTop+' on entry) and is being discarded. A dice-count '+
        'effect belongs BELOW the rebuild, beside Whisper\\'s Hex - see P923.');
    }
  }catch(e){}
  G.numDice=G.matchDice?G.matchDice.length:6;""",
    '2 the rebuild guard')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

if code.count('G._ndAtTurnTop=G.numDice') != 1:
    sys.exit('the entry stamp is not set exactly once (nothing written)')
if code.count('G._ndDiscarded=(G._ndDiscarded||0)+1') != 1:
    sys.exit('the guard does not count exactly once (nothing written)')
# THE STAMP MUST PRECEDE THE GUARD, or it compares against an unset value
_stamp = code.index('G._ndAtTurnTop=G.numDice')
_guard = code.index('G._ndDiscarded=(G._ndDiscarded||0)+1')
if _stamp > _guard:
    sys.exit('the entry stamp is taken after the guard reads it (nothing written)')
# and the guard must precede the rebuild it is warning about
_rebuild = code.index('G.numDice=G.matchDice?G.matchDice.length:6', _guard)
if _guard > _rebuild:
    sys.exit('the guard runs after the overwrite it reports (nothing written)')
# the rebuild still happens - this changes nothing about behaviour
if code.count('G.numDice=G.matchDice?G.matchDice.length:6') != 3:
    sys.exit('a rebuild site was added or lost (nothing written)')
# and Tar Pit is still below it, where P923 put it
_tar = code.index('G._oTarPit--')
if _tar < _rebuild:
    sys.exit('tar pit drifted back above the rebuild (nothing written)')
# the hex block, which is the pattern being pointed at, is untouched
if code.count('G.numDice=Math.max(3,G.numDice-1)') != 1:
    sys.exit('the hex block was disturbed (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
