# -*- coding: utf-8 -*-
u"""P884c: moment 2 never fired because `window.G` is permanently undefined.

G is declared `let G=null,LO=null;` (30882). A `let` at top level creates a
global BINDING but not a property on window, so `window.G` is undefined for the
life of the page. The guard read

    var p=(window.G&&G.pool)||[];

which short-circuits on the first term every single time, hands back an empty
array, finds no game die and returns false. The beat was unreachable on both
settle exits, which is why P884b - correct in itself, since the watchdog really
is a second exit and really did need the call - changed nothing measurable.

THE FILE ALREADY KNEW. _dropKeptToTray_OLD (31018) carries the note verbatim:
"G is a `let`, so it is NOT on window - `window.G` is undefined here and the
whole migration silently no-opped", and its guard is the idiom this now uses.
That is the third time in this run that a comment recorded the hazard before I
walked into it - the other two being the watchdog's "two exits, one payload"
and P821's world-up axis. Reading the neighbours is cheaper than measuring.

THREE MORE SITES HAVE THE SAME DEAD GUARD and are NOT touched here, because
each changes behaviour and none is FX work:
  - 12561  `window.G&&G.target&&G.pPts` gates a pressure ratio, so the ratio is
           permanently 1 and never takes its 1.15 / 1.3 / 1.5 steps.
  - 46902  `if(!(window.G&&G._oppTurnActive))return;` always returns early.
  - 46654 / 46877 save and restore `window.G` around the sim to make
           oppShouldBank neutral; they are writing a property nothing reads,
           so the intended neutralisation does not happen.
They are written up for Denis rather than fixed in a patch about beats: 46902
returning early may well be load-bearing by accident, and that is a decision
about behaviour, not a typo.
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


sub(u"""  _landed:function(d){
    if(!d||!d.match||!d.chip)return false;
    if(!window.FKFX||typeof _dieIsIcon!=='function')return false;
    try{
      var p=(window.G&&G.pool)||[],g=null;""",
    u"""  _landed:function(d){
    if(!d||!d.match||!d.chip)return false;
    if(!window.FKFX||typeof _dieIsIcon!=='function')return false;
    try{
      /* P884c: NOT window.G. G is a `let` (30882), so it is a global binding
         and not a property of window - `window.G` is undefined for the life of
         the page, and the guard that used it short-circuited every time,
         handed back an empty array and made this whole beat unreachable. The
         same note is already at 31018, where the same mistake silently
         no-opped a whole migration. FKFX and ENCH_ICONS are `var`, so those
         window reads are sound. */
      var p=(typeof G!=='undefined'&&G&&G.pool)||[],g=null;""",
    '1 the binding test')

# assert against the CODE FORM, not the identifier: the comment this patch
# writes necessarily contains the identifier it is warning about, and matching
# on that would fail against my own prose rather than against the source.
if '(window.G&&' in s[s.index('_landed:function(d){'):s.index('_physPose:function(d){')]:
    sys.exit('the beat still short-circuits on a window property (nothing written)')
# scoped to the function being changed: this idiom is already used four times
# elsewhere in the file, so a file-wide count is a fact about the codebase and
# not about this patch.
_body = s[s.index('_landed:function(d){'):s.index('_physPose:function(d){')]
if _body.count("typeof G!=='undefined'&&G&&G.pool") != 1:
    sys.exit('the corrected guard is not in _landed exactly once (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
