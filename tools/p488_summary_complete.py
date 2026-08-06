# -*- coding: utf-8 -*-
u"""P488 - the summary line must be able to express the states that hid tonight.

"44 pass, 0 fail, 0 error" was TRUE and concealed a real problem: 46 probes ran,
two skipped, and the summary prints pass/fail/error only. `ind` is counted at
L121 and never printed at all - so an INDETERMINATE probe, the exact thing this
runner's own header calls "precisely the lying suite", cannot appear in its
headline.

The count was not wrong. It was INCOMPLETE, which is worse, because a number
that cannot show a problem reads as evidence there is none. Same shape as the
--keep message claiming a browser that was not there, and as
rivalSeatWorks:true proving "does not throw" rather than "uses the right bank".

So: always print skip and indet, and make the totals reconcile against the
number of probes that ran. If pass+fail+err+skip+ind does not equal the probe
count, say so loudly rather than let the difference sit invisible - that
mismatch is what would have surfaced this instantly.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_probes.js')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u"console.log('\\n' + pass + ' pass, ' + fail + ' fail, ' + err + ' error');"
assert s.count(OLD) == 1, 'summary line matched %d' % s.count(OLD)

s = s.replace(OLD, u"""/* EVERY state, not just the flattering three. "44 pass, 0 fail, 0 error" was
   true while two probes had silently skipped and overwritten real verdicts -
   a headline that cannot express a state is read as evidence that state did
   not happen. `ind` in particular was counted and never printed, and an
   indeterminate check reported as nothing is what this runner's header calls
   the lying suite. */
console.log('\\n' + pass + ' pass, ' + fail + ' fail, ' + err + ' error, ' +
            skip + ' skip, ' + ind + ' indet');
var _accounted = pass + fail + err + skip + ind;
if (_accounted !== probes.length) {
  console.log('!! ' + probes.length + ' probes ran but only ' + _accounted +
              ' are accounted for - ' + (probes.length - _accounted) + ' unreported');
}
if (skip) console.log('   a skip measured NOTHING - it is not a pass');""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
assert s.count("' skip, '") == 1
assert s.count("' indet'") == 1
assert s.count('_accounted') == 4
assert s.count('let pass = 0, fail = 0, err = 0, skip = 0, ind = 0;') == 1, 'the counters must still exist'
# the P486/P487 record fixes must survive untouched
assert s.count('Object.assign({}, _prev)') == 1
assert s.count('nowIsNothing') == 2
assert s.count('fs.writeFileSync(BASELINE') == 1
assert s.count('{') == s.count('}'), 'brace mismatch %d vs %d' % (s.count('{'), s.count('}'))

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P488 applied: the summary can now show skip and indet')
