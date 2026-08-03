# -*- coding: utf-8 -*-
"""P439 - delete the two unreachable CFX handlers, and record why dice
availability is NOT the second shared query.

DELETE: tar_pit and _ward_retired. Neither is in FAM_LIVE, so neither can be
drafted or equipped, so famFire can never walk to them. Both were retired
BECAUSE something else does the job - Tar Pit in favour of Snuff ("two systems
for one effect"), Ward-the-card when the Ward enchant took bust mitigation - so
neither has a future to be parked for. An effect-system migration would
otherwise carry both forward as live content.

AND THE SECOND SHARED QUERY IS NOT SHARED. `!free.length` looked like one
condition across five handlers. Measured, the sets differ in ways that matter:

    encore / stargazer / steady_hand   !d.committed && !d._frozen
    sacrifice                          !d.committed && !d._shattered
    transmute                          !d.committed
    powder_keg                         G.pool.slice()   - everything, no filter

`_frozen` is a within-turn hold; `_shattered` is a die destroyed by Sacrifice or
an Obsidian break. A helper that folded these together would let a card touch a
die it must not - Powder Keg deliberately takes the WHOLE pool including kept
dice, which is its entire identity ("blow up your whole roll, kept ones
included"), and transmute deliberately ignores frozen state.

AND ONE ENTRY IN MY OWN PHASE 2 TABLE WAS WRONG. I listed `tamper` under
"!live.length" as a dice query. `live` there is `(G.oF||[]).filter(o=>!o.broken)`
- the OPPONENT'S UNBROKEN CARDS. Not dice at all. I grouped it by the variable
NAME rather than by what it holds, which is the same surface-resemblance mistake
this session keeps finding, committed inside the document that catalogues it.

So there is no lift here. Four predicates, four meanings, one deliberate
no-filter, and a fifth site that was never about dice.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

def cut_cfx(hay, cid):
    m = re.search(r'\nCFX\.' + cid + r'\s*=\s*\{', hay)
    assert m, 'CFX.%s not found' % cid
    i = m.end() - 1
    depth, j = 0, i
    while j < len(hay):
        if hay[j] == '{': depth += 1
        elif hay[j] == '}':
            depth -= 1
            if depth == 0: break
        j += 1
    end = j + 1
    while end < len(hay) and hay[end] in ';\n': end += 1
    return hay[:m.start() + 1] + hay[end:]

for cid in ('tar_pit', '_ward_retired'):
    before = s
    s = cut_cfx(s, cid)
    assert s != before, 'nothing removed for %s' % cid

# a note where the availability query would have gone, so the next reader does
# not re-derive the same non-answer
ANCHOR = u"function _fxMine(ev){return !!(ev&&ev.mine&&ev.owner==='p');}"
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, ANCHOR + u"""
/* THERE IS NO _fxFreeDice(), AND THAT IS THE FINDING, not an omission.
   `!free.length` reads like one shared condition across five handlers. The sets
   are four different things:
     encore / stargazer / steady_hand   !committed && !_frozen
     sacrifice                          !committed && !_shattered
     transmute                          !committed
     powder_keg                         the WHOLE pool, kept dice included -
                                        which is the card's entire identity
   _frozen is a within-turn hold; _shattered is a destroyed die. Folding these
   together would let a card touch a die it must not, and would quietly take
   Powder Keg's "blow up your whole roll, kept ones included" away from it.
   (tamper's `live` is not dice at all - it is the opponent's unbroken CARDS.) */""")

assert s != orig, 'nothing changed'
assert '\nCFX.tar_pit' not in s and '\nCFX._ward_retired' not in s
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P439 applied: 2 dead handlers removed, availability finding recorded in place')
