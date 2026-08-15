# -*- coding: utf-8 -*-
"""P738: ONE view of the player's dice, ONE table of what cards need.

Denis: 'ensure those fixes are done holistically and fix at the source
rather than add bespoke code for specific cards.' Correct - P737 fixed
honeytrap and P737c fixed preserve with a private helper each, which is
the same bug fixed twice and a third card away from being fixed three
times.

THE SOURCE was that every card asked G.kept directly. G.kept is the
COMMITTED record; the dice a player is pointing at (selected, not yet
committed) live in G.pool. Any card reading one and not the other is
blind to half the table by construction.

_tableDice() is now the single answer to 'what does the player have,
and in what order do they mean it': the live selection first (most
recent intent), then the kept groups newest-first, each entry
normalised to {val,mat,ench,lane,src}. _honeyPairs and _preserveCands
are gone - both are now two-line filters over that one view.

FAM_NEEDS declares what an active card requires as DATA ('pair',
'scorer', 'free'), _famNeedMet answers it from the same view, and
_famWhyNot renders the sentence from the need rather than from a
per-card message map. A card that declares a need gets its gate, its
reason line and its picker from one place; adding the next card is a
one-line table entry, not a new helper.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    global s, n
    c = s.count(old)
    if c != count and '\n' in old:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == count:
            old, c = old2, count
            new = new.replace('\n', '\r\n')
    if c != count:
        sys.exit('ANCHOR x%d (need %d) for %s' % (c, count, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# 1) the one view + the needs table, replacing _honeyPairs
sub(u"""/* P737: THE PAIR THE PLAYER MEANS. Two bugs lived here: only COMMITTED
   dice counted (so a pair you had just selected did not exist), and the
   winner was Object.keys' last match - ascending numeric order, i.e.
   always the HIGHEST pair on the table, never the one you just made.
   Recency decides now: the live selection first, then the most recent
   kept group, then anything else that pairs. */
function _honeyPairs(){
  var out=[];
  try{
    var sel=(G.pool||[]).filter(function(d){return d.sel&&!d.committed;});
    var sv={};sel.forEach(function(d){sv[d.val]=(sv[d.val]||0)+1;});
    Object.keys(sv).forEach(function(v){if(sv[v]>=2)out.push(Number(v));});
    for(var i=(G.kept||[]).length-1;i>=0;i--){
      var kv={};((G.kept[i]||{}).vals||[]).forEach(function(v){kv[v]=(kv[v]||0)+1;});
      Object.keys(kv).forEach(function(v){if(kv[v]>=2&&out.indexOf(Number(v))<0)out.push(Number(v));});
    }
    /* last resort: a pair spread across groups */
    var all={};
    (G.kept||[]).forEach(function(k){(k.vals||[]).forEach(function(v){all[v]=(all[v]||0)+1;});});
    Object.keys(all).forEach(function(v){if(all[v]>=2&&out.indexOf(Number(v))<0)out.push(Number(v));});
  }catch(e){}
  return out;
}""",
    u"""/* ═══ P738: ONE VIEW OF THE PLAYER'S DICE ═══
   Every card used to ask G.kept directly. G.kept is the COMMITTED
   record; the dice a player is pointing at - selected, not yet
   committed - live in G.pool, so a card reading one and not the other
   is blind to half the table BY CONSTRUCTION. That single fact was
   honeytrap's 'NOT NOW' and preserve's, and would have been the next
   card's. Ask this instead.

   ORDER IS INTENT: the live selection first (what the finger is on),
   then kept groups newest-first, then anything older. Entries are
   normalised, so a consumer never has to know which shape it came
   from. `src` says where it came from for the callers that care. */
function _tableDice(){
  var out=[];
  try{
    (G.pool||[]).forEach(function(d){
      if(d.sel&&!d.committed&&!d._frozen)
        out.push({val:d.val,mat:d.mat,ench:d.ench||null,
          lane:(typeof d.lane==='number')?d.lane:null,src:'sel',die:d});
    });
    for(var i=(G.kept||[]).length-1;i>=0;i--){
      var k=G.kept[i]||{};
      var ds=k.dice||((k.vals||[]).map(function(v){return {val:v,mat:k.mat};}));
      ds.forEach(function(dd){
        out.push({val:dd.val,mat:dd.mat||k.mat,ench:dd.ench||null,
          lane:(typeof dd.lane==='number')?dd.lane:null,src:'kept'});
      });
    }
  }catch(e){}
  return out;
}
/* values that appear at least twice, in intent order - a pair the
   player MADE beats an older one that merely exists */
function _tablePairs(){
  var seen={},out=[],all=_tableDice();
  ['sel','kept'].forEach(function(src){
    var c={};
    all.forEach(function(e){if(e.src===src)c[e.val]=(c[e.val]||0)+1;});
    Object.keys(c).forEach(function(v){
      if(c[v]>=2&&!seen[v]){seen[v]=1;out.push(Number(v));}});
  });
  return out;
}
/* WHAT A CARD NEEDS, as data. The gate, the sentence and the picker all
   read this - so a new card is a table entry, not a new helper. */
var FAM_NEEDS={honeytrap:'pair',preserve:'scorer'};
var FAM_NEED_TEXT={
  pair:'KEEP OR SELECT A PAIR FIRST',
  scorer:'KEEP OR SELECT A 1 OR A 5 FIRST',
  free:'ROLL FIRST'
};
function _famNeedMet(need){
  try{
    if(need==='pair')return _tablePairs().length>0;
    if(need==='scorer')return _tableDice().some(function(e){
      return (e.val===1||e.val===5)&&!(e.die&&_dieIsIcon(e.die));});
    if(need==='free')return (G.pool||[]).some(function(d){return !d.committed;});
  }catch(e){}
  return true;
}""",
    'one view + needs table')

# 2) honeytrap reads the shared view
sub(u"""CFX.honeytrap={
  canUse:function(){
    if(!G||G.phase==='opp')return false;
    return _honeyPairs().length>0;
  },
  use:function(inst){
    var pairVal=_honeyPairs()[0]||0;""",
    u"""CFX.honeytrap={
  canUse:function(){
    if(!G||G.phase==='opp')return false;
    return _famNeedMet('pair');/* P738: the shared view */
  },
  use:function(inst){
    var pairVal=_tablePairs()[0]||0;/* P738: intent order */""",
    'honeytrap uses the view')

# 3) preserve reads the shared view - its private helper goes
sub(u"""/* P737c: THE SAME BUG HONEYTRAP HAD, found by auditing the other cards
   for it (Denis: 'check other cards'). A 1 or 5 the player has SELECTED
   but not yet committed is on the table and visible - it just was not in
   G.kept, so Preserve answered NOT NOW while the player was looking at
   the die it wanted. Selection counts now, in both the gate and the
   picker, and it is preferred: it is what the player is pointing at. */
function _preserveCands(){
  var out=[];
  try{
    (G.pool||[]).forEach(function(d){
      if(d.sel&&!d.committed&&!d._frozen&&(d.val===1||d.val===5)&&!_dieIsIcon(d))
        out.push({val:d.val,mat:d.mat,ench:d.ench||null,
          lane:(typeof d.lane==='number')?d.lane:null});
    });
  }catch(e){}
  return out;
}
CFX.preserve={
  canUse:function(){
    if(!G||G.phase==='opp')return false;
    if(_preserveCands().length)return true;
    return (G.kept||[]).some(function(k){return (k.vals||[]).some(function(v){return v===1||v===5;});});
  },""",
    u"""CFX.preserve={
  canUse:function(){
    if(!G||G.phase==='opp')return false;
    return _famNeedMet('scorer');/* P738: the shared view, same as honeytrap */
  },""",
    'preserve uses the view')

# 4) the picker: one filter over the view, both sources, 1 preferred
sub(u"""    /* P737c: the selection first - the die under the player's finger -
       then the kept groups, still preferring the 1 (100 over 50). */
    [1,5].some(function(want){
      var _sc=_preserveCands().filter(function(c){return c.val===want;})[0];
      if(_sc){found=_sc.val;foundMat=_sc.mat||'bone';foundEnch=_sc.ench||null;
        foundLane=_sc.lane;return true;}
      return (G.kept||[]).some(function(k){""",
    u"""    /* P738: ONE filter over the shared view - selection first because
       that is intent order, still preferring the 1 (100 over the 5's 50).
       P534's law holds: a BRANDED face banks zero, so it is never a
       candidate. */
    [1,5].some(function(want){
      var _sc=_tableDice().filter(function(e){
        return e.val===want&&!(e.die&&_dieIsIcon(e.die));})[0];
      if(_sc){found=_sc.val;foundMat=_sc.mat||'bone';foundEnch=_sc.ench||null;
        foundLane=_sc.lane;return true;}
      return (G.kept||[]).some(function(k){""",
    'preserve picker uses the view')

# 5) the reason line derives from the need
sub(u"""    if(fx.canUse&&!fx.canUse(inst)){
      var why={
        honeytrap:'KEEP OR SELECT A PAIR FIRST',
        preserve:'KEEP A 1 OR A 5 FIRST',
        transmute:'ROLL FIRST — IT NEEDS A DIE TO CHANGE',
        powder_keg:'ROLL FIRST',
        sacrifice:'ROLL FIRST — IT NEEDS A DIE TO SPEND',
        stargazer:'ROLL FIRST',
        sleight:'ROLL FIRST',
        tamper:'THE RIVAL HAS NOTHING TO TAMPER WITH YET',
        ill_omen:'NOT THIS MOMENT — IT FIRES ON THEIR TURN'
      }[inst.id];
      return why||'NOT RIGHT NOW';
    }""",
    u"""    if(fx.canUse&&!fx.canUse(inst)){
      /* P738: the sentence comes from the card's declared NEED, so the
         gate and the explanation can never drift apart. Cards with a
         genuinely bespoke condition keep a line of their own below. */
      var need=FAM_NEEDS[inst.id];
      if(need&&FAM_NEED_TEXT[need])return FAM_NEED_TEXT[need];
      if(!(G.pool||[]).some(function(d){return !d.committed;}))return FAM_NEED_TEXT.free;
      var why={
        tamper:'THE RIVAL HAS NOTHING TO TAMPER WITH YET',
        ill_omen:'NOT THIS MOMENT — IT FIRES ON THEIR TURN'
      }[inst.id];
      return why||'NOT RIGHT NOW';
    }""",
    'reason from the need')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
