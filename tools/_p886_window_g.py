# -*- coding: utf-8 -*-
u"""P886: the three remaining `window.G` guards, two of them player-facing.

G is `let G=null,LO=null;` at top level. A `let` makes a global BINDING and
never a property of window, so `window.G` is undefined for the life of the page
and every guard of the form `window.G&&...` is dead. Measured on a fresh load:
typeof window.G is "undefined" and Object.hasOwnProperty(window,'G') is false,
while the `var` controls window.D3X and window.FKFX are both objects.

SITE A - THE BANK SOUND HAS NEVER PITCHED UP. SFX.bank() scales all three of
its voices with how close the player is to target: 1.15x at 65%, 1.3x at 85%,
1.5x at 95%, plus a fourth harmonic once r reaches 1.3. With r pinned at 1,
every bank in the game - all nine call sites - plays the same flat
520/660/900, and the hot harmonic is unreachable code. Measured through a
wrapped SFX._tone with the real binding set to four progress ratios: shipped
gives an identical triad at 20%, 70%, 88% and 98%; fixed gives 520/660/900,
598/759/1035, 676/858/1170+1287, 780/990/1350+1485. Zero blast radius -
bank() reads G and writes nothing.

SITE B - TAP-TO-FAST-FORWARD HAS NEVER WORKED. A capture-phase pointerdown
listener lets the player tap the board during a rival turn to run the rest of
it at 0.15x. The guard always returns. Measured: with the listener's guard
fixed and a real PointerEvent dispatched inside #screen-match, G._ffMult goes
1 -> 0.15; shipped, it stays 1. The event does reach document capture, so the
guard is the only thing stopping it. _ffMult is read at exactly one place,
_oppDelay, and is set and cleared inside runOppTurn/finOpp, so it cannot leak
across turns and is not serialised into a resume.
THIS ONE IS A BEHAVIOUR CHANGE, not a pure bug fix - it switches on a
documented affordance that has never once run. Noted and NOT acted on: with
it on, _afterOppSettle's MIN=_oppDelay(260) drops to 40ms, which is the window
that covers the 3D layer picking the dice up. That is a pre-existing shape -
the shipped fastRival setting already takes MIN to 104ms - and the honest
statement is that I could not time it on a ~1fps harness, so I have not
changed it. It is written up rather than guessed at.

SITE C - THE SIM'S ISOLATION FAILS TWICE OVER. `var _savedG=window.G;
window.G=null;` was meant to make oppShouldBank neutral during the balance sim.
It cannot: window.G is not the binding, and oppShouldBank reads bare `G` at six
sites, as do _ruleActive and _mendMin behind it. Measured: with G carrying a
sealed MENDING and window.G nulled, oppShouldBank still returned false where a
null G returns true - the isolation observed nothing. Also measured, the cost
when it bites: a console call during a match carrying a sealed mending took
bossWin from ~65% to ~100% and shifted patronWin ~40% to ~50%, both far outside
a +/-6 point noise floor over three repeats; sudden_death and rising_stakes sat
at or just outside it; ordinary matches showed none. From `?sim=1` on a fresh
page G is null anyway and nothing is contaminated, so severity is conditional
exactly as the brief says - but the ladder re-run goes through this path.

The fix is smaller than a flag: _runBalanceSim is a top-level function in the
same scope as the `let`, so assigning `G` there IS the binding, and one
assignment neutralises oppShouldBank, _ruleActive and _mendMin together.
Measured safe: the entire baseline table was produced with the real binding
nulled and returned valid, non-degenerate rows.

try/finally is not optional, and it is placed with care. Making the assignment
real creates a hazard the dead line never had: a throw inside the sim would
leave a LIVE MATCH holding G=null. But every function the sim declares sits
between the old assignment and `var rows=[]`, and only the TIERS_TO_RUN.forEach
actually executes - so the try wraps executable statements only and no function
declaration changes scope. `var rows=[]` stays outside it, so the tail that
consumes rows is untouched.
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


# ── A. the bank sound ────────────────────────────────────────────────
sub(u"""    var r=1;try{if(window.G&&G.target&&G.pPts){var p=G.pPts/G.target;r=p>=0.95?1.5:p>=0.85?1.3:p>=0.65?1.15:1;}}catch(e){}""",
    u"""    /* P886: this guard read a window property that does not exist. G is a
       `let`, so it is a binding and never lands on window - the note at the
       _dropKeptToTray_OLD guard says the same thing - and r was therefore
       pinned at 1 for the life of the page. Every bank in the game played the
       same flat 520/660/900 and the hot harmonic below was unreachable. */
    var r=1;try{if(typeof G!=='undefined'&&G&&G.target&&G.pPts){var p=G.pPts/G.target;r=p>=0.95?1.5:p>=0.85?1.3:p>=0.65?1.15:1;}}catch(e){}""",
    'A the bank pitches with the run again')

# ── B. tap to fast-forward ───────────────────────────────────────────
sub(u"""  if(!(window.G&&G._oppTurnActive))return;""",
    u"""  /* P886: same dead window guard - this affordance has never once run. The
     event does reach document capture; only this line stopped it. */
  if(!(typeof G!=='undefined'&&G&&G._oppTurnActive))return;""",
    'B tap-to-fast-forward can fire')

# ── C. the sim's isolation, made real and made safe ──────────────────
sub(u"""  var _savedG=window.G; window.G=null; /* oppShouldBank guards on G \u2014 neutral during sim */""",
    u"""  /* P886: THE ISOLATION IS REAL NOW, AND IT FAILED TWICE OVER BEFORE.
     `window.G=null` could not neutralise anything - G is a `let`, so window.G
     is not the binding - AND oppShouldBank reads bare `G` at six sites, as do
     _ruleActive and _mendMin behind it, so it would have read the live object
     even if the property had existed. Measured cost when it bites: a console
     call during a match carrying a sealed MENDING took bossWin from ~65% to
     ~100%, far outside a six-point noise floor. From ?sim=1 on a fresh page G
     is null anyway, so nothing was contaminated there.
     Assigning `G` works because this function is in the same scope as the
     declaration, and one assignment covers all three readers at once. The
     assignment is deferred to just above the run, and restored in a finally,
     so that a throw cannot leave a LIVE match holding a null G - a hazard the
     dead line never had, and the reason this is not a one-word change. */
  var _savedG=G;""",
    'C1 the save becomes the binding')

sub(u"""  var rows=[];
  TIERS_TO_RUN.forEach(function(ti){""",
    u"""  var rows=[];
  /* every function above is a declaration; this forEach is the only thing that
     runs, so the try wraps executable statements only and nothing changes
     scope. `rows` stays outside it for the tail that consumes it. */
  G=null;
  try{
  TIERS_TO_RUN.forEach(function(ti){""",
    'C2 null just above the run, inside a try')

sub(u"""  window.G=_savedG;
  try{console.table(rows);}catch(e){}""",
    u"""  }finally{ G=_savedG; }
  try{console.table(rows);}catch(e){}""",
    'C3 restored in a finally')

# ── post-asserts ─────────────────────────────────────────────────────
# STRIP COMMENTS FIRST. Every patch this session that asserted on a bare
# identifier matched the comment it had just written about that identifier -
# eleven times. A claim about the CODE has to be tested against the code.
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
for bad in ('(window.G&&', 'window.G=', '!(window.G'):
    if bad in code:
        sys.exit('a live window.G expression survives: %s (nothing written)' % bad)
if 'window.G' in code:
    sys.exit('window.G still appears in code (nothing written)')
if s.count('var _savedG=G;') != 1 or s.count('}finally{ G=_savedG; }') != 1:
    sys.exit('the sim save/restore is not exactly one pair (nothing written)')
if s.count('  G=null;\n  try{') != 1 and s.count('  G=null;\r\n  try{') != 1:
    sys.exit('the null/try pair is not present exactly once (nothing written)')
# the try must open AFTER the last function declaration in the sim
# SCOPED TO THE SIM. `  G=null;` occurs twice in this file, so a bare index()
# finds the other one and every position check below becomes nonsense.
_sim = s.index('var _savedG=G;')
_open = s.index('  G=null;', _sim)
_rows = s.index('  var rows=[];', _sim)
_lastfn = s.rindex('  function playMatch(', _sim, _open)
if not (_lastfn < _rows < _open):
    sys.exit('the try does not open after the declarations (nothing written)')
# and the finally must close before the tail that reads rows
_fin = s.index('}finally{ G=_savedG; }')
if s.index('window._simRows=rows;') < _fin:
    sys.exit('the finally closes after the tail (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
