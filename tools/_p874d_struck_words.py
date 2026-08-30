# -*- coding: utf-8 -*-
u"""P874d: the struck-word sweep, over every table rather than the diff.

The voice brief's section 5 asks for the struck list to be grepped "against
the final tables" and says any survivor "is a line that is still wearing the
wrong century". Run over the patron and gossip rows the pass rewrote, there
was one. Run over EVERY row - which is what the instruction actually says -
there are fifteen, and they are the most formal speakers in the game:

  trait:orderly  "Statistically unlikely."   the brief names `statistically`
  trait:orderly  "As expected."              in its strike list by hand
  trait:cunning  "As expected."
  boss:brutus    "Acceptable."               a soldier, in an HR memo
  boss:corvus    x4 on expected/unexpected
  boss:whisper   x5 on expected/unexpected

These sit outside section 3's tables and squarely inside section 1's RULES,
which is the distinction that matters: the register ladder is stated as a law
for the whole game, not as a note attached to the rows the pass happened to
rewrite. Denis's complaint was that it "overall feels quite formal for a lot
of the characters" - and the boss barks are where the formality was thickest.

CHARACTER IS PRESERVED, register is not. Corvus stays cold and clerical; he
just reaches for a ledger instead of a laboratory. Whisper stays amused.
Brutus stays blunt. Nobody becomes chatty - the words move a century, the
voices do not move at all.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

# anchored on the WHOLE row: "As expected." alone appears four times, so the
# text is not a unique key and a bare replace would hit the wrong speakers.
SWAPS = [
    (u"""{p:'trait:orderly:yourBust',s:0,g:'v2',t:"As expected."},""",
     u"""{p:'trait:orderly:yourBust',s:0,g:'v2',t:"That follows."},"""),
    (u"""{p:'trait:orderly:yourBank',s:0,g:'v1',t:"Statistically unlikely."},""",
     u"""{p:'trait:orderly:yourBank',s:0,g:'v1',t:"Uncommon, that."},"""),
    (u"""{p:'trait:cunning:bust',s:0,g:'v1',t:"As expected."},""",
     u"""{p:'trait:cunning:bust',s:0,g:'v1',t:"Mm. I had a notion."},"""),
    (u"""{p:'boss:corvus:loss',s:0,t:"Unexpected. I don't care for unexpected. I'll adjust my figures."},""",
     u"""{p:'boss:corvus:loss',s:0,t:"Irregular. I do not care for irregular. I shall amend my figures."},"""),
    (u"""{p:'boss:whisper:loss',s:0,t:"Unexpected. I do enjoy being surprised, on the rare occasion it happens."},""",
     u"""{p:'boss:whisper:loss',s:0,t:"Well. I do enjoy a surprise, on the rare occasion one arrives."},"""),
    (u"""{p:'boss:brutus:loss',s:1,g:'plain-military',t:"Acceptable."},""",
     u"""{p:'boss:brutus:loss',s:1,g:'plain-military',t:"It'll serve."},"""),
    (u"""{p:'boss:brutus:win',s:1,g:'plain-military',t:"As expected."},""",
     u"""{p:'boss:brutus:win',s:1,g:'plain-military',t:"As it should be."},"""),
    (u"""{p:'boss:corvus:win',s:1,g:'prediction-confirmed',t:"Expected. I find that comforting, oddly."},""",
     u"""{p:'boss:corvus:win',s:1,g:'prediction-confirmed',t:"Predictable. I find that comforting, oddly."},"""),
    (u"""{p:'boss:corvus:win',s:1,g:'cold-dismissal',t:"Hm. As expected."},""",
     u"""{p:'boss:corvus:win',s:1,g:'cold-dismissal',t:"Hm. As the ledger had it."},"""),
    (u"""{p:'boss:corvus:win',s:1,g:'plain-acknowledgment',t:"As expected, I suppose."},""",
     u"""{p:'boss:corvus:win',s:1,g:'plain-acknowledgment',t:"As the figures had it, I suppose."},"""),
    (u"""{p:'boss:whisper:loss',s:1,g:'detached-observation',t:"Unexpected, again. Rare, that."},""",
     u"""{p:'boss:whisper:loss',s:1,g:'detached-observation',t:"A surprise, again. Rare, that."},"""),
    (u"""{p:'boss:whisper:win',s:1,g:'knowing-amusement',t:"Mm. As I expected. I usually am."},""",
     u"""{p:'boss:whisper:win',s:1,g:'knowing-amusement',t:"Mm. Just as I reckoned. I usually do."},"""),
    (u"""{p:'boss:whisper:win',s:1,g:'plain-acknowledgment',t:"As expected."},""",
     u"""{p:'boss:whisper:win',s:1,g:'plain-acknowledgment',t:"Just so."},"""),
    (u"""{p:'boss:corvus:greet',s:0,g:'v1',c:['boss_wins:1'],t:"Unexpected. Noted. Sit, we'll see if it repeats."},""",
     u"""{p:'boss:corvus:greet',s:0,g:'v1',c:['boss_wins:1'],t:"Irregular. Noted. Sit, we'll see if it repeats."},"""),
    (u"""{p:'boss:whisper:greet',s:0,g:'v1',c:['boss_wins:1'],t:"Unexpected. I do enjoy being surprised. Sit."},""",
     u"""{p:'boss:whisper:greet',s:0,g:'v1',c:['boss_wins:1'],t:"A surprise. I do enjoy those. Sit."},"""),
]

for old, new in SWAPS:
    if s.count(old) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (s.count(old), old[:60]))
    s = s.replace(old, new)

# ── post-asserts: the strike list, over every row, must come back empty ──
STRUCK = ['acceptable', 'adequate', 'respectable', 'statistically', 'variance',
          'investment', 'strategic', 'composure', 'precisely',
          'correct decision', 'expected']
rows = re.findall(r'\{p:\'[^\']+\',[^\n]*?t:"((?:[^"\\]|\\.)*)"', s)
if len(rows) < 900:
    sys.exit('only parsed %d rows - the row regex is not seeing the table, so a '
             'clean result would be meaningless (nothing written)' % len(rows))
bad = []
for t in rows:
    low = t.lower()
    for w in STRUCK:
        if w in low:
            bad.append(w + ' :: ' + t[:70])
if bad:
    sys.exit('STRUCK WORDS SURVIVE x%d (nothing written):\n  %s'
             % (len(bad), '\n  '.join(bad[:8])))

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d rows moved out of the counting house; strike list clean over %d rows'
      % (len(SWAPS), len(rows)))
