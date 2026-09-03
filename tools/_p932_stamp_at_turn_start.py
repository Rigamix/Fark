# -*- coding: utf-8 -*-
u"""P932: the stamp is written where every path passes, not on one branch.

P930's guard fell back to 0 on a stamp mismatch, and that was right only BECAUSE
a mismatch was the bust path and 0 is the correct answer there. Which means it
could not tell a bust from a newly added credit path that forgot to stamp - the
four-times-failed shape it exists to catch. A guard whose failure mode is
indistinguishable from its success case is not a guard.

THE FIX IS 3.6's MOVE. The stamp goes where EVERY path passes - startPTurn,
which is what defines a player turn - and handleBank overwrites only the amount.
Then:

  correct operation      the stamp always matches, on every turn, bank or bust
  a bust                 reads 0 by EXPLICIT WRITE at turn start, not by a
                         stale mismatch that happens to fall the right way
  a new credit path      needs no stamp of its own; the turn already carries
                         the right one, so there is nothing to forget
  a turn without startPTurn   the stamp is stale, nothing else can produce
                         that, and it is a real fault worth throwing on

The stamp is written once per turn by one function instead of at every write of
the value, which also retires P930's pairing assert: there is no pair to keep in
step any more. That assert had itself failed on a substring - the sixth
wide-search-space instance - and the durable form of that lesson is to match
`=[^=]` rather than `=` when looking for assignments.
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


# ── 1. the stamp is set at turn start, to THIS turn ─────────────────
sub(u"""  G._pTurnBanked=0;G._pTurnBankedTurn=-1;/* P930: the stamp resets with it */""",
    u"""  /* P932: THE STAMP IS SET HERE, TO THIS TURN, and handleBank overwrites only
     the amount. P930 reset it to -1 and let handleBank stamp, so a mismatch at
     endPTurn meant EITHER a bust (legitimate, reads 0) OR a credit path that
     forgot to stamp (the bug) - indistinguishable, and 0 happened to be right
     for one of them. Writing it where every path passes makes the stamp match
     in all correct operation, so a mismatch has exactly one cause left: a
     player turn entered without startPTurn. That is a fault worth throwing on.
     Same move as 3.6 - the rule lives where every path goes through, not on one
     branch. */
  G._pTurnBanked=0;G._pTurnBankedTurn=G.turnNum;""",
    '1 the stamp is set at turn start')

# ── 2+3. handleBank writes the amount only ──────────────────────────
sub(u"""    G._lastBankAmount=total;G._pTurnBanked=total;G._pTurnBankedTurn=G.turnNum;/* P929/P930 */spawnBankPop(total);""",
    u"""    G._lastBankAmount=total;G._pTurnBanked=total;/* P929/P932: amount only - startPTurn owns the stamp */spawnBankPop(total);""",
    '2 the tab credit stops stamping')

sub(u"""    G.pPts+=total;G._lastBankAmount=total;G._pTurnBanked=total;G._pTurnBankedTurn=G.turnNum;/* P929/P930 */spawnBankPop(total);""",
    u"""    G.pPts+=total;G._lastBankAmount=total;G._pTurnBanked=total;/* P929/P932: amount only - startPTurn owns the stamp */spawnBankPop(total);""",
    '3 the normal credit stops stamping')

# ── 4. and the guard says what a mismatch now means ─────────────────
sub(u"""  var _pTurnBankedOK=(G._pTurnBanked||0)===0||G._pTurnBankedTurn===G.turnNum;""",
    u"""  /* P932: a mismatch now has ONE cause. The stamp is written at turn start by
     startPTurn and never elsewhere, so in all correct operation it equals
     turnNum here - on a bank and on a bust alike, since a bust reads the 0 that
     startPTurn wrote rather than falling through a mismatch that happened to
     give the right answer. If it does not match, a player turn was entered
     without startPTurn. */
  var _pTurnBankedOK=G._pTurnBankedTurn===G.turnNum;""",
    '4 the guard has one cause')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# ASSIGNMENTS, NOT COMPARISONS - `=[^=]`, the durable form
_stampWrites = re.findall(r'G\._pTurnBankedTurn=[^=]', code)
if len(_stampWrites) != 1:
    sys.exit('the stamp is written %d times; it must be written once, at turn '
             'start (nothing written)' % len(_stampWrites))
if 'G._pTurnBankedTurn=G.turnNum;' not in code:
    sys.exit('the stamp is not set to the current turn (nothing written)')
# and that one write sits in startPTurn, before the read in endPTurn
_write = code.index('G._pTurnBankedTurn=G.turnNum;')
_read = code.index('G._pTurnBankedTurn===G.turnNum')
if _write > _read:
    sys.exit('the stamp is written after it is read (nothing written)')
# the amount is still written at both credit sites and the reset
_valWrites = re.findall(r'G\._pTurnBanked=[^=]', code)
if len(_valWrites) != 3:
    sys.exit('the amount is written %d times, expected two credits and one reset '
             '(nothing written)' % len(_valWrites))
# the guard no longer treats a zero amount as automatically fine - that was the
# branch that made a bust and a forgotten stamp look alike
if '(G._pTurnBanked||0)===0||' in code:
    sys.exit('the guard still excuses a zero amount (nothing written)')
# the bust still reads zero, by the explicit write at turn start
if 'G._pTurnBanked=0;G._pTurnBankedTurn=G.turnNum;' not in code:
    sys.exit('the pair is not initialised together at turn start (nothing written)')
# endPTurn's read and the dev throw both survive
if code.count('(G.turnPts||0)||(_pTurnBankedOK?(G._pTurnBanked||0):0)') != 1:
    sys.exit('endPTurn no longer reads through the guard (nothing written)')
if code.count("throw new Error('[fark P930]") != 1:
    sys.exit('the dev throw was lost (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
