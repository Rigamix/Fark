# -*- coding: utf-8 -*-
"""P763: one table view, one amber rider - the forks P761 added collapse.

Denis: "the same exact flow as when the player uses them, with the
activation being from the npc - no duplicate code or mess." Auditing
P761 against that found two places where I built the effect twice under
one function's name:

1. THE CAPTURE. The player's preserve scans _tableDice() - THE one view
   of what is on the table; my rival branch scanned G.oppDice directly,
   a second implementation of 'find their kept scorer'. _tableDice now
   takes the actor ('o': this roll's keeps in intent order, then the
   held dice) and BOTH captures run the same [1,5] preference loop over
   the same view. The seats store dice differently; the view is where
   that difference is absorbed - once.

2. THE AMBER RIDER existed three times (player trap-close, player deal
   return, my rival return) and was about to exist a fourth: the retry
   loop that waits for the 3D layer to adopt a chip, then shells it.
   _amberRide(el,{watch,spray}) is the one copy; all sites call it. And
   the rival's capture now shells their standing die the moment the trap
   closes - the visual beat the player gets, which my version skipped.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    c = s.count(old)
    if c != 1:
        o2 = old.replace('\n', '\r\n')
        if s.count(o2) == 1:
            old, new = o2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
    s = s.replace(old, new)
    edits.append(label)


# ── 1. the one amber rider, beside the watcher it stashes for ──
sub("""function _amberReturnWhenSettled(){""",
    """/* P763: THE ONE AMBER RIDER. The 3D layer adopts chips on ITS tick, so
   a chip minted this frame has no die yet - every amber site was
   carrying its own copy of this retry loop (player trap-close, player
   deal, rival return: three, about to be four). One copy. watch=true
   stashes the chip for _amberReturnWhenSettled (the shell cracks when
   the next throw lands); spray=true is the trap-closing flourish. */
function _amberRide(el,o){
  o=o||{};
  if(!el)return;
  (function _try(t){
    var dd=window.D3X&&D3X._dieOfChip&&D3X._dieOfChip(el);
    if(dd&&D3X.amberShell){
      D3X.amberShell(dd,true);
      if(o.spray)try{_fxSpray(el,'#e8a23c',12,{speed:28,g:170,size:10,spread:0.6});}catch(e){}
      if(o.watch){
        window._fkAmberChip=el;window._fkAmberWrap=null;
        try{_amberReturnWhenSettled();}catch(e){}
      }
      return;
    }
    if((t||0)<40)setTimeout(function(){_try((t||0)+1);},60);
  })(0);
}
function _amberReturnWhenSettled(){""",
    'the one rider')

# player trap-close uses it
sub("""      if(_hit&&window.D3X&&D3X.amberShell){
        /* the 3D layer adopts chips on ITS tick, so a chip minted or
           re-rendered this frame has no die yet - retry briefly rather
           than shelling nothing (the same wait the payout uses) */
        (function _try(t){
          var _dd=D3X._dieOfChip(_hit);
          if(_dd){D3X.amberShell(_dd,true);
            try{_fxSpray(_hit,'#e8a23c',12,{speed:28,g:170,size:10,spread:0.6});}catch(e){}
            return;}
          if(t<40)setTimeout(function(){_try(t+1);},60);
        })(0);
      }""",
    """      if(_hit)_amberRide(_hit,{spray:true});/* P763: the one rider */""",
    'player trap-close rides')

# player deal uses it
sub("""      /* the amber holds until this throw is done, then cracks */
      (function _shell(t){
        var dd=window.D3X&&D3X._dieOfChip&&D3X._dieOfChip(_pel);
        if(dd&&D3X.amberShell){
          D3X.amberShell(dd,true);
          window._fkAmberChip=_pel;window._fkAmberWrap=null;
          try{_amberReturnWhenSettled();}catch(e){}
          return;
        }
        if((t||0)<40)setTimeout(function(){_shell((t||0)+1);},60);
      })(0);""",
    """      /* the amber holds until this throw is done, then cracks */
      _amberRide(_pel,{watch:true});/* P763: the one rider */""",
    'player deal rides')

# rival return uses it
sub("""      (function _oShell(t){
        var dd=window.D3X&&D3X._dieOfChip&&D3X._dieOfChip(_ovEl);
        if(dd&&D3X.amberShell){
          D3X.amberShell(dd,true);
          window._fkAmberChip=_ovEl;window._fkAmberWrap=null;
          try{_amberReturnWhenSettled();}catch(e){}
          return;
        }
        if((t||0)<40)setTimeout(function(){_oShell((t||0)+1);},60);
      })(0);""",
    """      _amberRide(_ovEl,{watch:true});/* P763: the one rider */""",
    'rival return rides')

# ── 2. one table view, both seats ──
sub("""function _tableDice(){
  var out=[];
  try{
    (G.pool||[]).forEach(function(d){""",
    """function _tableDice(actor){
  var out=[];
  /* P763: THE VIEW TAKES THE ACTOR. The seats store their dice
     differently (pool/kept vs oppDice/_oppHeld) - this is the one place
     that difference is absorbed, so every effect that asks "what is on
     the table" reads the same shape for either owner. 'o': this roll's
     keeps first (intent order, like the player's selection-first), then
     the held dice from earlier rolls. */
  if(actor==='o'){
    try{
      (G.oppDice||[]).forEach(function(d){
        if(d.kept)out.push({val:d.val,mat:d.mat,ench:d.ench||null,
          lane:(typeof d.lane==='number')?d.lane:null,src:'sel',el:d.el});
      });
      (G._oppHeld||[]).forEach(function(d){
        out.push({val:d.val,mat:d.mat,ench:d.ench||null,
          lane:(typeof d.lane==='number')?d.lane:null,src:'kept',el:d.el});
      });
    }catch(e){}
    return out;
  }
  try{
    (G.pool||[]).forEach(function(d){""",
    'the view takes the actor')

# ── 3. the rival capture reads the shared view + shells the die ──
sub("""    if(actor==='o'){
      var _kd=null;
      [1,5].some(function(w){
        _kd=(G.oppDice||[]).filter(function(d){return d.kept&&d.val===w;})[0];
        return !!_kd;
      });
      if(!_kd)return false;
      G._ovDie={val:_kd.val,mat:_kd.mat||'bone',ench:_kd.ench||null,lane:_kd.lane};
      setStatusMsg((G.rung&&G.rung.name||'RIVAL')+' TRAPS A DIE IN AMBER FOR NEXT TURN','red');
      return true;
    }""",
    """    if(actor==='o'){
      /* P763: the SAME preference loop over the SAME view the player's
         capture below runs - _tableDice absorbs the seat difference.
         And the trap closes visually where the die is standing, exactly
         as it does for the player. */
      var _kd=null;
      [1,5].some(function(w){
        _kd=_tableDice('o').filter(function(e){return e.val===w;})[0];
        return !!_kd;
      });
      if(!_kd)return false;
      G._ovDie={val:_kd.val,mat:_kd.mat||'bone',ench:_kd.ench||null,lane:_kd.lane};
      if(_kd.el)_amberRide(_kd.el,{spray:true});
      setStatusMsg((G.rung&&G.rung.name||'RIVAL')+' TRAPS A DIE IN AMBER FOR NEXT TURN','red');
      return true;
    }""",
    'capture through the view')

sub("""    if(actor==='o'){
      return !!(G&&!G._ovDie&&(G.oppDice||[]).some(function(d){
        return d.kept&&(d.val===1||d.val===5);}));
    }""",
    """    if(actor==='o'){
      return !!(G&&!G._ovDie&&_tableDice('o').some(function(e){
        return e.val===1||e.val===5;}));
    }""",
    'canUse through the view')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
