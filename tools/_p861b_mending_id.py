# -*- coding: utf-8 -*-
u"""P861b: the new rule's id becomes `mending`, not `the_mending`.

CAUGHT BY AN EXISTING PROBE, not by reading it back. tools/apv_tell_remap.js
carries `everyBadgeIdMatchesItsRule`, which asserts

    r.tell.id === r.tell.name.toLowerCase().replace(/^the /,'').replace(/\\s+/g,'_')

i.e. the file's convention is that a badge named "THE X" has the id `x` -
Ambrose's is `reckoning` against the name "THE RECKONING". P861 shipped
`the_mending` against "THE MENDING" and that verdict went false. The name is
the brief's and stays; only the id moves.

Worth recording WHICH check found it: this is not the patch's own probe
agreeing with the patch. It is a probe written for the P428 rename - a
different change, months earlier, guarding the class rather than the instance -
firing on a rule that did not exist when it was written. That is the check
doing exactly the job it was built for.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

n_before = s.count('the_mending')
if n_before == 0:
    sys.exit('the_mending not present - P861 did not land (nothing written)')

# every occurrence is one P861 introduced; the token existed nowhere before.
# ONE token replace covers every form - quoted ids, the two CSS selectors
# (tell-the_mending) and the prose in P861's own headers. The token existed
# nowhere in this file before P861 introduced it, so a global swap cannot
# touch anything it did not write.
s = s.replace('the_mending', 'mending')

leftover = s.count('the_mending')
if leftover:
    ctx = [ln for ln in s.split('\n') if 'the_mending' in ln]
    sys.exit('THE_MENDING SURVIVES x%d (nothing written):\n  %s'
             % (leftover, '\n  '.join(x.strip()[:120] for x in ctx[:5])))

if s.count("'mending'") < 6:
    sys.exit("'mending' appears only %d times - expected rung, pool, applyTell, gate x2, "
             "badge x2, rival (nothing written)" % s.count("'mending'"))
for needed in ["id:'mending',name:'THE MENDING'", 'tell-mending', "_ruleActive('mending','o')",
               "_tellById('mending')"]:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: renamed %d occurrences the_mending -> mending' % n_before)
