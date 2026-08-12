# -*- coding: utf-8 -*-
"""P634: the ROLL button's sideways jump, found at last, and it was never the pivot.

Denis, twice. First: "when I bank and pass my turn to the npc, the bank button
slides to the left side for no reason before settling back ... probably as you
changed the pivot point." Then, after two attempts at it: "Roll button still
jitters to the side."

P599 set transform-origin on both match buttons; P601 took it off again and held
the margins with a companion translate. Neither touched the cause, and the
handover said in as many words: do not guess a third mechanism, get a repro.

THE REPRO (tools/apv_roll_jitter_control.js). Calling restoreRollButton() - the
function the bank path calls - moves the ROLL button's left edge from 21.1px to
-109.8px. A HUNDRED AND THIRTY-ONE PIXELS off the left of a 430px screen, a
third of the width. The transform it wears while it happens, read off the live
element: matrix(1.04, 0, 0, 1.04, -125.859, 0).

THE CAUSE is one stale declaration in @keyframes rollBounce, read straight from
the built stylesheet:
    0% translateX(-50%) scale(1.04) | 100% translateX(-50%) scale(1)
That translateX is left over from when #btnRoll was absolutely positioned and
centred with the classic left:50% + translateX(-50%) pair. It is not centred
that way any more - the rule says so explicitly: `position:relative;left:auto;
transform:none`. So the compensating half-width shift has had nothing to
compensate for, and every time the bounce plays it drags the button a half-width
left and snaps it back 150ms later. -125.859px is exactly half of the button's
measured 251.7px width.

WHY IT IS INTERMITTENT, and why a probe that drove a REAL bank measured zero
travel across 151 samples before this control was run. #btnRoll.disabled
declares `transform:none !important`, and an !important author declaration
outranks an animation - measured as its own arm: with .disabled on, the same
animation moves the button 0px and computes to `none`. So whether Denis sees the
jump depends on whether anything re-disables the button inside those 150ms,
which is a race with code that has nothing to do with it. That is the whole
character of the bug he is describing, and it is why a single clean measurement
was not evidence of anything.

THE FIX IS TO DELETE THE STALE HALF, not to add a counter-anything. The bounce
is a scale pop; the translate was never part of the idea.

AND THE SAME STALE IDIOM SITS IN .match-btn-roll:active. It is outranked today by
#btnRoll:active, which is why it does not fire - a specificity accident, one
selector edit away from being the same 131px jump on every press. Removed with
it rather than left as a trap.

#btnRoll.disabled's `transform:none !important` STAYS. It was masking this, but
it is also what stops a disabled button showing a press state, which is correct.
Noted here so the next person knows it is load-bearing for a second reason.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── 1. the keyframe ──────────────────────────────────────────────────────
sub(u"/* \u2500\u2500\u2500 Roll bounce-back \u2500\u2500\u2500 */\n"
    u"@keyframes rollBounce{\n"
    u"  0%{transform:translateX(-50%) scale(1.04)}\n"
    u"  100%{transform:translateX(-50%) scale(1)}\n"
    u"}",
    u"/* \u2500\u2500\u2500 Roll bounce-back \u2500\u2500\u2500\n"
    u"   P634: THE translateX(-50%) IS GONE, and it is the whole of Denis's \"roll\n"
    u"   button jitters to the side\". It was the other half of a left:50% centring\n"
    u"   #btnRoll stopped using long ago - the rule now reads position:relative;\n"
    u"   left:auto;transform:none - so the compensating shift had nothing left to\n"
    u"   compensate for and simply dragged the button a half-width left for the\n"
    u"   150ms the bounce played. Measured: left edge 21.1px -> -109.8px, a 131px\n"
    u"   lunge off a 430px screen, with matrix(1.04,0,0,1.04,-125.859,0) on the\n"
    u"   element - and 125.859 is exactly half its 251.7px width.\n"
    u"   Intermittent because #btnRoll.disabled carries `transform:none !important`,\n"
    u"   which outranks an animation: whether the jump is seen depends on whether\n"
    u"   something re-disables the button inside those 150ms. A probe that drove a\n"
    u"   real bank measured 0px across 151 samples for exactly that reason.\n"
    u"   The bounce is a scale pop. That is all it ever was. */\n"
    u"@keyframes rollBounce{\n"
    u"  0%{transform:scale(1.04)}\n"
    u"  100%{transform:scale(1)}\n"
    u"}",
    'P634 rollBounce loses the stale centring')

# ── 2. the same idiom, one specificity accident from firing ──────────────
sub(u".match-btn-roll:active{transform:translateX(-50%) scale(.98)}",
    u"/* P634: the same stale centring as @keyframes rollBounce. It does not fire\n"
    u"   today only because #btnRoll:active outranks it - an accident, not a plan,\n"
    u"   and one selector edit from being the same 131px jump on every press. */\n"
    u".match-btn-roll:active{transform:scale(.98)}",
    'P634 the :active twin')

# ── 3. say why the !important that masked it is staying ──────────────────
sub(u"#btnRoll.disabled{transform:none !important}",
    u"/* P634: LOAD-BEARING TWICE. It stops a disabled button showing a press\n"
    u"   state, which is the reason it exists - and it also outranks animations,\n"
    u"   which is why rollBounce's stale translate was invisible on some bank paths\n"
    u"   and a 131px lunge on others. The translate is fixed at its source; this\n"
    u"   stays for its real job. */\n"
    u"#btnRoll.disabled{transform:none !important}",
    'P634 note the masking rule')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
