# -*- coding: utf-8 -*-
"""P830: sleight's land-pause-reroll beat - and the stale-face family
bug the extraction found underneath it.

THE BUG (display-vouches-for-bug class): every rival DEAL-LOOP value
rewrite (player's sleight, the rival's own stargazer peek, their
honeytrap, NPC hot streak) runs in mkDie's 40ms pre-adoption window -
d.el._d3 is undefined, reDrawDieFace's dots branch writes nothing, and
the mesh is born from mkDie's STALE _trueVal stamp: the face shown was
not the value scored. _tradePaint's comment documents the window.
FIX: reDrawDieFace stamps el._trueVal FIRST, unconditionally - a
pre-adoption rewrite is adopted at mesh birth (and the 2D rolling
placeholder path benefits identically via settleDie's _trueVal read).

THE BEAT (spec + Denis-witnessed confusion): sleight fired invisibly
pre-settle. Player->rival: the rewrite moves from the deal loop into
the _afterOppSettle callback - the original roll LANDS and sits for
the settle beat, then the values rewrite synchronously (the reckoning
below the insertion reads the final faces) while the re-tumble plays
on the physics tape (reDrawDieFace on an adopted die is a real
re-throw - the Gambler's Eye idiom, .card-reroll and all).
ORDER NOTE: the rival's own roll-forces (peek/honeytrap) now land at
the deal and sleight rerolls them away at the settle - the player's
reroll beats their scripted roll, which is what a forced reroll means.
Rival->player: the consumption already re-tumbles (working path); it
gains the .card-reroll glow and the roll sound.
Plus: the player's armed sleight now reads as armed on the card (the
rival's already did - the P825 live-state seam)."""
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


# 1) the hoist - the stale-face fix for every pre-adoption rewrite
sub("""/* Helper: redraw die face dots from d.val */
function reDrawDieFace(d){
  if(!d.el)return;
  if(d.el._d3){
    d.el._trueVal=d.val;""",
    """/* Helper: redraw die face dots from d.val */
function reDrawDieFace(d){
  if(!d.el)return;
  /* P830: the true value is stamped FIRST, unconditionally. A rewrite in
     the pre-adoption window (rival deal loop: sleight, their peek, their
     honeytrap, NPC hot streak) used to fall into the dots branch, write
     nothing, and the mesh was born 40ms later from mkDie's STALE stamp -
     the face shown was not the value scored. _tradePaint's comment has
     always documented the window. */
  d.el._trueVal=d.val;
  if(d.el._d3){""",
    'the true value is stamped first')

# 2) player->rival: the deal loop hands off, the settle callback rerolls
sub("""    if(G._famSleight&&oppRollNum===1){
      G._famSleight=false;
      G.oppDice.filter(function(d){return !d.kept;})
        .forEach(function(d){d.val=rollFace(d.mat);try{reDrawDieFace(d);}catch(e){}});
      setStatusMsg('SLEIGHT — THEIR ROLL COMES BACK DIFFERENT','gold');
    }""",
    """    if(G._famSleight&&oppRollNum===1){
      G._famSleight=false;
      G._famSleightGo=true;/* P830: consumed at the SETTLE - the original
        roll must be seen to land before the hand switches it */
    }""",
    'deal loop hands off')

sub("""    _afterOppSettle(()=>{
      G.oppDice.forEach(d=>{if(d.el){
        settleDie(d.el);
        if(G._lanternActive)d.el.classList.add('die-blind');""",
    """    _afterOppSettle(()=>{
      /* P830: SLEIGHT'S BEAT. The roll landed and sat for the settle
         beat; now the hand switches it - values rewritten SYNCHRONOUSLY
         (everything below this line reads the final faces) while the
         re-tumble plays on the physics tape: reDrawDieFace on an adopted
         die is a real re-throw (the Gambler's Eye idiom). */
      if(G._famSleightGo){
        G._famSleightGo=false;
        G.oppDice.filter(function(d){return !d.kept;})
          .forEach(function(d){d.val=rollFace(d.mat);
            if(d.el){d.el.classList.add('card-reroll');
              setTimeout(function(){if(d.el)d.el.classList.remove('card-reroll');},700);}
            try{reDrawDieFace(d);}catch(e){}});
        setStatusMsg('SLEIGHT — THEIR ROLL COMES BACK DIFFERENT','gold');
        try{SFX.roll&&SFX.roll();}catch(e){}
      }
      G.oppDice.forEach(d=>{if(d.el){
        settleDie(d.el);
        if(G._lanternActive)d.el.classList.add('die-blind');""",
    'the settle callback rerolls with the beat')

# 3) rival->player: the working-path consumption gains the glow + sound
sub("""  if(G&&G._oSleight&&G.phase!=='opp'&&(G.turnRollCount||0)===0){
    G._oSleight=false;
    var _slFree=G.pool.filter(function(d){return !d.committed&&!d._frozen;});
    _slFree.forEach(function(d){d.val=_rollD(d);try{reDrawDieFace(d);}catch(e){}});
    famLog('SLEIGHT — YOUR ROLL COMES BACK DIFFERENT');
  }""",
    """  if(G&&G._oSleight&&G.phase!=='opp'&&(G.turnRollCount||0)===0){
    G._oSleight=false;
    var _slFree=G.pool.filter(function(d){return !d.committed&&!d._frozen;});
    /* P830: the re-tumble already happens (adopted dice re-throw through
       reDrawDieFace) - it now wears the reroll glow and the roll sound
       so it reads as THEIR act, not a glitch. */
    _slFree.forEach(function(d){d.val=_rollD(d);
      if(d.el){d.el.classList.add('card-reroll');
        setTimeout(function(){if(d.el)d.el.classList.remove('card-reroll');},700);}
      try{reDrawDieFace(d);}catch(e){}});
    famLog('SLEIGHT — YOUR ROLL COMES BACK DIFFERENT');
    try{SFX.roll&&SFX.roll();}catch(e){}
  }""",
    'player-side beat')

# 4) the player's armed sleight reads as armed
sub("""    var _live=(inst.id==='reprisal'&&G&&((G.oPts||0)-(G.pPts||0))>=1000)
      ||(inst.id==='ill_omen'&&G&&!!G._famIllOmen);""",
    """    var _live=(inst.id==='reprisal'&&G&&((G.oPts||0)-(G.pPts||0))>=1000)
      ||(inst.id==='ill_omen'&&G&&!!G._famIllOmen)
      ||(inst.id==='sleight'&&G&&!!G._famSleight);/* P830: the rival's armed sleight already shows - the player's now does too */""",
    'armed sleight shows')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
