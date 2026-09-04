# -*- coding: utf-8 -*-
u"""P949: _paintForm's fall-through is a silent wrong render. Name the forms.

Denis's instruction, before the table mark is built on this function: it
implements only `crust` and `veil` and SILENTLY PAINTS A RIM for anything else,
so a table mark - which is neither - would render as something plausible and
wrong. "The first render will look deliberate and be wrong."

That is a worse failure than a crash, because it is a failure that reviews
cleanly. The audit that found it also found the header comment above the
function announcing "THE FOUR FORMS" and describing DIM as a fill, when there is
no dim branch at all: the code has been one form short of its own documentation
for as long as both have existed.

THE VOCABULARY IS EXACTLY THREE and this patch does not widen it. Counted rather
than assumed: six MARKS rows (rim x3 - card, sel, reroll; crust x2 - frozen,
damp; veil x1 - blind) plus two literal calls from the beat loop ('rim' at 28104,
'veil' at 28106), and the only other caller passes g.style straight from a roster
row. So `rim` becomes an explicit branch and anything else is an error.

WHY IT LOGS AS WELL AS THROWS, and this is the part worth reading. tick() wraps
_drawGlow and _drawStates in bare try{}catch(e){}, so a throw raised inside the
paint pass is SWALLOWED - a bare throw would convert a silent wrong render into
a silent absent one, which is not obviously an improvement and is harder to
diagnose. The console.error is therefore the signal that actually reaches a
human: it is what surfaced P946's ReferenceError in a probe run, via shoot.js's
page-error stream. The throw is still raised, because _paintForm is also called
directly (28104/28106) and from probes, where it does propagate.

Deduped per style, because this sits in a per-frame pass: one bad row would
otherwise write sixty identical lines a second and bury everything else in the
console, which is its own way of hiding a fault.
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


sub(u"""    this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM,undefined,opt());
  },""",
    u"""    /* P949: RIM IS A NAMED FORM, NOT THE FALL-THROUGH. It reached _paintHalo
       by being the last statement in the function, which meant every
       unrecognised style reached it too and painted a plausible ring instead of
       failing. A wrong render that looks deliberate is worse than a crash: it
       reviews cleanly and ships. */
    if(style==='rim'){
      this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM,undefined,opt());
      return;
    }
    /* THE CONSOLE LINE IS THE SIGNAL, NOT THE THROW. tick() wraps _drawGlow and
       _drawStates in bare try{}catch(e){}, so a throw raised inside the frame
       pass is swallowed whole - on its own it would trade a silent wrong render
       for a silent absent one. The error is logged so it reaches a human (it is
       how P946's ReferenceError surfaced, through shoot.js's page-error
       stream), and thrown as well because _paintForm is called directly by the
       beat loop and by probes, where it does propagate.
       Deduped per style: this is a per-frame pass, and sixty identical lines a
       second is another way of hiding a fault. */
    var _pfBad=(this._badForms||(this._badForms={}));
    if(!_pfBad[style]){
      _pfBad[style]=1;
      try{console.error('D3X._paintForm: unknown style '+JSON.stringify(style)+
        ' - the forms are rim, crust and veil. Nothing was painted for it.');}catch(e){}
    }
    throw new Error('_paintForm: unknown style '+style);
  },""",
    '1 rim is named and the default fails')

# ── post-asserts, against code with the comments stripped ──────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# THE ASSERTS ARE SCOPED TO _paintForm'S BODY. The first version counted
# occurrences file-wide and died on style==='veil', which also appears in
# _fxMark's dispatch (`style==='veil'?'flash':'glow'`) - a check searching a
# space far wider than its claim, which is the family this file keeps recording.
# The region is the unit; the token is not.
_pfStart = code.index('_paintForm:function(')
_pfEnd = code.index('_markPlan:function(', _pfStart)
body = code[_pfStart:_pfEnd]
# the three forms are all reachable by name, INSIDE the function that dispatches
for form in ("style==='crust'", "style==='veil'", "style==='rim'"):
    if body.count(form) != 1:
        sys.exit('%s is not a single named branch inside _paintForm '
                 '(nothing written)' % form)
# and there is no longer an unguarded tail call
if not re.search(r"if\(style==='rim'\)\{\s*this\._paintHalo", body):
    sys.exit('rim does not paint through _paintHalo (nothing written)')
if 'throw new Error(\'_paintForm: unknown style ' not in body:
    sys.exit('the default does not fail (nothing written)')
# EVERY STYLE THE FILE ACTUALLY PASSES MUST BE ONE OF THE THREE, or this patch
# breaks a live caller. Checked by extracting them rather than by trusting the
# count in the docstring.
styles = set(re.findall(r"style:'([a-z]+)'", code))
lits = set(re.findall(r"_paintForm\('([a-z]+)'", code))
unknown = (styles | lits) - {'rim', 'crust', 'veil'}
if unknown:
    sys.exit('these styles would now throw: %s (nothing written)' % sorted(unknown))
if not styles or not lits:
    sys.exit('the style scan found nothing - the regex has gone stale, and an '
             'empty search space cannot clear anything (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s); styles in play: %s' %
      (len(edits), ', '.join(edits), sorted(styles | lits)))
