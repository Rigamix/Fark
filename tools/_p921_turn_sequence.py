# -*- coding: utf-8 -*-
u"""P921: the driver records turn outcomes IN ORDER, so position is recoverable.

WHY. The exchangeability control on the reach resample has to separate two
failure modes with OPPOSITE signs, and a one-sided check cannot:

  HETEROGENEITY - turns differ systematically by position, because per-match
  consumables are spent early and one-shot effects do not come back. Pooling
  turns that are not homogeneous makes the RESAMPLED spread larger than the
  observed one.

  COUPLING - turn N's outcome depends on turn N-1's. That makes the OBSERVED
  spread larger than the resampled one.

Both can be present at once and cancel into a clean-looking pass. The repair is
to resample turn i from turn i's OWN bag, which needs the position of every
turn - and the driver did not record it. bankAmounts held the banked turns in
order and the busts were appended as zeros at the END, so a busted turn 2 and a
busted turn 9 were indistinguishable.

WHAT THIS RECORDS. turnSeq is one entry per COMPLETED player turn, in order,
holding the points banked or 0 for a bust. Its length must equal pTurns, which
is the same identity P920 asserted from the other direction.

AND IT IS RECORDED AT endPTurn, NOT AT doBust, because amber eats a bust and the
turn CONTINUES. A zero pushed at every doBust would invent a turn that never
ended. doBust spends _bustImmuneTurn on entry, so the wrap reads the flag BEFORE
delegating - that is the only moment at which "will this bust actually end the
turn" is answerable.
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


# ── 1. the wraps also build the ordered sequence ────────────────────
sub(u"""    let bustsInferred = 0, endPTurnsSeen = 0, bustJustFired = false;
    const _origBust = window.doBust, _origEndPT = window.endPTurn;
    const bustHooked = typeof _origBust === 'function' && typeof _origEndPT === 'function';
    if (bustHooked) {
      window.doBust = function () {
        busts++; bustJustFired = true;
        return _origBust.apply(this, arguments);
      };
      window.endPTurn = function () {
        endPTurnsSeen++;
        return _origEndPT.apply(this, arguments);
      };
    }""",
    u"""    let bustsInferred = 0, endPTurnsSeen = 0, bustJustFired = false;
    /* P921: ONE ENTRY PER COMPLETED TURN, IN ORDER - points banked, or 0 for a
       bust. bankAmounts holds the banked turns in order and the busts used to be
       appended as zeros at the END, so a busted turn 2 and a busted turn 9 were
       indistinguishable and "resample turn i from turn i's own bag" was not
       computable. That matters because the exchangeability check on a reach
       resample has to separate two failure modes with OPPOSITE signs -
       heterogeneity by position makes the resample run hot, coupling across
       positions makes the observed run hot - and a single ratio cannot, because
       both can be present and cancel.
       RECORDED AT endPTurn, NOT AT doBust: amber eats a bust and the turn
       CONTINUES, so a zero pushed at every doBust would invent a turn that never
       ended. doBust spends _bustImmuneTurn on entry, so the wrap has to read the
       flag BEFORE delegating - that is the only moment at which "will this bust
       actually end the turn" can be answered. */
    const turnSeq = [];
    let pendingBank = null, turnHadBust = false;
    const _origBust = window.doBust, _origEndPT = window.endPTurn;
    const bustHooked = typeof _origBust === 'function' && typeof _origEndPT === 'function';
    if (bustHooked) {
      window.doBust = function () {
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
      };
    }""",
    '1 the ordered sequence')

# ── 2. the bank decision records its amount for the turn ────────────
sub(u"""      if (doBank) { banks++; bankAmounts.push(turn); }""",
    u"""      if (doBank) { banks++; bankAmounts.push(turn); pendingBank = turn; }""",
    '2 the bank amount is held for endPTurn')

# ── 3. and it is returned, with the identity that guards it ─────────
sub(u"""      bustsInferred, endPTurnsSeen, bustHooked,""",
    u"""      bustsInferred, endPTurnsSeen, bustHooked,
      /* P921: the ordered per-turn record. Its length must equal pTurns - the
         same identity P920 asserts from the other side - or a resample built on
         it is drawing from a sample with holes. */
      turnSeq, turnSeqComplete: (_pT != null) && turnSeq.length === _pT,
      turnSeqBusts: turnSeq.filter(function (x) { return x === 0; }).length,""",
    '3 the sequence is returned')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# THE REGION IS THE UNIT. Scope everything to playMatch's body between the wrap
# install and the return object; `turnSeq` and `pendingBank` exist nowhere else,
# but scoping is the rule now rather than a thing done when it seems needed.
_hook = code.index('window.doBust = function ()')
_ret = code.index('return {', _hook)
region = code[_hook:_ret]

if region.count('turnSeq.push(') != 1:
    sys.exit('the turn is recorded other than once per endPTurn (nothing written)')
if 'turnSeq.push(' not in code[code.index('window.endPTurn = function ()'):_ret]:
    sys.exit('the turn is not recorded inside the endPTurn wrap (nothing written)')
# the bust flag must be read BEFORE doBust is delegated to, or the save is spent
_bustWrap = code.index('window.doBust = function ()')
_delegate = code.index('_origBust.apply', _bustWrap)
_readFlag = code.index('_bustImmuneTurn', _bustWrap)
if _readFlag > _delegate:
    sys.exit('the immunity flag is read after doBust spends it (nothing written)')
# pendingBank is set exactly where a bank is counted, and cleared exactly once
if region.count('pendingBank = null') != 1:
    sys.exit('pendingBank is cleared other than once (nothing written)')
if code.count('pendingBank = turn') != 1:
    sys.exit('pendingBank is set other than at the bank (nothing written)')
# and banks is still counted at the same site, so P920's identity survives
if code.count('banks++') != 1:
    sys.exit('banks is counted somewhere new (nothing written)')
for need in ('turnSeqComplete:', 'turnSeqBusts:', 'bustCountsAgree:', 'turnsAddUp:'):
    if code.count(need) != 1:
        sys.exit('%s is not returned exactly once (nothing written)' % need)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
