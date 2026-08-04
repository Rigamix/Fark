# -*- coding: utf-8 -*-
"""The opponent holds family cards. Do any of them do anything?

PROTO_NOTES says NPC cards land in P5 with "G.oF stays []" until then. That is
STALE: _famInitOpp is implemented and deals a boss 1-3 cards from its family,
scaling with the night. So the opponent already holds cards.

famFire iterates both sides - `['p','o'].forEach` - so those cards are visited.
The question is whether their hooks DO anything when visited, and the answer
turns on one helper:

    function _fxMine(ev){return !!(ev&&ev.mine&&ev.owner==='p');}

A hook gated on _fxMine returns early for an opponent-owned card. Every such
card is dealt, displayed, and inert.

THIS IS A COUNT I ALREADY GOT WRONG ONCE. A single-line regex found 9 hook
bodies and I nearly reported 8-of-9; there are far more, and most hook bodies
span lines. This brace-matches every CFX entry and every hook inside it, so
the denominator is the real one.

WHAT IT CANNOT SEE: a hook that gates on ev.owner in a way that happens to be
correct for the opponent, or one whose body only makes sense for the player
regardless of gating. Every hook not gated on _fxMine is LISTED, not assumed
fine - the point is to produce a set small enough to read.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

HOOKS = ('canUse', 'use', 'roll', 'bank', 'bankBonus', 'turnStart', 'bust',
         'commit', 'deadRoll', 'rivalTurn')

# TAKES THE STRING IT SEARCHES. The first version closed over `s` (the whole
# file) while callers passed indexes into `body` (one CFX entry) - so every
# "hook body" came back as CSS from the top of the file and the classification
# was meaningless. The tell was `--hud-h: 80px` appearing as a hook body;
# an index is only meaningful against the string it was computed from.
def block(txt, start):
    b = txt.index('{', start)
    d, j = 0, b
    while j < len(txt):
        if txt[j] == '{':
            d += 1
        elif txt[j] == '}':
            d -= 1
            if d == 0:
                return txt[b:j + 1]
        j += 1
    return ''

entries = []
for m in re.finditer(r'\bCFX\.([A-Za-z_][\w]*)\s*=\s*\{', s):
    entries.append((m.group(1), block(s, m.end() - 1)))

mine, owner, neither = [], [], []
for cid, body in entries:
    for hm in re.finditer(r'\b(' + '|'.join(HOOKS) + r')\s*:\s*function\s*\(', body):
        hb = block(body, hm.end())
        tag = (cid, hm.group(1))
        if '_fxMine' in hb:
            mine.append(tag)
        elif 'ev.owner' in hb or "owner===" in hb:
            owner.append(tag)
        else:
            neither.append((cid, hm.group(1), re.sub(r'\s+', ' ', hb)[:64]))

total = len(mine) + len(owner) + len(neither)
print('CFX entries: %d    hooks: %d\n' % (len(entries), total))
print('PLAYER-ONLY  (gated on _fxMine, inert for the opponent): %d' % len(mine))
for c, h in sorted(mine):
    print('   %-20s %s' % (c, h))
print('\nOWNER-AWARE  (reads ev.owner directly): %d' % len(owner))
for c, h in sorted(owner):
    print('   %-20s %s' % (c, h))
print('\nUNGATED      (fires for whoever holds it): %d' % len(neither))
for c, h, snip in sorted(neither):
    print('   %-20s %-10s %s' % (c, h, snip))

print('\n' + '=' * 74)
print('%d of %d hooks are player-only. Every opponent card whose hooks are all'
      % (len(mine), total))
print('in that set is dealt by _famInitOpp, shown to the player, and does')
print('nothing. That is the P5 question - not whether the opponent HAS cards,')
print('which it already does.')
