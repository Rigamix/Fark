# -*- coding: utf-8 -*-
u"""P945 (brief 3.1, build step 9): the lane marks re-key onto the lane.

THE RULING AS A DATA STRUCTURE. An enchant occupies a SPOT, not a die. Three
module keys - G._fog, G._snuff, G._snare - each held one mark, which is the
wrong axis twice over: two fogs on two lanes were impossible (_lmArm was
G[key]=m, a plain overwrite), while fog and snuff on ONE lane both lived,
because nothing compared lanes across two keys. It forbade what the ruling wants
and permitted what it forbids. P877 shipped the refusal half only, and refusal
cannot reach a case where the second lane is legitimately free.

One map keyed by lane: G._laneMark = { 2:{t:'_fog',...}, 4:{t:'_snare',...} }.
_lmArm returns false when the lane is taken, and THAT RETURN IS THE
ENFORCEMENT - no separate check to forget.

AND THE READ SITES HAD TO FOLLOW, or this would be half a fix. The whole point
is that two marks of one type can now exist; a read site that takes
G._fog.lane - singular - would arm two fogs and apply one. Each site now walks
the due marks of its type. That is the half P919 taught me not to leave: fixing
one side of a two-part invariant is worse than fixing neither, because the
disagreement is live and invisible.

THE FOG SPLICE IS THE HAZARD THE BRIEF NAMES. It splices three parallel arrays
(_fogV, _fogM, _fogE) by index, and two fogs mean two splices - where the first
shifts the indices the second was computed against. Collected and spliced in
DESCENDING order, which is the standard repair and the reason the brief said the
rival's scoring path was right to decline this before the re-key existed.

_oSnuffLane BECOMES A SET, because it was singular and has three consumers
(18054, _oHandAfterSweep, and the seat builder in runOppTurn). Two snuffs with a
single published lane would silently drop one. The old scalar is left assigned
alongside for one patch so nothing reading it breaks mid-turn, and it carries
the FIRST lane - which is what it carried before when only one could exist.

NOT SAVED, VERIFIED. The trio never appears in saveMatchState, so there is no
snapshot to migrate and no resume path to repair. That is the one consumer class
this reshape does not have.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. the map, and _lmOccupied becomes a lookup ────────────────────
sub(u"""var _LM_KEYS=['_fog','_snuff','_snare'];
function _lmOccupied(lane){
  if(!G||lane===null||lane===undefined||lane<0)return false;
  for(var i=0;i<_LM_KEYS.length;i++){
    var m=G[_LM_KEYS[i]];
    if(m&&m.live&&m.lane===lane)return true;
  }
  return false;
}""",
    u"""/* P945 (brief 3.1): ONE MARK PER SPOT, KEYED BY LANE. G._fog / G._snuff /
   G._snare are gone. They were keyed on TYPE, which is the wrong axis twice:
   two fogs on two lanes were impossible - _lmArm was G[key]=m, a plain
   overwrite - while fog and snuff on ONE lane both lived, because nothing
   compared lanes across two keys. It forbade what the ruling wants and
   permitted what it forbids.
     G._laneMark = { 2:{t:'_fog',lane:2,live:true,turn:5,turns:2}, ... }
   A mark's TYPE is now a field and its LANE is the key, so "is this spot
   taken" is a lookup rather than a scan, and _lmArm's refusal is the
   enforcement rather than a separate check somebody has to remember. */
var _LM_KEYS=['_fog','_snuff','_snare'];/* the three types, for iteration */
function _lmMap(){
  if(typeof G==='undefined'||!G)return {};
  if(!G._laneMark)G._laneMark={};
  return G._laneMark;
}
/* every LIVE mark, optionally of one type. The map is at most one entry per
   lane, so this is six iterations at worst. */
function _lmLive(type){
  var out=[],M=_lmMap();
  for(var L in M){
    if(!M.hasOwnProperty(L))continue;
    var m=M[L];
    if(m&&m.live&&(!type||m.t===type))out.push(m);
  }
  return out;
}
function _lmOccupied(lane){
  if(typeof G==='undefined'||!G||lane===null||lane===undefined||lane<0)return false;
  var m=_lmMap()[lane];
  return !!(m&&m.live);
}""",
    '1 the map and the occupancy lookup')

# ── 2. arm refuses a taken lane, and that return IS the rule ────────
sub(u"""function _lmArm(key,lane,turns,extra){
  if(!G)return;
  var m={lane:lane,live:true,turn:(G.oppTurnCount||0)+1,turns:turns||1};
  if(extra)for(var k in extra)if(extra.hasOwnProperty(k))m[k]=extra[k];
  G[key]=m;
}""",
    u"""/* P945: RETURNS FALSE WHEN THE LANE IS TAKEN, and that return is the whole
   enforcement of 3.1 - there is no separate occupancy check to forget, because
   the only way to place a mark is through here. A DEAD entry does not block:
   the test is `live`, so a spent mark frees its spot. */
function _lmArm(type,lane,turns,extra){
  if(typeof G==='undefined'||!G)return false;
  if(typeof lane!=='number'||lane<0)return false;
  var M=_lmMap(),cur=M[lane];
  if(cur&&cur.live)return false;
  var m={t:type,lane:lane,live:true,turn:(G.oppTurnCount||0)+1,turns:turns||1};
  if(extra)for(var k in extra)if(extra.hasOwnProperty(k))m[k]=extra[k];
  M[lane]=m;
  return true;
}""",
    '2 arm refuses a taken lane')

# ── 3. due and spend work on ALL marks of a type ────────────────────
sub(u"""/* THE WINDOW GATE. Every read of a lane marker goes through this. */
function _lmDue(key){
  var m=G&&G[key];
  return !!(m&&m.live&&m.turn===G.oppTurnCount);
}""",
    u"""/* THE WINDOW GATE. Every read of a lane marker goes through this.
   P945: a TYPE can now have more than one live mark, so the gate answers "is
   any mark of this type due" and _lmDueList hands back which. A read site that
   took the single stored lane would arm two and apply one. */
function _lmDueList(type){
  var c=(typeof G!=='undefined'&&G&&G.oppTurnCount)||0;
  return _lmLive(type).filter(function(m){return m.turn===c;});
}
function _lmDue(type){
  return _lmDueList(type).length>0;
}""",
    '3 due answers for a type, and lists which')

sub(u"""function _lmSpend(key){
  var m=G&&G[key];if(!m)return;
  m.turns=(m.turns||1)-1;
  if(m.turns>0)m.turn=(G.oppTurnCount||0)+1;
  else m.live=false;
}""",
    u"""/* P945: spends EVERY due mark of the type. Under the attempts ruling a due
   mark either fires or misses and both cost an attempt, so two due fogs cost
   two attempts whether one, both or neither landed. Spending only the first
   would let a second fog lurk for ever. */
function _lmSpend(type){
  if(typeof G==='undefined'||!G)return;
  _lmDueList(type).forEach(function(m){
    m.turns=(m.turns||1)-1;
    if(m.turns>0)m.turn=(G.oppTurnCount||0)+1;
    else m.live=false;
  });
}""",
    '4 spend charges every due mark of the type')

# ── 5. the die-removal shift re-keys the map ────────────────────────
sub(u"""  ['_snuff','_fog','_snare'].forEach(function(k){
    var m=G[k];if(!m||typeof m.lane!=='number')return;
    if(m.lane===L)m.live=false;
    else if(m.lane>L)m.lane--;
  });""",
    u"""  /* P945: the marks are keyed BY LANE now, so a removal re-keys the map
     rather than nudging three fields. A mark sitting ON L dies with the die;
     everything above L shifts down and moves to its new key. Rebuilt into a
     fresh object because renaming keys in place can collide with an entry not
     yet visited. */
  (function(){
    var M=(G._laneMark&&typeof G._laneMark==='object')?G._laneMark:null;
    if(!M)return;
    var out={};
    for(var k in M){
      if(!M.hasOwnProperty(k))continue;
      var m=M[k],ln=+k;
      if(!m||!isFinite(ln))continue;
      if(ln===L){m.live=false;continue;}
      var nl=(ln>L)?ln-1:ln;
      m.lane=nl;out[nl]=m;
    }
    G._laneMark=out;
  })();""",
    '5 removal re-keys the map')

# ── 6. the per-turn sweep walks the map ─────────────────────────────
sub(u"""  ['_snare','_fog','_snuff'].forEach(function(k){
    if(G[k]&&G[k].live&&G.oppTurnCount>(G[k].turn||0)+1)G[k]=null;
  });""",
    u"""  /* P945: one sweep over the map instead of three keys. A swept mark is
     marked dead rather than deleted, and _lmArm tests `live`, so its lane is
     free again immediately - which is what "a seat effect covers exactly one
     opposing turn" has to mean once a lane can be re-armed. */
  _lmLive().forEach(function(m){
    if(G.oppTurnCount>(m.turn||0)+1)m.live=false;
  });""",
    '6 the sweep walks the map')

# ── 7. a snuffed-seat test, beside the other lane helpers ───────────
sub(u"""function _lmOccupied(lane){
  if(typeof G==='undefined'||!G||lane===null||lane===undefined||lane<0)return false;
  var m=_lmMap()[lane];
  return !!(m&&m.live);
}""",
    u"""function _lmOccupied(lane){
  if(typeof G==='undefined'||!G||lane===null||lane===undefined||lane<0)return false;
  var m=_lmMap()[lane];
  return !!(m&&m.live);
}
/* P945: WAS THIS SEAT SNUFFED THIS TURN. G._oSnuffLane was a single published
   number with three readers, and a single number cannot answer for two snuffs -
   it would silently drop one. The published value is a LIST now and this is the
   one test all three readers share, so they cannot drift into two answers. */
function _lmSnuffed(lane){
  try{
    var L=(G&&G._oSnuffLanes)||[];
    return L.indexOf(lane)>=0;
  }catch(e){return false;}
}""",
    '7 the snuffed-seat test')

# ── 8. the snuff read site takes every due mark ─────────────────────
sub(u"""  var _snuffLane=-1;
  if(_lmDue('_snuff')){
    _snuffLane=G._snuff.lane;""",
    u"""  /* P945: EVERY due snuff, not one stored key. Two snuffs on two lanes are two
     entries now, and reading a single lane would arm both and apply one - the
     half-applied shape that makes a fix worse than none. */
  var _snuffLanes=[];
  if(_lmDue('_snuff')){
    var _snuffWant=_lmDueList('_snuff').map(function(m){return m.lane;})
      .filter(function(L){return typeof L==='number'&&L>=0;});""",
    '8a the snuff site collects every due lane')

sub(u"""    _lmSpend('_snuff');
    if(_snuffLane>=0&&left>1){
      left--;/* the seat itself is dropped where rungDice is built, below */
      try{setStatusMsg('THEIR '+(_snuffLane+1)+(_snuffLane===0?'ST':(_snuffLane===1?'ND':(_snuffLane===2?'RD':'TH')))+' DIE IS SNUFFED','gold');}catch(e){}
      try{famLog('SNUFF — THEY PLAY ONE SHORT');}catch(e){}
    }
  }""",
    u"""    _lmSpend('_snuff');
    /* THE ONE-DIE FLOOR IS PER SEAT TAKEN, not per mark due. Two snuffs on a
       two-die hand take one seat, not two, and the published list must hold
       only the seats actually dropped - otherwise a reader skips a seat that
       is still being dealt. */
    _snuffWant.forEach(function(L){
      if(left>1){
        left--;/* the seat itself is dropped where rungDice is built, below */
        _snuffLanes.push(L);
        try{setStatusMsg('THEIR '+(L+1)+(L===0?'ST':(L===1?'ND':(L===2?'RD':'TH')))+' DIE IS SNUFFED','gold');}catch(e){}
        try{famLog('SNUFF — THEY PLAY ONE SHORT');}catch(e){}
      }
    });
  }""",
    '8b the floor is per seat taken')

sub(u"""  G._oSnuffLane=_snuffLane;""",
    u"""  /* P945: a LIST now - see _lmSnuffed. The old scalar is still assigned so a
     reader outside this file's census keeps working, and it carries the first
     lane, which is exactly what it carried when only one could exist. */
  G._oSnuffLanes=_snuffLanes.slice();
  G._oSnuffLane=_snuffLanes.length?_snuffLanes[0]:-1;""",
    '9 the publish becomes a list')

# ── 10. the three readers of the published seat ─────────────────────
sub(u"""        if(_hl[_si]||_si===G._oSnuffLane)continue;""",
    u"""        if(_hl[_si]||_lmSnuffed(_si))continue;/* P945: a list, not a lane */""",
    '10a the EV table reads the list')

sub(u"""  var _sn=G._oSnuffLane;
  if(typeof _sn==='number'&&_sn>=0&&_sn<_all)_all-=1;
  return Math.max(1,_all);""",
    u"""  /* P945: one seat per snuffed lane in range, not one seat total. */
  var _sn=(G._oSnuffLanes||[]).filter(function(L){
    return typeof L==='number'&&L>=0&&L<_all;});
  _all-=_sn.length;
  return Math.max(1,_all);""",
    '10b the hand size counts every snuffed seat')

sub(u"""      if(_i===G._oSnuffLane)continue;/* P525: the published value, not the local */""",
    u"""      if(_lmSnuffed(_i))continue;/* P525/P945: the published list, not the local */""",
    '10c the seat builder reads the list')

# ── 11. fog: every due mark, spliced descending ─────────────────────
sub(u"""      var _fogCut=-1;
      if(_lmDue('_fog')){
        var _fi=-1;
        for(var _fj=0;_fj<_oFree.length;_fj++)if(_oFree[_fj].lane===G._fog.lane){_fi=_fj;break;}
        if(_fi>=0&&_fogV.length>1){
          _fogV.splice(_fi,1);_fogM.splice(_fi,1);if(_fogE)_fogE.splice(_fi,1);_fogCut=_fi;/* P762 */""",
    u"""      /* P945: A LIST OF CUTS. Two fogs on two lanes are two entries now, and
         this splices three parallel arrays by index - so the first splice
         shifts the indices the second was computed against. Collected first,
         then spliced in DESCENDING order, which is the standard repair and the
         reason the brief said this path was right to decline the change before
         the re-key existed. Kept ASCENDING in _fogCuts for the restore below,
         which has to reinsert in the other direction. */
      var _fogCuts=[];
      if(_lmDue('_fog')){
        var _fogIdx=[];
        _lmDueList('_fog').forEach(function(m){
          for(var _fj=0;_fj<_oFree.length;_fj++){
            if(_oFree[_fj].lane===m.lane){_fogIdx.push(_fj);break;}
          }
        });
        _fogIdx.sort(function(a,b){return a-b;});
        /* never blind the whole hand: leave at least one seat readable */
        while(_fogIdx.length&&_fogV.length-_fogIdx.length<1)_fogIdx.pop();
        var _fi=_fogIdx.length?_fogIdx[0]:-1;
        _fogCuts=_fogIdx.slice();
        _fogIdx.slice().sort(function(a,b){return b-a;}).forEach(function(ix){
          _fogV.splice(ix,1);_fogM.splice(ix,1);if(_fogE)_fogE.splice(ix,1);/* P762 */
        });
        if(_fogCuts.length){""",
    '11a fog collects and splices descending')

sub(u"""      if(_fogCut>=0&&used&&used.length<fV.length)used.splice(_fogCut,0,false);""",
    u"""      /* P945: reinsert ASCENDING, so each index is correct at the moment it is
         used - the mirror of the descending splice-out above. */
      if(_fogCuts.length&&used&&used.length<fV.length)
        _fogCuts.forEach(function(ix){used.splice(ix,0,false);});""",
    '11b the restore reinserts ascending')

sub(u"""      var _oVis=(_fogCut>=0)?_oFree.filter(function(d,i){return i!==_fogCut;}):_oFree;""",
    u"""      var _oVis=_fogCuts.length
        ?_oFree.filter(function(d,i){return _fogCuts.indexOf(i)<0;}):_oFree;""",
    '11c the visible list drops every fogged seat')

# ── 12. snare: every due mark bites ─────────────────────────────────
sub(u"""      if(_lmDue('_snare')){
        var _snIdx=-1;
        for(var _si=0;_si<_oFree.length;_si++)if(_oFree[_si].lane===G._snare.lane){_snIdx=_si;break;}
        if(total>0&&_snIdx>=0&&used&&used[_snIdx]){
          var _snX2=!!G._snare.x2;
          total=Math.floor(total/(_snX2?4:2));/* Kindred halves it twice */
          try{famLog('THE SNARE BITES — '+(_snX2?'HALVED TWICE':'HALVED'));}catch(e){}
          try{setStatusMsg('YOUR SNARE CATCHES THEM — '+(_snX2?'A QUARTER':'HALF'),'gold');}catch(e){}
        }""",
    u"""      if(_lmDue('_snare')){
        /* P945: every due snare bites, and two on two scoring seats halve
           twice. Reading one stored lane would arm both and apply one. */
        _lmDueList('_snare').forEach(function(m){
          var _snIdx=-1;
          for(var _si=0;_si<_oFree.length;_si++)if(_oFree[_si].lane===m.lane){_snIdx=_si;break;}
          if(total>0&&_snIdx>=0&&used&&used[_snIdx]){
            var _snX2=!!m.x2;
            total=Math.floor(total/(_snX2?4:2));/* Kindred halves it twice */
            try{famLog('THE SNARE BITES — '+(_snX2?'HALVED TWICE':'HALVED'));}catch(e){}
            try{setStatusMsg('YOUR SNARE CATCHES THEM — '+(_snX2?'A QUARTER':'HALF'),'gold');}catch(e){}
          }
        });""",
    '12 every due snare bites')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# the three type keys are no longer read or written as G._fog etc.
for gone in ('G._fog', 'G._snuff', 'G._snare'):
    if gone in code:
        sys.exit('%s still appears in code - the re-key is incomplete '
                 '(nothing written)' % gone)
# one map accessor, one occupancy test, one arm
for need, n in (('function _lmMap(', 1), ('function _lmLive(', 1),
                ('function _lmOccupied(', 1), ('function _lmArm(', 1),
                ('function _lmDueList(', 1), ('function _lmDue(', 1),
                ('function _lmSpend(', 1)):
    if code.count(need) != n:
        sys.exit('%s is not defined exactly %d time(s) (nothing written)' % (need, n))
# ARM REFUSES: the live test and the false return must both be there
_arm = code.index('function _lmArm(')
_armBody = code[_arm:_arm + 520]
if 'if(cur&&cur.live)return false;' not in _armBody:
    sys.exit('_lmArm does not refuse a taken lane (nothing written)')
if _armBody.count('return true;') != 1:
    sys.exit('_lmArm does not report success (nothing written)')
# spend walks the due list rather than one key
_sp = code.index('function _lmSpend(')
if '_lmDueList(type).forEach' not in code[_sp:_sp + 400]:
    sys.exit('_lmSpend does not charge every due mark (nothing written)')
# the removal rebuilds rather than mutating keys in place
_rm = code.index('function _oRemoveOppDieAt(')
_rmBody = code[_rm:_rm + 1800]
if 'G._laneMark=out;' not in _rmBody:
    sys.exit('the removal does not re-key the map (nothing written)')
if '_tradeSwaps' not in _rmBody or 'oLane' not in _rmBody:
    sys.exit('the removal lost its trade-ledger repair (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
