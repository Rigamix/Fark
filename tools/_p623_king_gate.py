# -*- coding: utf-8 -*-
"""P623 (Part 1): gate the King callbacks that live OUTSIDE the King pool.

THE BRIEF'S BUG A DOES NOT EXIST. Verified at runtime, not by reading: 2,100
fresh-run draws through _dlgPick, _dlgAmbient and _dlgSay produced ZERO tier-2
lines, with a control proving the probe sees tier-2 200/200 once king_intro is
set. The pool is 48 rows - 7 tier-1 tagged, 41 gated, 0 ungated. Rewiring
_dlgPick, as the brief asks, would have changed nothing that was wrong.

THE SYMPTOM IS REAL AND COMES FROM ELSEWHERE. _dlgSay resolves patron:<key>
BEFORE reaction:king, so a King line inside a PERSONAL pool never meets the gate
at all. Two exist, and both fire as the patron's opening line on a fresh run:
  patron:remny    127/400 runs (32%)  "We spoke of the King's visit already..."
  patron:ferrand  206/400 runs (52%)  "A King wants a game, he can find me..."
Worse, it never self-corrects: _dlgSay records _dlgHeard only for reaction:* rows
or rows carrying a tag, so hearing one of these leaves the heard-set EMPTY - the
run can be told the conversation already happened and still have heard nothing.

FERRAND IS NOT IN THE BRIEF'S CAST. It says to sweep "the other 23 named
patrons"; the build has 29, and the worse of the two offenders is one of the six
the brief never lists. A sweep scoped to the brief's roster would have missed it.

WHY GATING ALONE WOULD HAVE BEEN A NEW BUG. _dlgPick prefers MOST conditions, so
a single conditioned row outranks every unconditioned one in the same pool: once
king_intro is heard, that one line would become the patron's permanent default
and repeat forever. So each gated callback ships with companions at the same
specificity, in the same voice, in distinct sentiment groups - which is also what
lets P621's de-dup vary them.
"""
import io, os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:110]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── the two offenders, gated and grouped ─────────────────────────────────
sub(u'{p:\'patron:remny\',s:0,t:"We spoke of the King\'s visit already, you and I. Or someone did. Might\'ve been you."}',
    u'{p:\'patron:remny\',s:0,c:[\'heard:king_intro\'],g:\'king-callback\','
    u't:"We spoke of the King\'s visit already, you and I. Or someone did. Might\'ve been you."}',
    'P623 remny gated')

sub(u'{p:\'patron:ferrand\',s:0,t:"A King wants a game, he can find me. I don\'t run from crowns any more than blades."}',
    u'{p:\'patron:ferrand\',s:0,c:[\'heard:king_intro\'],g:\'king-callback\','
    u't:"A King wants a game, he can find me. I don\'t run from crowns any more than blades."}',
    'P623 ferrand gated')

# ── companions, so a gated line cannot become a permanent default ────────
COMPANIONS = [
    ('remny', 'king-misremembered',
     "I remember exactly where I was standing when the King news came. Roughly where you are, actually."),
    ('remny', 'king-retold',
     "I've told the King story a dozen times. Some of them even the same way."),
    ('ferrand', 'king-unimpressed',
     "Crown or no crown, a man still sits down and rolls like anybody else."),
    ('ferrand', 'king-unimpressed',
     "They can announce whoever they like at the door. Doesn't change what's on this table."),
]
rows = [u"  {p:'patron:%s',s:0,c:['heard:king_intro'],g:'%s',t:%s}," % (who, g, json.dumps(t))
        for who, g, t in COMPANIONS]

end = s.index('\n];', s.index('var PATRON_LINES=['))
block = (u",\n  /* \u2500\u2500 P623 (Part 1): COMPANIONS FOR THE GATED KING CALLBACKS \u2500\u2500\n"
         u"     Not decoration. _dlgPick prefers MOST conditions, so the two rows\n"
         u"     gated above would each outrank their own patron's unconditioned\n"
         u"     lines and become that patron's ONLY line once king_intro is heard.\n"
         u"     These give the top specificity band something to vary between, and\n"
         u"     their `g` labels let P621's de-dup do the varying. \u2500\u2500 */\n"
         + u"\n".join(rows).rstrip(',') + u"\n")

# the row this lands after has no trailing comma of its own
s = s[:end] + block + s[end:]
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d rows gated, %d companions added' % (n, len(rows)))
