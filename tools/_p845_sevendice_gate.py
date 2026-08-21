# -*- coding: utf-8 -*-
"""P845: seven_dice was unreachable in real play - the P834 redesign
(Denis: "Reroll one die free... activate during your turn") shipped
behind timing:'idle', and the pool is ALWAYS empty at idle (measured:
turn-2 idle pool 0, gate open, handler refusing NOTHING TO REROLL).
The P834 probe drove activateSevenDice() directly and never ran the
gate - the instrument didn't run the code (the gate) it vouched for.
Found by the P844 per-mutator sweep. The gate moves to 'choosing',
where the handler was proven to work.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = "{id:'seven_dice',name:'SEVEN DICE',icon:'\U0001F3B2',rarity:'gold',type:'active',maxUses:1,timing:'idle',"
new = "{id:'seven_dice',name:'SEVEN DICE',icon:'\U0001F3B2',rarity:'gold',type:'active',maxUses:1,timing:'choosing',/* P845: was 'idle', where the pool is always empty - unreachable */"
if s.count(old) != 1:
    sys.exit('ANCHOR x%d (nothing written)' % s.count(old))
s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: seven_dice gate -> choosing')
