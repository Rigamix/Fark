# -*- coding: utf-8 -*-
"""P455 - the two die materials a patron can hold that had no tint.

apv_table_totality has been the suite's one red all session. Nobody had looked
at what it was actually saying. It reports MATCOL missing four of DICE_TYPES'
ids: jade3, brass, crystal, ruby - each of which would render with D3X's
default colour instead of its own.

REACHABILITY SPLITS THEM, which is why this is a two-line fix and not a
four-line one:

  brass, crystal   REACHABLE. Both appear in patron dieBias tables -
                   `ones` biases toward iron/lead/brass/crystal, `hoard`
                   toward amber/crystal/lead - so _generatePatronInner can
                   deal them to an opponent and they reach the table untinted.
  jade3, ruby      defined in DICE_TYPES and referenced NOWHERE ELSE in the
                   file. No pool, no bias, no shop entry. Defined-but-dead.

So two entries are added and two are not, and the probe's domain is the reason
it could not tell them apart: it checks MATCOL against ALL of DICE_TYPES, which
is the right domain for "could this ever be asked for" and the wrong one for
"can a player see this". Both numbers are useful; conflating them is what made
the red look like four bugs.

THE COLOURS ARE THE MATERIALS' OWN, not invented. Brass is a warm yellow metal
and sits between iron's blue-grey and amber's orange; crystal is a pale near-
white with a blue cast, distinct from silver's brighter grey-white and from
bone's flat white. Checked against the existing entries so neither is a
near-duplicate of a neighbour - the mistake the relic tints already had to be
fixed for, where six of eight were byte-identical to their family colour.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u"    lucky:0xffd270,"
assert s.count(OLD) == 1, 'MATCOL lucky anchor matched %d' % s.count(OLD)
s = s.replace(OLD,
u"""    lucky:0xffd270,
    /* BRASS AND CRYSTAL, added 2026-08-03. Both were in DICE_TYPES and absent
       here, so D3X tinted them with its default - and both are REACHABLE:
       patron dieBias hands brass to the `ones` persona and crystal to `ones`
       and `hoard`, so an opponent can put either on the table.
       DICE_TYPES also holds jade3 and ruby with no MATCOL entry, and those are
       deliberately still absent: neither is referenced anywhere else in the
       file - no pool, no bias, no shop - so nothing can ask for their tint.
       Adding placeholder colours for dice a player cannot obtain would make
       the totality probe green by describing content that does not exist. */
    brass:0xc08a3e, crystal:0xd8e6f2,""")

assert s != orig, 'nothing changed'
assert s.count('brass:0xc08a3e') == 1
assert s.count('crystal:0xd8e6f2') == 1
# and the two dead ones stay out
for dead in ('jade3:', 'ruby:'):
    assert ('    ' + dead) not in s.split('MATCOL:{')[1][:1200], \
        '%s was added to MATCOL' % dead
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P455 applied: brass + crystal tinted; jade3 + ruby left out on purpose')
