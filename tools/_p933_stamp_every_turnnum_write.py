# -*- coding: utf-8 -*-
u"""P933: the stamp is re-established at EVERY writer of turnNum, not at one of them.

P932 moved the stamp to startPTurn on the reasoning that startPTurn is what
defines a player turn. That was half right. G.turnNum has THREE writers, and
startPTurn is not one of them:

  37110  G.turnNum++              in endPTurn, at the handover
  42156  G.turnNum=rd.turnNum     in the resume path
  (startPTurn stamps against turnNum but does not write it)

The resume path restores turnNum and never stamps. So on the first player turn
after resuming a saved match, _pTurnBankedTurn is stale against a restored
turnNum, the guard fails, the dev build throws, and production falls back to
(G.turnPts||0)||0 - which on a banking turn is 0. That is P929's Ill Omen defect
returning through the back door, on the resume path, which is the standing risk
area for exactly this reason.

THE RULE IS MECHANICAL AND SO IS THE CHECK. The banked amount is meaningful only
relative to a turn number, so the pair must be re-established wherever that turn
number changes. One helper, called at every writer, and a post-assert that every
write of G.turnNum has the reset beside it - so a fourth writer added later
fails the patch rather than the player.

WHY NOT "STAMP IN startPTurn ONLY, AND ALSO AT RESUME". That fixes today's two
sites and leaves the same census question open for the next one. The failure
mode here is not that a particular site was forgotten; it is that the invariant
lived in someone's head. Four lane-record bugs and one peek-snapshot bug have
all been this shape.

BEHAVIOUR IS UNCHANGED IN NORMAL PLAY. endPTurn's increment is immediately
followed by the reset, and the next startPTurn writes the same values again - so
a normal turn is stamped twice with identical results. The redundancy is the
point: play stays correct even if a path skips startPTurn entirely.
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


# ORDER MATTERS HERE, and the anchor count caught it. The helper's BODY is
# literally `G._pTurnBanked=0;G._pTurnBankedTurn=G.turnNum;` - the same text this
# edit replaces in startPTurn - so inserting the helper first made the anchor
# ambiguous (x2) and the patch refused. The call site is rewritten BEFORE the
# helper is introduced, so each anchor is unique when it is used.
# ── 1. startPTurn calls the helper ───────────────────────────────────────────
sub(u"""  G._pTurnBanked=0;G._pTurnBankedTurn=G.turnNum;""",
    u"""  _pTurnBankReset();/* P933 */""",
    '2 startPTurn calls it')

# ── 2. the helper itself, defined beside the other turn-scoped helpers ─────
sub(u"""function _turnScoreClear(){if(!G)return;G.turnPts=0;G.kept=[];}""",
    u"""function _turnScoreClear(){if(!G)return;G.turnPts=0;G.kept=[];}
/* P933: THE BANKED AMOUNT IS MEANINGLESS WITHOUT ITS TURN, so the pair is
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
   lane-record bugs and one peek-snapshot bug have all had. */
function _pTurnBankReset(){
  if(typeof G==='undefined'||!G)return;
  G._pTurnBanked=0;G._pTurnBankedTurn=G.turnNum;
}""",
    '1 the helper')

# ── 3. the handover increment ───────────────────────────────────────
sub(u"""  G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;""",
    u"""  G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;_pTurnBankReset();/* P933 */""",
    '3 the handover increment re-stamps')

# ── 4. and the resume restore, the one that was missed ──────────────
sub(u"""    G.pPts=rd.pPts;G.oPts=rd.oPts;G.turnNum=rd.turnNum;G.numDice=rd.numDice;""",
    u"""    G.pPts=rd.pPts;G.oPts=rd.oPts;G.turnNum=rd.turnNum;G.numDice=rd.numDice;
    /* P933: THE WRITER THAT WAS MISSED. A resumed match has no in-flight banked
       amount - the snapshot is taken at a turn boundary - so 0 against the
       restored turnNum is the correct pair. Without this the first player turn
       after a resume read a stamp from before the restore. */
    _pTurnBankReset();""",
    '4 the resume restore re-stamps')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# THE CENSUS, ENFORCED. Every write of G.turnNum - assignment or increment, and
# `=[^=]` so a comparison is not mistaken for one - must have the reset beside
# it. A fourth writer added later fails here.
_writes = [m for m in re.finditer(r'G\.turnNum(?:\+\+|--|\s*[+-]?=[^=])', code)]
if len(_writes) != 2:
    sys.exit('found %d writers of G.turnNum, expected the handover increment and '
             'the resume restore - a new one needs _pTurnBankReset() beside it '
             '(nothing written)' % len(_writes))
for m in _writes:
    if '_pTurnBankReset()' not in code[m.end():m.end() + 260]:
        sys.exit('a write of G.turnNum at offset %d has no _pTurnBankReset() '
                 'after it (nothing written)' % m.start())
# one helper, and it writes the pair together
if code.count('function _pTurnBankReset(') != 1:
    sys.exit('the helper is not defined exactly once (nothing written)')
_h = code.index('function _pTurnBankReset(')
_body = code[_h:_h + 200]
if 'G._pTurnBanked=0' not in _body or 'G._pTurnBankedTurn=G.turnNum' not in _body:
    sys.exit('the helper does not write both halves of the pair (nothing written)')
# and nothing writes the stamp outside the helper
_stamps = re.findall(r'G\._pTurnBankedTurn=[^=]', code)
if len(_stamps) != 1:
    sys.exit('the stamp is written %d times; only the helper may write it '
             '(nothing written)' % len(_stamps))
# three callers: startPTurn, the handover, the resume
if code.count('_pTurnBankReset();') != 3:
    sys.exit('the helper has %d call sites, expected 3 (nothing written)'
             % code.count('_pTurnBankReset();'))
# THE HELPER IS DEFINED BEFORE ITS FIRST CALLER at parse time is not required
# for function declarations, but the guard that reads the pair must still exist
if code.count('var _pTurnBankedOK=G._pTurnBankedTurn===G.turnNum;') != 1:
    sys.exit('the guard was disturbed (nothing written)')
# and the amount is still written by handleBank at both credit sites
if len(re.findall(r'G\._pTurnBanked=total', code)) != 2:
    sys.exit('a handleBank credit site lost its amount write (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
