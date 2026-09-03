# -*- coding: utf-8 -*-
u"""P930: _pTurnBanked carries the turn it belongs to, and endPTurn refuses a stale one.

P929 introduced a second field that has to stay in step with a first - the shape
that has now cost four bugs in the lane records (P520/P530/P531/P919) and one in
the peek snapshot (P925). The invariant is shipped with the field rather than
promised for later, because a field added to FIX a staleness bug is precisely
where nobody should be relying on remembering.

WHAT COULD GO WRONG. _pTurnBanked is written in handleBank and reset at the top
of startPTurn. If any path enters a player turn without startPTurn, the reset is
skipped and a BUSTED turn reads the previous turn's bank - which would make a
rival Ill Omen MISS when it should land. That is P929's bug with the sign
flipped, and it would be just as invisible.

WHY NOT "pPts AFTER MINUS pPts BEFORE". That was the obvious invariant and it is
NOT always true: pPts moves during a turn for reasons other than the bank -
Reprisal, Pickpocket, the tab release, Thick Skin and Last Stitch bust-saves, the
challenge penalty, SCORE_DRAIN, and Ill Omen itself. A dev check that fires on
legitimate card activity is noise, and a noisy check gets switched off, which is
worse than no check because it reads as coverage. This is the lane-audit lesson
applied before shipping rather than after.

SO THE VALUE IS STAMPED WITH ITS TURN. handleBank records turnNum beside the
amount; endPTurn refuses a value stamped for a different turn, falling back to 0
- the safe answer, since 0 is what a turn that did not bank should report. Under
_fkDbgOn it throws, for the same reason P927 throws: this file's history is of
passive warnings surviving for two hundred patches.
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


# ── 1+2. both credit sites stamp the turn ───────────────────────────
sub(u"""    G._lastBankAmount=total;G._pTurnBanked=total;/* P929 */spawnBankPop(total);""",
    u"""    G._lastBankAmount=total;G._pTurnBanked=total;G._pTurnBankedTurn=G.turnNum;/* P929/P930 */spawnBankPop(total);""",
    '1 the tab credit stamps its turn')

sub(u"""    G.pPts+=total;G._lastBankAmount=total;G._pTurnBanked=total;/* P929 */spawnBankPop(total);""",
    u"""    G.pPts+=total;G._lastBankAmount=total;G._pTurnBanked=total;G._pTurnBankedTurn=G.turnNum;/* P929/P930 */spawnBankPop(total);""",
    '2 the normal credit stamps its turn')

# ── 3. the reset clears the stamp too ───────────────────────────────
sub(u"""  G._pTurnBanked=0;""",
    u"""  G._pTurnBanked=0;G._pTurnBankedTurn=-1;/* P930: the stamp resets with it */""",
    '3 the reset clears the stamp')

# ── 4. and endPTurn refuses a value from another turn ───────────────
sub(u"""  var _pTurnPts=(G.turnPts||0)||(G._pTurnBanked||0);""",
    u"""  /* P930: THE STAMP IS CHECKED, NOT TRUSTED. _pTurnBanked is a second field
     that has to stay in step with a first, which is the shape that has cost
     four bugs in the lane records and one in the peek snapshot. If a path ever
     enters a player turn without startPTurn, the reset is skipped and a BUSTED
     turn would read the previous turn's bank - P929's bug with the sign
     flipped, and just as invisible.
     NOT "pPts after minus pPts before": that invariant is false, because pPts
     moves within a turn for Reprisal, Pickpocket, the tab release, Thick Skin,
     Last Stitch, the challenge penalty, SCORE_DRAIN and Ill Omen itself. A
     check that fires on legitimate card activity is noise, and a noisy check
     gets switched off - which reads as coverage while being none. */
  var _pTurnBankedOK=(G._pTurnBanked||0)===0||G._pTurnBankedTurn===G.turnNum;
  if(!_pTurnBankedOK){
    G._pTurnBankedStale=(G._pTurnBankedStale||0)+1;
    if(window.console&&console.warn)console.warn(
      '[fark P930] _pTurnBanked='+G._pTurnBanked+' is stamped for turn '+
      G._pTurnBankedTurn+' but this is turn '+G.turnNum+
      ' - a player turn was entered without startPTurn, so the reset was '+
      'skipped. Reading 0 instead.');
  }
  var _pTurnPts=(G.turnPts||0)||(_pTurnBankedOK?(G._pTurnBanked||0):0);""",
    '4 endPTurn checks the stamp')

# ── 5. and it throws in dev, like P927 ──────────────────────────────
sub(u"""  G._pTurnPts=_pTurnPts;
  G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;""",
    u"""  G._pTurnPts=_pTurnPts;
  /* P930: loud in dev, for the reason P927 is - this file's history is of
     passive warnings surviving two hundred patches. Raised after _pTurnPts is
     published so the value is consistent for anything already reading it. */
  if(!_pTurnBankedOK&&window._fkDbgOn)
    throw new Error('[fark P930] _pTurnBanked was stale (stamped turn '+
      G._pTurnBankedTurn+', current '+G.turnNum+'). A player turn was entered '+
      'without startPTurn and the reset was skipped.');
  G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;""",
    '5 the dev throw')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

if code.count('G._pTurnBankedTurn=G.turnNum') != 2:
    sys.exit('the stamp is not written at both credit sites (nothing written)')
if code.count('G._pTurnBankedTurn=-1') != 1:
    sys.exit('the stamp is not reset exactly once (nothing written)')
# EVERY WRITE OF THE VALUE IS PAIRED WITH A WRITE OF THE STAMP - the whole point
# ASSIGNMENTS ONLY, NOT COMPARISONS. `G._pTurnBankedTurn===G.turnNum` contains
# `G._pTurnBankedTurn=` as a substring, so a plain count read 4 stamp writes
# against 3 value writes and reported them unpaired. The negative lookahead
# excludes `==`/`===`. Counting a mention instead of the thing, inside the very
# assert written to enforce pairing.
_val = [m.start() for m in re.finditer(r'G\._pTurnBanked=(?!=)', code)]
_stamp = [m.start() for m in re.finditer(r'G\._pTurnBankedTurn=(?!=)', code)]
if len(_val) != len(_stamp):
    sys.exit('%d writes of the value against %d of the stamp - they are not '
             'paired (nothing written)' % (len(_val), len(_stamp)))
for v in _val:
    if not any(0 <= t - v <= 80 for t in _stamp):
        sys.exit('a write of _pTurnBanked has no stamp beside it (nothing written)')
# the guard is computed before it is read, and before the throw
_ok = code.index('var _pTurnBankedOK=')
_use = code.index('_pTurnBankedOK?(G._pTurnBanked||0):0')
_throw = code.index("throw new Error('[fark P930]")
if not (_ok < _use < _throw):
    sys.exit('the stamp check is not computed before its uses (nothing written)')
# _pTurnPts is published before the throw, so a reader already holding it is consistent
if code.index('G._pTurnPts=_pTurnPts') > _throw:
    sys.exit('the throw pre-empts publishing _pTurnPts (nothing written)')
# P929's read still prefers turnPts when it has one
if code.count('(G.turnPts||0)||(_pTurnBankedOK?(G._pTurnBanked||0):0)') != 1:
    sys.exit('endPTurn no longer prefers turnPts (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
