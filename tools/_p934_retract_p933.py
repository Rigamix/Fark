# -*- coding: utf-8 -*-
u"""P934: P933 IS RETRACTED. Its premise was false and its comment claimed a
mechanism that is not in the file.

WHAT P933 CLAIMED. That the resume path restores G.turnNum without stamping and
does NOT pass through startPTurn, so the first player turn after a resume reads a
stale stamp, the guard fails, and endPTurn falls back to 0 on a banking turn -
P929's Ill Omen defect returning through the resume path.

THE SECOND CLAUSE IS FALSE, and it is the load-bearing one. initMatchScreen's
tail is unconditional:

  42436  var _matchStartDelay=params._resumeData?200:800;
  42453  if(!params._resumeData){        <- the three early returns all live here
  42510  setTimeout(startPTurn,_matchStartDelay);

The only returns between the resume block and that tail (42464, 42472, 42477)
are inside `if(!params._resumeData)`, so a resume skips them and reaches 42510
unconditionally. startPTurn then runs 200ms later and stamps against the RESTORED
turnNum. The stale-stamp scenario cannot occur.

AND THE PROBE MANUFACTURED IT. apv_resume_stamp.js ran startPTurn's reset FIRST
and the restore SECOND - startPTurn -> restore -> bank -> endPTurn - when the
real order is restore -> startPTurn -> bank -> endPTurn. Its control arm
reproduced a state the shipping code never reaches, so both arms were about
nothing and the clean separation between them was an artefact of the inversion.
That is the "what else produces this reading" failure inverted: a reading nothing
in production produces.

THE COUNT WAS WRONG TOO - four writers, not two. `turnNum:1` in newG's returned
literal (31504) and `turnNum:3` in dbgWin's whole-object replacement (11326) are
writes my regex could not see, because it only matched `G.turnNum`. Neither
stamps. Both are harmless for exactly the reason that retires the whole patch:
startPTurn always runs before anything reads the pair.

AND THE COMMENT PROMISED AN ENFORCEMENT THAT IS NOT HERE. "A post-assert enforces
it, so a fourth writer added later fails the patch" - the post-assert lives in
the patch script, which a reader of this file cannot see, and it counted two of
the four writers anyway. A comment vouching for coverage that does not exist is
the defect this work has been cataloguing all session; writing one into the fix
for that defect is worse than not commenting.

SO: back to P932's shape. The pair is reset where a player turn BEGINS, which is
startPTurn, and that is the correct rule - not "wherever turnNum is written".
turnNum changes at the END of a turn and at match construction; the pair belongs
to the turn that is starting. All eight startPTurn call sites begin a player
turn, and every path into a match reaches one.
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


# ── 1. the handover no longer resets ────────────────────────────────
sub(u"""  G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;_pTurnBankReset();/* P933 */""",
    u"""  G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;""",
    '1 the handover reset is withdrawn')

# ── 2. nor the resume restore ───────────────────────────────────────
sub(u"""    G.pPts=rd.pPts;G.oPts=rd.oPts;G.turnNum=rd.turnNum;G.numDice=rd.numDice;
    /* P933: THE WRITER THAT WAS MISSED. A resumed match has no in-flight banked
       amount - the snapshot is taken at a turn boundary - so 0 against the
       restored turnNum is the correct pair. Without this the first player turn
       after a resume read a stamp from before the restore. */
    _pTurnBankReset();""",
    u"""    G.pPts=rd.pPts;G.oPts=rd.oPts;G.turnNum=rd.turnNum;G.numDice=rd.numDice;
    /* P934: NO STAMP NEEDED HERE, and P933 was wrong to add one. This restores
       turnNum, and initMatchScreen's tail then reaches
       `setTimeout(startPTurn,_matchStartDelay)` unconditionally - the three
       early returns between here and there all sit inside
       `if(!params._resumeData)`, so a resume passes them. startPTurn stamps
       against the restored value 200ms later, before anything can read it. */""",
    '2 the resume reset is withdrawn')

# ── 3. and the helper's comment stops promising what is not here ────
sub(u"""/* P933: THE BANKED AMOUNT IS MEANINGLESS WITHOUT ITS TURN, so the pair is
   re-established wherever that turn number changes. G.turnNum has three
   writers - endPTurn's increment, the resume restore, and nothing else - and
   P932 stamped in startPTurn, which is not one of them. The resume path
   therefore restored turnNum without stamping, and the first player turn after
   a resume read a stale stamp: the guard failed, dev threw, and production fell
   back to 0 on a banking turn, which is P929's Ill Omen defect returning
   through the resume path.
   CALL THIS AT EVERY WRITE OF G.turnNum. A post-assert enforces it, so a fourth
   writer added later fails the patch rather than the player - the invariant
   lives in the check instead of in someone's memory, which is the shape four
   lane-record bugs and one peek-snapshot bug have all had. */""",
    u"""/* THE PAIR IS RESET WHERE A PLAYER TURN BEGINS - startPTurn, its only caller.
   P933 tried to reset it at every writer of G.turnNum instead and was RETRACTED
   (P934) on three counts, all worth keeping because the reasoning is the useful
   part:
     THE PREMISE WAS FALSE. It claimed the resume path restores turnNum without
     passing through startPTurn. initMatchScreen's tail is unconditional -
     `setTimeout(startPTurn,_matchStartDelay)` - and the three early returns
     above it are all inside `if(!params._resumeData)`, so a resume reaches it
     and startPTurn stamps against the restored value before anything reads it.
     THE COUNT WAS WRONG. turnNum has FOUR writers, not two: newG's returned
     literal (`turnNum:1`) and dbgWin's whole-object replacement (`turnNum:3`)
     are writes that a `G.turnNum` search cannot see. Neither stamps, and
     neither needs to - for the same reason.
     AND THE RULE WAS THE WRONG SHAPE. turnNum changes at the END of a turn and
     at match construction; the pair belongs to the turn that is STARTING. "Where
     a player turn begins" is one place, and every path into a match reaches it.
   So the invariant is: after startPTurn, _pTurnBankedTurn === turnNum, and
   endPTurn's guard reads it. Nothing else may write the stamp. */""",
    '3 the comment records the retraction')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# ONE CALLER, and it is startPTurn's
if code.count('_pTurnBankReset();') != 1:
    sys.exit('the helper has %d call sites, expected 1 (nothing written)'
             % code.count('_pTurnBankReset();'))
_call = code.index('_pTurnBankReset();')
_sp = code.index('function startPTurn(){')
_spEnd = code.index('function ', _sp + 10)
if not (_sp < _call < _spEnd):
    sys.exit('the only call site is not inside startPTurn (nothing written)')
# the helper still exists and writes the pair together
if code.count('function _pTurnBankReset(') != 1:
    sys.exit('the helper is not defined exactly once (nothing written)')
# the stamp is written in exactly one place
if len(re.findall(r'G\._pTurnBankedTurn=[^=]', code)) != 1:
    sys.exit('the stamp is written from more than one place (nothing written)')
# NOTHING PROMISES AN ENFORCEMENT THAT IS NOT IN THE FILE
if 'A post-assert enforces it' in s:
    sys.exit('the false enforcement claim survives (nothing written)')
if 'CALL THIS AT EVERY WRITE OF G.turnNum' in s:
    sys.exit('the withdrawn rule is still stated (nothing written)')
# P929/P932's machinery is intact
if code.count('var _pTurnBankedOK=G._pTurnBankedTurn===G.turnNum;') != 1:
    sys.exit('the guard was disturbed (nothing written)')
if len(re.findall(r'G\._pTurnBanked=total', code)) != 2:
    sys.exit('a handleBank credit site lost its amount write (nothing written)')
if code.count('(G.turnPts||0)||(_pTurnBankedOK?(G._pTurnBanked||0):0)') != 1:
    sys.exit('endPTurn no longer reads through the guard (nothing written)')
# and the handover increment is back to its original form
if code.count("G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;") != 1:
    sys.exit('the handover line was not restored (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
