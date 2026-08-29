# -*- coding: utf-8 -*-
u"""P861c: the tell-HUD refresh stops being gated on ONE rule's id.

FOUND BY DRIVING P861, not by reading it: The Mending's rule passed on both
seats and its badge counter sat at 0/2 for the whole match. The element was
built correctly and the update branch was correct; nothing ever called it.

THE BUG IS IN THE CALLER, AND IT IS THE SHAPE THIS PROJECT KEEPS HITTING.
_updateTellHUD() switches on the rule internally, early-returns without a
tell, and every branch inside is id-guarded. The comment sitting directly
above the call already says so in as many words:

    "Each surface ignores the call when it is not the one showing the rule."

And yet both roll-path callers were wrapped in _ruleActive('drill_order','p'),
so the wrapper was not protecting anything - it was deciding WHICH rules are
permitted to have a live counter. Drill Order was allowed one. Any rule added
afterwards silently was not. Fixing this inside the rule (adding
||_ruleActive('mending','p') at two sites) would have shipped the same trap
for the next rule, one site wider.

TWO SITES, COUNTED, NOT SPOT-FIXED: the identical line appears at turn-start
and after-roll, and the assert below fails if that count is ever not two.

famRenderRow() KEEPS its gate. It is a different and heavier surface, it is
not self-guarding the way _updateTellHUD is, and nothing here measured that it
is safe to run on every roll - so it is left exactly as it was. Ungating the
one call that was proven safe by its own comment is the change; ungating its
neighbour because it is adjacent is not.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

OLD = ("  if(_ruleActive('drill_order','p')){try{_updateTellHUD();}catch(e){}"
       "try{famRenderRow();}catch(e){}}")
NEW = ("""  /* P861c: THE HUD REFRESH IS UNGATED. _updateTellHUD early-returns without
     a tell and every branch inside it is id-guarded - the comment right above
     says exactly that - so this wrapper never protected the call. It decided
     which rules were ALLOWED a live counter, and the answer was "drill_order
     and nothing added later". The Mending's badge read 0/2 for a whole match
     on a rule that was otherwise working on both seats.
     famRenderRow keeps its gate: different surface, heavier, and not
     self-guarding - nothing here measured it safe to run every roll. */
  try{_updateTellHUD();}catch(e){}
  if(_ruleActive('drill_order','p')){try{famRenderRow();}catch(e){}}""")

n = s.count(OLD)
if n != 2:
    # \r?\n tolerance is irrelevant here - the anchor is a single line - so a
    # miscount is a real change in the file, not a line-ending artefact.
    sys.exit('EXPECTED 2 GATED CALL SITES, FOUND %d (nothing written). '
             'Both must move together or the two paths disagree.' % n)
s = s.replace(OLD, NEW)

if s.count("if(_ruleActive('drill_order','p')){try{_updateTellHUD();}") != 0:
    sys.exit('A GATED CALL SURVIVED (nothing written)')
if s.count('try{_updateTellHUD();}catch(e){}\n  if(_ruleActive(') != 2 and \
   s.count('try{_updateTellHUD();}catch(e){}\r\n  if(_ruleActive(') != 2:
    sys.exit('UNGATED CALLS NOT PAIRED WITH THEIR famRenderRow GATE (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: 2 call sites ungated')
