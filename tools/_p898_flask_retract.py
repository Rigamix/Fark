# -*- coding: utf-8 -*-
u"""P898: item 0's premise is wrong, it was my error, and the real question
underneath it is a timing one.

WHAT I CLAIMED, in P896's notes, labelled "measured": that activateGrogsFlask
never sets `d.roll`, so the flask reroll has no tumble in 3D and the beat
decorates a jump cut. I read the chain - _setDieVal writes d.val, the CSS
animation:dRoll was spinning an invisible chip - and wrote it down as a
measurement. It was a reading. Denis promoted it to open item 0 on that word.

WHAT IS ACTUALLY THERE. _setDieVal calls reDrawDieFace, which for a `_d3` die
calls D3.roll(..., {dur:420}), which calls D3X._physQueue whenever the die's
group is 'match' - the same entry an ordinary roll uses. Driven on a real match
die: d.roll appears 63ms later and the solution is 1017 frame-milliseconds of
flight, against 1433 for an ordinary roll. The flask tumbles, and it tumbles
through the shipped physics.

THE REAL QUESTION IS THE ONE THE WRONG CLAIM WAS STANDING ON. §18 budgets the
whole card reroll at 400ms and puts the value change at +210. The die is in the
air for about a second. The envelope this file ships ends at 580ms - roughly
440ms BEFORE the die lands - so the rim decorates the throw and is gone by the
time the face is readable. That is a change to the sheet, not a dial, so the
numbers are left exactly as authored and the discrepancy is written where the
shape is defined rather than guessed at.

ONE COMMENT, AT THE SHAPE. All four reroll sites share BEAT_ENV.reroll and all
four route through the same flight, so the note belongs at the definition. Four
copies beside four call sites is the hand-maintained roster this brief keeps
deleting, and a comment only ever documents its own site.

THE DESIGN DECISION P896 MADE IS UNCHANGED AND NOW ACTUALLY SUPPORTED. I argued
beats must not be roll-gated because the card-reroll beat plays during the
re-throw, and then undercut it with an aside saying `_rolling()` was false there
anyway. The aside was wrong in the direction that strengthens the argument:
d.roll IS set, `_rolling()` IS true, and a `through:false` roll gate would have
deleted the first beat in the sheet.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def sub(path, old, new, label):
    s = io.open(path, encoding='utf-8', newline='').read()
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    io.open(path, 'w', encoding='utf-8', newline='').write(
        s[:m.start()] + rep + s[m.end():])
    edits.append(label)


PAGE = os.path.join(ROOT, 'fark_proto.html')

sub(PAGE,
    u"""  /* §18's card-reroll sheet, as a shape: 100ms in, hold, 200ms out. The
     stagger and the +140 wind-up are per-die and passed as `delay`. */
  BEAT_ENV:{reroll:{'in':100,hold:140,out:200}},""",
    u"""  /* §18's card-reroll sheet, as a shape: 100ms in, hold, 200ms out. The
     stagger and the +140 wind-up are per-die and passed as `delay`.
     P898 - MEASURED AND MISTIMED, and left as authored rather than guessed
     at. The sheet budgets the whole card reroll at 400ms with the value
     changing at +210, which reads as a die that snaps to its new face. It
     does not: _setDieVal calls reDrawDieFace, which calls D3.roll, which
     calls _physQueue - the same entry an ordinary roll uses - and the
     solution is 1017 frame-milliseconds of flight against 1433 for an
     ordinary roll. So this envelope is over at 580ms, about 440ms before the
     die lands, and the rim decorates the throw rather than the result.
     All four reroll sites share this shape and all four take that flight, so
     the note is here rather than copied beside each of them.
     Re-timing it is a change to the sheet, which is Denis's - see OPEN.md. */
  BEAT_ENV:{reroll:{'in':100,hold:140,out:200}},""",
    'the shape carries the discrepancy')

sub(PAGE,
    u"""    /* §18's sheet exactly: the card fires, then die 1 winds up at +140 and
       die 2 at +210. settleDie stays on its own timer - it is the flat path's
       landing, not part of the beat. */""",
    u"""    /* §18's stagger: die 1 winds up at +140, die 2 at +210. The envelope's
       own timing is under question - see BEAT_ENV.reroll. settleDie stays on
       its timer: it is the flat path's landing, not part of the beat. */""",
    'the flask comment stops claiming the sheet is met')

# ── OPEN.md: retract, and put the real question in its place ────────
DOC = os.path.join(ROOT, 'docs', 'OPEN.md')
s = io.open(DOC, encoding='utf-8', newline='').read()
anchor = u'## Which canvas does a beat'
i = s.find(anchor)
if i < 0:
    sys.exit('could not find the canvas entry to insert before (nothing written)')

NEW = u"""## Item 0 is my mistake — the flask DOES tumble. The real question is timing

**Retracting it plainly:** I wrote that `activateGrogsFlask` never sets
`d.roll`, and I labelled it *measured*. It was a reading. You promoted it to
open item 0 on that word, so the correction is mine to make loudly.

`_setDieVal` → `reDrawDieFace` → `D3.roll(…, {dur:420})` → `D3X._physQueue`
whenever the die's group is `match` — the same entry an ordinary roll uses.
Driven on a real match die: `d.roll` appears **63 ms** later and the solution is
**1017 frame-ms of flight**, against **1433** for an ordinary roll. Same
physics, slightly shorter throw. The instrument's control is the ordinary roll
in the same run, so the positive is not an instrument artefact.

**What the wrong claim was standing on is a real conflict, and it survives.**
§18 budgets the whole card reroll at 400 ms and puts the value change at +210.
The die is in the air for about a second. The envelope now shipping ends at
580 ms — roughly **440 ms before the die lands** — so the rim decorates the
throw and is gone by the time the face is readable.

*Recommendation: anchor the reroll rim to the settle rather than to a clock,
which §16 already asks for — "anchor everything to the roll".* But that makes
its end **condition-bound**, and by your new rule that makes it a `MARKS` row,
not an `FX_MARKS` entry: *"this die is being re-thrown"* is a state with a
predicate (`d.roll`), a duration set by the flight, and `through:true` by
necessity.

**And the per-firing ink objection does not apply to this one.** It was the
reason beats could not be rows — one die, two overlapping firings, one ink
slot. A die is in exactly one flight at a time, so the condition is exclusive
and a per-die ink is well defined here. That is either a neat consequence of
your rule or the first crack in it, and I would rather you looked at it than
have me pick.

*The alternative is to re-time the sheet to the flight — rim in at +140, hold
until the die settles, fade over 200. Same look, no new row.* I have changed
nothing: the numbers are as you authored them and the discrepancy is recorded
at `BEAT_ENV.reroll`.

---

"""

s = s[:i] + NEW + s[i:]
if s.count('Item 0 is my mistake') != 1:
    sys.exit('the retraction is not present exactly once (nothing written)')
io.open(DOC, 'w', encoding='utf-8', newline='').write(s)
edits.append('the OPEN.md retraction')

# ── post-asserts on the page ────────────────────────────────────────
code = re.sub(r'/\*.*?\*/', '', io.open(PAGE, encoding='utf-8', newline='').read(),
              flags=re.S)
if "BEAT_ENV:{reroll:{'in':100,hold:140,out:200}}" not in code:
    sys.exit('the authored envelope changed - it must not (nothing written, '
             'but the page may already be edited)')
if code.count('_dieBeat(') - 1 != 18:
    sys.exit('a call site moved (nothing written, page may already be edited)')

print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
