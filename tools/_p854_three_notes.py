# -*- coding: utf-8 -*-
"""P854: Denis's three play notes.

1. SHORT FUSE HAS NO DESCRIPTION. Its FAM_CARDS text array is
   ['<tier I text>','',''] - tiers II and III are EMPTY STRINGS, so an
   upgraded Short Fuse showed a blank card. Filled.
   THE REAL FINDING, reported not papered over: CFX.short_fuse reads no
   tier anywhere - the gate is rc<3, the multiplier is a flat ev.mul(2)
   and the burn is the full lost total at every tier. The card has NO
   tier progression, so upgrading it does nothing but spend the offer.
   The text now says what is true at all three tiers; whether II/III
   SHOULD do more (fire from roll 2? x2.5?) is a design question in
   OPEN.md, not something to invent here.

2. FINNICK PICKPOCKETS HALF AS OFTEN. chance .30 -> .15 on his tell
   row, per Denis. The desc says "30%" in words, so it moves with the
   number - a tell whose text and behaviour disagree is the exact
   class of bug the P776 card-text audit existed to kill.

3. SACRIFICE CANNOT LAND THE WINNING BLOW. Denis: "shouldn't be able
   to be used to win... otherwise it's too easy and you just keep it
   until the end anyway."
   _turnBonusPot is SHARED (Stakes Rising, hot dice, Iron Crown), so
   excluding the whole pot would nerf three innocent mechanics. A
   sacrifice-only tally rides alongside it (G._sacPot), and the bank's
   win check subtracts it: the points still BANK, the match just does
   not END on them. So hoarding it for the last turn buys nothing -
   you must survive another turn to win - while every non-winning
   sacrifice is untouched. The tally is cleared everywhere the pot is
   (bank credit + every bust path clears the pot; _sacPot follows it
   at the two turn-boundary sites that own the lifecycle).
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


# ── 1. Short Fuse's missing description ──────────────────────────────
sub(""" {id:'short_fuse',fam:'obsidian',kind:'passive',name:'Short Fuse',
  text:['From your third roll each turn, everything scores double. But bust after that and the fire spreads to your banked points.','','']},""",
    """ /* P854: tiers II and III were EMPTY STRINGS - an upgraded Short Fuse
    showed a blank card (Denis: "Short Fuse doesn't have a description").
    They read the same because the CARD behaves the same: CFX.short_fuse
    reads no tier at all - rc<3 gate, flat ev.mul(2), full-loss burn -
    so it is the one family card an upgrade does not change. Whether
    II/III should scale is a design question in OPEN.md; the text is not
    the place to promise something the code does not do. */
 {id:'short_fuse',fam:'obsidian',kind:'passive',name:'Short Fuse',
  text:['From your third roll each turn, everything scores double. But bust after that and the fire spreads to your banked points.',
        'From your third roll each turn, everything scores double. But bust after that and the fire spreads to your banked points.',
        'From your third roll each turn, everything scores double. But bust after that and the fire spreads to your banked points.']},""",
    '1 short_fuse text')

# ── 2. Finnick's pickpocket, halved ──────────────────────────────────
sub("""    tell:{id:'pickpocket',name:'PICKPOCKET',desc:"\u201cEvery roll, a 30% chance I palm one of your dice.\u201d",icon:'\u270B',chance:.30}},""",
    """    /* P854: halved on Denis's note (.30 -> .15). The desc carries the
       number in words, so it moves with it - a tell whose text and
       behaviour disagree is exactly what the P776 audit existed to kill. */
    tell:{id:'pickpocket',name:'PICKPOCKET',desc:"\u201cEvery roll, a 15% chance I palm one of your dice.\u201d",icon:'\u270B',chance:.15}},""",
    '2 pickpocket .30->.15')

# 2b) THE FALLBACK MOVES WITH THE RECORD. The site's own P563 comment
# predicted this exact edit: "retune the record and the two paths
# diverge in silence." Paired operation, not a spot-fix.
sub("""     They agree today (the RUNGS record carries chance:.30 against a 0.3
     fallback) - which is precisely D22's point: retune the record and the two
     paths diverge in silence. */
  var _ppDef=(G._tell&&G._tell.id===_ppId)?G._tell:(_tellById(_ppId)||{});
  if(Math.random()>(_ppDef.chance||0.3))return;""",
    """     They agree today (the RUNGS record carries chance:.15 against a 0.15
     fallback) - which is precisely D22's point: retune the record and the two
     paths diverge in silence. P854 retuned it (.30 -> .15 on Denis's note)
     and moved BOTH, because this comment said what would happen otherwise. */
  var _ppDef=(G._tell&&G._tell.id===_ppId)?G._tell:(_tellById(_ppId)||{});
  if(Math.random()>(_ppDef.chance||0.15))return;""",
    '2b pickpocket fallback')

# ── 3. Sacrifice cannot land the winning blow ────────────────────────
sub("""    G._turnBonusPot=(G._turnBonusPot||0)+P;
    famLog('SACRIFICE \u2014 THE DIE SHATTERS FOR '+P+' ON THE TURN');_famPop('+'+P);""",
    """    G._turnBonusPot=(G._turnBonusPot||0)+P;
    /* P854 (Denis): SACRIFICE CANNOT LAND THE WINNING BLOW - "you just
       keep it until the end anyway". _turnBonusPot is shared with
       Stakes Rising, hot dice and Iron Crown, so the win check cannot
       simply ignore the pot; this tally is the sacrifice-only slice of
       it, subtracted at the win check in handleBank. The points still
       BANK - the match just does not END on them. */
    G._sacPot=(G._sacPot||0)+P;
    famLog('SACRIFICE \u2014 THE DIE SHATTERS FOR '+P+' ON THE TURN');_famPop('+'+P);""",
    '3a sacPot tally')

sub("""  if(G.pPts>=G.target){
    /* P719/P728 (P819 restore): the WINNING press must hold BANK TO WIN""",
    """  /* P854 (Denis): the sacrifice slice of this turn's pot cannot be the
     points that end the match. Banked, credited, shown - but a win has
     to stand up without them, so hoarding the card for the last turn
     buys nothing. Any OTHER turn's sacrifice is untouched, and the
     match still ends the moment a clean total crosses. */
  var _sacHeld=(G._sacPot||0);
  if(_sacHeld>0&&G.pPts>=G.target&&(G.pPts-_sacHeld)<G.target){
    try{famLog('THE SHATTERED DIE WILL NOT WIN IT \u2014 BANKED, BUT NOT THE BLOW');}catch(e){}
    try{setStatusMsg('SACRIFICE CANNOT WIN THE MATCH','red');}catch(e){}
    G._sacPot=0;
    showYieldButton();return;
  }
  G._sacPot=0;
  if(G.pPts>=G.target){
    /* P719/P728 (P819 restore): the WINNING press must hold BANK TO WIN""",
    '3b win-check exclusion')

# the tally dies with the pot on every bust path that clears it
sub("""    _turnScoreClear();G._turnBonusPot=0;""",
    """    _turnScoreClear();G._turnBonusPot=0;G._sacPot=0;/* P854 */""",
    '3c ward-path clear')
sub("""  /* Stakes Rising bonus is also lost on bust (it was "on the table" turn pts) */
  G._turnBonusPot=0;""",
    """  /* Stakes Rising bonus is also lost on bust (it was "on the table" turn pts) */
  G._turnBonusPot=0;G._sacPot=0;/* P854: the tally dies with the pot */""",
    '3d bust clear')

# post-asserts
for needed in ['G._sacPot=(G._sacPot||0)+P;', '_sacHeld', 'chance:.15']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
if "text:['From your third roll each turn, everything scores double. But bust after that and the fire spreads to your banked points.','','']" in s:
    sys.exit('SHORT FUSE BLANKS SURVIVED (nothing written)')
# assert against CODE, not prose - an earlier draft of this check matched
# the string inside the P563 comment and refused a correct patch
if "icon:'✋',chance:.30" in s:
    sys.exit('OLD PICKPOCKET CHANCE SURVIVED (nothing written)')
if "(_ppDef.chance||0.3)" in s:
    sys.exit('PICKPOCKET FALLBACK NOT MOVED (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
