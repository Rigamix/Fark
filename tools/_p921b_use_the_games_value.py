# -*- coding: utf-8 -*-
u"""P921b: the turn's value comes from the game, not from the harness's bookkeeping.

P921 reconstructed each turn's score in the driver - pendingBank set at the bank
decision, turnHadBust set in the doBust wrap, and endPTurn choosing between them.
That is a reimplementation of something the game already computes, and it was
about to be wrong.

THE GAME HAS THE FIELD, AND ITS COMMENT SAYS SO. endPTurn's first statement is

    var _pTurnPts=(G.turnPts||0);
    G._pTurnPts=_pTurnPts;

under a comment that reads "A bust is a turn worth ZERO, not no turn - it
happened and it produced a value", and that records the measurement behind it:
of ten endPTurn call sites, the seven that clear turnPts first are the five bust
paths plus steal_low_bank and block_low_bank, all cases where the player banked
nothing; the normal bank routes via handleYield, which never touches turnPts, so
it arrives carrying its real total.

WHERE MY VERSION WOULD HAVE BEEN WRONG. Amber eats a bust, and doBust has TWO
exits from that branch - the play-on path and an `!_amOK` bank-out where the
player banks what they have. On that path the driver never taps bank, so
pendingBank is null and turnHadBust is false, and P921 would have recorded 0 for
a turn that banked. steal_low_bank and block_low_bank are two more paths the
harness knows nothing about. Ten call sites, and the harness modelled two.

So the wrap reads G.turnPts BEFORE delegating - the same value at the same
moment as the game's own first line - and every path is covered by construction
rather than by enumeration.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', 'fark_driver.js')
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


sub(u"""    const turnSeq = [];
    let pendingBank = null, turnHadBust = false;""",
    u"""    const turnSeq = [];""",
    '1 the bookkeeping goes')

sub(u"""      window.doBust = function () {
        busts++; bustJustFired = true;
        /* read the save BEFORE doBust spends it */
        try { if (!(G && G._bustImmuneTurn)) turnHadBust = true; } catch (e) { turnHadBust = true; }
        return _origBust.apply(this, arguments);
      };
      window.endPTurn = function () {
        endPTurnsSeen++;
        turnSeq.push(turnHadBust ? 0 : (pendingBank != null ? pendingBank : 0));
        pendingBank = null; turnHadBust = false;
        return _origEndPT.apply(this, arguments);
      };""",
    u"""      window.doBust = function () {
        busts++; bustJustFired = true;
        return _origBust.apply(this, arguments);
      };
      window.endPTurn = function () {
        endPTurnsSeen++;
        /* P921b: THE GAME'S OWN NUMBER, read at the game's own moment. endPTurn's
           first statement is `var _pTurnPts=(G.turnPts||0)` under a comment that
           says "A bust is a turn worth ZERO, not no turn - it happened and it
           produced a value", and that records the measurement: of TEN endPTurn
           call sites, seven clear turnPts first - the five bust paths plus
           steal_low_bank and block_low_bank - and the normal bank routes via
           handleYield, which never touches turnPts.
           The harness modelled two of those ten. Reconstructing the value from
           bank taps and bust events would have recorded 0 for amber's `!_amOK`
           bank-out, where the bust is eaten and the player banks anyway without
           the driver ever tapping bank. Reading the field covers every path by
           construction instead of by enumeration. */
        try { turnSeq.push(G ? (G.turnPts || 0) : 0); } catch (e) { turnSeq.push(0); }
        return _origEndPT.apply(this, arguments);
      };""",
    '2 the value is read from the game')

sub(u"""      if (doBank) { banks++; bankAmounts.push(turn); pendingBank = turn; }""",
    u"""      if (doBank) { banks++; bankAmounts.push(turn); }""",
    '3 the bank site is left alone again')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# the harness no longer reconstructs anything
for gone in ('pendingBank', 'turnHadBust'):
    if gone in code:
        sys.exit('%s survives - the reconstruction is still there (nothing written)' % gone)
# the read happens BEFORE the original clears turnPts
_end = code.index('window.endPTurn = function ()')
_push = code.index('turnSeq.push(', _end)
_delegate = code.index('_origEndPT.apply', _end)
if not (_push < _delegate):
    sys.exit('the turn value is read after endPTurn clears it (nothing written)')
# exactly one place records a turn, and it is inside the endPTurn wrap
if code.count('turnSeq.push(') != 2:   # the read, plus the catch fallback
    sys.exit('the turn is recorded from %d sites, expected the read and its catch '
             '(nothing written)' % code.count('turnSeq.push('))
_ret = code.index('return {', _end)
if code[_end:_ret].count('turnSeq.push(') != 2:
    sys.exit('a turn is recorded outside the endPTurn wrap (nothing written)')
# P920's identity and its control are untouched
for need in ('turnSeqComplete:', 'bustCountsAgree:', 'turnsAddUp:', 'bustHookOnPath:'):
    if code.count(need) != 1:
        sys.exit('%s is not returned exactly once (nothing written)' % need)
if code.count('banks++') != 1 or code.count('busts++') != 1:
    sys.exit('the bank or bust counter moved (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
