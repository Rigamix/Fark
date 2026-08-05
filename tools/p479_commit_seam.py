# -*- coding: utf-8 -*-
u"""P479 - the opponent's `commit` seam. Eight of eight.

RULED: NPCs should make real selections and `commit` falls out of that. The
sizing found the rival ALREADY makes a real selection - it calls scoreRoll and
marks exactly the dice `used[]` names - so the payload exists today and the seam
was never blocked on the decision work.

REUSE, NOT REIMPLEMENT. famCommitBonus already derives every payload field from
a set of dice: isTriple from face counts, isStraight from the longest run, jade
by material, hitFirst/hitLast by position in the row. Writing that again for the
rival would be two derivations free to drift - the exact thing five of tonight's
findings were. So the function takes an `actor` and both seats call it.

THREE THINGS IT WAS BOUND TO THE PLAYER BY, all now seat-aware:

  G.pF     the family-card list it gates on          -> G.oF for the rival
  G.pool   the positional row (first/last, and the   -> G.oppDice for the rival
           Palm's adjacency test)
  G._featJadePend  a PLAYER feat flag                -> only ever set for 'p'

AND A CORRECTION TO MY OWN SIZING: I reported famCommitBonus as having zero UI
calls. It calls _famPop twice - my UI pattern did not list it. The function is
still safe to call from the rival's turn (a popup is harmless and the sim
silences it), but "pure" was wrong and the number came from a pattern that could
not see that name.

PLACED AFTER THE PLAYER-ARMED REROLL BLOCK, not straight after the keep step.
Crown Authority / Blessed Dice can un-keep the rival's dice and zero `total`
between the two, so raising earlier would commit a selection the player then
destroyed. Guarded on total>0 for the same reason.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. famCommitBonus becomes seat-aware ──
one = lambda old, new, label: None
def rep(old, new, label):
    global s
    assert s.count(old) == 1, '%s matched %d' % (label, s.count(old))
    s = s.replace(old, new)

rep(u"function famCommitBonus(selD,pts){\n  if(!G||!G.pF||!G.pF.length||pts<=0)return pts;",
    u"""function famCommitBonus(selD,pts,actor){
  /* P479 - SEAT-AWARE. Both sides derive the commit payload here rather than
     each writing its own copy; two derivations of "is this a straight" would be
     free to drift, which is what five of tonight's findings turned out to be. */
  var _cAct=(actor==='o')?'o':'p', _cIsO=(_cAct==='o');
  var _cFam=_cIsO?G.oF:G.pF;
  var _cRow=(_cIsO?G.oppDice:G.pool)||[];
  if(!G||!_cFam||!_cFam.length||pts<=0)return pts;""",
    'famCommitBonus header')

rep(u"  if(_isStraight&&_jadeDice.length)G._featJadePend=true;",
    u"  if(_isStraight&&_jadeDice.length&&!_cIsO)G._featJadePend=true;/* player feat only */",
    'jade feat flag')
rep(u"  var first=G.pool[0],last=G.pool[G.pool.length-1];",
    u"  var first=_cRow[0],last=_cRow[_cRow.length-1];",
    'positional row')
rep(u"  var _cev={actor:'p',sel:selD,", u"  var _cev={actor:_cAct,sel:selD,", 'payload actor')
rep(u"  var _palm=G.pool.filter(function(d){return d.mat==='finnicks_palm';})[0];",
    u"  var _palm=_cRow.filter(function(d){return d.mat==='finnicks_palm';})[0];",
    'palm lookup')
rep(u"    var pi=G.pool.indexOf(_palm),adj=0;\n    selD.forEach(function(d){var di=G.pool.indexOf(d);",
    u"    var pi=_cRow.indexOf(_palm),adj=0;\n    selD.forEach(function(d){var di=_cRow.indexOf(d);",
    'palm adjacency')

# ── 2. the rival collects its selection, then commits it ──
KEEP = u"G.oppDice.filter(d=>!d.kept).forEach((d,i)=>{if(used[i]){d.kept=true;"
assert s.count(KEEP) == 1, 'keep step matched %d' % s.count(KEEP)
s = s.replace(KEEP, u"var _oSel=[];G.oppDice.filter(d=>!d.kept).forEach((d,i)=>{if(used[i]){_oSel.push(d);d.kept=true;")

ANCH = u"        triggerCard(_rkCardId,'KEPT DICE REROLLED!',true);"
assert s.count(ANCH) == 1, 'reroll-block anchor matched %d' % s.count(ANCH)
# find the end of the enclosing `if(G._playerRerollKeptArmed){ ... }` block
i = s.index(u"if(G._playerRerollKeptArmed){")
b = s.index('{', i)
d, j = 0, b
while j < len(s):
    if s[j] == '{':
        d += 1
    elif s[j] == '}':
        d -= 1
        if d == 0:
            break
    j += 1
ins = j + 1
s = s[:ins] + u"""
      /* THE OPPONENT'S commit SEAM - eight of eight. The rival's selection is
         final here and not one line earlier: the player-armed reroll above can
         un-keep every die and zero `total`, so committing before it would raise
         a selection the player then destroyed.
         Same function the player commits through, with actor 'o' - the payload
         is derived once rather than twice. */
      if(_oSel.length&&total>0){ try{ total=famCommitBonus(_oSel,total,'o'); }catch(e){} }""" + s[ins:]

assert s != orig
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count("famCommitBonus(selD,pts,actor)") == 1
assert body.count("famCommitBonus(_oSel,total,'o')") == 1
assert body.count("famCommitBonus(selDice,pts)") == 1, "the player's call site changed"
assert 'var _oSel=[]' in body
assert body.count("actor:_cAct") == 1
# the positional read inside famCommitBonus must be seat-aware now.
# SCOPED TO THAT FUNCTION: G.pool[0] legitimately appears in four others
# (_bookendsEligible, toggleDie, _applyCommitBonuses x2) and a whole-file check
# flagged those as failures - the assert was wrong, not the patch.
_fcb = re.search(r'function famCommitBonus[\s\S]{0,2200}?\n\}', body)
assert _fcb, 'famCommitBonus body not found for the scoped check'
assert 'G.pool[0]' not in _fcb.group(0), 'famCommitBonus still reads G.pool positionally'
assert '_cRow[0]' in _fcb.group(0), 'the seat-aware row is not in place'
# every other opponent seam intact
for h in ['turnStart', 'roll', 'bust', 'bankBonus', 'rivalTurn', 'deadRoll']:
    assert s.count("famFire('%s',{actor:'o'" % h) == 1, '%s seam disturbed' % h

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print("P479 applied: commit raised for the rival - 8 of 8 seams")
