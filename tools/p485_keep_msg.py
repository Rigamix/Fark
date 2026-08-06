# -*- coding: utf-8 -*-
u"""P485 - stop --keep claiming something measurement says is false.

MEASURED, twice, once without the `timeout` wrapper in case my own instrument
was the cause:

  node tools/shoot.js --keep ...
    -> prints "browser left running on port 9465"
    -> owner pid DEAD, 0 msedge on that profile, port 9465 NOT listening

So the browser does NOT outlive the node process here - it is spawned as a
child without `detached`, and it goes when its parent goes. That is a
PRE-EXISTING bug in --keep, older than the cleanup work; it only became
visible because P482 started printing the profile path and I checked it.

NOT FIXING --keep's persistence. Making the browser genuinely detach is a
change to what the flag does, and it is not what the leak work was asked to
cover. Fixing the MESSAGE, because a confident false line is worse than no
line - it is the thing that would stop anyone checking.

Also drops "(swept after 30min)", which the ownership rule already made wrong:
a profile whose owner is gone is collected on the NEXT run, not on a timer.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shoot.js')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = (u"  else console.log('browser left running on port ' + PORT +\n"
       u"                   '\\n  profile kept at ' + PROFILE + ' (swept after 30min)');")
assert s.count(OLD) == 1, 'keep-log matched %d' % s.count(OLD)
s = s.replace(OLD, u"""  else console.log('browser asked to stay on port ' + PORT +
                   '\\n  profile at ' + PROFILE +
                   '\\n  NOTE: measured - the browser is spawned as a child of this' +
                   '\\n  process and does NOT reliably outlive it, so this port may' +
                   '\\n  already be dead. Pre-existing --keep behaviour, not the' +
                   '\\n  cleanup. If it did exit, the profile is collected on the' +
                   '\\n  next run (dead owner), not on a timer.');""")

assert s != orig, 'nothing changed'
assert 'swept after 30min' not in s, 'the false timer claim must be gone'
assert 'browser left running on port' not in s, 'the false persistence claim must be gone'
assert s.count(".shoot-owner") == 3
assert s.count("if (KEEP) {") == 1
assert s.count("fs.rmSync") == 2
assert s.count("'/T'") == 1
assert s.count('{') == s.count('}'), 'brace mismatch %d vs %d' % (s.count('{'), s.count('}'))

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P485 applied: --keep no longer claims a browser that is not there')
