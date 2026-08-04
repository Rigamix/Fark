# -*- coding: utf-8 -*-
"""P452 - `matchArmed`, the run-scoped domain's one real seam.

RULED: build the run-scoped domain as a genuine parallel system. The seam
measurement proposed TWO - seatCommit and matchArmed. Reading the exact lines
to write this patch disqualified one of them, which is the third time that
step has changed the answer today (endMatch, then seatCommit).

seatCommit IS NOT A MOMENT. Its three cards sit at launchSeat body lines 23,
26 and 33, and the work between them is load-bearing:

    _rsTake('_dsArmed'); if(_dsPlay) buy = ...*2      <- Double Stakes
    S.run.gold = (S.run.gold||0) - buy;               <- MUST follow the double
    _rsTake('_fkArmed'); if(_fkPlay) famBurn(...)     <- For Keeps
    night.seatsPlayed[...]=true; save();
    var oCards = generateOppCards(patron);
    if(famOwnTier('high_table')>0) patron.target += 500  <- High Table

Firing one hook at one point would mean moving High Table's target change
above save() and generateOppCards, or Double Stakes below the gold deduction.
Either reorders things that depend on each other. Same shape as endMatch's
disqualification and the two-phase turn clear: the gap between them is what
each one is.

matchArmed IS a moment - three CONSECUTIVE lines, nothing in between, all three
cards stamping their flag onto the freshly built G and telling the player. That
is a single instant with three independent participants, which is exactly what
a seam is for.

ORDER DOES NOT MATTER HERE and that is worth stating, because it is the
opposite of the commit hook. These three write three different flags on G and
read nothing of each other's. famFire needed ev.mul because its participants
composed; RSX's do not. No accumulator, no ordering rule - just dispatch.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

DASH = u'—'
OLD = (
u"    if(_fkPlay&&G){G._forKeeps=true;famLog('FOR KEEPS " + DASH + u" THIS MATCH IS FOR DICE');}\n"
u"    if(_dsPlay&&G){G._doubleStakes=true;famLog('DOUBLE STAKES " + DASH + u" TWICE THE BUY-IN, TWICE THE POT');}\n"
u"    if(G&&G.rung&&G.rung._highTable){G._highTable=true;famLog('HIGH TABLE " + DASH + u" TARGET RAISED 500 FOR BOTH SIDES');}"
)
assert s.count(OLD) == 1, 'matchArmed block matched %d' % s.count(OLD)
s = s.replace(OLD,
u"""    /* THE matchArmed SEAM. G has just been built; each run-scoped card
       stamps its flag and says so. Three consecutive lines with nothing
       between them was the whole test for whether this is one moment. */
    _rsFire('matchArmed',{plays:{double_stakes:_dsPlay,for_keeps:_fkPlay}});""")

# ── the seam and its table, declared next to the run-scoped arm ──
ANCHOR = u"function _rsToggle(key){"
assert s.count(ANCHOR) == 1, '_rsToggle anchor %d' % s.count(ANCHOR)
s = s.replace(ANCHOR,
u"""/* == THE RUN-SCOPED SEAM BUS ==========================================
   The match domain has famFire and ten hooks. The run domain has ONE seam,
   and the number is measured rather than modest: of the moments the six
   run-scoped cards reach into, exactly one is a moment rather than a
   function several cards happen to share.

     matchArmed   G has just been built; each card stamps its flag and tells
                  the player. Three consecutive lines, nothing between.

   WHAT WAS REJECTED, so nobody re-proposes it from the same evidence:

     endMatch     4 cards touch it - the most of anything - across 619 lines,
                  from 6%% to 98%% of the body. Cursed Table's circle count and
                  Hair of the Dog's arming are ~570 lines apart. A shared
                  FUNCTION, not a shared moment.
     seatCommit   3 cards at launchSeat lines 23/26/33 with load-bearing work
                  between: the gold deduction MUST follow Double Stakes
                  doubling the buy-in, and High Table's target change sits
                  below save() and generateOppCards. Firing one hook would
                  reorder things that depend on each other.

   NO ACCUMULATOR AND NO ORDERING RULE, unlike famFire. Its participants
   compose - short_fuse multiplies what bloom adds - which is why ev.mul had
   to exist. These three write three different flags on G and read none of
   each other's, so dispatch is the whole job. Adding an accumulator here
   would be inventing a requirement, which is the mistake the multiplier
   decision was dropped for.

   RSX is keyed by card id, like CFX. Deliberately a separate table: a
   run-scoped card on the match bus would be given a lifetime the match bus
   cannot express, which is the whole reason this domain exists. */
var RSX={
  for_keeps:{matchArmed:function(ev){
    if(!ev.plays.for_keeps||!G)return;
    G._forKeeps=true;famLog('FOR KEEPS \\u2014 THIS MATCH IS FOR DICE');}},
  double_stakes:{matchArmed:function(ev){
    if(!ev.plays.double_stakes||!G)return;
    G._doubleStakes=true;famLog('DOUBLE STAKES \\u2014 TWICE THE BUY-IN, TWICE THE POT');}},
  /* reads G.rung, not ev.plays: High Table is not armed by the player, it
     applies whenever the card is owned - launchSeat stamps patron._highTable
     and the rung carries it in. */
  high_table:{matchArmed:function(ev){
    if(!(G&&G.rung&&G.rung._highTable))return;
    G._highTable=true;famLog('HIGH TABLE \\u2014 TARGET RAISED 500 FOR BOTH SIDES');}}
};
function _rsFire(seam,ev){
  ev=ev||{};ev.plays=ev.plays||{};
  for(var id in RSX){
    if(!RSX.hasOwnProperty(id))continue;
    var fx=RSX[id];if(!fx||!fx[seam])continue;
    try{fx[seam](ev);}catch(e){console.error('rsFX',id,seam,e);}
  }
  return ev;
}
""" + ANCHOR)

assert s != orig, 'nothing changed'
assert s.count('function _rsFire(') == 1
assert s.count("_rsFire('matchArmed'") == 1
assert s.count('matchArmed:function(ev)') == 3, \
    'matchArmed hooks %d (want 3)' % s.count('matchArmed:function(ev)')
# the three hand-written stamps must be gone
for gone in ('if(_fkPlay&&G){G._forKeeps=true',
             'if(_dsPlay&&G){G._doubleStakes=true',
             'if(G&&G.rung&&G.rung._highTable){G._highTable=true'):
    assert gone not in s, 'old stamp survives: %s' % gone
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P452 applied: matchArmed seam, RSX with 3 cards')
