# -*- coding: utf-8 -*-
"""P628 (Part 7): the NPC hesitates, but only when the decision is genuinely close.

THE BRIEF ASKED FOR A THRESHOLD AND THERE ISN'T ONE TO PICK. oppShouldBank is a
cascade of early returns - hard rules first (oppBank>=3000 banks, sub-minBank at
3+ dice pushes), then context branches - with exactly TWO probabilistic exits at
the end, `Math.random()>agg && oppBank>bankFloor` and the agg<0.6 conservative
bank. There is no margin to sit near.

WHAT CLOSENESS ACTUALLY IS HERE: `agg`. Every branch above converges on it - the
rung's base, a pair seen, sudden death, rising stakes, the adaptive gap,
desperation, the loss-streak softener - and then the call is literally
`Math.random() > agg`. So the same board goes either way when agg is near 0.5,
and is a foregone conclusion at 0.15 or 0.9. The band 0.40-0.65 is taken from the
two exits that actually gate on it, not chosen for feel.

THREE BOUNDARIES KEPT, all from what the code already is:
 - oppShouldBank STAYS PURE. It returns a boolean and knows nothing about
   presentation; the dialogue fires at the CALL SITE. agg is stashed on G at the
   point it is finalised, the same way G._lastBankAmount already exposes a value
   computed mid-decision - the smaller change than restructuring the return.
 - THE TWO MOMENTS FALL OUT OF THE RETURN VALUE. bank===false in band is
   hesitating-before-a-push; bank===true in band is hesitating-before-banking.
   No new state.
 - IT REUSES _dlgEvent, so it inherits the per-patron-override-beats-trait
   precedence the brief asks for, for free.

KEYED TO `strong`, NOT `bullish`. The build's six traits are cunning, greedy,
orderly, reckless, steady, strong. PERSONAS (ones/triples/straights/aggro/hoard/
combo) is a DIFFERENT six-way split for loadouts - close enough in shape that
writing to the wrong one would have shipped 36 lines that never fire.

AND THE SIMULATOR STAYS SILENT: oppShouldBank has a second caller inside FSIM
(fark_proto.html:40145). The hook is on the in-match call only, so a 12,000-turn
sim does not spend its time picking dialogue.
"""
import io, os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:110]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── 1. expose agg where it is finalised ──────────────────────────────────
sub(u"  var pProg=playerTotal/target,oProg=oppTotal/target;\n"
    u"  if(pProg>0.70&&(pProg-oProg)>0.30)agg=Math.max(agg,0.85);\n"
    u"  else if(pProg>0.50&&(pProg-oProg)>0.20)agg=Math.max(agg,0.78);",
    u"  var pProg=playerTotal/target,oProg=oppTotal/target;\n"
    u"  if(pProg>0.70&&(pProg-oProg)>0.30)agg=Math.max(agg,0.85);\n"
    u"  else if(pProg>0.50&&(pProg-oProg)>0.20)agg=Math.max(agg,0.78);\n"
    u"  /* P628: agg is FINAL here - nothing below mutates it, the branches only\n"
    u"     read it. Stashed so the call site can tell a coin-flip from a foregone\n"
    u"     conclusion without this function knowing anything about dialogue. Same\n"
    u"     pattern as G._lastBankAmount: expose a value computed mid-decision\n"
    u"     rather than reshape the return. */\n"
    u"  try{if(typeof G!=='undefined'&&G)G._oppAgg=agg;}catch(e){}",
    'P628 stash agg')

# ── 2. the helper ────────────────────────────────────────────────────────
sub(u"/* the four DLG events these answer, and which side each belongs to */",
    u"/* P628: DOES THIS DECISION DESERVE A PAUSE?\n"
    u"   Only when it was genuinely close. `agg` is what oppShouldBank converges on\n"
    u"   and its last word is `Math.random() > agg`, so near 0.5 the same board goes\n"
    u"   either way and at 0.15 or 0.9 it does not. The band is taken from the two\n"
    u"   exits that gate on agg, not chosen for feel.\n"
    u"   Returns null for a blowout, and null is the caller's cue to say nothing -\n"
    u"   a hesitation on an obvious decision reads as noise, not character. */\n"
    u"var _HESITATE_LO=0.40,_HESITATE_HI=0.65;\n"
    u"function _dlgHesitate(willBank){\n"
    u"  try{\n"
    u"    var a=(typeof G!=='undefined'&&G)?G._oppAgg:undefined;\n"
    u"    if(typeof a!=='number')return null;\n"
    u"    if(a<_HESITATE_LO||a>_HESITATE_HI)return null;\n"
    u"    /* the two moments fall straight out of the decision itself */\n"
    u"    return _dlgEvent(willBank?'banksafe':'push');\n"
    u"  }catch(e){return null;}\n"
    u"}\n"
    u"/* the four DLG events these answer, and which side each belongs to */",
    'P628 _dlgHesitate')

# ── 3. the hook, in the pause that already exists ────────────────────────
sub(u"      const bank=oppShouldBank(G.rung,oppBank,left,G.oPts,G.pPts,G.target);\n"
    u"      setTimeout(()=>{if(bank)finOpp(oppBank);else step();},_oppDelay(1900));",
    u"      const bank=oppShouldBank(G.rung,oppBank,left,G.oPts,G.pPts,G.target);\n"
    u"      /* P628: the hesitation beat goes in the pause that was ALREADY here.\n"
    u"         _oppDelay(1900) exists so the rival's decision does not land\n"
    u"         instantly; on a close call it now has something in it. No new timing,\n"
    u"         and the delay is unchanged whether or not a line comes back.\n"
    u"         Here and not inside oppShouldBank, which stays pure - and this is the\n"
    u"         in-match call, so FSIM's own caller never speaks. */\n"
    u"      try{var _hes=_dlgHesitate(bank);if(_hes)setStatusMsg(_hes,'');}catch(e){}\n"
    u"      setTimeout(()=>{if(bank)finOpp(oppBank);else step();},_oppDelay(1900));",
    'P628 hook at the call site')

# ── 4. the lines ─────────────────────────────────────────────────────────
H = {
 ('steady','push'):["Hm. One more, or is that greedy...","Let me think on this one a moment.","Careful, now. Careful."],
 ('steady','banksafe'):["Might be more here. Might not be worth the risk, though.","Small bank's still a bank. Let me weigh it.","Tempting to push. Tempting isn't the same as wise."],
 ('strong','push'):["...No, go again. Probably.","One more. Just one more, I mean it this time.","Fine, FINE, let me actually think for a second."],
 ('strong','banksafe'):["Feels small. Feels too small to stop at.","Banking already? Let me just... no. Fine. Maybe.","Ugh. Banking's boring. But smart, probably."],
 ('orderly','push'):["Recalculating the odds here. Give me a moment.","The numbers aren't clear yet. Let me work it through.","One more roll changes the math considerably. Thinking."],
 ('orderly','banksafe'):["Is this the optimal point? Checking.","The expected value here is close. Very close.","Worth a moment's calculation before I commit."],
 ('reckless','push'):["...actually thinking about this one. Weird feeling.","Even I pause sometimes. Rare, but it happens.","Hm. That's a lot on the table. Even for me."],
 ('reckless','banksafe'):["Banking feels wrong. But maybe, this once.","Every instinct says push. Every instinct's usually right, too.","Fighting myself on this one, honestly."],
 ('greedy','push'):["That's real coin sitting there. Real coin.","One more roll could double it. Could also lose it.","Counting what's already banked versus what's still possible."],
 ('greedy','banksafe'):["Feels small to walk away with. Feels safe, too.","Bird in hand, and all that. Still tempting, though.","Weighing the sure thing against the maybe-more."],
 ('cunning','push'):["Calculating something. Won't say what.","There's a read here worth taking a moment for.","Patience now pays later. Usually."],
 ('cunning','banksafe'):["Might know something you don't. Thinking it through.","The safe play isn't always the smart one. Weighing it.","A pause here is worth more than it looks."],
}
rows = []
for (trait, moment) in sorted(H):
    for t in H[(trait, moment)]:
        rows.append("  {p:'trait:%s:%s',s:0,g:'hesitate-%s',t:%s}," % (trait, moment, moment, json.dumps(t)))

end = s.index('\n];', s.index('var PATRON_LINES=['))
block = (u",\n  /* \u2500\u2500 P628 (Part 7): HESITATION BEFORE A CLOSE DECISION \u2500\u2500\n"
         u"     Trait-keyed, not per-patron - the brief's reasoning, and it also means\n"
         u"     these apply in EVERY match rather than only named-patron ones.\n"
         u"     `strong` is this build's name for the brief's BULLISH; PERSONAS is a\n"
         u"     different six-way split and writing to it would have shipped 36 lines\n"
         u"     that never fire. Reached through _dlgEvent, so a per-patron override\n"
         u"     would beat these for free if one is ever written. \u2500\u2500 */\n"
         + u"\n".join(rows).rstrip(',') + u"\n")
s = s[:end] + block + s[end:]

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits + %d hesitation lines' % (n, len(rows)))
