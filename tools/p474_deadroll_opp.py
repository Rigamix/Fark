# -*- coding: utf-8 -*-
u"""P474 - the opponent's deadRoll seam. Seven of eight now raise.

RULED: ship deadRoll alone; hold commit for a ruling. deadRoll needed one value
that is already to hand, and every consumer gates on _fxMine so raising it
ungates nothing.

PLACEMENT MIRRORS THE PLAYER'S EXACTLY, which took three reads to get right:

  player   if(!anyScoring(...) && !_anchorRescues(cards)){
             famFire('deadRoll', {actor:'p', free:free})    <- AFTER the rescue
             if(claimed) return;
             if(_tryBustSave(free)) return;                 <- BEFORE the saves
             _delayedDoBust(free);

  rival    if(total===0){ ...Encore/Stargazer conversion... }
             famFire('deadRoll', {actor:'o', free:...})     <- AFTER the rescue
             var bustSaved=false; ...bust-save cascade...   <- BEFORE the saves

TWO PLACEMENTS I REJECTED, both from misreading which `total===0` is which:

  L28078 is NOT the rival's dead roll. Its own comment says so - it is the
  PLAYER-DISRUPTION path (Quick Hands / Grog's Bump zeroed the roll), and "the
  main bust resolution already ran above". Raising there would fire the seam
  only when the player disrupted, a rare subset.

  The TOP of L27877's block is too early. The Encore/Stargazer branch inside it
  converts blanks into scorers, so a roll can stop being dead. The player's
  raise sits after its own equivalent (_anchorRescues), and matching that
  relative position is the whole point of a mirror.

`free` IS `G.oppDice.filter(d=>!d.kept)` - the exact expression already used
twice in this function, at L28069 and L28079, for the rival's unkept dice.

A STATED ASYMMETRY, under Law 6, because a silence here would be the thing that
law was written against:

  THE PLAYER'S SEAM IS CLAIMABLE. `if(_drEv._claimed)return;` cancels the bust -
  a hook can rescue the roll. THE RIVAL'S IS NOT, YET, and that is deliberate.
  What a claimed rival dead-roll should DO next is undecided: Brutus Grit, the
  one in-file precedent for "rescued, do not bust", clears G.oppDice and
  re-rolls - which would DISCARD whatever the claiming hook just did to those
  dice. Inventing the answer would put fictional behaviour on a real seam, the
  same reason `commit` is being held.

  Nothing can claim it today: every consumer gates on _fxMine and returns early
  for an opponent owner. So this costs nothing now and is written down rather
  than left for someone to discover.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

ANCH = u"      /* NPC bust immunity (hold_the_line, sundays_rest, one_more_round) */"
assert s.count(ANCH) == 1, 'anchor matched %d' % s.count(ANCH)

s = s.replace(ANCH, u"""      /* THE OPPONENT'S deadRoll SEAM. The rival's roll scored nothing and the
         bust has not resolved yet - the same instant the player's raise sits
         at: AFTER the rescue that can un-deaden a roll (Encore/Stargazer here,
         _anchorRescues there) and BEFORE the bust-save cascade below.
         NOT at L28078 - that `total===0` is the player-disruption path by its
         own comment, and would fire only when the player disrupted.
         `free` is the expression this function already uses twice for the
         rival's unkept dice.
         CLAIM IS NOT HONOURED HERE AND THAT IS DELIBERATE (Law 6 wants the
         reason stated, not the asymmetry hidden): the player's seam lets a
         hook cancel the bust, but what a rescued RIVAL roll does next is
         undecided - the one precedent, Brutus Grit, clears oppDice and
         re-rolls, which would discard whatever the hook just did. Nothing can
         claim it today; every consumer gates on _fxMine. */
      try{famFire('deadRoll',{actor:'o',free:G.oppDice.filter(function(d){return !d.kept;})});}catch(e){}
""" + ANCH)

assert s != orig, 'nothing changed'
assert s.count("famFire('deadRoll',{actor:'o'") == 1
# the player's raise is untouched
assert s.count("famFire('deadRoll',_drEv);") == 1
assert s.count("if(_drEv._claimed)return;") == 1
# it landed before the bust-save cascade and after the Encore block
i_raise = s.index("famFire('deadRoll',{actor:'o'")
i_saves = s.index("var bustSaved=false,bustSavedCid=null;")
i_enc = s.index("var _oEnc=_npcFamCard('encore')")
assert i_enc < i_raise < i_saves, 'placement is wrong relative to rescue/saves'
# and NOT at the disruption path
i_disrupt = s.index("if(total===0){_oppBustOut();return;}")
assert i_raise < i_disrupt, 'raise landed on the disruption path'
# the six already shipped are intact
for h, a in [('turnStart', 'o'), ('roll', 'o'), ('bust', 'o'), ('bankBonus', 'o'), ('rivalTurn', 'o')]:
    assert s.count("famFire('%s',{actor:'%s'" % (h, a)) == 1, '%s seam disturbed' % h

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P474 applied: opponent deadRoll seam raised - 7 of 8')
