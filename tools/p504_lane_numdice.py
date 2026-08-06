# -*- coding: utf-8 -*-
u"""P504 - removing a die must shrink numDice too, or lanes duplicate.

REPORTED: a die taken by a mechanic, then a reroll, and lanes stop holding.

THE PLAN'S HYPOTHESIS WAS WRONG IN A USEFUL WAY. It predicted lane is read from
array index at RENDER time, which would have meant rebuilding lane assignment
architecture. It is not: `_laneOf` returns a stable per-die id and only falls
back to indexOf for legacy dice. That architecture is correct and needed no
work. The corruption is at STAMP time:

    var hotN = G.numDice || 6;
    for (let i = 0; i < hotN; i++)
      G.pool.push({ ..., mat:  G.matchDice[i % G.matchDice.length],
                         ench: G._enchArr[i % G.matchDice.length],
                         lane: i % G.matchDice.length });

The loop LENGTH comes from G.numDice; the INDEX comes from G.matchDice.length.
Remove a die and update only one of them and the modulo WRAPS: six iterations
over five lanes gives 0,1,2,3,4,0 - lane 0 duplicated, lane 5 gone, and the
sixth die inheriting lane 0's MATERIAL and ENCHANT as well. Starting from
jade,iron,bone,bone,bone the player gets back a second jade.

THREE OF FOUR SPLICE SITES OMIT THE DECREMENT, and they are the same three
P480 had to fix for _enchArr - Break is again the only complete one:

    L14266  sacrifice / obsidian shatter    no decrement
    L19098  break                           HAS it
    L24572  royal_seizure (steal_die)       no decrement
    L24580  blessed_confiscation (steal_die) no decrement

Third instance of this exact shape at these exact sites. Break was written
first and completely; the later three copied the splice without the bookkeeping
around it.

FIXED AT THE SITES, NOT AT THE READER. Clamping in the pool build would paper
over an inconsistent state rather than stop it existing, and the same
divergence would still be visible to anything else that reads either value.
Follows Break's own line exactly so there is one pattern in the file.

NOT PICKPOCKET. Checked: it splices G.pool only - never matchDice, numDice,
_enchArr or lane - so it cannot cause this. If the reporter's mechanic really
was a per-roll palm, that is a SEPARATE positional bug and this fix should not
be credited with it.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

DEC = (u"\n        if(G.numDice)G.numDice=Math.max(1,G.numDice-1);"
       u"/* P504: numDice must shrink with matchDice or the pool build's"
       u" i%%matchDice.length wraps and duplicates lane 0 */")

# ── sacrifice / obsidian shatter ──
SAC = u"if(mi>=0)G.matchDice.splice(mi,1);if(mi>=0&&G._enchArr&&mi<G._enchArr.length)G._enchArr.splice(mi,1);}"
assert s.count(SAC) == 1, 'sacrifice matched %d' % s.count(SAC)
s = s.replace(SAC, SAC[:-1] + (DEC % ()) + u"}")

# ── the two steal_die sites: identical splice text, disambiguated by the
#    comment above each, exactly as P480 had to do ──
TB = (u"/* Remove die — player plays with 5 */" + "\n"
      u"        G.matchDice.splice(pBestIdx3,1);")
assert s.count(TB) == 1, 'take_best matched %d' % s.count(TB)
s = s.replace(TB, TB + (DEC % ()))

TU = (u"/* Remove from player, add to NPC */" + "\n"
      u"        G.matchDice.splice(pBestIdx3,1);")
assert s.count(TU) == 1, 'take_and_use matched %d' % s.count(TU)
s = s.replace(TU, TU + (DEC % ()))

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
# every splice of matchDice must now have a numDice update within reach
n_sp = 0
for m in re.finditer(r'G\.matchDice\.splice\(', body):
    n_sp += 1
    win = body[m.start():m.start() + 340]
    assert re.search(r'G\.numDice\s*=', win), \
        'a matchDice splice at offset %d still does not touch numDice' % m.start()
assert n_sp == 4, 'expected 4 splice sites, found %d' % n_sp
# P480's enchant splices must survive untouched
assert body.count('G._enchArr.splice(') == 4
# and the three new decrements are present
assert body.count('G.numDice=Math.max(1,G.numDice-1);') == 3, \
    'expected 3 new decrements, got %d' % body.count('G.numDice=Math.max(1,G.numDice-1);')

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P504 applied: all four matchDice removals now shrink numDice')
