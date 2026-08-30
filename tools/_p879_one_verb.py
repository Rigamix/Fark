# -*- coding: utf-8 -*-
u"""P879 (FX BRIEF, the two amendments at the head of Part Six): three verbs
become two, and the cardmark's cost argument stops depending on a timer that
one of its callers does not set.

AMENDMENT 1 - SNARE'S MISS IS _lmSpend, AND _lmRetire THEN HAS NO CALLERS.
"A due mark costs an attempt" IS _lmSpend. At turns:1 it is identical to
retiring, and it survives snare ever being given a second attempt. Once the
miss uses it the hit should too, and the whole branch collapses: all three lane
marks now spend once, unconditionally, inside their due block. Fog, snuff and
snare finally do the same thing.

THREE COMMENTS ARGUED FOR THE SPLIT AND ALL THREE ARE UPDATED, because a
deleted function that three comments still recommend is worse than the function
itself. One of them had become flatly false: "Giving Snare a shared _lmSpend
would hand it a second turn - the exact wager its own comment says it must not
have." It would not. _lmSpend decrements first, and snare arms with turns:1, so
1-1=0 and the mark dies on the spot. The fear was real under the old reading of
`turns` as a lurk window; under attempts it cannot happen.

The effect bus at 14901 cites the split to justify `claim` being a verb rather
than a number. That argument is still right - deadRoll's two outcomes really
are a decision, not a quantity - so only the illustration changes. It now
points at the pair that survives.

AMENDMENT 2 - THE CARDMARK'S COST ARGUMENT IS PER-FRAME, NOT PER-DURATION.
P876's comment justified widening the wake condition by calling the mark
transient - "its whole 900ms". That is true of Steady Hand's pick and false of
_breakBegin, which adds `cardmark` to every candidate with NO timer at all: a
Break prompt paints for exactly as long as the player deliberates, which may be
a minute. The bound that actually holds is the one 27085 makes about shape
count - a thin hull on an otherwise empty surface - and it holds however long
the mark lives. Establishing it now matters because the state layer is next and
states are long-lived by definition; it cannot inherit an argument about
transience.
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


# ── 1. snare: one spend, hit or miss, like the other two ─────────────
sub(u"""          var _snX2=!!G._snare.x2;
          total=Math.floor(total/(_snX2?4:2));/* Kindred halves it twice */
          _lmRetire('_snare');
          try{famLog('THE SNARE BITES \u2014 '+(_snX2?'HALVED TWICE':'HALVED'));}catch(e){}
          try{setStatusMsg('YOUR SNARE CATCHES THEM \u2014 '+(_snX2?'A QUARTER':'HALF'),'gold');}catch(e){}
        }else{
          /* P878: THE MISS, which the comment above this block has promised
             since it was written - "the mark then clears whether it fired or
             not" - and which the code never did. Retiring only on the hit left
             a missed snare live:true with `turn` pointing at the turn that had
             just passed, and _lmDue tests turn===oppTurnCount: live for ever,
             due never. Snare arms with turns:1 and its Kindred halves twice on
             one shot rather than buying a second attempt, so retiring and
             spending the last attempt are the same act here. */
          _lmRetire('_snare');
        }
      }""",
    u"""          var _snX2=!!G._snare.x2;
          total=Math.floor(total/(_snX2?4:2));/* Kindred halves it twice */
          try{famLog('THE SNARE BITES \u2014 '+(_snX2?'HALVED TWICE':'HALVED'));}catch(e){}
          try{setStatusMsg('YOUR SNARE CATCHES THEM \u2014 '+(_snX2?'A QUARTER':'HALF'),'gold');}catch(e){}
        }
        /* P879: ONE SPEND, HIT OR MISS - the same line fog and snuff carry,
           so all three lane marks finally do the same thing. The block above
           used to retire on the hit and (P878) retire again on the miss, which
           is two ways of writing one act. A due mark costs an attempt: snare
           arms with turns:1, so spending it is what clears it, and the comment
           this block has always carried - "the mark then clears whether it
           fired or not" - is now what the code does. */
        _lmSpend('_snare');
      }""",
    '1 snare spends like the others')

# ── 2. the verb with no callers ──────────────────────────────────────
sub(u"""/* CONSUMED - for an effect whose HIT uses the whole window at once, whatever
   its count said. Distinct from _lmSpend, which charges one attempt.
   P878: THIS COMMENT USED TO PRESENT SNARE AS THE CONSIDERED PATTERN - "it
   retires inside the branch where it actually halved something" - and that
   reading is what sent P876 to make fog and snuff match it. Snare was not the
   template; it was the one missing its miss case. A due mark ALWAYS costs an
   attempt. Snare calls this on both paths because it arms with a single
   attempt, so consuming the window and spending its last attempt coincide. */
function _lmRetire(key){var m=G&&G[key];if(m)m.live=false;}""",
    u"""/* P879: _lmRetire is DELETED, as _lmDefer was. It expressed "this hit used the
   whole window whatever the count said", and under the attempts ruling no hit
   does: fog and snuff bought two FIRINGS with Kindred, so a hit must not
   consume the rest, and snare's window is one attempt, so spending it and
   consuming it are the same act. Three verbs became two - arm, due, spend -
   and the machinery is done. */""",
    '2 the retire verb deleted')

# ── 3. the paragraph that argued the split, now false ────────────────
sub(u"""   RETIREMENT IS NOT SHARED, deliberately. Snare is ONE turn and is consumed on
   the bite: it clears inside the branch where it actually halved something, and
   its one-turn window is enforced by the gate rather than by clearing. Fog and
   Snuff run for `turns` turns and re-arm. Giving Snare a shared _lmSpend would
   hand it a second turn - the exact wager its own comment says it must not
   have ("until it fires tested at 97.7% inside six turns, which is not a bet").""",
    u"""   P879: RETIREMENT IS SHARED NOW, and the paragraph that stood here was
   FALSE by the end. It said "giving Snare a shared _lmSpend would hand it a
   second turn - the exact wager its own comment says it must not have". It
   would not: _lmSpend decrements before it tests, and Snare arms with turns:1,
   so 1-1=0 and the mark dies on the spot. The fear was real while `turns` was
   read as a window the mark lurks in; under the ruling it counts ATTEMPTS, and
   one attempt spent is one mark gone. All three now spend once per due turn.""",
    '3 the false paragraph')

# ── 4. the effect bus keeps its point, loses its example ─────────────
sub(u"""  /* CLAIM IS A DECISION, NOT A QUANTITY. deadRoll has two outcomes - the turn
     continues or it ends - and encoding that as a number would mean choosing a
     sentinel that every future claiming card has to know. Same argument as
     Snare's _lmRetire being separate from _lmSpend: a distinct outcome earns a
     distinct verb rather than an overloaded one. */""",
    u"""  /* CLAIM IS A DECISION, NOT A QUANTITY. deadRoll has two outcomes - the turn
     continues or it ends - and encoding that as a number would mean choosing a
     sentinel that every future claiming card has to know. A distinct outcome
     earns a distinct verb rather than an overloaded one.
     P879: the illustration used to be Snare's _lmRetire against _lmSpend. That
     pair is gone - the ruling collapsed the two outcomes it named into one act
     on the marker - so the example now points at the pair that survives:
     _lmArm and _lmSpend are placing a mark and charging it, which really are
     two things. The argument for `claim` is unaffected; only the example
     needed replacing, and an example that no longer exists is worse than
     none. */""",
    '4 the illustration replaced')

# ── 5. the cardmark's cost argument stops depending on a timer ───────
sub(u"""        /* P876: A CARD MARK WAKES THIS TOO. The guard tested `selected` alone,
           and Steady Hand's pick CLEARS selected before it adds the mark - so
           unless some other die happened to be selected, P856's mark was a
           class on an element and nothing else for its whole 900ms. P856 moved
           the mark onto a painter that refuses to run in the state P856's own
           call site creates. */""",
    u"""        /* P876: A CARD MARK WAKES THIS TOO. The guard tested `selected` alone,
           and Steady Hand's pick CLEARS selected before it adds the mark - so
           unless some other die happened to be selected, P856's mark was a
           class on an element and nothing else. P856 moved the mark onto a
           painter that refuses to run in the state P856's own call site
           creates.
           P879: THE COST ARGUMENT IS PER-FRAME, NOT PER-DURATION. This comment
           used to call the mark transient and cite its own timeout, and that
           is only true of Steady Hand's pick. _breakBegin adds `cardmark` to every
           candidate with NO timer, so a Break prompt paints for as long as the
           player deliberates. What actually bounds the cost is the same thing
           the note below says about the selection glow: one thin hull on an
           otherwise empty surface, which holds however long the mark lives.
           The state layer is built on this next, and states are long-lived by
           definition - so it must not inherit an argument about transience. */""",
    '5 the cost argument corrected')

# ── post-asserts ─────────────────────────────────────────────────────
if '_lmRetire' in s.replace('_lmRetire is DELETED', '').replace(
        "Snare's _lmRetire against _lmSpend", '').replace(
        'used to be Snare\'s _lmRetire', ''):
    _left = [l.strip()[:90] for l in s.split('\n') if '_lmRetire' in l]
    sys.exit('_lmRetire still referenced x%d (nothing written):\n  %s'
             % (len(_left), '\n  '.join(_left[:4])))
if s.count("_lmSpend('_snare')") != 1:
    sys.exit('snare spends from %d places, expected 1 (nothing written)'
             % s.count("_lmSpend('_snare')"))
for k in ("_lmSpend('_fog')", "_lmSpend('_snuff')"):
    if s.count(k) != 1:
        sys.exit('%s is not exactly once (nothing written)' % k)
if '900ms' in s[s.index('A CARD MARK WAKES THIS TOO'):s.index('A CARD MARK WAKES THIS TOO')+2000]:
    sys.exit('the duration argument survives in the cardmark comment (nothing written)')
if 'RETIREMENT IS NOT SHARED' in s:
    sys.exit('the false paragraph survives (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
