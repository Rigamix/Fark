# -*- coding: utf-8 -*-
u"""P900: the tag cannot be derived - measured - so its cost is written at the
row; and `env`'s no-caller note moves to the definition.

I WENT LOOKING FOR THE SEAM AND THERE ISN'T ONE. Three candidates, each
checked rather than assumed:

  A card-resolving flag. There is none - `_activeCard` at 44104 is a local in
  boss-card code and nothing else claims the idea. Adding one would not work
  either: the flight starts about 60ms AFTER activation returns (measured in
  P898 - d.roll appears at 63ms), so a flag true only during the synchronous
  activation is false by the time there is a flight to attribute, and a flag
  left set past it would attribute the next ordinary roll.

  A cause carried to the flight. D3.roll IS the universal entry - it is the
  only caller of _physQueue - but it takes no cause, and the deal uses it too
  (five call sites: the deal at dur 560, reDrawDieFace at 420, and three
  others). "This die is in flight" is countable there; "a card put it there"
  is not.

  _setDieVal, which is the seam Denis names for value changes, and it already
  covers five of the seven. The other two - sleight, both seats - set d.val
  directly and call reDrawDieFace, and that bypass is deliberate: _setDieVal
  fires famTableChanged, which runs _steadyDisarm and _clearRollForces, and
  those two sites run inside the deal loop where the roll-scoped buffers
  (P811's peek lanes, the honeytrap marks) are still being consumed. Routing
  them through it would change behaviour well beyond the mark.

So seven sites is the honest cost, and it is now stated at the row - along
with the census that finds an eighth, which is the part that actually helps:
every in-place value change is either a `_setDieVal(` (6 calls) or a
`reDrawDieFace(` (25). A reroll path that is not in that union does not exist.

AND THE `env` NOTE MOVES TO THE DEFINITION. It was recorded in the BEAT_ENV
tombstone, which is a different place - a comment documents only its own site,
and the next reader arrives at _beatAlpha. In Denis's form, so the intent is
reconstructible rather than inferred: what, since when, kept for what, and the
condition under which it goes.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ══ 1. the row states its own census ═══════════════════════════════
sub(u"""       UNDER, like every state - a state is part of the table and is occluded
       by the dice. Only beats sit on top. */
    {id:'reroll',layer:'under',through:true,style:'rim',fallback:'#ffb428',""",
    u"""       UNDER, like every state - a state is part of the table and is occluded
       by the dice. Only beats sit on top.

       SEVEN CALL SITES, AND NO SEAM - which is the same shape as the defect
       this row was built out of, so it is stated rather than left to be
       rediscovered. §9's censuses count MARKERS, not mechanics: `card-reroll`
       was added at four sites and missed Steady Hand, Powder Keg and
       Quicksilver, under-reporting the reroll scope by 43%. A class census is
       only safe where a canonical seam exists - _setDieVal for a value change,
       _removeDieAt for a removal - because then every path goes through it.
       Three candidates were checked for this tag and none works:
         no card-resolving flag exists, and one would not help - the flight
           starts ~60ms AFTER activation returns (P898 measured d.roll at 63ms),
           so a flag true only during activation is false when there is
           something to attribute, and one left set would claim the next roll;
         D3.roll is the universal flight entry - the only caller of _physQueue
           - but carries no cause and the deal uses it too;
         _setDieVal covers five of the seven, but sleight (both seats) bypasses
           it deliberately: it fires famTableChanged, whose _clearRollForces
           would eat the roll-scoped buffers those two sites run inside.
       SO: seven sites, and here is how to find an eighth. Every in-place value
       change in this file is a `_setDieVal(` or a `reDrawDieFace(` call. Any
       reroll outside that union does not exist; any inside it without a
       _dieReroll beside it is an unmarked one. */
    {id:'reroll',layer:'under',through:true,style:'rim',fallback:'#ffb428',""",
    '1 the row states its census')

# ══ 2. env's note moves to its definition ══════════════════════════
sub(u"""  /* the beat's alpha at `now`, which is the only thing `delay` and `env`
     change. Returns 0 before the delay elapses, so an armed-but-not-yet-due
     beat costs a hull and nothing else. */
  _beatAlpha:function(mk,now){""",
    u"""  /* the beat's alpha at `now`, which is the only thing `delay` and `env`
     change. Returns 0 before the delay elapses, so an armed-but-not-yet-due
     beat costs a hull and nothing else.
     `env` HAS NO CALLER as of P899, when BEAT_ENV.reroll went with the beats
     it timed. Kept for §18's remaining sheeted shapes - moment 2's 120ms
     brand-landing rim-in, the miss, and the lane mark's fade - each of which
     specifies an in/hold/out. DELETE IT IF THOSE LAND WITHOUT IT. Written here
     rather than at the tombstone because a comment documents only its own
     site, and this is the site. */
  _beatAlpha:function(mk,now){""",
    '2a env, at its definition')

sub(u"""     the wrong fix, because the mark is a state whose end is the flight's end.
     The `env` parameter on _fxMark stays and currently has NO CALLER. That is
     said plainly rather than left to be found: §18 sheets three more shapes
     that want an in/hold/out - moment 2's 120ms rim-in, moment 4's lane veil,
     the miss - and deleting a tested evaluator to re-add it next patch is
     churn. If none of them wants it, it should go. */""",
    u"""     the wrong fix, because the mark is a state whose end is the flight's end.
     The `env` parameter it fed is still on _fxMark; its no-caller note lives
     at _beatAlpha, which is where it is read. */""",
    '2b the tombstone points at it')

# ── post-asserts, comments NOT stripped: these ARE comments ─────────
if s.count('SEVEN CALL SITES, AND NO SEAM') != 1:
    sys.exit('the row census note is not present exactly once (nothing written)')
if s.count('`env` HAS NO CALLER as of P899') != 1:
    sys.exit('the env note is not at its definition exactly once (nothing written)')
# the note must sit with _beatAlpha, not somewhere that merely mentions it
_note = s.index('`env` HAS NO CALLER')
_def = s.index('_beatAlpha:function')
if not (0 < _def - _note < 700):
    sys.exit('the env note is not adjacent to _beatAlpha (nothing written)')
# and the old copy must be gone, or there are two notes to keep in step
if s.count('The `env` parameter on _fxMark stays') != 0:
    sys.exit('the tombstone still carries its own copy of the note '
             '(nothing written)')

# the census the comment claims must be the census the file has
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
counts = {k: code.count(k) - 1 for k in ('_setDieVal(', 'reDrawDieFace(',
                                         '_dieReroll(')}
if counts['_dieReroll('] != 7:
    sys.exit('%d reroll sites, the comment says seven (nothing written)'
             % counts['_dieReroll('])
if counts['_setDieVal('] != 6 or counts['reDrawDieFace('] != 25:
    sys.exit('the census in the comment is stale: _setDieVal %d, reDrawDieFace '
             '%d (nothing written)' % (counts['_setDieVal('],
                                       counts['reDrawDieFace(']))
# every reroll site must sit inside that union, which is what makes it a census
for mm in re.finditer(r'_dieReroll\(', code):
    if code[max(0, mm.start() - 9):mm.start()] == 'function ':
        continue
    after = code[mm.end():mm.end() + 300]
    if '_setDieVal(' not in after and 'reDrawDieFace(' not in after:
        sys.exit('a reroll site is outside the census union the comment names '
                 '(nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
print('census as shipped: _setDieVal %d, reDrawDieFace %d, _dieReroll %d'
      % (counts['_setDieVal('], counts['reDrawDieFace('], counts['_dieReroll(']))
