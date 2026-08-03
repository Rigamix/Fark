# -*- coding: utf-8 -*-
"""P434 - Preserve delivers the die it promised.

MEASURED BEFORE TOUCHING ANYTHING. Preserve spent its charge, printed
"THE AMBER CRACKS - A 1 ALREADY KEPT", and delivered nothing. Verified on a
live match by setting the exact state CFX.preserve.use writes and calling the
consumer: G.kept came back [], numDice 6, stash consumed.

THREE FAULTS, and the first one hid the other two.

1. THE CLOBBER. startPTurn set G.kept and G.numDice from the stash, then four
   lines later - same function, no early return between - `G.kept=[]` and
   `G.numDice=G.matchDice.length` overwrote both. The fix is ordering: the
   restore has to happen AFTER the turn is reset, not before it. Moved, and the
   reset line now says why it must stay upstream.

2. mat:'bone' WAS HARDCODED. A preserved amber or jade die came back as bone,
   losing its material - and with it the family trait the player paid for. The
   kept entry it came from already carries `mat`; it was simply not read.

3. numDice=5 WAS HARDCODED. It assumes a six-die loadout, so it is wrong the
   moment Break has taken one for the match: a five-die player would have got
   five back and lost nothing for the preserve.

DELIBERATELY NOT BUILT: the die/lane fields _breakPreserved is written to read.
Nothing collides with adding them, but nothing needs them yet either - a
preserved die arrives in G.kept, and Break targets G.pool, so the guard has no
reachable case. It stays armed and unreached rather than gaining speculative
structure to match. Recorded so the next person does not read its absence as an
oversight.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

def sub_once(hay, old, new, what):
    n = hay.count(old)
    assert n == 1, 'anchor %s matched %d times (want 1)' % (what, n)
    return hay.replace(old, new)

# ── 1. the writer: capture the DIE, not just a number ─────────────────
s = sub_once(s,
  u"""  use:function(inst){
    var found=null;
    (G.kept||[]).some(function(k){return (k.vals||[]).some(function(v){if(v===1||v===5){found=v;return true;}return false;});});
    if(!found)return false;
    G._famPreserve={val:found,pts:found===1?100:50,crack:(inst.tier===3?100:0)};""",
  u"""  use:function(inst){
    /* CAPTURE THE MATERIAL, NOT JUST THE NUMBER. The old version stored a bare
       value and the consumer rebuilt it as bone, so preserving an amber or jade
       die quietly downgraded it - the player paid for a family trait and got a
       plain die back. The kept entry it came from already carries `mat`. */
    var found=null,foundMat=null;
    (G.kept||[]).some(function(k){
      return (k.vals||[]).some(function(v){
        if(v===1||v===5){found=v;foundMat=k.mat||'bone';return true;}
        return false;
      });
    });
    if(!found)return false;
    G._famPreserve={val:found,mat:foundMat,pts:found===1?100:50,crack:(inst.tier===3?100:0)};""",
  'preserve use')

# ── 2. the consumer: after the reset, not before it ───────────────────
OLD_BLOCK = u"""  if(G&&G._famPreserve){
    var _fp=G._famPreserve;G._famPreserve=null;
    G.kept=[{vals:[_fp.val],mat:'bone',pts:_fp.pts+(_fp.crack||0)}];
    G.numDice=5;
    famLog('THE AMBER CRACKS — A '+_fp.val+' ALREADY KEPT'+(_fp.crack?' (+'+_fp.crack+')':''));
  }
"""
assert s.count(OLD_BLOCK) == 1, 'preserve consumer matched %d' % s.count(OLD_BLOCK)
s = s.replace(OLD_BLOCK, u'')

RESET = (u"  G.phase='idle';G.turnPts=0;G.kept=[];G.numDice=G.matchDice?G.matchDice.length:6;"
         u"G.pool=[];G.turnRollCount=0;G._encorePending=false;G._slowHandUsedThisTurn=false;"
         u"G._warmHandsActive=false;G._lastHotDice=false;G._firstRollCommitted=0;"
         u"G._bustSavedThisTurn=false;\n")
assert s.count(RESET) == 1, 'reset line matched %d' % s.count(RESET)
s = s.replace(RESET, RESET +
  u"""  /* PRESERVE PAYS OUT HERE, AFTER THE RESET, AND THE ORDER IS THE WHOLE FIX.
     This block used to sit four lines UPSTREAM of the reset above, so it wrote
     G.kept and G.numDice and then had both overwritten before the turn began -
     Preserve spent its charge, announced "THE AMBER CRACKS", and delivered
     nothing. Anything restored into a fresh turn has to land after the turn is
     cleared, not before. If the reset ever moves, this moves with it. */
  if(G&&G._famPreserve){
    var _fp=G._famPreserve;G._famPreserve=null;
    /* the die's own material, not bone - see CFX.preserve.use */
    G.kept=[{vals:[_fp.val],mat:_fp.mat||'bone',pts:_fp.pts+(_fp.crack||0),
             dice:[{val:_fp.val,mat:_fp.mat||'bone'}]}];
    G.turnPts=G.kept[0].pts;
    /* ONE FEWER THAN THE LOADOUT, not a hardcoded five. A player whose loadout
       is already down a die to Break has five, and would have been handed five
       back - paying nothing for the preserve. */
    G.numDice=Math.max(1,(G.matchDice?G.matchDice.length:6)-1);
    famLog('THE AMBER CRACKS — A '+_fp.val+' ALREADY KEPT'+(_fp.crack?' (+'+_fp.crack+')':''));
    try{refreshKeptTray();updHUD();}catch(e){}
  }
""", 1)

assert s != orig, 'nothing changed'
assert u"mat:'bone',pts:_fp.pts" not in s, 'hardcoded bone survives'
assert u"G.numDice=5;" not in s, 'hardcoded numDice survives'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P434 applied: preserve restores after the reset, keeps its material, sizes off the loadout')
