# -*- coding: utf-8 -*-
"""P448 - the run-scoped arm, for the TWO cards that actually share it.

RULED: build the shared primitive for Double Stakes and For Keeps only. The Tab
stays standalone (a quantity, two settlement paths, a deadline - and a sample
size of one is not an abstraction, it is that card's logic with ceremony round
it). Hair of the Dog splits into a trivial arming boolean and a resolve half.

AND HAIR OF THE DOG'S RESOLVE HALF CANNOT REUSE _lm*, WHICH WAS THE EXPLICIT
QUESTION. Checked rather than assumed, and it fails on two independent counts:

  1. _lmDue compares `m.turn === G.oppTurnCount`. Its window is measured in
     OPPONENT TURNS. Hair of the Dog's is measured in BANKS
     (G._famBankCount===1) - a different counter that also resets per match.
  2. _lm* stores its marker on G[key], and `G=null` at match end (two sites).
     Hair of the Dog must survive from the end of one match to a bank in the
     NEXT, which is exactly why it lives on S.run.

Generalising _lm* to take a host object and a counter would make it a new
abstraction with the lane markers as one instance - the same sample-size-of-one
trap ruled against for The Tab, one level up. So: no reuse, and no new code
either. Both of Hair of the Dog's halves already exist and are correct; the
split is a description, not a change. It is documented at the two sites.

WHAT THE PRIMITIVE IS. Three verbs over one boolean on S.run:

  _rsToggle(key)   the Room control flips it, and saves
  _rsArmed(key)    is it armed - for rendering
  _rsTake(key)     read-and-clear at the seat. ONE call, because the read and
                   the clear are a pair: `var x=!!S.run.k; S.run.k=false;` was
                   written out twice, and a future third site copying it could
                   read without clearing and leave the card armed forever.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── the two seat-launch takes, converted BEFORE the helper exists ──
# (P447's self-match: a patch that introduces the text it searches for has to
#  search first. Same discipline here even though the strings differ.)
OLD_DS = u"  var _dsPlay=!!S.run._dsArmed;S.run._dsArmed=false;"
assert s.count(OLD_DS) == 1, 'ds take %d' % s.count(OLD_DS)
s = s.replace(OLD_DS, u"  var _dsPlay=_rsTake('_dsArmed');")

OLD_FK = u"  var _fkPlay=!!S.run._fkArmed;S.run._fkArmed=false;"
assert s.count(OLD_FK) == 1, 'fk take %d' % s.count(OLD_FK)
s = s.replace(OLD_FK, u"  var _fkPlay=_rsTake('_fkArmed');")

# ── the Room toggles, both views, both cards ──
for key in ('_dsArmed', '_fkArmed'):
    old = u"_getS();S.run.%s=!S.run.%s;save();" % (key, key)
    n = s.count(old)
    assert n == 2, '%s toggle matched %d (want 2 - both Room views)' % (key, n)
    s = s.replace(old, u"_rsToggle('%s');" % key)

# ── now the primitive ──
ANCHOR = u"function _tabSettle(){"
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR,
  u"""/* == RUN-SCOPED ARM ===================================================
   Double Stakes and For Keeps are the same card mechanically: the player arms
   it in the Room before choosing a seat, it rides on S.run so it survives
   leaving the screen, and it is spent when the match actually starts.

   TWO CARDS, NOT FOUR, and that was measured. The Tab carries a QUANTITY with
   two settlement paths and a night deadline; Hair of the Dog is armed by an
   OUTCOME rather than by the player and resolves mid-match. Folding four
   things this different into one arm/resolve would need a "maybe the player
   armed it" concept and a resolve that might be a seat, a bank or a night -
   a switch with three arms wearing one name. Same call as Trade staying out
   of the lane markers.

   WHY _rsTake IS ONE VERB. The read and the clear are a pair:
   `var x=!!S.run.k; S.run.k=false;` was written out at both seat-launch sites,
   and the failure mode of copying it is reading without clearing - which
   leaves the card armed forever, spending a one-shot on every match, with
   nothing to show that it happened. */
function _rsToggle(key){_getS();S.run[key]=!S.run[key];save();}
function _rsArmed(key){_getS();return !!S.run[key];}
/* spend it: returns whether it was armed, and disarms in the same breath */
function _rsTake(key){
  _getS();var was=!!S.run[key];
  if(was){S.run[key]=false;try{save();}catch(e){}}
  return was;
}
function _tabSettle(){""")

assert s != orig, 'nothing changed'
assert s.count('function _rsToggle(') == 1
assert s.count('function _rsTake(') == 1
# EXACT: 2 takes + declaration, 4 toggles (2 cards x 2 Room views) + declaration
assert s.count('_rsTake(') == 3, '_rsTake sites %d (want 3)' % s.count('_rsTake(')
assert s.count('_rsToggle(') == 5, '_rsToggle sites %d (want 5)' % s.count('_rsToggle(')
# nothing pokes the two flags directly any more, outside the primitive
import re
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
for key in ('_dsArmed', '_fkArmed'):
    bad = re.findall(r'S\.run\.' + key + r'\s*=', code)
    assert not bad, '%s still assigned directly: %d' % (key, len(bad))
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P448 applied: _rsToggle/_rsArmed/_rsTake, 2 cards, 6 call sites')
