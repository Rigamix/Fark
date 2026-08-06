# -*- coding: utf-8 -*-
u"""P502 - combo gets its number, measured rather than guessed.

combo was held at the maximal keep all through the persona work because its
value-per-live-die had never been measured, and a placeholder would only have
had to be re-derived later. This measures it. It matters more now than when it
was parked: Whisper carries combo since P501, so her difficulty rides on it.

THE NUMBER ALREADY EXISTED, in the harness. tools/sim_harness.js evTable()
samples 900 rolls per dice-count against the REAL scorer and returns, for
k = 1..6, the bust probability and the expected points. That is exactly
"what is a live die worth", and it is harness code calling game functions, so
it can live in the game - the same move that brought _legalKeeps across.

MEASURED, and it settles two design questions:

  bone    bust .657 .464 .270 .151 .082 .018   gain  26  47  85 137 247 454
  Whisper bust .696 .432 .240 .079 .031 .003   gain  24  52 130 278 428 629

  1. The marginal value of a live die is CONVEX - on bone, 21/38/52/110/207 for
     the 2nd through 6th. Dice are worth far more in bulk than singly, so a flat
     per-die constant would have been wrong at both ends.
  2. It is strongly MATERIAL-DEPENDENT - Whisper's own loadout gains 629 at six
     dice against bone's 454, and busts at .003 against .018. A static table
     would have been wrong for the one boss who now uses it.

So the table is computed from the actual dice and cached by material key, not
embedded as constants.

N=300 here rather than the harness's 900: one cached build costs ~1800 scoreRoll
calls instead of ~5400, and this runs inside a live turn rather than a batch.
The cache key is the material list, so it is built once per loadout.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

ANCH = u"function _npcChooseKeep(keeps,rung){"
assert s.count(ANCH) == 1, 'chooser anchor matched %d' % s.count(ANCH)

s = s.replace(ANCH, u"""/* _npcEvTable - what is a live die actually worth, for THESE dice?
   Ported from tools/sim_harness.js evTable, which has been measuring it for the
   sim all along. For k = 1..6 it rolls k dice N times through the real scorer
   and returns the bust rate and the mean points.

   Measured and it decided the design twice over:
     - the marginal value of a die is CONVEX (bone: 21/38/52/110/207 for the 2nd
       through the 6th), so a flat per-die constant is wrong at both ends
     - it is strongly MATERIAL-dependent (Whisper's loadout gains 629 at six
       dice against bone's 454), so a static table is wrong for the one boss
       that uses it

   Cached by material list: built once per loadout, not per roll. */
var _npcEvCache=null,_npcEvKey=null;
function _npcEvTable(mats){
  mats=(mats&&mats.length)?mats:['bone'];
  var key=mats.join(',');
  if(_npcEvKey===key&&_npcEvCache)return _npcEvCache;
  var N=300,cards=(G&&G.oCards)||[];
  var tab={bust:[0,0,0,0,0,0,0],gain:[0,0,0,0,0,0,0]};
  for(var k=1;k<=6;k++){
    var bust=0,gain=0;
    for(var t=0;t<N;t++){
      var vals=[],ms=[];
      for(var i=0;i<k;i++){
        var mat=mats[i%mats.length];
        ms.push(mat);
        vals.push((typeof rollFace==='function')?rollFace(mat):(1+Math.floor(Math.random()*6)));
      }
      var r;
      try{ r=scoreRoll(vals,cards,0,{},ms); }catch(e){ continue; }
      if(!r||!r.total||r.total<=0){bust++;continue;}
      gain+=r.total;
    }
    tab.bust[k]=bust/N;
    tab.gain[k]=gain/N;
  }
  _npcEvCache=tab;_npcEvKey=key;
  return tab;
}

""" + ANCH)

# combo stops sharing hoard's branch and gets the measured rule
OLD = u"""  }else{
    /* hoard takes everything scoring and protects it - which is what used[]
       already did."""
assert s.count(OLD) == 1, 'maximal branch matched %d' % s.count(OLD)
s = s.replace(OLD, u"""  }else if(key==='combo'){
    /* THE ONLY PERSONA THAT CALCULATES. Everything else follows a fixed rule;
       combo weighs the points in hand against what the dice it leaves live are
       actually worth, using a table measured off its own dice rather than a
       constant someone picked.

       value = pts + (1 - bust[L]) * gain[L]
       take the points, add what the remaining dice are expected to bring, and
       discount that by the chance they bring nothing.

       L===0 is deliberately scored as 0 rather than as a hot-dice reroll. The
       rival's all-kept path exists but its exact rule was not read, and
       assuming a full six-dice reroll would hand this branch the single
       largest EV in the table on an assumption. Conservative here means combo
       needs a real reason to empty its hand, which is the safe direction. */
    var _evT=_npcEvTable((G&&G.matchOppDice)||(G&&G.oppDice||[]).map(function(d){return d.mat;}));
    var _best=null,_bestV=-Infinity;
    for(var _ci=0;_ci<c.length;_ci++){
      var _k=c[_ci],_L=_k.left|0;
      var _v=_k.pts;
      if(_L>=1&&_L<=6)_v+=(1-(_evT.bust[_L]||0))*(_evT.gain[_L]||0);
      if(_v>_bestV){_bestV=_v;_best=_k;}
    }
    pick=_best||c[0];

  }else{
    /* hoard takes everything scoring and protects it - which is what used[]
       already did."""
)

# and the stale note saying combo lands in the maximal branch
OLD2 = u"""       combo lands here TOO, deliberately: it is meant to weigh points against
       an estimated value per die left live, and that number has not been
       measured. A placeholder would only have to be re-derived properly later,
       so it holds at maximal until the measurement exists. */"""
assert s.count(OLD2) == 1
s = s.replace(OLD2, u"""       combo no longer lands here - P502 measured its number and gave it the
       branch above. This is hoard's alone now. */""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count('function _npcEvTable(') == 1
assert body.count('_npcEvTable(') == 2, 'defined once, called once'
assert "key==='combo'" in body, 'combo must have its own branch now'
assert body.count('_npcEvCache') == 4
# the other personas are untouched
for k in ['aggro', 'straights', 'triples']:
    assert ("key==='" + k + "'") in body, '%s branch disturbed' % k
assert "key==='ones'" not in body, 'ones must still share the maximal branch'
assert body.count('function _npcChooseKeep(') == 1
assert body.count('_oppChooseFrom(') == 7
assert body.count('_sixRun') == 3

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P502 applied: combo calculates, from a table measured off its own dice')
