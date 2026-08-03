# -*- coding: utf-8 -*-
"""P440 - the two-phase turn-state clear, named.

WHAT THE TRACE FOUND, and it is not what was proposed before it. The proposal
was `endTurnState(reason)` - one call. Nine branch paths later, the real shape
is TWO phases with the path's own save and animation work in the gap:

    G.turnPts=0; G.kept=[]        <- phase A, the SCORE goes
        ...ward halves the bank, thick skin pays out, stitch rerolls...
    clearRow('playerDiceRow'); G.pool=[]   <- phase B, the TABLE goes

A single wrapper cannot express that, because the work between the phases is
what each path IS. So this names the two phases and leaves the gap alone.

AND ONLY THE CORE IS SHARED. The companions genuinely differ per path:

    safeTurnStreak=0     5 of the score-clears, but NOT ward, NOT handleBank
    _turnBonusPot=0      ward only
    numDice=6            handleBank only
    updHUD/refresh/...   four of them, not the others

So the helpers do the CORE AND NOTHING ELSE, and every site keeps its own
companions verbatim. Folding the companions in would be the powder_keg mistake
one level finer: the four lines that look like noise are five different
statements about what else this particular exit owes.

WHY THIS IS WORTH DOING AT ALL, given it saves no lines: phase B becomes a
NAMED BOUNDARY. `_turnTableClear` is the thing a restore must land after -
which Preserve discovered by being wiped, and the branch trace confirmed
independently. Today that boundary is a convention in a comment; after this it
is a function a future restore can be documented against.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── the two phases, declared next to clearRow which phase B calls ──
ANCHOR = u"function clearRow(id){"
assert s.count(ANCHOR) == 1, 'clearRow anchor %d' % s.count(ANCHOR)
s = s.replace(ANCHOR,
  u"""/* ══ THE TURN-STATE CLEAR, IN TWO PHASES ══════════════════════════════
   Nine branch paths end a player's turn - six in doBust (plain, ward, second
   wind, thick skin, last stand, stitch) and three in handleBank - and every
   one of them clears the same four things in the same two stages, with its own
   save and animation work in between:

       _turnScoreClear()    the SCORE goes
           ...this path's work: ward halves the bank, thick skin pays out...
       _turnTableClear()    the TABLE goes

   THE GAP IS NOT INCIDENTAL - it is what each path IS, which is why a single
   endTurnState() call cannot express this and was not built.

   THESE DO THE CORE AND NOTHING ELSE. Every call site keeps its own
   companions: safeTurnStreak=0 on five of them but not ward and not
   handleBank, _turnBonusPot=0 on ward alone, numDice on handleBank alone.
   Those are not noise to absorb; they are each a statement about what that
   particular exit also owes.

   AND PHASE B IS A BOUNDARY WITH A NAME NOW. A restore into the next turn must
   land AFTER _turnTableClear - Preserve found that by having its die wiped by
   clearRow (P435b), and the branch trace arrived at the same line from the
   opposite direction. Two routes, no shared assumption. Anything restoring
   turn state belongs after this call, and can now be documented against it
   rather than against a comment. */
function _turnScoreClear(){if(!G)return;G.turnPts=0;G.kept=[];}
function _turnTableClear(){clearRow('playerDiceRow');if(G)G.pool=[];}
function clearRow(id){""")

# ── phase A: the identical core, companions preserved ──
A = [
  # ANCHORED ON _bustTolls(), NOT ON THE BARE PATTERN. That statement appears
  # TWICE: here in ward's bust path, and at line ~24399 where aldrics_vow FAILS.
  # The vow site clears the score and never the table - a PARTIAL, like
  # _afterRollImpl - so converting it would label a mid-turn card effect as a
  # turn-end phase and imply a phase B that never comes. Left alone.
  (u"_bustTolls();\n    G.turnPts=0;G.kept=[];G._turnBonusPot=0;",
   u"_bustTolls();\n    _turnScoreClear();G._turnBonusPot=0;", 1),
  (u"G.safeTurnStreak=0;G.turnPts=0;G.kept=[];updHUD();refreshKeptTray();setBtns(false,false);",
   u"G.safeTurnStreak=0;_turnScoreClear();updHUD();refreshKeptTray();setBtns(false,false);", 4),
  (u"G.safeTurnStreak=0;G.turnPts=0;G.kept=[];\n",
   u"G.safeTurnStreak=0;_turnScoreClear();\n", 1),
  (u"G.turnPts=0;G.kept=[];G.numDice=6;\n",
   u"_turnScoreClear();G.numDice=6;\n", 1),
  # handleBank's two card paths (steal_low_bank, block_low_bank) do BOTH phases
  # in ONE statement instead of two stages. Their table half is converted by
  # phase B below, so converting the score half here keeps them from ending up
  # half-named. This is the "inconsistency to fold in" case, not a distinct
  # intent - unlike the vow site above, both of these do go on to clear the
  # table in the same breath.
  (u"G.turnPts=0;G.kept=[];G.numDice=6;updHUD();",
   u"_turnScoreClear();G.numDice=6;updHUD();", 2),
]
for old, new, want in A:
    got = s.count(old)
    assert got == want, 'phase A %r matched %d (want %d)' % (old[:44], got, want)
    s = s.replace(old, new)

# ── phase B: same treatment ──
B = [
  (u"clearRow('playerDiceRow');G.pool=[];G.numDice=G.matchDice?G.matchDice.length:6;",
   u"_turnTableClear();G.numDice=G.matchDice?G.matchDice.length:6;", 2),
  # FIVE, not the three I first guessed: ward, second wind, thick skin, last
  # stand and the plain bust. Three of those sit inside a setTimeout and end
  # the line at G.pool=[] with the callback continuing below, so they match the
  # same shape. All five are genuine phase-B sites in doBust.
  (u"clearRow('playerDiceRow');G.pool=[];\n",
   u"_turnTableClear();\n", 5),
  (u"updHUD();refreshKeptTray();clearRow('playerDiceRow');G.pool=[];setBtns(false,false);",
   u"updHUD();refreshKeptTray();_turnTableClear();setBtns(false,false);", 3),
]
for old, new, want in B:
    got = s.count(old)
    assert got == want, 'phase B %r matched %d (want %d)' % (old[:44], got, want)
    s = s.replace(old, new)

assert s != orig, 'nothing changed'
assert s.count(u"function _turnScoreClear()") == 1
assert s.count(u"function _turnTableClear()") == 1
nA = s.count(u"_turnScoreClear();") - 1     # minus the declaration
nB = s.count(u"_turnTableClear();") - 1
print('phase A call sites: %d   phase B call sites: %d' % (nA, nB))
# EXACT, not a floor. 8 score-clears and 9 table-clears is what the nine paths
# plus handleBank's two single-statement card paths come to; a floor would have
# passed the run where the card-paths entry silently failed to apply and left
# them half-named.
assert nA == 8, 'phase A call sites %d (want 8)' % nA
assert nB == 9, 'phase B call sites %d (want 9)' % nB
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P440 applied')
