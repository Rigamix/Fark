# -*- coding: utf-8 -*-
"""P685: one lighting setting for every match - bosses get the candle, the
props, the prop shadows and the dice shadows.

Denis: "shadows should be on on boss matches? Same with the props? Use the
same setting for all matches for now."

WHAT THE GATE ACTUALLY DID, measured before this: _matchDress's
`if(isBoss){window._mLight={on:false};return;}` skipped the whole dressing
pass for bosses - no candle light, no props, no prop shadows - and set the
light off. But the OFF was a lie half the time: _mLightCalc runs on every
shadow tick from D3X and recomputes the light with NO boss check, flipping it
back ON whenever the table plate is visible. That is why Denis saw dice
shadows in one boss screenshot and none most other times - the gate and the
tick fought, and whichever ran last won. Removing the gate ends the fight in
the direction Denis chose: everything on, everywhere.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = u"  if(isBoss){window._mLight={on:false};return;}"
new = (u"  /* P685: bosses used to skip the whole dressing pass here (no candle, no\n"
       u"     props, no shadows) - and the off-flag it left was overwritten by\n"
       u"     _mLightCalc on every shadow tick anyway, so boss shadows flickered\n"
       u"     between sessions depending on which ran last. Denis: one setting for\n"
       u"     all matches. The gate goes; bosses dress like everyone else. */")
c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)' % c)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('  ok  P685 one lighting for all matches')
