# -*- coding: utf-8 -*-
"""P772: the decision core goes G-free, and the sim finally runs the
real chooser.

Phase 2 opens here (Denis: "teaching the sim to run the live chooser is
the piece that turns 'the patrons behave correctly' into 'the patrons
are tuned correctly'"). The blocker was coupling: _oppChooseFrom reads
the live match (G.rung, G.oCards, G.matchOppDice, oppShouldBank's G
context) while simTurn is pure-functional - which is exactly WHY the sim
kept the maximal set and stayed structurally blind to every persona bug.

_npcDecide(freeD,total,bank,ctx) is the core: candidates, EV pricing,
the bank plan, the floor, the persona pick - everything from P760, with
every outside fact arriving in ctx {cards, rung, evTable, hotHand,
bankFn}. _oppChooseFrom becomes the live-match wrapper (byte-identical
behaviour); simTurn('o') builds die objects and calls the same core, so
the sim's rival now keeps and banks exactly as the table's rival does.

Supporting: _legalKeeps takes an optional cards override (the sim must
not inherit a stale live match's G.oCards); _npcChooseKeep takes an
optional ctx so combo prices off the caller's table instead of reading
G; npcTurn threads the rung through to simTurn.
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


# ── 1. _legalKeeps: cards can be injected ──
sub("""  if(locked==null)locked=_lkO?0:((G&&G.kept)?G.kept.reduce(function(a,k){return a+(k.pts||0);},0):0);
  var cards=_lkO?(G.oCards||[]):(typeof effectiveCards==='function'?effectiveCards():(G.pCards||[]));""",
    """  if(locked==null)locked=_lkO?0:((G&&G.kept)?G.kept.reduce(function(a,k){return a+(k.pts||0);},0):0);
  /* P772: the SIM passes its own cards - inheriting a stale live match's
     G.oCards would score sim dice with real-match rules */
  var cards=(cardsOverride!==undefined&&cardsOverride!==null)?cardsOverride
    :(_lkO?(G.oCards||[]):(typeof effectiveCards==='function'?effectiveCards():(G.pCards||[])));""",
    'cards injectable')

sub("function _legalKeeps(free,actor,locked){",
    "function _legalKeeps(free,actor,locked,cardsOverride){/* P772 */",
    'legalKeeps signature')

# ── 2. _npcChooseKeep: combo prices off the caller's table when given ──
sub("function _npcChooseKeep(keeps,rung){",
    "function _npcChooseKeep(keeps,rung,ctx){/* P772: ctx carries evTable/hotHand for G-free callers */",
    'chooseKeep signature')

sub("""    var _evT=_npcEvTable((G&&G.matchOppDice)||(G&&G.oppDice||[]).map(function(d){return d.mat;}));
    var _best=null,_bestV=-Infinity;""",
    """    var _evT=(ctx&&ctx.evTable)||_npcEvTable((G&&G.matchOppDice)||(G&&G.oppDice||[]).map(function(d){return d.mat;}));
    var _best=null,_bestV=-Infinity;""",
    'combo table from ctx')

sub("""      var _hotL=(_L===0)?_oHandAfterSweep():_L;""",
    """      var _hotL=(_L===0)?((ctx&&ctx.hotHand)||_oHandAfterSweep()):_L;""",
    'combo hot hand from ctx')

# ── 3. the core, carved out of _oppChooseFrom ──
sub("""function _oppChooseFrom(freeD,total,bank){
  if(typeof G!=='undefined'&&G)G._oPlannedBank=null;/* P760: never stale */
  if(!freeD||!freeD.length)return null;
  if(!total||total<=0)return null;/* bust: there is nothing to keep */
  var cands;
  try{ cands=_legalKeeps(freeD,'o',bank||0); }catch(e){ return null; }
  if(!cands||!cands.length)return null;
  /* P760: PRICE EVERY CANDIDATE ONCE - pts + survival x expected gain,
     off the same measured table combo already used. Hot dice (left 0)
     prices the hand a sweep actually deals. */
  try{
    var _evT=_npcEvTable((G&&G.matchOppDice)||(G&&G.oppDice||[]).map(function(d){return d.mat;}));
    var _bestEV=-Infinity;
    cands.forEach(function(k){
      var _L=(k.left===0)?_oHandAfterSweep():k.left;
      k.ev=k.pts+((_L>=1&&_L<=6)?(1-(_evT.bust[_L]||0))*(_evT.gain[_L]||0):0);
      if(k.ev>_bestEV)_bestEV=k.ev;
    });
    /* P760: THE BANK PLAN. Keep and bank are ONE decision (every Farkle
       solver couples them): ask the bank question FIRST, against the
       max-pts keep - and if the answer is bank, take everything
       scoring. The verdict is stashed with the base it priced, so the
       bank site reuses it rather than re-rolling its dice. */
    if(typeof oppShouldBank==='function'&&G&&G.rung){
      var _c0=cands[0];/* _legalKeeps sorts by pts desc */
      var _l0=(_c0.left===0)?_oHandAfterSweep():_c0.left;
      var _plan=false;
      try{_plan=oppShouldBank(G.rung,(bank||0)+_c0.pts,_l0,G.oPts,G.pPts,G.target);}catch(e){}
      if(_plan){
        G._oPlannedBank={verdict:true,base:(bank||0)+_c0.pts};
        return _c0;
      }
    }
    /* P760: THE FLOOR. Personas choose freely among candidates within
       NPC_MAX_GIVE of the best - style decides WHICH good option, never
       whether to take a bad one. */
    var _sane=cands.filter(function(k){return k.ev>=_bestEV-NPC_MAX_GIVE;});
    if(_sane.length)cands=_sane;
  }catch(e){}
  var pick;
  try{ pick=_npcChooseKeep(cands,(typeof G!=='undefined'&&G)?G.rung:null); }catch(e){ return null; }
  return (pick&&pick.sel&&pick.sel.length)?pick:null;
}""",
    """/* P772: THE DECISION CORE, G-FREE. Everything P760 built - candidate
   pricing, the bank plan, the floor, the persona pick - with every
   outside fact arriving in ctx:
     cards    scoring rules for the candidate enumeration
     rung     the persona owner
     evTable  the measured bust/gain table for THESE dice
     hotHand  what a sweep re-deals (seats minus snuff)
     bankFn   (ptsAfterKeep, diceLeft) -> bank? - the caller's banking
   _oppChooseFrom wraps it with the live match; simTurn calls it with
   sim-local state, which is what finally lets the sim run the REAL
   chooser instead of keeping the maximal set. Returns
   {pick, bank, base} or null. */
function _npcDecide(freeD,total,bank,ctx){
  if(!freeD||!freeD.length)return null;
  if(!total||total<=0)return null;/* bust: there is nothing to keep */
  ctx=ctx||{};
  var cands;
  try{ cands=_legalKeeps(freeD,'o',bank||0,ctx.cards); }catch(e){ return null; }
  if(!cands||!cands.length)return null;
  /* P760: PRICE EVERY CANDIDATE ONCE - pts + survival x expected gain,
     off the same measured table combo already used. Hot dice (left 0)
     prices the hand a sweep actually deals. */
  try{
    var _evT=ctx.evTable||_npcEvTable((G&&G.matchOppDice)||(G&&G.oppDice||[]).map(function(d){return d.mat;}));
    var _hot=ctx.hotHand||((typeof _oHandAfterSweep==='function')?_oHandAfterSweep():6);
    var _bestEV=-Infinity;
    cands.forEach(function(k){
      var _L=(k.left===0)?_hot:k.left;
      k.ev=k.pts+((_L>=1&&_L<=6)?(1-(_evT.bust[_L]||0))*(_evT.gain[_L]||0):0);
      if(k.ev>_bestEV)_bestEV=k.ev;
    });
    /* P760: THE BANK PLAN. Keep and bank are ONE decision (every Farkle
       solver couples them): ask the bank question FIRST, against the
       max-pts keep - and if the answer is bank, take everything
       scoring. */
    if(ctx.bankFn){
      var _c0=cands[0];/* _legalKeeps sorts by pts desc */
      var _l0=(_c0.left===0)?_hot:_c0.left;
      var _plan=false;
      try{_plan=!!ctx.bankFn((bank||0)+_c0.pts,_l0);}catch(e){}
      if(_plan)return {pick:_c0,bank:true,base:(bank||0)+_c0.pts};
    }
    /* P760: THE FLOOR. Personas choose freely among candidates within
       NPC_MAX_GIVE of the best - style decides WHICH good option, never
       whether to take a bad one. */
    var _sane=cands.filter(function(k){return k.ev>=_bestEV-NPC_MAX_GIVE;});
    if(_sane.length)cands=_sane;
  }catch(e){}
  var pick;
  try{ pick=_npcChooseKeep(cands,ctx.rung||null,{evTable:ctx.evTable,hotHand:ctx.hotHand}); }catch(e){ return null; }
  return (pick&&pick.sel&&pick.sel.length)?{pick:pick,bank:false}:null;
}
/* the live-match wrapper: same behaviour P760 shipped, one caller of
   the core */
function _oppChooseFrom(freeD,total,bank){
  if(typeof G!=='undefined'&&G)G._oPlannedBank=null;/* P760: never stale */
  var ctx={
    cards:(typeof G!=='undefined'&&G&&G.oCards)||[],
    rung:(typeof G!=='undefined'&&G)?G.rung:null,
    evTable:null,/* the core falls back to the live table */
    hotHand:null,
    bankFn:(typeof oppShouldBank==='function'&&G&&G.rung)?function(p,l){
      var v=false;
      try{v=oppShouldBank(G.rung,p,l,G.oPts,G.pPts,G.target);}catch(e){}
      return v;
    }:null
  };
  var d=_npcDecide(freeD,total,bank,ctx);
  if(!d)return null;
  if(d.bank&&typeof G!=='undefined'&&G)G._oPlannedBank={verdict:true,base:d.base};
  return d.pick;
}""",
    'the core + the wrapper')

# ── 4. the sim runs the chooser ──
sub("""  function simTurn(side,dice6,bankAdd,cs,bankFn,myTotal,oppTotal,target,oppDone,pushHot){""",
    """  function simTurn(side,dice6,bankAdd,cs,bankFn,myTotal,oppTotal,target,oppDone,pushHot,rung){/* P772: rung threads to the chooser */""",
    'simTurn signature')

sub("""      var gain=r.total*(lit()?2:1);
      turn+=gain;
      if(cs.ids.slow_cook&&rolls>2)turn+=cardP(cs,'slow_cook');
      if(cs.ids.bloom&&bloomHit(vals,mats,r.used))turn+=cardP(cs,'bloom');
      var left=[];for(var i=0;i<mats.length;i++)if(!r.used[i])left.push(mats[i]);
      if(!left.length){mats=dice6.slice();if(pushHot&&turn<3000)continue;}
      else mats=left;
      if((myTotal+turn+bankAdd)>=target)return bank();
      if(oppDone){
        if(myTotal+turn+bankAdd>oppTotal)return bank();
        continue;/* last licks */
      }
      if(bankFn(turn,mats.length))return bank();""",
    """      /* P772: THE SIM RUNS THE REAL CHOOSER for the rival. The old line
         kept the maximal set (r.used) always - which is why the sim was
         structurally blind to every persona bug this program fixed. The
         player side keeps its policy-driven maximal keep: player
         policies are the sim's independent variable, not the chooser's. */
      var _keptPts=r.total,_usedMask=r.used,_decided=null;
      if(side==='o'&&rung&&typeof _npcDecide==='function'){
        var _freeObjs=mats.map(function(m,i){return {val:vals[i],mat:m,ench:null,lane:i};});
        _decided=_npcDecide(_freeObjs,r.total,turn,{
          cards:[],/* the sim scores bare - same as its scoreRoll calls */
          rung:rung,
          evTable:_npcEvTable(dice6),
          hotHand:dice6.length,
          bankFn:function(p,l){return !!bankFn(p,l);}
        });
        if(_decided&&_decided.pick){
          _keptPts=_decided.pick.pts;
          _usedMask=_freeObjs.map(function(o){return _decided.pick.sel.indexOf(o)>=0;});
        }
      }
      var gain=_keptPts*(lit()?2:1);
      turn+=gain;
      if(cs.ids.slow_cook&&rolls>2)turn+=cardP(cs,'slow_cook');
      if(cs.ids.bloom&&bloomHit(vals,mats,_usedMask))turn+=cardP(cs,'bloom');
      var left=[];for(var i=0;i<mats.length;i++)if(!_usedMask[i])left.push(mats[i]);
      if(!left.length){mats=dice6.slice();if(pushHot&&turn<3000)continue;}
      else mats=left;
      if((myTotal+turn+bankAdd)>=target)return bank();
      if(oppDone){
        if(myTotal+turn+bankAdd>oppTotal)return bank();
        continue;/* last licks */
      }
      /* the core already answered the bank question for the rival */
      if(_decided){if(_decided.bank)return bank();}
      else if(bankFn(turn,mats.length))return bank();""",
    'sim runs the chooser')

sub("""    return simTurn('o',dice6,bankAdd,oc,function(turn,diceLeft){
      return oppShouldBank(rung,turn,diceLeft,myTotal,playerTotal,target);
    },myTotal,playerTotal,target,playerDone,false);""",
    """    return simTurn('o',dice6,bankAdd,oc,function(turn,diceLeft){
      return oppShouldBank(rung,turn,diceLeft,myTotal,playerTotal,target);
    },myTotal,playerTotal,target,playerDone,false,rung);/* P772 */""",
    'npcTurn threads the rung')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
