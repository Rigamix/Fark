# -*- coding: utf-8 -*-
"""P773: the persona measurement harness - phase 2's instrument.

_runPersonaSim(cfg) joins the sim block: N turns of npcTurn per persona
under fixed conditions (same gear, same score context), collecting per
persona the numbers the weight design needs:

  meanBanked   points per completed turn (busts count as 0)
  bustRate     turns lost entirely
  meanRolls    push depth
  evGiveMean   how much EV the persona's keeps gave up vs the best
               candidate (the floor's headroom actually used)

That last column is measured inside the core via an optional ctx.onPick
tap - zero cost when absent, and the tap is how the sim reads decisions
without the core growing a stats dependency. The table is the baseline
the weights (brief section 3) get tuned against; distinctness between
personas is the design property, meanBanked spread is the balance
input.
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
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# ── 1. the core taps its decision for a listening caller ──
sub("""  var pick;
  try{ pick=_npcChooseKeep(cands,ctx.rung||null,{evTable:ctx.evTable,hotHand:ctx.hotHand}); }catch(e){ return null; }
  return (pick&&pick.sel&&pick.sel.length)?{pick:pick,bank:false}:null;
}""",
    """  var pick;
  try{ pick=_npcChooseKeep(cands,ctx.rung||null,{evTable:ctx.evTable,hotHand:ctx.hotHand}); }catch(e){ return null; }
  if(!(pick&&pick.sel&&pick.sel.length))return null;
  /* P773: a listening caller (the persona sim) reads what the choice
     cost - zero work when nobody listens */
  if(ctx.onPick){
    var _bev=-Infinity;
    for(var _pi=0;_pi<cands.length;_pi++)if(cands[_pi].ev>_bev)_bev=cands[_pi].ev;
    try{ctx.onPick({give:(isFinite(_bev)&&pick.ev!==undefined)?(_bev-pick.ev):0,
      kept:pick.sel.length,left:pick.left});}catch(e){}
  }
  return {pick:pick,bank:false};
}""",
    'the onPick tap')

# ── 2. the harness, beside _runBalanceSim ──
sub("""function _runBalanceSim(cfg){""",
    """/* P773: PER-PERSONA TURN STATS - phase 2's calibration instrument.
   N turns of npcTurn per persona, fixed gear and score context. The
   onPick tap reads what each keep gave up against the best candidate.
   Run from the ?sim=1 console: _runPersonaSim({turns:600}) */
function _runPersonaSim(cfg){
  cfg=cfg||{};
  var TURNS=cfg.turns||600;
  var dice6=cfg.dice||['bone','bone','bone','bone','bone','bone'];
  var target=cfg.target||6800;
  var keys=cfg.personas||Object.keys(PERSONAS);
  var rows=[];
  keys.forEach(function(pk){
    var rung={name:'SIM',persona:pk,agg:(cfg.agg!=null)?cfg.agg:0.6,
      minBank:(cfg.minBank!=null)?cfg.minBank:300,
      diceStop:(cfg.diceStop!=null)?cfg.diceStop:2};
    var banked=0,busts=0,rolls=0,gives=[],kepts=[];
    var oc=mkCards([]);
    /* the tap rides through npcTurn -> simTurn -> _npcDecide via a
       transient hook on the rung object the ctx carries */
    rung._onPick=function(info){gives.push(info.give);kepts.push(info.kept);};
    for(var t=0;t<TURNS;t++){
      var r=npcTurn(rung,2000,2000,target,false,oc);
      banked+=r.banked;rolls+=r.rolls;
      if(r.busted)busts++;
    }
    var giveMean=gives.length?Math.round(gives.reduce(function(a,b){return a+b;},0)/gives.length):0;
    var keptMean=kepts.length?+(kepts.reduce(function(a,b){return a+b;},0)/kepts.length).toFixed(2):0;
    rows.push({persona:pk,meanBanked:Math.round(banked/TURNS),
      bustRate:+(busts/TURNS).toFixed(3),meanRolls:+(rolls/TURNS).toFixed(2),
      evGiveMean:giveMean,keptMean:keptMean,picks:gives.length});
  });
  try{console.table(rows);}catch(e){}
  return rows;
}
function _runBalanceSim(cfg){""",
    'the persona harness')

# ── 3. simTurn passes the tap through ──
sub("""        _decided=_npcDecide(_freeObjs,r.total,turn,{
          cards:[],/* the sim scores bare - same as its scoreRoll calls */
          rung:rung,
          evTable:_npcEvTable(dice6),
          hotHand:dice6.length,
          bankFn:function(p,l){return !!bankFn(p,l);}
        });""",
    """        _decided=_npcDecide(_freeObjs,r.total,turn,{
          cards:[],/* the sim scores bare - same as its scoreRoll calls */
          rung:rung,
          evTable:_npcEvTable(dice6),
          hotHand:dice6.length,
          bankFn:function(p,l){return !!bankFn(p,l);},
          onPick:rung._onPick||null/* P773: the persona sim listens */
        });""",
    'the tap threads through')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
