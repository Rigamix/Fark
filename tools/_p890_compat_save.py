# -*- coding: utf-8 -*-
u"""P890: P888 inverted sim_verify's control, so the emulation of the thing
P888 deleted has to go with it.

FSIM's __shippedCompat existed to emulate TWO ways the game's in-file
_runBalanceSim differed from this harness: no hot-dice bonus, and one free
bust-save a turn for owning a silver die. sim_verify runs the same batch twice
and uses "compat lands on the shipped number" as proof that the gap between the
two harnesses is the shipped sim's staleness rather than a bug in FSIM.

P888 deleted the free save from the shipped sim, because Silver's save was
retired and its own definition says so. The emulation did not know that, so the
control is now backwards: the compat arm grants a save the thing it emulates no
longer has, and would report a spurious gap - in FSIM's favour, which is the
worst direction for a check whose job is to catch FSIM being wrong.

So the save half of the emulation is deleted and the flag keeps its other half.
The hot-dice difference is untouched and still real: FSIM adds a 250 turn-bonus
pot that the shipped sim has no notion of, and compat still suppresses it.

_compatSaveLeft had exactly two readers and one writer, all here, and the
'compatsave' state string had one consumer - so the whole emulation comes out
cleanly rather than being left switched off.

This is a tools-only change. It is written down rather than done quietly
because a verification harness that silently stops verifying is worse than one
that is obviously broken, and the next person to run sim_verify would have had
a mysterious gap to chase.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def patch(rel, pairs):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding='utf-8', newline='').read()
    for old, new, label in pairs:
        pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
        ms = list(re.finditer(pat, s))
        if len(ms) != 1:
            sys.exit('ANCHOR x%d for %s in %s (nothing written)'
                     % (len(ms), label, rel))
        m = ms[0]
        rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
        s = s[:m.start()] + rep + s[m.end():]
        edits.append(rel + ': ' + label)
    return p, s


# ── sim_harness.js: the save emulation comes out ────────────────────
hp, hs = patch('tools/sim_harness.js', [
    (u"""    /* SHIPPED-COMPAT: not a rule, an emulation of a KNOWN STALE assumption in
       the game's own in-file _runBalanceSim (it grants one free bust-save a
       turn for owning a silver die \u2014 Silver's deleted identity). Off by
       default; used once, by sim_verify, to prove the gap between the two
       harnesses is that stale assumption and not a bug in this one. */
    if(F.__shippedCompat&&_compatSaveLeft>0){_compatSaveLeft--;return 'compatsave';}
""",
     u"""    /* P890: THE COMPAT BUST-SAVE IS DELETED, because the assumption it
       emulated is gone. The shipped _runBalanceSim used to grant one free
       bust-save a turn for owning a silver die - Silver's retired identity -
       and this emulated it so sim_verify could show the gap between the two
       harnesses was that staleness rather than a bug here. P888 removed the
       save from the shipped sim. Keeping the emulation would have inverted
       the control: the compat arm would grant a save the shipped sim no
       longer has, reporting a gap in FSIM's favour, which is the worst
       direction for a check whose job is to catch FSIM being wrong. */
""",
     '1 the save emulation deleted'),
    (u"""var _compatSaveLeft=0;
F.__shippedCompat=false;""",
     u"""/* P890: __shippedCompat now emulates ONE difference, not two - the missing
   hot-dice bonus. Its bust-save half went with the shipped sim's own. */
F.__shippedCompat=false;""",
     '2 the counter deleted'),
    (u"""  _compatSaveLeft=F.__shippedCompat?1:0;
""", u"""""", '3 the per-match grant deleted'),
    (u"""    if(st==='compatsave'){try{handleBank();}catch(e){}break;}
""", u"""""", '4 the state consumer deleted'),
])

# ── sim_verify.js: the header no longer promises two ────────────────
vp, vs = patch('tools/sim_verify.js', [
    (u""" *     once with __shippedCompat on (which emulates the two things that sim
 *     does differently \u2014 no hot-dice bonus, one free bust-save a turn from
 *     Silver's DELETED identity). If compat lands on the shipped number, the
 *     gap is that sim's staleness and not a bug here.""",
     u""" *     once with __shippedCompat on. P890: that flag now emulates ONE
 *     difference, the missing hot-dice bonus. Its other half - one free
 *     bust-save a turn from Silver's retired identity - emulated a stale
 *     assumption the shipped sim really had, and P888 deleted it there, so
 *     keeping it here would have made the compat arm MORE generous than the
 *     thing it models. If compat lands on the shipped number, the gap is that
 *     sim's staleness and not a bug here.""",
     '5 the header'),
])

# ── post-asserts, against code with comments stripped ───────────────
for p, s, rel in ((hp, hs, 'sim_harness.js'), (vp, vs, 'sim_verify.js')):
    code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    if '_compatSaveLeft' in code:
        sys.exit('_compatSaveLeft survives in %s (nothing written)' % rel)
    if 'compatsave' in code:
        sys.exit("the 'compatsave' state survives in %s (nothing written)" % rel)

# the flag itself must SURVIVE - its hot-dice half is still real
hcode = re.sub(r'/\*.*?\*/', '', hs, flags=re.S)
if hcode.count('__shippedCompat') < 2:
    sys.exit('the compat flag lost its remaining use (nothing written)')
if 'if(!F.__shippedCompat)G._turnBonusPot' not in hcode:
    sys.exit('the hot-dice half of compat is gone too (nothing written)')

io.open(hp, 'w', encoding='utf-8', newline='').write(hs)
io.open(vp, 'w', encoding='utf-8', newline='').write(vs)
print('done: %d edits\n  %s' % (len(edits), '\n  '.join(edits)))
