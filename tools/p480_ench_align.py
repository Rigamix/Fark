# -*- coding: utf-8 -*-
u"""P480 - keep _enchArr aligned when a die is removed. Three sites.

RULED: fix now, before opponent enchants - a live indexing bug should not sit
under new work that would then get blamed for it.

THE BUG: `_enchArr` is indexed by LANE. Exactly one place in the file splices it
alongside G.matchDice - Break, L18782. Three others remove a die and leave it:

  royal_seizure (Whisper)        steal_die / take_best
  blessed_confiscation (Ambrose) steal_die / take_and_use
  Sacrifice                      obsidian shatter

After any of them every enchant above the removed lane applies to a DIFFERENT
DIE. Silent - no error, no message, the brand moves to a neighbour. Both
steal_die cards are pooled and live.

A SECOND CONSEQUENCE, found while reading the restore path: the resume guard
requires `_rdEnch.length === G.matchDice.length`. After an unspliced removal
those lengths differ, so resuming a match DISCARDS the whole _diceOut record and
the "dice out" seats vanish from the loadout. One missing splice, two symptoms,
neither of which announces itself.

WHY SPLICING IS SAFE - the thing the ruling asked to establish before touching
anything: _diceOut is a RECORD, not a restore. Its only consumers build the
"OUT" seat elements in the loadout and a resume snapshot; nothing re-inserts
into _enchArr from it. So removing the entry keeps the two arrays in step
without touching what _diceOut is for.

FOLLOWS BREAK EXACTLY, including its guard shape, so there is one pattern in the
file rather than a second one that merely looks similar.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

SPLICE = (u"\n        if(G._enchArr&&%s<G._enchArr.length)G._enchArr.splice(%s,1);"
          u"/* P480: the lane array must shrink with the dice */")

# ── steal_die: two splices, both at pBestIdx3. Anchored on the COMMENT above
# each, because `G.matchDice.splice(pBestIdx3,1);` is identical in both branches
# and an ambiguous anchor is how a patch lands in the wrong one.
TB = (u"/* Remove die — player plays with 5 */" + "\n"
      u"        G.matchDice.splice(pBestIdx3,1);")
assert s.count(TB) == 1, 'take_best matched %d' % s.count(TB)
s = s.replace(TB, TB + (SPLICE % ('pBestIdx3', 'pBestIdx3')))

TU = (u"/* Remove from player, add to NPC */" + "\n"
      u"        G.matchDice.splice(pBestIdx3,1);")
assert s.count(TU) == 1, 'take_and_use matched %d' % s.count(TU)
s = s.replace(TU, TU + (SPLICE % ('pBestIdx3', 'pBestIdx3')))

# ── Sacrifice: splices at the material's index ──
SAC = u"if(mi>=0)G.matchDice.splice(mi,1);}"
assert s.count(SAC) == 1, 'sacrifice matched %d' % s.count(SAC)
s = s.replace(SAC, u"if(mi>=0)G.matchDice.splice(mi,1);"
              u"if(mi>=0&&G._enchArr&&mi<G._enchArr.length)G._enchArr.splice(mi,1);}"
              u"/* P480: keep the lane array in step */")

assert s != orig
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
# four splices of matchDice, and now every one has an _enchArr splice near it
n_md = len(re.findall(r'G\.matchDice\.splice\(', body))
n_ea = len(re.findall(r'G\._enchArr\.splice\(', body))
assert n_md == 4, 'matchDice splices: %d' % n_md
assert n_ea == 4, '_enchArr splices: %d, expected one per removal' % n_ea
# and each matchDice splice has an _enchArr splice within a short window after it
for m in re.finditer(r'G\.matchDice\.splice\(', body):
    win = body[m.start():m.start() + 260]
    assert 'G._enchArr.splice(' in win, \
        'a matchDice splice at offset %d has no _enchArr splice after it' % m.start()
# the recording of ench into _diceOut is untouched - it is what shows the OUT seat
assert body.count('_diceOut=(G._diceOut||[]).concat') == 3
# nothing else moved
assert body.count('BANK_FX.') == 8 and body.count("famCommitBonus(_oSel,total,'o')") == 1

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P480 applied: every matchDice removal now splices _enchArr (4 of 4)')
