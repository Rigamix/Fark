# -*- coding: utf-8 -*-
"""P450 - one seat-target function, because P449 fixed one surface of three.

P449 made the seat sheet show the target the match will actually use - base
plus High Table's +500, which launchSeat applies after the sheet closes. That
was right and it was INCOMPLETE: three surfaces display that number and I
corrected one, so the sheet said 3300 while the patron table still said 2800.

Found by checking rather than by reasoning from my own description of the fix.
The three:

  _gbPeek        the seat sheet          (corrected in P449)
  _ptRoom        st.target -> #ptvTarget (still base)
  the pk-meta preview                    (still base)

WHY A FUNCTION AND NOT THREE MORE EDITS. This is the same shape as
_rubOutCircles one patch earlier: a value that must be computed identically in
several places, already duplicated, and about to be duplicated again by the fix
for the duplication. Every future modifier of the match target - and the
handicaps below launchSeat's High Table line already multiply it - has one
place to be added.

DISPLAY ONLY, AND THAT IS LOAD-BEARING. launchSeat still performs the real
mutation (`patron.target += 500`). If this helper mutated as well the target
would rise by 1000. It reads and returns; it never writes.

WHAT IT DELIBERATELY DOES NOT MODEL: the handicap multipliers applied in
launchSeat right after High Table - last_call x1.5, rising_stakes x1.8,
sudden_death - because those are properties of the SEAT the player has already
been told about by other means, and folding them in here would change three
displays on a guess about which ones the player is meant to see in advance.
High Table is different: it is the player's OWN card silently changing the
number they are choosing against.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── convert the three call sites BEFORE the helper exists (P447's lesson) ──
A = (u"    +((pat.target||0)+((famOwnTier('high_table')>0)?500:0)).toLocaleString()\n"
     u"      +((famOwnTier('high_table')>0)?' <span style=\"opacity:.7\">+500 high table</span>':'')")
assert s.count(A) == 1, 'peek target matched %d' % s.count(A)
s = s.replace(A,
     u"    +_seatTarget(pat).toLocaleString()\n"
     u"      +(_seatTargetRaised()?' <span style=\"opacity:.7\">+500 high table</span>':'')")

B = u"      price:buy,target:pat.target||0,"
assert s.count(B) == 1, 'ptRoom target matched %d' % s.count(B)
s = s.replace(B, u"      price:buy,target:_seatTarget(pat),")

C = u"    +'<div class=\"pk-meta\"><span>TARGET<b>'+(pat.target||0).toLocaleString()+'</b></span>'"
assert s.count(C) == 1, 'pk-meta target matched %d' % s.count(C)
s = s.replace(C,
     u"    +'<div class=\"pk-meta\"><span>TARGET<b>'+_seatTarget(pat).toLocaleString()+'</b></span>'")

# ── now the helper ──
ANCHOR = u"function _tabSettle(){"
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR,
  u"""/* THE TARGET A SEAT WILL ACTUALLY BE PLAYED AT, for display.
   Three surfaces show this number - the seat sheet, the patron table's
   #ptvTarget, and the pk-meta preview - and High Table's +500 is applied by
   launchSeat AFTER all three are gone. So every one of them was showing a
   target the player would not be playing against, and fixing only the sheet
   (P449) left it disagreeing with the other two.

   READS, NEVER WRITES. launchSeat still does the real `patron.target += 500`;
   if this mutated as well the target would rise by 1000. That is the same
   two-writers-to-one-value shape as Preserve's clobber and the chalk board's
   dual structure, so it is worth being explicit: this function is a view.

   NOT MODELLED, on purpose: the handicap multipliers launchSeat applies just
   below High Table (last_call x1.5, rising_stakes x1.8, sudden_death). Those
   are properties of the SEAT, already announced by other means; High Table is
   the player's own card quietly changing the number they are choosing
   against, which is why it is the one that belongs here. */
function _seatTargetRaised(){
  return typeof famOwnTier==='function'&&famOwnTier('high_table')>0;
}
function _seatTarget(pat){
  return (pat&&pat.target||0)+(_seatTargetRaised()?500:0);
}
function _tabSettle(){""")

assert s != orig, 'nothing changed'
assert s.count('function _seatTarget(') == 1
# MINUS THE DECLARATION. `function _seatTarget(pat){` contains the call
# pattern, so a bare count reads 4. Counting a definition as a use of itself is
# the same self-match P447 hit from the other direction, and it has now cost
# two patches a re-run.
_calls = s.count('_seatTarget(pat)') - s.count('function _seatTarget(pat)')
assert _calls == 3, '_seatTarget call sites %d (want 3)' % _calls
# and no display site computes the +500 by hand any more
import re
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert "famOwnTier('high_table')>0)?500:0" not in code, 'a hand-rolled +500 survives'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P450 applied: _seatTarget on all three display surfaces')
