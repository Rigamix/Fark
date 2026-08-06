# -*- coding: utf-8 -*-
u"""P494 - the persona choice runs. All six scoring sites.

Sized in docs/KEEP_WIRING_SIZE.md. Eight assignments to `total` sit between the
score and the keep loop; six of them are FRESH SCORINGS that replace total AND
used together, and those six are where a choice can hang. The other two kinds -
snare/Vow multiplying, and zeroings - leave `used` alone and must keep applying
to whatever was chosen, which is exactly what happens if the choice lands first.

ALL SIX, not the four tractable ones. Wiring only the initial score would make a
persona's choice evaporate the moment a disruption card fired - the shape that
forced all seven call sites in P489, and the slippery_table re-keep before it. A
boss whose personality switches off because the player played a card is worse
than no personality.

FOG, which the sizing did not fully resolve and which reading it again exposed:
at the initial site the rival is deliberately BLIND to one seat. If the chooser
enumerated candidates over the whole free list it would be choosing WITH the die
fog exists to hide - silently cancelling the tell. So the helper returns the
chosen candidate rather than a mask, and each caller builds the mask against its
own list: at the fog site the visible list excludes the hidden seat, and that
die then simply is not in pick.sel, so its mask entry is false without any
special case.

Ordered AFTER P491's fog re-expansion at that site, or the mask would be built
against indices that are one short.

THE CONTROL, provable before it runs: hoard and combo take the maximal
candidate, and the maximal candidate's points equal the scorer's total - 852
bone rolls, 0 divergences. So a maximal persona on bone dice must produce
literally no change. The jade arm is expected to move, and should: 32 keep
divergences survive P489 and they are choice, not scoring.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. the helper ──
ANCH = u"function _npcChooseKeep(keeps,rung){"
assert s.count(ANCH) == 1, 'chooser anchor matched %d' % s.count(ANCH)
s = s.replace(ANCH, u"""/* _oppChooseFrom - enumerate this roll's legal keeps and let the persona pick.
   Returns the CANDIDATE, not a mask: the caller knows which list its `used`
   array is indexed against, and only the caller can know that at the fogged
   site the rival must choose from the seats it can actually SEE. Handing back a
   mask here would have quietly let the chooser use the die fog hides.
   Null means "nothing to choose" - a bust, or no legal keep - and every caller
   leaves total and used exactly as they were. */
function _oppChooseFrom(freeD,total,bank){
  if(!freeD||!freeD.length)return null;
  if(!total||total<=0)return null;/* bust: there is nothing to keep */
  var cands;
  try{ cands=_legalKeeps(freeD,'o',bank||0); }catch(e){ return null; }
  if(!cands||!cands.length)return null;
  var pick;
  try{ pick=_npcChooseKeep(cands,(typeof G!=='undefined'&&G)?G.rung:null); }catch(e){ return null; }
  return (pick&&pick.sel&&pick.sel.length)?pick:null;
}

""" + ANCH)

# ── 2. the five full-visibility scoring sites ──
FIVE = [
    ('_encRs', u"total=_encRs.total;used=_encRs.used;"),
    ('_resR',  u"total=_resR.total;used=_resR.used;"),
    ('_qhR',   u"total=_qhR.total;used=_qhR.used;"),
    ('_gbR',   u"total=_gbR.total;used=_gbR.used;"),
    ('_stR',   u"total=_stR.total;used=_stR.used;"),
]
for tag, old in FIVE:
    assert s.count(old) == 1, '%s site matched %d' % (tag, s.count(old))
    s = s.replace(old, old + (u"""
          /* P494: the persona chooses. Fog only clouds the FIRST reckoning of a
             turn, so here the rival sees every free seat. */
          var _pk%s=G.oppDice.filter(function(d){return !d.kept;});
          var _pc%s=_oppChooseFrom(_pk%s,total,oppBank);
          if(_pc%s){total=_pc%s.pts;used=_pk%s.map(function(d){return _pc%s.sel.indexOf(d)>=0;});}"""
        % (tag, tag, tag, tag, tag, tag, tag)))

# ── 3. the fogged initial site, AFTER P491's re-expansion ──
REEXP = u"      if(_fogCut>=0&&used&&used.length<fV.length)used.splice(_fogCut,0,false);"
assert s.count(REEXP) == 1, 're-expansion anchor matched %d' % s.count(REEXP)
s = s.replace(REEXP, REEXP + u"""
      /* P494 - THE PERSONA CHOOSES, from the seats it can SEE.
         Fog hides one seat from the rival's reckoning, so the candidates are
         enumerated over the VISIBLE dice only. Choosing over the full list
         would hand the chooser the very die the tell exists to hide, which
         would cancel FOG without anything announcing it.
         The hidden die is simply absent from pick.sel, so its entry in the mask
         is false with no special case - and `used` is built against _oFree, the
         full list, which is what the keep loop indexes. Placed after the
         re-expansion above so both are talking about the same indices. */
      var _oVis=(_fogCut>=0)?_oFree.filter(function(d,i){return i!==_fogCut;}):_oFree;
      var _oPick=_oppChooseFrom(_oVis,total,oppBank);
      if(_oPick){
        total=_oPick.pts;
        used=_oFree.map(function(d){return _oPick.sel.indexOf(d)>=0;});
      }""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count('function _oppChooseFrom(') == 1
# six call sites, no more and no fewer
assert body.count('_oppChooseFrom(') == 7, 'definition + 6 sites, got %d' % body.count('_oppChooseFrom(')
# the fogged site must choose from the VISIBLE list, not the full one
assert '_oppChooseFrom(_oVis,total,oppBank)' in body, 'the fogged site is not using the visible list'
assert '_oFree.filter(function(d,i){return i!==_fogCut;})' in body
# and it must still build its mask against the FULL list
assert 'used=_oFree.map(' in body
# ordering: the choice comes after the re-expansion, never before
assert body.index('used.splice(_fogCut,0,false)') < body.index('_oppChooseFrom(_oVis'), \
    'the choice runs before the fog re-expansion'
# every one of the five recompute sites got one
for tag, _ in FIVE:
    assert body.count('_oppChooseFrom(_pk%s,total,oppBank)' % tag) == 1, '%s not wired' % tag
# earlier work intact
assert body.count('function _npcChooseKeep(') == 1
assert body.count('function _handShape(') == 1
assert body.count('_scoreRollBest(') == 8
assert body.count("famCommitBonus(_oSel,total,'o')") == 1

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P494 applied: the persona chooses at all six scoring sites')
