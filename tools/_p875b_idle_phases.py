# -*- coding: utf-8 -*-
u"""P875b: two holes in the idle clock, found by a phase census rather than by
reading the code I had just written.

An audit of every G.phase write - twenty assignments, not the handful a first
grep suggests - turned up two cases the clock gets wrong.

ONE: THE NAG IS SPENT ON THE ROLL ANIMATION. `choosing` is written from ten
different places and `rolling` sits between the player pressing ROLL and the
dice landing. The clock is re-armed by the pointerdown that PRESSED roll, so
it can expire while the phase is still `rolling` - and the guard returned
without re-arming. The turn's one nag was consumed by a moment the player was
not idle for, and a player who rolls, watches the tumble, then thinks for a
full minute was never nagged at all. Transient phases now RE-ARM instead of
dropping. Only the rival's turn drops it, and runOppTurn clears it there
anyway, so the common case never reaches this branch.

TWO: `gamblers_eye` IS A PLAYER-ACTING PHASE and was not in the list. It is
written by activateGamblersEye and means "select dice to keep, tap roll" -
the player is deciding, exactly like `choosing`. Both the fire guard and the
re-arm hook treated it as dead time, so during a Gambler's Eye selection the
clock could neither fire nor be re-armed by tapping.

Neither is a crash and neither would have shown up in the probe I wrote,
because both need a phase the probe never entered. That is the argument for
censusing every writer of a field rather than the ones the happy path uses.
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


# ── 1. the fire guard: transient phases re-arm, only the rival's drops ──
sub(u"""    if(typeof G==='undefined'||!G||G._endMatchFired)return;
    if(G.phase!=='idle'&&G.phase!=='choosing')return;
    var sc=document.getElementById('screen-match');
    if(!sc||!sc.classList.contains('active'))return;
    _dlgIdleFired=true;                 /* once per turn - latched here, not on arm */
    if(window.DLG)DLG.trigger('PLAYER_IDLE');""",
    u"""    if(typeof G==='undefined'||!G||G._endMatchFired)return;
    var sc=document.getElementById('screen-match');
    if(!sc||!sc.classList.contains('active'))return;
    /* P875b: TRANSIENT PHASES RE-ARM RATHER THAN DROP. `rolling` sits between
       the player pressing ROLL and the dice landing, and the clock was
       re-armed by that very press - so it could expire mid-animation, return
       here, and silently spend the turn's one nag on a moment the player was
       not idle for. Someone who rolled, watched, then thought for a minute
       was never nagged at all. Only the rival's turn drops the clock, and
       runOppTurn clears it there anyway. */
    if(!_dlgPlayerActing()){
      if(G.phase!=='opp')_dlgIdleArm();
      return;
    }
    _dlgIdleFired=true;                 /* once per turn - latched here, not on arm */
    if(window.DLG)DLG.trigger('PLAYER_IDLE');""",
    '1 transient phases re-arm')

# ── 2. one definition of "the player may act", used by both readers ──
sub(u"""var DLG_IDLE_MS=9000;      /* long enough to read the board, short enough to land */""",
    u"""var DLG_IDLE_MS=9000;      /* long enough to read the board, short enough to land */
/* P875b: ONE definition of "the player may act", because the fire guard and
   the re-arm hook both need it and two copies would drift. `gamblers_eye` is
   in the list and was missed first time round: activateGamblersEye writes it
   and it means "select dice to keep, tap roll" - the player is deciding,
   exactly as in `choosing`. Without it the clock could neither fire nor be
   re-armed by tapping during a Gambler's Eye selection. */
function _dlgPlayerActing(){
  try{
    if(typeof G==='undefined'||!G)return false;
    return G.phase==='idle'||G.phase==='choosing'||G.phase==='gamblers_eye';
  }catch(e){return false;}
}""",
    '2 one acting-phase test')

# ── 3. the re-arm hook uses the same test ────────────────────────────
sub(u"""  try{document.addEventListener('pointerdown',function(){
    if(typeof G==='undefined'||!G)return;
    if(G.phase!=='idle'&&G.phase!=='choosing')return;
    _dlgIdleArm();
  },true);}catch(e){}""",
    u"""  try{document.addEventListener('pointerdown',function(){
    if(!_dlgPlayerActing())return;      /* P875b: the shared test */
    _dlgIdleArm();
  },true);}catch(e){}""",
    '3 hook uses the shared test')

# ── post-asserts ─────────────────────────────────────────────────────
if s.count('function _dlgPlayerActing()') != 1:
    sys.exit('the shared test is not defined exactly once (nothing written)')
# and NOBODY may still be doing the phase test by hand - that is the drift
# this patch exists to prevent
# SCOPED to the idle clock. The same expression exists in unrelated game code
# (handleRoll's own guard), which this patch has no business touching - a
# file-wide test asserts against code it did not write and should not own.
# bounded by two markers this patch owns, not by a brace scan - the region is
# CRLF in places and a \n-anchored search silently ran past the clock and into
# unrelated code, which is how the first version of this assert failed on a
# correct patch.
_blkA = s.index('P875: THE IDLE CLOCK')
_blkB = s.index('function _dlgIdleHook(') + 800
if "G.phase!=='idle'&&G.phase!=='choosing'" in s[_blkA:_blkB]:
    sys.exit('A HAND-ROLLED ACTING-PHASE TEST SURVIVES INSIDE THE IDLE CLOCK - '
             'it will drift from the shared one (nothing written)')
if s.count('_dlgPlayerActing()') != 3:
    sys.exit('the shared test is used %d times, expected 3 (definition, fire '
             'guard, re-arm hook) (nothing written)' % s.count('_dlgPlayerActing()'))
if "if(G.phase!=='opp')_dlgIdleArm();" not in s:
    sys.exit('the transient re-arm is missing (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
