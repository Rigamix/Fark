# -*- coding: utf-8 -*-
"""P438 - Effect Phase 2: lift the ownership guard, and ONLY where it is the
same question.

Nine handlers open with `!ev.mine||ev.owner!=='p'`, spelled character-for-
character. famFire already computes ev.mine and every one of them re-derives it.
One meaning, nine sites, no disagreement today - and the risk being removed is
that they ever drift, which is exactly how Vagabond came to read a stale
variable while its dispatch was perfect.

BUT THERE IS A SECOND, DIFFERENT OWNERSHIP TEST AND IT MUST NOT BE SWEPT IN.
Three handlers check `ev.owner==='p'` INLINE, without an early return and
WITHOUT ev.mine:

    slow_cook.turnStart   if(ev.owner==='p')ev.me.state.acc=0;
    slow_cook.bust        if(ev.owner==='p')ev.me.state.acc=0;
    short_fuse.turnStart  if(ev.owner==='p')...

`ev.mine` is `(ev.actor===owner)`, so form 2 ALSO fires when the OPPONENT is the
actor - a player's slow_cook resets its accumulator on the rival's turn start
too. Whether that is intended (reset before your turn, whoever triggered it) or
an oversight is a BEHAVIOUR question, and unifying the two spellings would
answer it silently in whichever direction the shared helper happened to pick.

That is the same trap as collapsing canUse into the event hooks because both
"look like guards", one level deeper. So: the nine move, the three stay, and the
discrepancy is named at the site rather than resolved by tidying.

NO HOISTING INTO famFire, either. The guard is on 9 of 42 hooks; filtering in
the dispatcher would silently change the other 33 - and `powder_keg.use` opens
with `_tryBustSave(free)`, a guard that SPENDS a bust save, so speculative or
shared evaluation would double-spend it.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── the shared condition, next to famFire which already computes ev.mine ──
ANCHOR = u"function famLog(msg,color){"
assert s.count(ANCHOR) == 1, 'famLog anchor %d' % s.count(ANCHOR)
s = s.replace(ANCHOR,
  u"""/* ── SHARED CONDITION #1: does this event belong to the player, as MINE? ──
   Nine handlers asked this by hand, spelled identically, and famFire computes
   half of it (ev.mine) before handing the event over. One meaning, one place.

   IT IS CALLED PER HANDLER, NEVER HOISTED INTO famFire. Only 9 of 42 hooks ask
   it, so filtering in the dispatcher would silently change the other 33 - and
   powder_keg.use guards with _tryBustSave(), which SPENDS a bust save, so any
   speculative or shared evaluation of guards would double-spend it. Conditions
   in this layer are helpers the handler calls at its own moment, not a filter
   applied on its behalf.

   NOT THE SAME AS `ev.owner==='p'` ALONE, which three handlers use inline -
   see the note at slow_cook. That form omits ev.mine and therefore also fires
   when the RIVAL is the actor. Different question, deliberately left alone. */
function _fxMine(ev){return !!(ev&&ev.mine&&ev.owner==='p');}
function famLog(msg,color){""")

# ── the six plain guards ──
PLAIN_OLD = u"if(!ev.mine||ev.owner!=='p')return;"
n_plain = s.count(PLAIN_OLD)
assert n_plain == 6, 'plain guard count %d (want 6)' % n_plain
s = s.replace(PLAIN_OLD, u"if(!_fxMine(ev))return;")

# ── the three compound ones, state clause preserved verbatim ──
for extra in ('armed', 'lit', 'burn'):
    old = u"if(!ev.mine||ev.owner!=='p'||!ev.me.state.%s)return;" % extra
    assert s.count(old) == 1, 'compound %s count %d' % (extra, s.count(old))
    s = s.replace(old, u"if(!_fxMine(ev)||!ev.me.state.%s)return;" % extra)

# ── name the discrepancy where it lives, without changing it ──
SC = u"  turnStart:function(ev){if(ev.owner==='p')ev.me.state.acc=0;},"
assert s.count(SC) == 1, 'slow_cook turnStart anchor %d' % s.count(SC)
s = s.replace(SC,
  u"""  /* `ev.owner==='p'` ALONE, not _fxMine - and the difference is real, not a
     spelling. ev.mine is (ev.actor===owner), so this ALSO fires when the RIVAL
     is the actor: the accumulator resets on their turn start as well as yours.
     Left exactly as it was. Whether that is intended (reset before your turn,
     whoever triggered it) or an oversight is a BEHAVIOUR question, and
     unifying the two spellings would have answered it silently in whichever
     direction the shared helper happened to pick. Same shape as short_fuse's
     turnStart and slow_cook's bust below. */
  turnStart:function(ev){if(ev.owner==='p')ev.me.state.acc=0;},""")

assert s != orig, 'nothing changed'
assert s.count(u"!ev.mine||ev.owner!=='p'") == 0, 'a hand-written guard survives'
# COUNT CALLS, NOT THE DECLARATION. The first version counted "_fxMine(ev)"
# and got 10 - because `function _fxMine(ev){...}` contains it too. Every one of
# the nine guards negates the call, so that is the string that means "call site".
assert s.count(u"!_fxMine(ev)") == 9, '_fxMine guards %d (want 9)' % s.count(u"!_fxMine(ev)")
assert s.count(u"function _fxMine(ev)") == 1, 'helper declared %d times' % s.count(u"function _fxMine(ev)")
assert s.count(u"if(ev.owner==='p')") == 3, "inline form changed: %d" % s.count(u"if(ev.owner==='p')")
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P438 applied: 9 guards -> _fxMine, 3 inline checks deliberately untouched')
