# -*- coding: utf-8 -*-
u"""P899c: two OPEN.md entries are answered, so they are deleted rather than
marked - the file's own rule.

  "Which canvas does a beat's RIM belong on?" - answered as a principle, not a
  convention: a state is part of the table and is occluded by the dice; a beat
  is a notification about something that just happened and sits on top. Two
  rims wanting different canvases is not an exception to "the form decides"; it
  is that rule applying to states and a different one applying to beats.

  "Item 0 is my mistake" - the retraction stands in the brief and in P898's
  history; the design question it raised is now built, so it stops being open.

Nothing replaces them. The ladder stays the only thing waiting on a decision.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'docs', 'OPEN.md')
s = io.open(P, encoding='utf-8', newline='').read()
before = len(s)

for head in (u'## Item 0 is my mistake', u'## Which canvas does a beat'):
    i = s.find(head)
    if i < 0:
        sys.exit('could not find %r (nothing written)' % head)
    j = s.find(u'\n## ', i + 4)
    if j < 0:
        sys.exit('could not find the entry after %r (nothing written)' % head)
    s = s[:i] + s[j + 1:]

for gone in (u'Item 0 is my mistake', u'Which canvas does a beat'):
    if gone in s:
        sys.exit('%r survived the deletion (nothing written)' % gone)
# the one thing that must NOT have been swept up with them
if u'THE LADDER RE-RUN IS STILL UNMEASURED' not in s:
    sys.exit('the ladder entry went with them (nothing written)')
if len(s) >= before:
    sys.exit('the file did not shrink (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: two answered entries deleted, %d bytes' % (before - len(s)))
