# -*- coding: utf-8 -*-
u"""P473 - lift the generateOppCards stub. Patrons hold cards again.

RULED: lift it, with a same-seed before/after so the difficulty delta is
attributable to THIS and not blended with the aggression pass or the challenge
fix. Third change on that axis this session; OPEN.md 6 exists for exactly this.

SIZED FIRST (docs/OPPCARDS_LIFT_SIZE.md): all 41 pooled ids resolve, every field
the dead code reads still exists, the 8 start_bonus cards are handled, and
steal_on_bust works by card id. Deleting one line is the whole change.

WHAT THIS SWITCHES ON, stated plainly because it is a balance change and not a
refactor: three patron-favouring mirror mechanics, every mechanic-dispatched
patron card, and every start_bonus - up to +3500 for Whisper.

ALSO FIXES THREE COMMENTS THAT NAME THE WRONG CARD. They would send the next
reader hunting a mechanic no card has:

  L25017  "iron_gate_npc: reroll one scoring die (uses:2)"  sits above a
          reroll_scoring branch. Iron Gate is steal_on_bust.
  L26247  "Block opp's low bank (iron_gate_npc)"            block_low_bank is
  L26776  "Block low bank (iron_gate_npc)"                  carried by NO card.

The replacements name the MECHANIC, which is checkable against the branch
directly below them, rather than a card id that can drift away from it. That is
the same failure as mabels_pinch earlier - a plausible name beside correct
numbers, surviving a whole patch because nobody checks a comment.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── the lift ──
STUB = u"  return [];/* P1 cutover: NPC family cards land in P5 */\n"
assert s.count(STUB) == 1, 'stub matched %d' % s.count(STUB)
s = s.replace(STUB, u"""  /* P473 - THE STUB IS LIFTED. This returned [] unconditionally since the P1
     cutover, so G.oCards was ALWAYS empty and every patron card was dealt to
     nobody. Sized before lifting: all 41 pooled ids resolve in NPC_CARDS, every
     field below still exists, the 8 start_bonus cards have handlers, and
     steal_on_bust is wired by card id. Nothing under here needed changing. */
""")

def one(old, new, label):
    global s
    assert s.count(old) == 1, '%s matched %d' % (label, s.count(old))
    s = s.replace(old, new)

# ── the three misattributing comments ──
one(u"/* iron_gate_npc: reroll one scoring die (uses:2) */",
    u"/* reroll_scoring: reroll one scoring die, up to eff.uses times.\n"
    u"       NOT iron_gate_npc - that card carries steal_on_bust. Naming the\n"
    u"       mechanic keeps this checkable against the branch below it. */",
    'L25017 comment')
one(u"/* Block opp's low bank (iron_gate_npc) */",
    u"/* block_low_bank, opponent side. NO CARD currently declares this\n"
    u"           mechanic - it is implemented on both seats and never dealt. */",
    'L26247 comment')
one(u"/* Block low bank (iron_gate_npc) */",
    u"/* block_low_bank, player side. NO CARD currently declares this\n"
    u"       mechanic - implemented on both seats and never dealt. */",
    'L26776 comment')

assert s != orig, 'nothing changed'
# the stub is gone and the body below it is intact
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
m = re.search(r'function\s+generateOppCards\s*\(', body)
b = body.index('{', m.end() - 1)
d, j = 0, b
while j < len(body):
    if body[j] == '{':
        d += 1
    elif body[j] == '}':
        d -= 1
        if d == 0:
            break
    j += 1
fn = body[b:j + 1]
assert not re.match(r'\{\s*return\s*\[\s*\]\s*;', fn), 'function still returns [] first'
for needed in ['rung.cardPool', 'rung.cardChance', 'S.npcWonCards',
               'rung.cardCount', '_sig', '_picked']:
    assert needed in fn, 'lift damaged the body: %s missing' % needed
# no comment names iron_gate_npc as a mechanic it does not carry
assert "iron_gate_npc: reroll" not in s
assert "(iron_gate_npc)" not in s, 'a misattributing comment survives'
# iron_gate_npc's real wiring is untouched
assert s.count("indexOf('iron_gate_npc')") == 1
assert s.count("G.pCards.includes('iron_gate_npc')") == 1

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P473 applied: generateOppCards lifted; 3 misattributing comments corrected')
