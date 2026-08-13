# -*- coding: utf-8 -*-
"""P690: the innkeep's book and the trophy shelf are removed, not restyled.

Denis: "we don't need the innkeeper book panel anymore you can remove. Are
there other screens with that treatment? They might not be needed anymore."

The census, before deleting anything:
  _gbBook   ZERO callers - it was already dead code wearing new paint.
  _gbShelf  ONE caller (the win screen's TO THE SHELF), and the master
            brief's own ruling - quoted in the old _gbBarred comment - says
            there IS no trophy shelf; the feats wall is the only meta
            surface. The overlay contradicted the design it survived.
  KEPT because they are functional, not decorative: the patron/boss peeks
  (SIT DOWN / CHALLENGE), the shop's die inspect and enchant picker, the
  confirm modals (new run, abandon, spoils, enchant), and _gbInspect (the
  tell-badge explainer).

A feature switched off is worse than one deleted - both bodies go, and the
win screen's button row loses the dead destination.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def cut_fn(name):
    global s, n
    i = s.index('function %s(){' % name)
    j = s.index('\n}\n', i) + 3
    body = s[i:j]
    s = s[:i] + ('/* P690: %s removed - see the patch header. */\n' % name) + s[j:]
    n += 1
    print('  ok  P690 %s removed (%d chars)' % (name, len(body)))


cut_fn('_gbBook')
cut_fn('_gbShelf')


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


sub(u"  if(won)h+='<div class=\"go-btn\" onclick=\"_gbShelf()\"><img class=\"plq\" src=\"Art/Assets/Buttons/optimized/Button_new_02_opt.webp\" alt=\"\"><span>TO THE SHELF</span></div>';\n",
    u"  /* P690: TO THE SHELF removed with the shelf - the brief rules the feats\n"
    u"     wall the only meta surface */\n",
    'P690 the button goes with it')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
