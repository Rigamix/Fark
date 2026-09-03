# -*- coding: utf-8 -*-
u"""P920: the driver's bust counter was blind, and the fix comes with its control.

MEASURED, NOT SUSPECTED. Three matches at band 1 / bank500 reported busts:0
while a wrap on the game's own doBust counted 1, 2 and 0. The driver saw none
of them.

WHY IT COULD NOT SEE THEM. Its busts++ sits inside the branch that runs after
`phase==='choosing'` with clickable dice - it infers a bust from a scoreless
choosing phase. A farkle does not produce one. The game runs doBust and hands
over, so the driver's until() waits out its full twelve seconds, returns null,
and `continue`s. The bust is real, the turn is spent, and nothing counted it.
That is an assumption about the UI standing in for an event the game announces.

WHAT MADE IT VISIBLE WITHOUT A BROWSER RUN. banks + busts should equal pTurns,
because a player turn ends in exactly one of the two. It did not: 9 banks and 9
pTurns with a bust in the middle is arithmetically impossible. The check was
computable from data the driver already returned, on every run, and was never
written down - so the tool reported an impossible triple three times without
noticing.

THREE CHANGES:

  the event is counted where it happens. doBust and endPTurn are wrapped for the
  duration of the match and restored after. endPTurn is the POSITIVE CONTROL,
  not decoration: every player turn ends there, bank or bust, so its count must
  equal pTurns - and without it a zero from the bust wrap is indistinguishable
  from a wrap that is not on the path the game calls. That is the whole reason
  the first zero was believed for three matches.

  the arithmetic is asserted, not just reported. bustsDerived = pTurns - banks
  is computed from two sources that share nothing but the game itself - a
  DOM-tap counter and a game field - and bustCountsAgree says whether the two
  independent measurements match. Convergence between instruments that share a
  mechanism proves nothing; these do not share one.

  and the twelve seconds are given back. The wrap sets a flag, the wait for a
  choosing phase watches it, and a busted turn ends the wait immediately instead
  of timing out. Three busts cost thirty-six seconds across three matches; over
  a ladder that is hours.

The old inference is kept as bustsInferred rather than deleted, because a
disagreement between it and the event is the signature of the UI shape changing
underneath the harness - and that is worth a refusal later, not a silent repair.
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


# ── 1. install the wraps, with the control ──────────────────────────
sub(u"""    const target = targetOf();
    let busts = 0, banks = 0, rolls = 0, keeps = 0, stalled = null;""",
    u"""    const target = targetOf();
    let busts = 0, banks = 0, rolls = 0, keeps = 0, stalled = null;
    /* P920: THE BUST IS COUNTED WHERE IT HAPPENS, and endPTurn is the control.
       The old count inferred a bust from a scoreless `choosing` phase, which a
       farkle never produces - the game runs doBust and hands over, so the wait
       below timed out and the turn went uncounted. Measured: 1, 2 and 0 real
       busts across three matches, all three reported as zero.
       endPTurn is wrapped BESIDE it and is not decoration. Every player turn
       ends there, bank or bust, so its count must equal pTurns; without that a
       zero from the bust wrap cannot be told apart from a wrap sitting off the
       path the game calls, which is exactly how the first zero survived three
       matches. A bust count is only readable when bustHookOnPath is true. */
    let bustsInferred = 0, endPTurnsSeen = 0, bustJustFired = false;
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
    }
    const unhook = function () {
      if (!bustHooked) return;
      window.doBust = _origBust; window.endPTurn = _origEndPT;
    };""",
    '1 the wraps and the control')

# ── 2. the wait ends on a bust instead of timing out ────────────────
sub(u"""      const got = await until(() => G._endMatchFired ||
        (G.phase === 'choosing' &&
         (G.pool || []).some(d => !d.committed && d.el && d.el.onclick)), 12000);
      if (G._endMatchFired) break;
      if (got == null) continue;""",
    u"""      /* P920: A BUSTED TURN ENDS THIS WAIT. It used to run the full twelve
         seconds and return null, because a farkle never reaches a choosing
         phase - twelve seconds of nothing per bust, which over a ladder is
         hours. The wrap knows the moment it happens. */
      bustJustFired = false;
      const got = await until(() => G._endMatchFired || bustJustFired ||
        (G.phase === 'choosing' &&
         (G.pool || []).some(d => !d.committed && d.el && d.el.onclick)), 12000);
      if (G._endMatchFired) break;
      if (bustJustFired) {
        /* let the handover land before the loop looks for the next roll */
        const turnWas = G.turnNum;
        await until(() => G._endMatchFired || G.turnNum !== turnWas ||
                          G.phase === 'idle', 12000);
        continue;
      }
      if (got == null) continue;""",
    '2 the wait ends on the event')

# ── 3. the old inference is kept, not deleted ───────────────────────
sub(u"""      if (!r || !r.total || r.total <= 0) {
        busts++;""",
    u"""      if (!r || !r.total || r.total <= 0) {
        /* P920: THE OLD INFERENCE, KEPT AND RENAMED. It is not the bust count
           any more - the event is - but a disagreement between the two is the
           signature of the UI shape changing under the harness, which is worth
           seeing rather than silently repairing. */
        bustsInferred++;""",
    '3 the inference is renamed')

# ── 4. and the arithmetic that would have caught it is asserted ─────
sub(u"""      busts, banks, rolls, keeps, bankAmounts,""",
    u"""      busts, banks, rolls, keeps, bankAmounts,
      /* P920: THE CHECK THAT WAS COMPUTABLE ALL ALONG. A player turn ends in
         exactly one of a bank or a bust, so banks + busts === pTurns. Nine
         banks and nine pTurns with a bust among them is impossible, and the
         driver returned that triple three times without anyone able to see it,
         because the identity was never written down. bustsDerived comes from a
         DOM-tap counter and a game field; busts comes from a wrap on the game's
         own event. They share nothing but the game, so their agreement is
         evidence rather than an echo. */
      bustsInferred, endPTurnsSeen, bustHooked,
      bustHookOnPath: bustHooked && _pT != null && endPTurnsSeen === _pT,
      bustsDerived: (_pT != null) ? _pT - banks : null,
      bustCountsAgree: (_pT != null) ? (_pT - banks) === busts : null,
      turnsAddUp: (_pT != null) ? (banks + busts) === _pT : null,""",
    '4 the identity is asserted')

# ── 5. pTurns read once, before the return needs it ─────────────────
sub(u"""    const pPts = (G && G.pPts) || 0, oPts = (G && G.oPts) || 0;
    return {""",
    u"""    unhook();
    const pPts = (G && G.pPts) || 0, oPts = (G && G.oPts) || 0;
    /* read once - four fields below compare against it and a re-read between
       them would let them disagree about the same match */
    const _pT = (function () { try { return G ? (G.pTurns || 0) : null; }
                               catch (e) { return null; } })();
    return {""",
    '5 pTurns is read once')

sub(u"""      pTurns: (function(){ try { return G ? (G.pTurns || 0) : null; } catch(e){ return null; } })(),""",
    u"""      pTurns: _pT,""",
    '6 pTurns uses the single read')

sub(u"""      hitTheCap: (function(){ try { return !!(G && G.turnCap && (G.pTurns||0) >= G.turnCap); }
                              catch(e){ return null; } })(),""",
    u"""      hitTheCap: (function(){ try { return !!(G && G.turnCap && _pT != null && _pT >= G.turnCap); }
                              catch(e){ return null; } })(),""",
    '7 hitTheCap uses the single read')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# THE WRAPS MUST BE RESTORED ON EVERY EXIT FROM playMatch, or the next match in
# the same page runs with a stale counter still incrementing. There are two
# returns after the hook is installed: the stall path is inside the loop and
# falls through to the tail, so the tail's unhook covers both.
if code.count('const unhook = function ()') != 1:
    sys.exit('unhook is not defined once (nothing written)')
if code.count('unhook();') != 1:
    sys.exit('unhook is not called exactly once (nothing written)')
_hookAt = code.index('window.doBust = function ()')
_unhookAt = code.index('unhook();')
if _unhookAt < _hookAt:
    sys.exit('the wraps are restored before they are installed (nothing written)')
# and no `return` between the hook and the unhook would skip it
_between = code[_hookAt:_unhookAt]
if re.search(r'\n    return ', _between):
    sys.exit('a top-level return skips unhook (nothing written)')
# the control and the identity are both present
for need in ('bustHookOnPath:', 'bustsDerived:', 'bustCountsAgree:', 'turnsAddUp:'):
    if code.count(need) != 1:
        sys.exit('%s is not returned exactly once (nothing written)' % need)
# the old inference survives under its new name and is no longer the count
if 'bustsInferred++' not in code:
    sys.exit('the old inference was deleted rather than renamed (nothing written)')
if code.count('busts++') != 1:
    sys.exit('busts is incremented somewhere other than the wrap (nothing written)')
# pTurns IS READ ONCE INSIDE THE RETURN, which is the scope that matters - the
# pre-match check at the top legitimately reads it too, to confirm it is 0
# before the match starts, and a file-wide count called that a violation. Third
# time this session an assert counted a string instead of the thing it names.
# scanned from the RETURN OBJECT, not from the declaration - _pT's own
# definition necessarily contains the read it exists to replace, and the first
# version of this check flagged it
_ret = code.index('return {', code.index('const _pT = '))
if 'G.pTurns' in code[_ret:]:
    sys.exit('the return block still reads G.pTurns directly (nothing written)')
# exactly two reads survive ahead of the return object, and both are meant to:
# the pre-match check that pTurns is 0, and _pT's own definition
if code[:_ret].count('G.pTurns') != 2:
    sys.exit('expected the pre-match check and _pT and found %d reads (nothing written)'
             % code[:_ret].count('G.pTurns'))
if '(G.pTurns || 0) === 0' not in code[:_ret]:
    sys.exit('the pre-match pTurns check was disturbed (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
