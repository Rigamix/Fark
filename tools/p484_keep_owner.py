# -*- coding: utf-8 -*-
u"""P484 - under --keep, the profile must be owned by the BROWSER, not by node.

A bug P483 would have shipped, found while writing up why P483 works:

  --keep deliberately leaves the browser running for inspection. node then
  exits. But the marker written at launch holds NODE's pid, and node is now
  dead - so the next run's sweep reads "owner dead", calls the profile an
  orphan, and DELETES IT OUT FROM UNDER A BROWSER SOMEONE IS STILL USING.

The ownership rule was right; the recorded owner was wrong. Under --keep the
process still using the directory is the browser, so hand the claim over to it
before exiting. When that browser is finally closed its pid dies and the next
sweep collects the profile normally - which is the behaviour --keep wants:
kept for as long as it is genuinely in use, and no longer.

Same class as the seat bug in _legalKeeps: a value that is correct for the
path it was written on and wrong for the other one.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shoot.js')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u"""  /* --keep exists so a browser can be inspected after the run; killing it
     here would defeat the flag. Its profile is left deliberately and the
     startup sweep collects it later on age. */
  if (KEEP) return;"""
assert s.count(OLD) == 1, 'keep-guard matched %d' % s.count(OLD)
s = s.replace(OLD, u"""  /* --keep exists so a browser can be inspected after the run; killing it
     here would defeat the flag. */
  if (KEEP) {
    /* HAND THE CLAIM TO THE BROWSER. The marker currently names this node
       process, which is about to exit - so the next sweep would read "owner
       dead", call the profile an orphan and delete it while the kept browser
       is still using it. The browser is the process that still needs the
       directory, so it becomes the owner. When it is finally closed, its pid
       dies and the profile is collected normally. */
    try {
      if (proc && proc.pid) fs.writeFileSync(path.join(PROFILE, '.shoot-owner'), String(proc.pid));
    } catch (e) {}
    return;
  }""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
assert s.count(".shoot-owner") == 3, 'written at launch, handed over on keep, read by the sweep'
assert s.count("if (KEEP) {") == 1
assert s.count("String(proc.pid)") == 2, "the taskkill call already uses it; this adds the second"
assert s.count("String(process.pid)") == 1, 'the launch-time claim must still be node'
assert s.count("process.kill(owner, 0)") == 1
assert s.count("fs.rmSync") == 2
assert s.count("'/T'") == 1
assert s.count('{') == s.count('}'), 'brace mismatch %d vs %d' % (s.count('{'), s.count('}'))

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P484 applied: --keep hands profile ownership to the browser')
