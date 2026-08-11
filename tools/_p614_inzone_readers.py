# -*- coding: utf-8 -*-
"""P614: the last two readers of `.in-zone` go, and triggerCard gets its animation back.

Nothing writes the class any more (P612), so both of these are branches that can
only take one path. Left alone they are not merely inert - triggerCard's is
actively WRONG now: `isInZone` suppressed the card-trigger flash and reparented
the floating effect label into #activateZone, and with the class never set the
suppression silently stops applying. That is the right outcome, but it should be
stated rather than arrived at by a condition that can no longer be true.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


sub(u"      /* Carry over greyed-state class so body-promoted tooltip stays desaturated for used/in-zone cards */\n"
    u"      if(mcardEl.classList.contains('in-zone')||mcardEl.classList.contains('used')"
    u"||mcardEl.classList.contains('draft-greyed')||mcardEl.classList.contains('draft-locked')){",
    u"      /* Carry over greyed-state so the body-promoted tooltip stays desaturated.\n"
    u"         P614: `.in-zone` dropped from the test - nothing sets it since the\n"
    u"         threshold replaced the zone, and `.used` was always the real signal\n"
    u"         for a spent card anyway. */\n"
    u"      if(mcardEl.classList.contains('used')"
    u"||mcardEl.classList.contains('draft-greyed')||mcardEl.classList.contains('draft-locked')){",
    'P614 tooltip grey test')

sub(u"  const zone=document.getElementById('activateZone');\n"
    u"  let mc=bar?bar.querySelector('.mcard[data-cid=\"'+cardId+'\"]'):null;\n"
    u"  const isInZone=mc&&mc.classList.contains('in-zone');\n"
    u"  SFX.cardTrigger();\n"
    u"  if(mc&&!isInZone){",
    u"  let mc=bar?bar.querySelector('.mcard[data-cid=\"'+cardId+'\"]'):null;\n"
    u"  /* P614: the `isInZone` suppression is gone with the zone. It existed to\n"
    u"     stop a card that had been PARKED from playing its trigger flash, and to\n"
    u"     reparent the floating effect label into #activateZone. Nothing is parked\n"
    u"     now - a spent card sits in its own slot - so every card that fires plays\n"
    u"     the flash in place, which is what the redesign wants. */\n"
    u"  SFX.cardTrigger();\n"
    u"  if(mc){",
    'P614 triggerCard flash')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n)
