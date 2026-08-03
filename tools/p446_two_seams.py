# -*- coding: utf-8 -*-
"""P446 - the `deadRoll` and `rivalTurn` seams, closing Phase 4's hook gap.

The commit hook (P445) was the first of three moments the bus could not reach.
These are the other two:

  deadRoll   the roll scored nothing, BEFORE the bust resolves.
             fools_gold_f rerolls here and can CLAIM the roll, cancelling the
             bust entirely.
  rivalTurn  the rival's turn has resolved, with what they scored.
             ill_omen pays out here - it was declared on `use`, a whole turn
             earlier, and nothing on the bus reaches the moment it lands.

TWO HOOKS, TWO NEW EV VERBS, and neither is add/mul:

  ev.claim()     deadRoll only. "I handled this, do not bust." famFire already
                 returns a number, so the claim rides on ev._claimed and the
                 caller reads it - the return value stays the delta and every
                 existing hook is untouched.
  ev.pts         rivalTurn only. READ-ONLY input, not an accumulator: what the
                 rival scored this turn. ill_omen's whole condition is
                 `pts<=0`, and a hook that cannot see the outcome it is
                 predicting cannot express the card.

WHY CLAIM IS NOT JUST `ev.add(...)` OR A TRUTHY RETURN. A dead roll has exactly
two outcomes - the turn continues or the turn ends - and that is a decision, not
a quantity. Encoding it as a number would mean picking a sentinel, and the next
card that wants to claim without scoring would have to know the sentinel.
Snare's separate `_lmRetire` verb is the same argument: a distinct outcome gets
a distinct verb rather than an overloaded one.

WHAT THIS DOES NOT TOUCH. The rival-turn block also contains the NPC's OWN
cards (slow_cook, double_or_nothing, pickpocket, retort via _npcFamCard). Those
are the opponent-side implementation, deliberately separate until P5, and they
are NOT migrated here - `rivalTurn` fires for the PLAYER's cards that resolve
during the rival's turn, which is a different thing that happens to share a
moment. Migrating them would quietly do P5's job with none of P5's decisions.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. famFire learns to be claimed ──
OLD = u"""  ev.add=function(n){ev._delta+=n;};
  ev.mul=function(n){ev._mul*=n;};"""
assert s.count(OLD) == 1, 'famFire verbs matched %d' % s.count(OLD)
s = s.replace(OLD,
  u"""  ev.add=function(n){ev._delta+=n;};
  ev.mul=function(n){ev._mul*=n;};
  /* CLAIM IS A DECISION, NOT A QUANTITY. deadRoll has two outcomes - the turn
     continues or it ends - and encoding that as a number would mean choosing a
     sentinel that every future claiming card has to know. Same argument as
     Snare's _lmRetire being separate from _lmSpend: a distinct outcome earns a
     distinct verb rather than an overloaded one. */
  ev._claimed=false;ev.claim=function(){ev._claimed=true;};""")

# ── 2. fools_gold_f's reroll becomes CFX.fools_gold_f.deadRoll ──
OLD_FG = u"""function famFoolsGold(free){
  var inst=famInst('fools_gold_f');
  if(!inst||inst.charges<=0)return false;
  inst.charges--;try{famRenderRow();}catch(e){}"""
assert s.count(OLD_FG) == 1, 'famFoolsGold head matched %d' % s.count(OLD_FG)
s = s.replace(OLD_FG,
  u"""/* THE BODY OF CFX.fools_gold_f.deadRoll, kept as a named function.
   The hook is the seam; this is still where the work reads best, and inlining
   sixteen lines into a CFX entry would bury the one branch that matters (the
   second roll failing is what arms the burn). Called ONLY from the hook. */
function famFoolsGold(free){
  var inst=famInst('fools_gold_f');
  if(!inst||inst.charges<=0)return false;
  inst.charges--;try{famRenderRow();}catch(e){}""")

OLD_ENTRY = u"CFX.fools_gold_f={\n  bust:function(ev){"
assert s.count(OLD_ENTRY) == 1, 'fools_gold_f entry matched %d' % s.count(OLD_ENTRY)
s = s.replace(OLD_ENTRY,
  u"""CFX.fools_gold_f={
  /* TWO MOMENTS, BY DESIGN, and this is why the card looked half-migrated:
     "Rolled nothing? Reroll everything. But if the second roll fails too, the
     bust burns your turn AND the same amount from your banked points."
     The reroll fires on the dead roll; the burn fires on the bust that follows
     it. Complementary, not duplicated - the bus simply had no dead-roll seam
     until now. */
  deadRoll:function(ev){if(!_fxMine(ev))return;
    if(famFoolsGold(ev.free))ev.claim();},
  bust:function(ev){""")

# ── 3. the dead-roll call site fires the hook ──
OLD_CALL = u"    if(famFoolsGold(free))return;"
assert s.count(OLD_CALL) == 1, 'dead-roll call site matched %d' % s.count(OLD_CALL)
s = s.replace(OLD_CALL,
  u"""    /* THE deadRoll SEAM: nothing scored, and the bust has not resolved yet.
       A hook may claim the roll, which cancels the bust. */
    var _drEv={actor:'p',free:free};
    famFire('deadRoll',_drEv);
    if(_drEv._claimed)return;""")

# ── 4. ill_omen's payout becomes CFX.ill_omen.rivalTurn ──
OLD_IO = u"""    /* ILL OMEN resolution: declared before this rival turn */
    if(G._famIllOmen){
      var _ioT=G._famIllOmen.tier||1,_ioP=famDef('ill_omen').p[_ioT-1];
      if(pts<=0){var take=Math.min(_ioP[0],G.oPts);G.oPts-=take;G.pPts+=take;
        G._featOmenTrue=true;/* OMENS TRUE */
        famLog('THE OMEN LANDS — YOU TAKE '+take);}
      else{G.oPts+=_ioP[1];famLog('THE OMEN MISSES — THEY GAIN '+_ioP[1]);}
      G._famIllOmen=null;try{updHUD();}catch(e){}
    }"""
assert s.count(OLD_IO) == 1, 'ill_omen block matched %d' % s.count(OLD_IO)
s = s.replace(OLD_IO,
  u"""    /* THE rivalTurn SEAM: the rival's turn has resolved and pts is what they
       scored. Ill Omen is declared a whole turn earlier on `use` and lands
       here, which is why it looked half-migrated - nothing on the bus reached
       this moment.
       ev.pts is READ-ONLY input, not an accumulator. The NPC's own cards
       resolve just above via _npcFamCard and are NOT on this hook: that is the
       opponent-side implementation, deliberately separate until P5. This hook
       is for the PLAYER's cards that resolve during the rival's turn - a
       different thing that happens to share a moment. */
    famFire('rivalTurn',{actor:'p',pts:pts});""")

OLD_IO_ENTRY = u"CFX.ill_omen={"
assert s.count(OLD_IO_ENTRY) == 1, 'ill_omen entry matched %d' % s.count(OLD_IO_ENTRY)
s = s.replace(OLD_IO_ENTRY,
  u"""CFX.ill_omen={
  /* declared on `use`, paid here, one rival turn later */
  rivalTurn:function(ev){if(!_fxMine(ev)||!G._famIllOmen)return;
    var _ioT=G._famIllOmen.tier||1,_ioP=famDef('ill_omen').p[_ioT-1];
    if(ev.pts<=0){var take=Math.min(_ioP[0],G.oPts);G.oPts-=take;G.pPts+=take;
      G._featOmenTrue=true;/* OMENS TRUE */
      famLog('THE OMEN LANDS — YOU TAKE '+take);}
    else{G.oPts+=_ioP[1];famLog('THE OMEN MISSES — THEY GAIN '+_ioP[1]);}
    G._famIllOmen=null;try{updHUD();}catch(e){}},""")

assert s != orig, 'nothing changed'
assert s.count("famFire('deadRoll'") == 1
assert s.count("famFire('rivalTurn'") == 1
assert s.count('deadRoll:function(ev)') == 1
assert s.count('rivalTurn:function(ev)') == 1
# the old direct call and the old inline block must both be gone
assert 'if(famFoolsGold(free))return;' not in s, 'old dead-roll call survives'
assert "if(G._famIllOmen){\n      var _ioT" not in s, 'old ill_omen block survives'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P446 applied: deadRoll + rivalTurn seams, ev.claim, 2 cards migrated')
