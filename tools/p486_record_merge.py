# -*- coding: utf-8 -*-
u"""P486 - --record must not let a skip erase a real verdict.

FOUND BY DOING IT. The --record run just now was 44 pass / 0 fail / 0 error
across 46 probes. The two unaccounted for were SKIPS:

    apv_amber_oneshot.js      'precondition never arrived'
    apv_break_doublepush.js   'precondition never arrived'

Both had REAL PASSING VERDICTS in the previous baseline - amber_oneshot with
four checks, break_doublepush with one. They are setup-dependent (the run has
to actually produce an amber one-shot / a Break double-push), so they fire on
some runs and not others.

`if (RECORD) fs.writeFileSync(BASELINE, JSON.stringify(results))` is a wholesale
overwrite, so recording on a run where they skipped replaced four known-good
assertions with {skipped:true}. After that the baseline diff treats "skipped" as
the expected state, and if those checks later BREAK, there is nothing to notice
it against. Every --record on an unlucky run erodes the file a little more.

A skip is the probe saying "I could not measure this". That is not evidence, and
it must not overwrite evidence. So: merge. A probe that skipped or errored this
run keeps whatever real verdict the baseline already held; everything else is
taken from the current run as before.

Deliberately NOT the reverse: a real verdict this run always wins over an old
one, including a failing one. The baseline should track the latest actual
measurement - it is only the ABSENCE of a measurement that must not overwrite.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_probes.js')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u"""if (RECORD) {
  fs.writeFileSync(BASELINE, JSON.stringify(results, null, 1));
  console.log('\\nbaseline recorded — ' + Object.keys(results).length + ' probes');"""
assert s.count(OLD) == 1, 'record block matched %d' % s.count(OLD)

s = s.replace(OLD, u"""if (RECORD) {
  /* A SKIP IS NOT A MEASUREMENT, SO IT MUST NOT OVERWRITE ONE.
     Recording used to be a wholesale overwrite. A setup-dependent probe that
     happened to skip on the recording run therefore replaced its real verdict
     with {skipped:true} - measured: apv_amber_oneshot (4 checks) and
     apv_break_doublepush (1) were erased exactly that way. After that the diff
     expects "skipped", and a genuine later break has nothing to register
     against. Every unlucky --record eroded the file a little further.

     A real verdict from this run always wins, including a FAILING one - the
     baseline should track the latest actual measurement. It is only the
     absence of one that is not allowed to overwrite. */
  var _rec = results, _kept = [];
  if (fs.existsSync(BASELINE)) {
    try {
      var _prev = JSON.parse(fs.readFileSync(BASELINE, 'utf8'));
      _rec = {};
      Object.keys(results).forEach(function (k) {
        var now = results[k], was = _prev[k];
        var nowIsNothing = !now || now.skipped || now.error;
        var wasReal = was && !was.skipped && !was.error;
        if (nowIsNothing && wasReal) { _rec[k] = was; _kept.push(k); }
        else _rec[k] = now;
      });
    } catch (e) { _rec = results; }
  }
  fs.writeFileSync(BASELINE, JSON.stringify(_rec, null, 1));
  if (_kept.length) console.log('\\nkept prior verdicts for ' + _kept.length +
    ' probe(s) that did not measure this run:\\n  ' + _kept.join('\\n  '));
  console.log('\\nbaseline recorded — ' + Object.keys(_rec).length + ' probes');""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
assert s.count('nowIsNothing') == 2
assert s.count('wasReal') == 2
assert s.count('fs.writeFileSync(BASELINE') == 1, 'exactly one baseline write'
assert 'JSON.stringify(_rec, null, 1)' in s
assert 'JSON.stringify(results, null, 1)' not in s, 'the raw overwrite must be gone'
assert s.count('const RECORD') == 1
assert s.count('{') == s.count('}'), 'brace mismatch %d vs %d' % (s.count('{'), s.count('}'))

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P486 applied: a skip no longer erases a recorded verdict')
