# -*- coding: utf-8 -*-
"""P458 - the sheet teaches your dice, not only scoring.

RULED: ship the draft, and delete the dead rules overlay.

EVERY CLAIM VERIFIED AGAINST LIVE CODE FIRST, because this is the screen that
exists to stop the game saying untrue things and it cannot afford to say one:

  silver rolls 1s and 5s more often  rollTable:[1,5,1,5,2,3,4,6] - 1 and 5 twice
                                     each in eight slots. Its own desc agrees.
  jade turns wild                    effect.mechanic='wild_quad'
  obsidian shatters for points       effect.mechanic='shatter_bonus',
                                     chance 0.06, amount 1000
  cards read the ends of the row     vanguard_f, live in FAM_LIVE, reads
                                     G.pool[0] and G.pool[length-1]. Tier I
                                     pays the first spot, II both ends, III
                                     the full bookends.
  marks reach the seat opposite      snare/snuff/fog mark a LANE and the check
                                     is `_oFree[i].lane === marker.lane` - the
                                     SAME index on their row.

ONE WORDING CHANGE FROM THE DRAFT. "the seat opposite" could be read as the
MIRRORED seat - your first against their last. It is the same index, and the
game's own line says "THEIR 3RD DIE IS SNUFFED". So: "the same seat on their
side of the table", which cannot be misread. That is the whole reason this
screen was worth checking rather than shipping as written.

AND THE DEAD OVERLAY IS ALREADY GONE. OPEN.md described eight tabs of authored
copy one onclick from being live; the markup no longer exists - the live sheet
is _gbSettings('rules') and the book icon calls it. What survives is two CSS
rules referencing .rules-tab and .rules-close, selectors nothing matches.
Removed. The item was real when written and had been overtaken.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = (u"      +'<div class=\"rnote\">all six dice score: HOT DICE &mdash; +250, roll them all again<br>'\n"
       u"      +'nothing scores: BUST &mdash; the turn&#39;s points are lost</div>';")
if OLD not in s:
    OLD = (u"      +'<div class=\"rnote\">all six dice score: HOT DICE — +250, roll them all again<br>'\n"
           u"      +'nothing scores: BUST — the turn&#39;s points are lost</div>';")
assert s.count(OLD) == 1, 'rules tail matched %d' % s.count(OLD)

s = s.replace(OLD, OLD[:-1] + u"""
      /* YOUR DICE. The brief asks for a "scoring & your dice" sheet and only
         the scoring half existed - nothing taught materials, marks or why
         loadout order matters. Three sections because three is what fits
         without scrolling.
         Every claim below was checked against live code before shipping:
         silver's rollTable is [1,5,1,5,2,3,4,6]; jade's mechanic is
         'wild_quad'; obsidian's is 'shatter_bonus' at 6% for 1000; vanguard_f
         is live and reads G.pool[0] and G.pool[length-1]; and the lane markers
         match the SAME index on the rival's row, which is why this says "the
         same seat on their side" rather than "opposite" - opposite could be
         read as mirrored. */
      +'<div class="sep"></div>'
      +'<div class="ttl">Your dice</div>'
      +'<div class="rnote">Six dice, yours to change. Materials lean the odds '
      +'&mdash; silver rolls <span class="df">1</span>s and <span class="df">5</span>s '
      +'more often, jade turns wild, obsidian shatters for points.</div>'
      +'<div class="sep"></div>'
      +'<div class="ttl">Marks</div>'
      +'<div class="rnote">A branded face banks nothing and does something '
      +'instead. Keep it and the mark fires: coin pays gold, shield softens a '
      +'bust, skull breaks a die.</div>'
      +'<div class="sep"></div>'
      +'<div class="ttl">Order matters</div>'
      +'<div class="rnote">Dice sit in fixed places at the table. Some cards '
      +'read the ends of the row, and some marks reach the same seat on their '
      +'side of the table.</div>';""")

# the orphan CSS - selectors nothing matches since the overlay markup went
for old, new in [
    (u".menu-btn,.rules-tab,.rules-close{transition:transform .06s ease,filter .06s ease}",
     u"/* .rules-tab/.rules-close dropped 2026-08-03 with the dead rules overlay -\n"
     u"   the markup was already gone and these matched nothing. */\n"
     u".menu-btn{transition:transform .06s ease,filter .06s ease}"),
    (u".menu-btn:active,.rules-tab:active,.rules-close:active{transform:scale(.93);filter:brightness(1.3)}",
     u".menu-btn:active{transform:scale(.93);filter:brightness(1.3)}"),
]:
    assert s.count(old) == 1, 'orphan css matched %d: %r' % (s.count(old), old[:40])
    s = s.replace(old, new)

assert s != orig, 'nothing changed'
assert s.count('Your dice') == 1
# STRIP COMMENTS BEFORE ASSERTING - the replacement comment names the selectors
# it removed, so a raw search finds its own prose. P443 already solved this and
# wrote it down; this is the sixth time today the pattern has come up and the
# fix keeps being re-derived instead of reached for. Doing it the settled way.
import re as _re
_code = _re.sub(r'/\*.*?\*/', '', s, flags=_re.S)
assert 'rules-tab' not in _code, 'an orphan .rules-tab selector survives'
assert 'rules-close' not in _code, 'an orphan .rules-close selector survives'
assert 'the seat opposite' not in s, 'the ambiguous wording survives'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P458 applied: three teaching sections + orphan overlay CSS removed')
