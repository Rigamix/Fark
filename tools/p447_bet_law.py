# -*- coding: utf-8 -*-
"""P447 - the two Bet Law failures, fixed in the mechanic and in the copy.

Measured (docs/PHASE4_MIGRATION.md, the six run-scoped cards): two of the six
had no downside at all, which the Bet Law forbids - every card opens a gamble
or bends risk in both directions, no pure passive upside.

  HAIR OF THE DOG  fired on a loss you did not choose and cost nothing.
  CURSED TABLE     touched only the win branch. Its own code comment said so:
                   "This card only changes the WIN side, so the copy only
                   claims the win side."

Both fixes are Denis's, verbatim, and both deliberately keep the card's shape
and length rather than rewriting it:

  Hair of the Dog: "...doubled - but bust before banking, and it costs an extra
                   circle." The automatic-on-loss trigger stays (you do not
                   choose to have a hangover); the RESPONSE becomes the wager.
  Cursed Table:    "...THREE circles, not two - lose, and it costs you two
                   circles, not one." Symmetric, which is what makes a curse a
                   curse rather than a one-sided bonus with a spooky name.

BOTH REUSE THE EXISTING CIRCLE MECHANISM rather than inventing a currency. The
chalk board is `S.run.points` with a parallel `S.run._chalkMeta` array, and the
two must move together - _tabSettle and the cursed-seat loss both decrement the
count AND pop the meta. A fix that moved one without the other would desync the
board from its own history, and nothing would report it.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ORDER MATTERS HERE AND THE FIRST RUN PROVED IT. Inserting the helper first
# made its own body - the same two lines, same indentation - a second match for
# the call-site pattern, and the exact-count assert caught it. Convert the call
# sites first, THEN add the helper: a patch that introduces the text it is
# searching for has to do the search before the introduction.
# the two existing sites move onto it
OLD_TAB = u"""    S.run.points=Math.max(0,(S.run.points||0)-1);
    if(Array.isArray(S.run._chalkMeta))S.run._chalkMeta.pop();"""
assert s.count(OLD_TAB) == 1, 'tab default site %d' % s.count(OLD_TAB)
s = s.replace(OLD_TAB, u"""    _rubOutCircles(1);""")

OLD_SEAL = u"""    S.run.points=Math.max(0,S.run.points-1);
    if(Array.isArray(S.run._chalkMeta))S.run._chalkMeta.pop();/* the board rubs one out */"""
assert s.count(OLD_SEAL) == 1, 'cursed loss site %d' % s.count(OLD_SEAL)
s = s.replace(OLD_SEAL,
  u"""    /* CURSED TABLE now cuts BOTH ways. It used to amplify only the win side
       (3 circles instead of 2) while the loss stayed at the baseline 1 - a
       pure upside, which the Bet Law forbids. Symmetric now: the card that
       wins you an extra circle costs you an extra one. */
    _rubOutCircles((G&&G._sealRule&&famOwnTier('marked_table')>0)?2:1);""")

# ── a shared helper, because there are now THREE circle-cost sites ──
ANCHOR = u"function _tabSettle(){"
assert s.count(ANCHOR) == 1, '_tabSettle anchor %d' % s.count(ANCHOR)
s = s.replace(ANCHOR,
  u"""/* RUB OUT N CIRCLES. The chalk board is TWO structures - S.run.points is the
   count and S.run._chalkMeta is the per-circle history - and they must move
   together or the board disagrees with its own record. That pairing was already
   duplicated at the tab default and the cursed-seat loss; this patch would have
   made it three. Named once instead. */
function _rubOutCircles(n){
  if(!S||!S.run)return 0;
  var gone=0;
  for(var i=0;i<(n||1);i++){
    if((S.run.points||0)<=0)break;
    S.run.points=Math.max(0,(S.run.points||0)-1);
    if(Array.isArray(S.run._chalkMeta))S.run._chalkMeta.pop();
    gone++;
  }
  return gone;
}
function _tabSettle(){""")

# ── Hair of the Dog: the wager it never had ──
OLD_HOTD = u"""    if(G._famBankCount===1&&S&&S.run&&S.run._hotdNext){
      total*=2;S.run._hotdNext=false;try{save();}catch(e){}"""
assert s.count(OLD_HOTD) == 1, 'hotd payout %d' % s.count(OLD_HOTD)
s = s.replace(OLD_HOTD,
  u"""    /* HAIR OF THE DOG pays here and is SPENT here - see the bust half in
       doBust. Banking first is what wins the wager. */
    if(G._famBankCount===1&&S&&S.run&&S.run._hotdNext){
      total*=2;S.run._hotdNext=false;try{save();}catch(e){}""")

# the losing half: bust before you have banked
BUST_ANCHOR = u"function _bustTolls(){"
assert s.count(BUST_ANCHOR) == 1, '_bustTolls anchor %d' % s.count(BUST_ANCHOR)
s = s.replace(BUST_ANCHOR,
  u"""/* HAIR OF THE DOG, THE LOSING HALF. The card used to be a consolation
   payout: it armed automatically on a loss and cost nothing, which is not a
   bet. Now the doubled bank is the prize and busting before you have banked
   anything is the price.
   GATED ON _famBankCount===0, not on "did this turn bust" - the wager is about
   reaching a bank at all this match. Once the first bank lands the card has
   already paid and cleared itself, so a later bust cannot charge for it twice.
   Called from _bustTolls so it sits with the other bust costs rather than in a
   branch of doBust: the toll applies however the bust arrived. */
function _hotdToll(){
  if(!S||!S.run||!S.run._hotdNext)return;
  if(!G||(G._famBankCount||0)>0)return;
  S.run._hotdNext=false;
  var gone=_rubOutCircles(1);
  try{save();}catch(e){}
  if(gone)try{famLog('THE HANGOVER BITES — A CIRCLE RUBBED OUT');}catch(e){}
}
function _bustTolls(){
  try{_hotdToll();}catch(e){}""")

# ── the copy, both cards ──
OLD_HOTD_TXT = u"text:['Lose a match, and your first bank next match is doubled.','','']}"
assert s.count(OLD_HOTD_TXT) == 1, 'hotd text %d' % s.count(OLD_HOTD_TXT)
s = s.replace(OLD_HOTD_TXT,
  u"text:['Lose a match, and your first bank next match is doubled \\u2014 but bust before banking, and it costs an extra circle.','','']}")

OLD_MT_TXT = u"text:['Beat the patron the smoke clings to and the board chalks you THREE circles, not two.','','']}"
assert s.count(OLD_MT_TXT) == 1, 'marked_table text %d' % s.count(OLD_MT_TXT)
s = s.replace(OLD_MT_TXT,
  u"text:['Beat the patron the smoke clings to and the board chalks you THREE circles, not two \\u2014 lose, and it costs you two circles, not one.','','']}")

assert s != orig, 'nothing changed'
assert s.count('function _rubOutCircles(') == 1
# EXACT: three callers - tab default, cursed loss, hangover toll
assert s.count('_rubOutCircles(') == 4, \
    '_rubOutCircles sites %d (want 4: decl + 3 callers)' % s.count('_rubOutCircles(')
assert s.count('function _hotdToll()') == 1
assert s.count('_hotdToll();') == 1
# and the old hand-rolled pairs are gone
assert 'if(Array.isArray(S.run._chalkMeta))S.run._chalkMeta.pop();' not in s.replace(
    'if(Array.isArray(S.run._chalkMeta))S.run._chalkMeta.pop();\n    gone++;', ''), \
    'a hand-rolled chalk pair survives'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P447 applied: both Bet Law fixes, 3 circle sites on one helper')
