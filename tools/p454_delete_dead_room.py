# -*- coding: utf-8 -*-
"""P454 - delete _gbRenderRoom's 81 unreachable lines.

RULED: delete. Unreachable, confirmed by direct test rather than inference, and
authored-but-dead code sitting one edit away from someone patching the wrong
copy is worse than losing the lines.

HOW THE UNREACHABILITY WAS ESTABLISHED, because "I read it and it looks dead"
is not what this project accepts. `_gbRenderRoom`'s eighth line is:

    if(typeof _ptRoom==='function'){_ptRoom(host,tier,bossReady);return;}

`_ptRoom` is a top-level function declaration, so it is hoisted and always
defined - the gate can never fall through. That is the inference. THE TEST is
that P451 patched the chip row in BOTH copies and only `_ptRoom`'s rendered:
the hangover marker appeared from `_ptRoom` and never from here.

WHY THIS IS NOT STEEPED OR BOOKKEEPER'S PAINTING, both of which were parked
rather than deleted this same session: those have a named future use - P5's
design record, a possible future feat. Nothing points to this copy ever
mattering again. It is not parked for a reason; it had not been swept yet.

THE GUARD BECOMES UNCONDITIONAL. Keeping `if(typeof _ptRoom==='function')`
with nothing after it would mean that if _ptRoom ever went missing the Room
would silently render nothing, where today it renders the old layout. A throw
is better than silence, and the condition cannot be false anyway.

TESTED AROUND THE DELETION, not at it - the standing rule. The Room's rendered
output is captured before and after: innerHTML length, the chip row's text, the
seat count. Deleting code that never ran should change none of them.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

m = re.search(r'\nfunction _gbRenderRoom\(', s)
assert m, '_gbRenderRoom not found'
b = s.index('{', m.end())
d, j = 0, b
while j < len(s):
    if s[j] == '{': d += 1
    elif s[j] == '}':
        d -= 1
        if d == 0:
            break
    j += 1
body_end = j                      # index of the function's closing brace

GATE = u"  if(typeof _ptRoom==='function'){_ptRoom(host,tier,bossReady);return;}"
gi = s.find(GATE, b, body_end)
assert gi > 0, 'delegation gate not found inside _gbRenderRoom'

dead = s[gi + len(GATE):body_end]
dead_lines = dead.count('\n')
assert dead_lines > 60, 'expected ~81 dead lines, found %d' % dead_lines
assert dead.count('chips+=') == 5, \
    'expected 5 chip sites in the dead region, found %d' % dead.count('chips+=')

s = s[:gi] + (
u"""  /* THE PAINTED ROOM IS THE ROOM. This used to be a gate with 81 lines of
     fallback layout below it - the pre-P22 Room, kept after _ptRoom replaced
     it. _ptRoom is a top-level declaration so the gate could never fall
     through, and the copy below never ran: P451 patched the chip row in BOTH
     and only _ptRoom's rendered.
     Deleted 2026-08-03. Unconditional now on purpose - if _ptRoom ever goes
     missing this should throw rather than silently render an empty Room. */
  _ptRoom(host,tier,bossReady);""") + s[body_end:]

assert s != orig, 'nothing changed'
assert s.count(GATE) == 0, 'the old gate survives'
# the function must still be balanced and much shorter
m2 = re.search(r'\nfunction _gbRenderRoom\(', s)
b2 = s.index('{', m2.end())
d, j2 = 0, b2
while j2 < len(s):
    if s[j2] == '{': d += 1
    elif s[j2] == '}':
        d -= 1
        if d == 0:
            break
    j2 += 1
now = s[b2:j2].count('\n') + 1
assert now < 20, '_gbRenderRoom is still %d lines' % now
print('P454: removed %d dead lines; _gbRenderRoom is now %d lines'
      % (dead_lines, now))
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
