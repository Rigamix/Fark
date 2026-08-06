# -*- coding: utf-8 -*-
u"""P487 - `--record --only X` must not delete the other 45 probes.

CAUGHT WHILE TRYING TO VERIFY P486 CHEAPLY. To test that a skip no longer
erases a verdict, the obvious move is to re-record just the two skipping
probes: `--record --only amber`. That would have written a baseline containing
TWO probes and silently dropped the other 44.

`results` only ever holds probes that actually ran, and the record step writes
exactly those keys - so a filtered record truncates the file to the filter.
Pre-existing, not introduced by P486; P486 inherited it by iterating
Object.keys(results) too.

FIX: start from the existing baseline and overlay this run's results, instead
of starting from the results. A probe that did not run in this invocation keeps
whatever the baseline already knew about it.

The trade is a stale entry for a probe that gets DELETED from the repo, which
lingers until someone records after the deletion. That is strictly better than
destroying 44 known-good verdicts, and it is visible - a probe in the baseline
with no file is easy to spot, a baseline that quietly lost 44 entries is not.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_probes.js')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u"""      var _prev = JSON.parse(fs.readFileSync(BASELINE, 'utf8'));
      _rec = {};
      Object.keys(results).forEach(function (k) {"""
assert s.count(OLD) == 1, 'merge head matched %d' % s.count(OLD)

s = s.replace(OLD, u"""      var _prev = JSON.parse(fs.readFileSync(BASELINE, 'utf8'));
      /* START FROM THE BASELINE, not from this run. `results` holds only the
         probes that actually RAN, so with --only a record used to truncate the
         file to the filter - `--record --only amber` would have written a
         two-probe baseline and dropped the other 44. A probe that did not run
         keeps what the baseline already knew. */
      _rec = Object.assign({}, _prev);
      Object.keys(results).forEach(function (k) {""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
assert s.count('Object.assign({}, _prev)') == 1
assert s.count('_rec = {};') == 0, 'the truncating initialiser must be gone'
assert s.count('fs.writeFileSync(BASELINE') == 1
assert s.count('nowIsNothing') == 2, 'P486 skip-guard must survive'
assert s.count('JSON.stringify(_rec, null, 1)') == 1
assert s.count('{') == s.count('}'), 'brace mismatch %d vs %d' % (s.count('{'), s.count('}'))

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P487 applied: a filtered record no longer truncates the baseline')
