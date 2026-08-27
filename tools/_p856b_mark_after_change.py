# -*- coding: utf-8 -*-
"""P856b: the pick-mark has to be applied AFTER the table change, not
before it.

Driven result from P856: arm marks nothing (correct), square outline
gone (correct), but the PICKED die ended with no mark. Cause, and it
is P855's own machinery working exactly as designed: the tap handler
added .cardmark, then called _setDieVal -> famTableChanged ->
_steadyDisarm, and P856's 5a edit had just taught _steadyDisarm to
strip .cardmark along with .break-target. The mark was erased
microseconds after being drawn.

So the two reroll arms mark AFTER their reroll lands. Transmute is
untouched here: its tap opens the face modal and changes no dice, so
its mark survives to the pick and is cleared by _transPick's own
_setDieVal - which is the right moment for that card.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


MARK = ("""        /* P856b: AFTER the reroll, not before - _setDieVal fires
           famTableChanged, whose _steadyDisarm strips this very class.
           Marking first drew the ring and erased it in the same tick. */
        try{if(d.el){d.el.classList.add('cardmark');
          setTimeout(function(){if(d.el)d.el.classList.remove('cardmark');},900);}}catch(e){}
""")

# steady_hand: drop the early add, mark after the value write
sub("""        G._steadyArmed=false;
        try{d.el.classList.add('cardmark');
          setTimeout(function(){if(d.el)d.el.classList.remove('cardmark');},900);}catch(e){}""",
    """        G._steadyArmed=false;""",
    'a steady early add removed')
sub("""        _setDieVal(d,_rollD(d));d.sel=false;
        if(d.el)d.el.classList.remove('selected');
        try{famLog('STEADY HAND \u2014 '+d.val);}catch(e){}""",
    """        _setDieVal(d,_rollD(d));d.sel=false;
        if(d.el)d.el.classList.remove('selected');
""" + MARK + """        try{famLog('STEADY HAND \u2014 '+d.val);}catch(e){}""",
    'b steady marks after')

# seven_dice: same shape
sub("""      G._sevenArmed=false;
      try{d.el.classList.add('cardmark');
        setTimeout(function(){if(d.el)d.el.classList.remove('cardmark');},900);}catch(e){}""",
    """      G._sevenArmed=false;""",
    'c seven early add removed')
sub("""      famLog('SEVEN DICE \u2014 '+d.val);""",
    MARK.replace('        ', '      ') + """      famLog('SEVEN DICE \u2014 '+d.val);""",
    'd seven marks after')

if s.count("classList.add('cardmark')") != 4:
    sys.exit("cardmark adds = %d, expected 4 (nothing written)" % s.count("classList.add('cardmark')"))
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
