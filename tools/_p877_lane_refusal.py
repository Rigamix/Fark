# -*- coding: utf-8 -*-
u"""P877 (brief section 9b, the half that does not need a re-key): an
occupying enchant will not fire into a spot that already carries a live mark,
and a refused brand scores its face instead of banking zero.

DENIS'S RULING: "When an enchant is activated in match you can't have another
one in that spot until it has affected the opponent." Section 9b makes the
exclusion per SPOT, at FIRE time, and only for the enchants that occupy one -
fog, snuff and snare arm a lane and pay out on the rival's turn; tithe, trade,
break and ward resolve on the spot and are never refused.

WHAT THIS FIXES AND WHAT IT DOES NOT, because the ruling has two halves and
only one of them is reachable without rewriting the rival's scoring path:

  FIXED - snuff onto a lane that already carries a fog. Two different types
    use two different module keys and nothing ever compared lanes, so both
    went live on one spot. That is the case the ruling forbids and the model
    permitted.

  NOT FIXED HERE - two fogs on two different lanes. G._fog holds ONE mark, so
    arming a second overwrites the first: it fires, plays its beat, logs "THEY
    WILL NOT SEE THAT SEAT", banks zero, and does nothing. Refusal cannot
    reach that, because the second fog's lane is legitimately free - the key
    is simply on the wrong axis. The fix is section 9b.3's re-key to
    G._laneMark, and it rewrites all three consumers: each currently searches
    the rival's dice for the ONE die matching a stored lane, and would have to
    iterate lanes instead. Fog's consumer splices parallel arrays and already
    carries a P491 comment about putting a hidden seat back because the
    indices shift - doing that for two lanes at once is exactly the kind of
    change that wants its own patch and its own probe, not the tail of a long
    session in the opponent's scoring path.

A REFUSED BRAND MUST NOT BANK ZERO. _iconFire is built on one law - a brand
banks zero BECAUSE it fired - so if the fire is refused the second half of
that sentence is false and the first half must be too. The refusal is applied
in _splitIcons, which is the one place that decides whether a die is withheld
from scoring, and it is consulted by all seven of its callers including the
preview - so what the player is shown and what they get agree by construction.
Only a 1 or a 5 can carry a brand (_iconFaces), so a refused brand always has
a natural score: 100 or 50, never nothing.

_iconFire ALSO guards, and that is deliberate belt-and-braces rather than
duplication: with the split routing a refused die to `rest` the handler should
never see one, and if some future caller reaches it directly the law still
holds - the guard returns before the beat, before def.fire, before the
zero_hour check and before brand-spent, which is the order section 9b.4 asks
for and the order that matters.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new); edits.append(label); return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. who occupies a spot, and is this spot taken ───────────────────
sub(u"""function _splitIcons(dice){
  var icons=[],rest=[];
  (dice||[]).forEach(function(d){(_dieIsIcon(d)?icons:rest).push(d);});
  return {icons:icons,rest:rest};
}""",
    u"""/* P877 (brief 9b): WHICH ENCHANTS HOLD A SPOT. Fog, snuff and snare arm a
   lane and pay out on the rival's turn, so they occupy it for a window. Tithe,
   trade, break and ward resolve on the spot or on your own turn, hold nothing,
   and are never refused. The ruling is per SPOT, not per type: a second fog
   and a snuff on top of a fog are refused on the same grounds. */
var _LM_OCCUPYING={fog:1,snuff:1,snare:1};
var _LM_KEYS=['_fog','_snuff','_snare'];
function _lmOccupied(lane){
  if(!G||lane===null||lane===undefined||lane<0)return false;
  for(var i=0;i<_LM_KEYS.length;i++){
    var m=G[_LM_KEYS[i]];
    if(m&&m.live&&m.lane===lane)return true;
  }
  return false;
}
/* would this brand be turned away this instant? Pure read - it is consulted
   from the preview as well as the commit, which is what makes what the player
   is SHOWN and what they GET agree by construction. */
function _iconRefused(d){
  try{
    if(!d||!d.ench||!_LM_OCCUPYING[d.ench.t])return false;
    return _lmOccupied(_laneOf(d));
  }catch(e){return false;}
}
function _splitIcons(dice){
  var icons=[],rest=[],refused=[];
  (dice||[]).forEach(function(d){
    if(!_dieIsIcon(d)){rest.push(d);return;}
    /* P877: A REFUSED BRAND IS NOT AN ICON THIS TURN. _iconFire is built on
       one law - a brand banks zero BECAUSE it fired - so a refused fire must
       not take the zero with it. It joins `rest` and scores its natural face,
       which it always has: only a 1 or a 5 can be branded. */
    if(_iconRefused(d)){refused.push(d);rest.push(d);return;}
    icons.push(d);
  });
  return {icons:icons,rest:rest,refused:refused};
}""",
    '1 the refusal predicate and the split')

# ── 2. the handler holds the same law ────────────────────────────────
sub(u"""function _iconFire(d,side){
  var def=ENCH_ICONS[d&&d.ench&&d.ench.t];
  if(!def)return 0;""",
    u"""function _iconFire(d,side){
  var def=ENCH_ICONS[d&&d.ench&&d.ench.t];
  if(!def)return 0;
  /* P877: REFUSED, AND THE ORDER IS THE POINT. This returns before the beat,
     before def.fire, before the zero_hour check and before brand-spent -
     because a brand that did not fire must not play its effect's sound, must
     not end the turn, and must not be marked spent. _splitIcons should mean
     this is never reached; it is kept so the law holds for any caller that
     reaches the handler directly. */
  if(_iconRefused(d))return 0;""",
    '2 the handler guard')

# ── 3. tell the player, once, at the commit ──────────────────────────
sub(u"""    var _sp=_splitIcons(selDice),_iconSel=_sp.icons,_scoreDice=_sp.rest;""",
    u"""    var _sp=_splitIcons(selDice),_iconSel=_sp.icons,_scoreDice=_sp.rest;
    /* P877: say why, or a refused brand reads as the enchant being broken.
       Nothing was lost - the die scored - so this is information, not a
       penalty, and it is gold rather than red. */
    if(_sp.refused&&_sp.refused.length){
      try{setStatusMsg('THAT SEAT IS ALREADY MARKED','gold');}catch(e){}
      try{famLog('THE SPOT IS TAKEN \\u2014 THE BRAND KEEPS ITS FACE');}catch(e){}
    }""",
    '3 the player is told')

# ── post-asserts ─────────────────────────────────────────────────────
for needed in ['var _LM_OCCUPYING=', 'function _lmOccupied(', 'function _iconRefused(',
               'refused:refused', 'THAT SEAT IS ALREADY MARKED']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
if s.count('function _iconRefused(') != 1:
    sys.exit('the predicate is not defined exactly once (nothing written)')
# the guard must sit ABOVE everything it is supposed to precede
_f = s.index('function _iconFire(')
_body = s[_f:_f+4000]
_iGuard = _body.index('if(_iconRefused(d))return 0;')
for later in ['FKFX.play', 'def.fire(', "_ruleActive('zero_hour'", "classList.add('brand-spent')"]:
    if _body.index(later) < _iGuard:
        sys.exit('THE REFUSAL GUARD SITS AFTER %s - a refused brand would still '
                 'do it (nothing written)' % later)
# non-occupying enchants must never be refusable
for t in ('tithe', 'trade', 'break', 'ward'):
    if ("%s:1" % t) in s[s.index('var _LM_OCCUPYING='):s.index('var _LM_KEYS=')]:
        sys.exit('%s was listed as occupying - it resolves on the spot and may '
                 'never be refused (nothing written)' % t)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
