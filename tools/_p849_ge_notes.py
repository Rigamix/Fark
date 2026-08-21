# -*- coding: utf-8 -*-
"""P849: Denis's two P848 verification notes, neither a bug.

1. Spur beating _geExclude in the deal ternary is the RIGHT priority
   (a real probability bias outranks a presentation rule) but nothing
   said so - and an unstated right decision is what a future reader
   "fixes". Stated at the site.

2. famTableChanged's gate did not include _geExclude - safe today only
   by the call graph (every reader of the buffer is a roll, every roll
   clears it), not by construction. The function whose job is "the
   table changed, drop the roll-scoped state" must drop ALL of it, or
   the next buffer added to _clearRollForces inherits a gate that can
   skip it. One character's work.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


sub("""    /* P848: a Gambler's Eye reroll must visibly differ from the face it
       replaces - the flag on the roll, not a second roll path. */
    const val=useSpur?rollFaceSpur(d.mat)""",
    """    /* P848: a Gambler's Eye reroll must visibly differ from the face it
       replaces - the flag on the roll, not a second roll path.
       P849: SPUR WINS THE TERNARY ON PURPOSE. Spur is a real
       probability bias (extra 1s and 5s in the pool); visibly-differs
       is a presentation rule. A spurred die under Gambler's Eye may
       legitimately repeat its face - do not "fix" this by reordering
       the ternary. */
    const val=useSpur?rollFaceSpur(d.mat)""",
    'Spur priority stated')

sub("""  if(_hadPromise||((window._pkGhosts||[]).length)||((window._htMarks||[]).length)||G._transArmed){
    _clearRollForces();""",
    """  if(_hadPromise||((window._pkGhosts||[]).length)||((window._htMarks||[]).length)||G._transArmed||G._geExclude){
    /* P849: every roll-scoped buffer _clearRollForces owns must be in
       this gate - the invariant holds by construction, not by the
       current call graph. Add the next buffer HERE too. */
    _clearRollForces();""",
    '_geExclude joins the gate')

for needed in ['SPUR WINS THE TERNARY', '||G._geExclude){']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
