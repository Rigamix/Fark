# -*- coding: utf-8 -*-
u"""P929: _pTurnPts was 0 on every banked turn, so a rival ILL OMEN always landed.

MEASURED FIRST. Sixteen matches recorded G.turnPts at the top of endPTurn and got
0 on every single turn, including turns that banked 8050. G._pTurnPts, the field
endPTurn computes from it, was 0 too.

WHY. endPTurn's comment says "The normal bank routes via handleYield, which never
touches turnPts, so it arrives carrying its real total." handleYield indeed never
touches it - but handleBank does, before ever reaching handleYield: it credits
G.pPts+=total and then calls _turnScoreClear(), which is G.turnPts=0. By the time
endPTurn runs, the turn's value has already been moved into pPts and wiped. The
comment is stale for the bank path, and it is load-bearing.

AND IT IS A LIVE GAMEPLAY BUG, not just a harness annoyance. endPTurn fires
famFire('rivalTurn',{actor:'o',pts:_pTurnPts}), and CFX.ill_omen.rivalTurn
branches on exactly that:

    if(ev.pts<=0){ /* THE OMEN LANDS - take points */ }
    else         { /* the omen misses - small consolation */ }

With _pTurnPts always 0, a RIVAL-held Ill Omen always lands - whether the player
busted or banked two thousand. Its own text is "BUST NEXT TURN AND PAY". The
mirror fire at finOpp passes a real local, so the PLAYER's Ill Omen has always
worked correctly, which makes the card asymmetric against the player. P766's
comment describes the intent as "Exactly the player's numbers upside down,
MINTING INCLUDED"; this is the half that never was.

THE VALUE ALREADY EXISTS TWO LINES EARLIER. handleBank sets G._lastBankAmount=
total at the credit, right before _turnScoreClear. That field cannot be reused
directly - THE RECKONING (37153, 38449) compares the rival's bank against it
across the rival's turn, so it must persist - so a turn-scoped twin is captured
beside it and reset at the top of each player turn.

BUST SEMANTICS ARE PRESERVED. A busted turn never reaches handleBank, so the
twin stays 0 from the turn's reset and _pTurnPts is 0 - which is what the
existing comment correctly wants: "A bust is a turn worth ZERO, not no turn."
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def patch(path, pairs, checks):
    s = io.open(path, encoding='utf-8', newline='').read()
    for _i, (old, new) in enumerate(pairs):
        label = '%s #%d' % (os.path.basename(path), _i + 1)
        pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
        ms = list(re.finditer(pat, s))
        if len(ms) != 1:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
        m = ms[0]
        rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
        s = s[:m.start()] + rep + s[m.end():]
        edits.append(label)
    code = re.sub(r'/\*[\s\S]*?\*/', '', s)
    for fn, msg in checks:
        if not fn(code):
            sys.exit('%s (nothing written)' % msg)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)


P = os.path.join(ROOT, 'fark_proto.html')
patch(P, [
    # ── the two credit sites capture a turn-scoped twin ──
    (u"""    G._tabHeldPlayer=(G._tabHeldPlayer||0)+total;
    G._lastBankAmount=total;spawnBankPop(total);""",
     u"""    G._tabHeldPlayer=(G._tabHeldPlayer||0)+total;
    G._lastBankAmount=total;G._pTurnBanked=total;/* P929 */spawnBankPop(total);"""),
    (u"""    G.pPts+=total;G._lastBankAmount=total;spawnBankPop(total);""",
     u"""    G.pPts+=total;G._lastBankAmount=total;G._pTurnBanked=total;/* P929 */spawnBankPop(total);"""),
    # ── reset per player turn, beside the rest of the turn wipe ──
    (u"""  G.numDice=G.matchDice?G.matchDice.length:6;""",
     u"""  G.numDice=G.matchDice?G.matchDice.length:6;
  /* P929: the turn-scoped twin of _lastBankAmount, reset here so a BUSTED turn
     cannot inherit the previous turn's bank. _lastBankAmount itself must NOT be
     reset - THE RECKONING compares the rival's bank against it across the
     rival's turn - which is why this is a separate field. */
  G._pTurnBanked=0;"""),
    # ── and endPTurn reads the value that still exists ──
    (u"""     block_low_bank - all cases where the player banked nothing, so 0 is the
     right answer. The normal bank routes via handleYield, which never touches
     turnPts, so it arrives carrying its real total. */
  var _pTurnPts=(G.turnPts||0);""",
     u"""     block_low_bank - all cases where the player banked nothing, so 0 is the
     right answer.
     P929: THE SECOND HALF OF THAT SENTENCE WAS WRONG, AND IT WAS LOAD-BEARING.
     It read "The normal bank routes via handleYield, which never touches
     turnPts, so it arrives carrying its real total." handleYield indeed never
     touches turnPts - but handleBank does, before ever reaching it: it credits
     G.pPts+=total and then calls _turnScoreClear(), which is G.turnPts=0. So on
     EVERY banked turn this read 0. Measured across sixteen matches, including
     turns that banked 8050.
     That made famFire('rivalTurn',{pts:_pTurnPts}) below always carry zero, and
     CFX.ill_omen.rivalTurn branches on `ev.pts<=0` to decide whether the omen
     LANDS - so a rival-held Ill Omen collected on every turn regardless of what
     the player did, against a card that reads "BUST NEXT TURN AND PAY". The
     player-held mirror at finOpp passes a real local and has always worked,
     which is what made the card asymmetric.
     _pTurnBanked is captured at the credit in handleBank, two lines before the
     clear, and reset at the top of each player turn - so a bust still reads 0,
     which is what the paragraph above correctly wants. */
  var _pTurnPts=(G.turnPts||0)||(G._pTurnBanked||0);"""),
], [
    (lambda c: c.count('G._pTurnBanked=total') == 2,
     'the twin is not captured at both credit sites'),
    (lambda c: c.count('G._pTurnBanked=0') == 1,
     'the twin is not reset exactly once'),
    (lambda c: c.count('(G.turnPts||0)||(G._pTurnBanked||0)') == 1,
     'endPTurn does not read the twin'),
    # THE RESET MUST PRECEDE THE READ IN PROGRAM ORDER within a turn: reset sits
    # in startPTurn, the read in endPTurn, and startPTurn is the earlier function
    (lambda c: c.index('G._pTurnBanked=0') < c.index('(G.turnPts||0)||(G._pTurnBanked||0)'),
     'the reset is defined after the read'),
    # and _lastBankAmount is NOT reset - the Reckoning depends on it persisting
    (lambda c: c.count('G._lastBankAmount=0') == 0,
     '_lastBankAmount was given a reset it must not have'),
    (lambda c: c.count('G._lastBankAmount=total') == 2,
     'a _lastBankAmount credit site was disturbed'),
    (lambda c: c.count("famFire('rivalTurn',{actor:'o',pts:_pTurnPts})") == 1,
     'the rivalTurn fire was disturbed'),
])

D = os.path.join(ROOT, 'tools', 'fark_driver.js')
patch(D, [
    (u"""        /* P921b: THE GAME'S OWN NUMBER, read at the game's own moment. endPTurn's""",
     u"""        /* P929: read AFTER the original runs, from G._pTurnPts - the field
           endPTurn computes. The previous version read G.turnPts BEFORE
           delegating, on the strength of endPTurn's comment, and got 0 on every
           banked turn across sixteen matches because handleBank clears turnPts
           before endPTurn is ever reached. Taking the game's computed field
           after the fact means the harness inherits the fix rather than
           duplicating the reasoning behind it.
           P921b's note, kept because the reasoning still holds: endPTurn's""")
    ,
    (u"""        try { turnSeq.push(G ? (G.turnPts || 0) : 0); } catch (e) {}
        return _origEndPT.apply(this, arguments);""",
     u"""        const ret = _origEndPT.apply(this, arguments);
        try { turnSeq.push(G ? (G._pTurnPts || 0) : 0); } catch (e) { turnSeq.push(0); }
        return ret;"""),
], [
    (lambda c: c.count('turnSeq.push(G ? (G._pTurnPts || 0) : 0)') == 1,
     'the driver does not read the computed field'),
    (lambda c: 'turnSeq.push(G ? (G.turnPts || 0) : 0)' not in c,
     'the old pre-delegation read survives'),
    (lambda c: c.index('_origEndPT.apply') < c.index('turnSeq.push(G ? (G._pTurnPts'),
     'the driver reads the field before endPTurn computes it'),
])

print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
