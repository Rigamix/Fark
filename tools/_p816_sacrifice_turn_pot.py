# -*- coding: utf-8 -*-
"""P816: sacrifice pays the TURN, not the bank - Denis's ruling.

Audit finding (OBSIDIAN): the +800 landed in G.pPts the instant the
die shattered - bust-proof - while the spec says "adds immediately to
the current TURN total". Denis: "move it to the turn total. A
bust-proof payout on a card called Sacrifice, in the family whose
whole identity is 'burn it all', undersells the entire point."

The vehicle is G._turnBonusPot - the shared "turn bonus that banks and
is lost": handleBank adds it (33533), every bust path zeroes it, ward
halves over it, and the bank button counts it as bankable (32556).
refreshSelUI owns the turnPts recompute, so the fire only writes the
pot and calls the refreshers.

P817 rides along: double_or_nothing keeps its pre-bank arm (Denis:
"fix the card text, not the timing") - the texts now say the arm
comes first.
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
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# 1) the credit moves to the turn pot
sub("""    var P=famDef('sacrifice').p[inst.tier-1];
    G.pPts+=P;famLog('SACRIFICE — THE DIE SHATTERS FOR '+P);_famPop('+'+P);
    try{updHUD();refreshSelUI();}catch(e){}""",
    """    var P=famDef('sacrifice').p[inst.tier-1];
    /* P816: THE TURN, NOT THE BANK (Denis). This was G.pPts+=P -
       bust-proof - against the spec's "current turn total" and the
       family's whole identity. _turnBonusPot is the shared turn bonus
       that banks and is lost: handleBank adds it, every bust path
       zeroes it, ward halves over it. refreshSelUI owns the turnPts
       recompute. */
    G._turnBonusPot=(G._turnBonusPot||0)+P;
    famLog('SACRIFICE — THE DIE SHATTERS FOR '+P+' ON THE TURN');_famPop('+'+P);
    try{updHUD();refreshSelUI();refreshKeptTray();}catch(e){}""",
    'sacrifice pays the turn pot')

# 2) sacrifice card text carries the risk
sub("""  text:['Shatter one of your own dice, gone for the match, for +800 right now.',
        'Shatter one of your own dice, gone for the match, for +1200 right now.',
        'Shatter one of your own dice, gone for the match, for +2000 right now.']},""",
    """  text:['Shatter one of your own dice, gone for the match, for +800 on this turn. Bank it or lose it.',
        'Shatter one of your own dice, gone for the match, for +1200 on this turn. Bank it or lose it.',
        'Shatter one of your own dice, gone for the match, for +2000 on this turn. Bank it or lose it.']},""",
    'sacrifice text says the turn')

# 3) FAM_SHORT follows
sub("""  sacrifice:'Shatter one of your dice for +800 now.',""",
    """  sacrifice:'Shatter one of your dice: +800 on this turn. Bank it or lose it.',""",
    'sacrifice short text')

# 4) P817: double_or_nothing text says the arm comes BEFORE the bank
sub("""  text:['After banking, flip for it: double the bank or lose half.',
        'After banking, flip for it: double the bank or lose a third.',
        'After banking, flip for it: double the bank or lose a quarter.']},""",
    """  text:['Arm it, then bank: the flip doubles that bank or loses half.',
        'Arm it, then bank: the flip doubles that bank or loses a third.',
        'Arm it, then bank: the flip doubles that bank or loses a quarter.']},""",
    'double_or_nothing text: arm first')

# 5) FAM_SHORT follows
sub("""  double_or_nothing:['After banking, flip: double it or lose half.',
                     'After banking, flip: double it or lose a third.',
                     'After banking, flip: double it or lose a quarter.'],""",
    """  double_or_nothing:['Arm, then bank: the flip doubles it or loses half.',
                     'Arm, then bank: the flip doubles it or loses a third.',
                     'Arm, then bank: the flip doubles it or loses a quarter.'],""",
    'double_or_nothing short text')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
