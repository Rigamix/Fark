# -*- coding: utf-8 -*-
"""P848: Gambler's Eye stops being a second roll implementation.

Denis, verifying P847: the GE branch had needed _setDieVal, then
famFire('roll'), and still owed deadRoll (fool's gold never fired on a
GE bust - the player busted holding a live rescue charge), the tell
hooks, and _afterRowSettle (its bust check ran on a flat 600ms timer
while physics settles at ~2000ms - resolving a bust on dice the player
hasn't seen). Five seams grafted one at a time onto a parallel path is
the two-copies bug arriving in slow motion.

THE FIX (his shape): the branch does only its OWN work - validate the
split, freeze the holds - then FALLS THROUGH to the main roll path.
The main path already rolls exactly the free, unfrozen dice (the
frozen-die skip at the deal writes the story itself), and every seam
comes with it: famFire('roll'), deadRoll -> fool's gold, the tell
hooks, famApplyRollForces, _afterRowSettle, the real physics throw.
The tell-extraction backlog item closes as moot - the main path IS the
extraction.

The one real difference - a reroll must visibly differ from the face
it replaces - is a FLAG ON THE ROLL (G._geExclude, lane->old face,
consulted by the deal's value writer), not a reason for a second roll.
It is a per-roll buffer, so its one exit is _clearRollForces (R4).

Deleted with the parallel path: the inline reroll loop, the duplicate
600ms bust check, the duplicate onclick restore, the duplicate
turnRollCount++/SFX, P847's grafted famFire (the main path fires it),
and the numDice=toReroll.length write (the P518 mistake shape - frozen
dice keep their lanes; the main path's ceiling handles the count).

Known edge, accepted and stated: a Drill Order cap can refuse the
fall-through roll AFTER the freeze - the player keeps their holds and
banks, which is what the cap means; G._geExclude dies in
_clearRollForces either way.
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


# E1: the branch keeps its own work, loses the parallel roll
sub("""    geSelected.forEach(function(d){d._frozen=true;d.sel=false;if(d.el){d.el.classList.remove('selected');d.el.classList.add('die-frozen');if(d.el._d3)D3.draw(d.el._d3);}});
    /* Reroll non-held free dice */
    var toReroll=geFree.filter(function(d){return !d._frozen;});
    G.numDice=toReroll.length;
    toReroll.forEach(function(d){
      _setDieVal(d,rollFaceExclude(d.mat,d.val,d));d.sel=false;
      if(d.el){d.el.classList.add('card-reroll');
        setTimeout(function(){d.el.classList.remove('card-reroll');d.el.classList.add('card-reroll-settle');settleDie(d.el);
          setTimeout(function(){d.el.classList.remove('card-reroll-settle');},400);},400);}
    });
    /* P847: this IS a roll - the player tapped ROLL - and it never
       reached the seam every roll-counting system reads (slow_cook's
       P813 accrual missed every GE reroll). Same payload shape as the
       main path at _afterRollImpl. The post-roll TELL hooks are still
       main-path-only: that block wants ONE extraction with two
       callers, not a copy here - AUDIT_BACKLOG carries it. */
    try{famFire('roll',{actor:'p',rollNum:(G.turnRollCount||0)+1});}catch(e){}
    SFX.roll();G.turnRollCount++;
    setTimeout(function(){
      var free2=G.pool.filter(function(d){return !d.committed;});var fv=free2.map(function(d){return d.val;});var fm=free2.map(function(d){return d.mat;});var cards=effectiveCards();
      if(!anyScoring(fv,cards,fm,free2)&&!_anchorRescues(cards)){if(_tryBustSave(free2))return;_delayedDoBust(free2);return;}
      _steadyDisarm();/* these dice are new - the arm was about the old ones */
      free2.forEach(function(d){d.el.onclick=function(){toggleDie(d);};});
      G.phase='choosing';refreshSelUI();
    },600);
    return;
  }""",
    """    geSelected.forEach(function(d){d._frozen=true;d.sel=false;if(d.el){d.el.classList.remove('selected');d.el.classList.add('die-frozen');if(d.el._d3)D3.draw(d.el._d3);}});
    /* P848: NO SECOND ROLL IMPLEMENTATION. This branch used to reroll
       inline and return - a parallel roll path that had already needed
       _setDieVal (P846) and famFire('roll') (P847) grafted on, and
       still skipped deadRoll (fool's gold never fired on a GE bust -
       the player busted holding a live rescue charge), the post-roll
       tell hooks, and _afterRowSettle (its bust resolved on a 600ms
       timer under ~2000ms physics). The main path below rolls exactly
       the free, unfrozen dice - which after the freeze above is
       precisely this card's reroll set - so every seam comes for free,
       now and for whatever seam is added next. The one real
       difference, "the reroll must visibly differ", is a flag on the
       roll: the deal's value writer consults G._geExclude (lane -> old
       face) and rolls through rollFaceExclude for those lanes. It is a
       per-roll buffer; its one exit is _clearRollForces. */
    G._geExclude={};
    geFree.forEach(function(d){if(!d._frozen)G._geExclude[d.lane]=d.val;});
    /* falls through to the main roll path - no return */
  }""",
    'E1 the branch falls through')

# E2: the deal's value writer consults the exclude flag
sub("""    if(d._frozen){d.sel=false;if(d.el){d.el.classList.remove('sel');}return;}
    const val=useSpur?rollFaceSpur(d.mat):_rollD(d);d.val=val;d.sel=false;""",
    """    if(d._frozen){d.sel=false;if(d.el){d.el.classList.remove('sel');}return;}
    /* P848: a Gambler's Eye reroll must visibly differ from the face it
       replaces - the flag on the roll, not a second roll path. */
    const val=useSpur?rollFaceSpur(d.mat)
      :((G._geExclude&&G._geExclude[d.lane]!==undefined)?rollFaceExclude(d.mat,G._geExclude[d.lane],d):_rollD(d));
    d.val=val;d.sel=false;""",
    'E2 deal writer consults _geExclude')

# E3: the buffer's one exit
sub("""  G._famPeekVals=null;G._famHoneyVal=null;""",
    """  G._famPeekVals=null;G._famHoneyVal=null;
  G._geExclude=null;/* P848: the GE visibly-differs flag is roll-scoped */""",
    'E3 _clearRollForces owns _geExclude')

# post-asserts
if 'G.numDice=toReroll.length' in s:
    sys.exit('PARALLEL PATH SURVIVED: numDice write (nothing written)')
if s.count("rollNum:(G.turnRollCount||0)+1") != 1:
    sys.exit('famFire roll count %d != 1 (nothing written)' % s.count("rollNum:(G.turnRollCount||0)+1"))
for needed in ['G._geExclude={};', "G._geExclude[d.lane]!==undefined", 'G._geExclude=null;']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
