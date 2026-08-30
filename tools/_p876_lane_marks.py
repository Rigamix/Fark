# -*- coding: utf-8 -*-
u"""P876 (Denis's steer): three certain fixes - fog and snuff stop burning a
turn of their window on a no-op, and the card mark starts painting at all.

SNARE IS THE TEMPLATE AND THE FILE ALREADY SAYS SO. The comment above
_lmRetire reads: "Snare is the only consumer today - it retires inside the
branch where it actually halved something." Fog and snuff were left calling
_lmSpend from OUTSIDE the branch that does the work:

  fog   - _lmSpend sits at the end of `if(_lmDue)`, outside the inner
          `if(_fi>=0 && _fogV.length>1)` that actually removes a seat. If the
          fogged lane is not among their free dice, or they are down to one
          die, the fog misreads nothing and still spends a turn.
  snuff - _lmSpend runs BEFORE `if(_snuffLane>=0 && left>1)`, so a snuff that
          cannot fire (they are down to one die) spends a turn regardless.

A KINDRED-DOUBLED FOG IS THE CASE THAT HURTS: two turns bought, one of them
silently thrown away on a turn where the mark did nothing at all.

WHY THIS NEEDED A THIRD PRIMITIVE RATHER THAN JUST MOVING THE CALL. _lmDue
requires `m.turn === G.oppTurnCount`. Simply not spending leaves `m.turn`
pointing at the turn that just passed, so the mark stays live and is NEVER due
again - live for ever, firing never, which is worse than the bug being fixed.
The no-op path has to re-arm WITHOUT decrementing, and that is a different
verb from both _lmSpend and _lmRetire. It gets its own name, in the same style
the file already uses to keep those two apart.

THE CARD MARK NEVER PAINTED. _drawGlow refuses to run the whole pass unless
some die carries `selected`. Steady Hand's pick clears `selected` and THEN
adds `cardmark` - so unless another die happens to be selected, P856's mark is
a class on an element and nothing else, for its entire 900ms. P856 moved the
mark onto a painter that will not run in the state P856's own call site
creates. The guard now also wakes for a mark.

RECORDED, NOT FIXED - snuff has a second, separate defect. The announce and
`left--` are gated on `left>1`, but the SEAT is actually removed much later
under a different condition entirely (`_rungMats.length>1`). Two gates for one
effect, so "did the snuff do anything" has two different answers depending on
which site is asked. The spend below follows the announce, because that is the
half the player is told about and the half whose absence means nothing
happened to them. Making the two gates agree is a behaviour change and belongs
in its own patch.
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


# ── 1. the third verb ────────────────────────────────────────────────
sub(u"""function _lmSpend(key){
  var m=G&&G[key];if(!m)return;
  m.turns=(m.turns||1)-1;
  if(m.turns>0)m.turn=(G.oppTurnCount||0)+1;
  else m.live=false;
}""",
    u"""function _lmSpend(key){
  var m=G&&G[key];if(!m)return;
  m.turns=(m.turns||1)-1;
  if(m.turns>0)m.turn=(G.oppTurnCount||0)+1;
  else m.live=false;
}
/* P876: THE NO-OP PATH. A third verb, and it is not a convenience - it is the
   only correct answer when the window came due and the mark could not act.
   _lmSpend would take a turn the mark never used; doing nothing at all is
   WORSE, because _lmDue tests `m.turn===G.oppTurnCount` and a mark whose turn
   points at the turn that just passed is live for ever and due never. So the
   window is re-armed for the next opponent turn with its count untouched:
   nothing was spent because nothing happened. That is the brief's rule - the
   window ends when it has affected the opponent - stated as code. */
function _lmDefer(key){
  var m=G&&G[key];if(!m||!m.live)return;
  m.turn=(G.oppTurnCount||0)+1;
}""",
    '1 the defer verb')

# ── 2. fog spends only when it misread a seat ────────────────────────
sub(u"""          }catch(e){}
        }
        /* KINDRED holds it for a second opponent turn (#32) */
        _lmSpend('_fog');
      }""",
    u"""          }catch(e){}
          /* P876: THE SPEND MOVED IN HERE, beside the work, which is where
             Snare's retire already sits and where its comment says it belongs.
             KINDRED holds it for a second opponent turn (#32) - and a Kindred
             fog is exactly the case this was costing: two turns bought, one
             thrown away on a turn where nothing was misread. */
          _lmSpend('_fog');
        }else{
          /* due, but there was no seat to take - the lane is not among their
             free dice, or they are down to their last one. Nothing happened to
             them, so the window is not spent; it re-arms for the next turn. */
          _lmDefer('_fog');
        }
      }""",
    '2 fog spends on effect')

# ── 3. snuff likewise ────────────────────────────────────────────────
sub(u"""    _snuffLane=G._snuff.lane;
    /* KINDRED holds it for a second turn: spend one, and re-arm for the next
       opponent turn rather than clearing */
    _lmSpend('_snuff');
    if(_snuffLane>=0&&left>1){
      left--;/* the seat itself is dropped where rungDice is built, below */
      try{setStatusMsg('THEIR '+(_snuffLane+1)+(_snuffLane===0?'ST':(_snuffLane===1?'ND':(_snuffLane===2?'RD':'TH')))+' DIE IS SNUFFED','gold');}catch(e){}
      try{famLog('SNUFF \u2014 THEY PLAY ONE SHORT');}catch(e){}
    }""",
    u"""    _snuffLane=G._snuff.lane;
    if(_snuffLane>=0&&left>1){
      left--;/* the seat itself is dropped where rungDice is built, below */
      try{setStatusMsg('THEIR '+(_snuffLane+1)+(_snuffLane===0?'ST':(_snuffLane===1?'ND':(_snuffLane===2?'RD':'TH')))+' DIE IS SNUFFED','gold');}catch(e){}
      try{famLog('SNUFF \u2014 THEY PLAY ONE SHORT');}catch(e){}
      /* P876: KINDRED holds it for a second turn - spend one, re-arm for the
         next. This used to run ABOVE the guard, so a snuff that could not fire
         because they were down to one die spent a turn of its window anyway. */
      _lmSpend('_snuff');
    }else{
      /* nothing was taken from them, so nothing is spent. NOTE: this follows
         the ANNOUNCE gate. The seat is actually removed much later under a
         DIFFERENT condition (_rungMats.length>1), so the two disagree about
         whether a snuff happened - recorded as its own defect rather than
         changed here, because reconciling them moves behaviour. */
      _lmDefer('_snuff');
    }""",
    '3 snuff spends on effect')

# ── 4. the card mark wakes the painter ───────────────────────────────
sub(u"""      for(var i=0;i<this.dice.length;i++){
        var q=this.dice[i];
        if(q.match&&q.obj.visible&&q.chip.classList.contains('selected')){skip=false;break;}
      }""",
    u"""      for(var i=0;i<this.dice.length;i++){
        var q=this.dice[i];
        /* P876: A CARD MARK WAKES THIS TOO. The guard tested `selected` alone,
           and Steady Hand's pick CLEARS selected before it adds the mark - so
           unless some other die happened to be selected, P856's mark was a
           class on an element and nothing else for its whole 900ms. P856 moved
           the mark onto a painter that refuses to run in the state P856's own
           call site creates. */
        if(!q.match||!q.obj.visible)continue;
        if(q.chip.classList.contains('selected')||q.chip.classList.contains('cardmark')){skip=false;break;}
      }""",
    '4 the mark wakes the painter')

# ── post-asserts ─────────────────────────────────────────────────────
if s.count('function _lmDefer(') != 1:
    sys.exit('the defer verb is not defined exactly once (nothing written)')
if s.count("_lmDefer('_fog')") != 1 or s.count("_lmDefer('_snuff')") != 1:
    sys.exit('the no-op paths are not wired exactly once each (nothing written)')
if s.count("_lmSpend('_fog')") != 1 or s.count("_lmSpend('_snuff')") != 1:
    sys.exit('a spend was duplicated or lost (nothing written)')
# snare must be untouched - it is the template, not a patient
if s.count("_lmRetire('_snare')") != 1:
    sys.exit('snare was disturbed (nothing written)')
if "q.chip.classList.contains('cardmark')" not in s:
    sys.exit('the mark guard is missing (nothing written)')
# The fog spend must sit INSIDE the seat-removal branch and BEFORE the no-op
# path. Asserted by ORDERING rather than by scanning back a fixed number of
# bytes - the fog block carries ~25 lines of visual code, so a byte window is
# a guess about formatting and the first version of this guessed too small.
_iGate = s.index('_fogV.length>1')
_iSpend = s.index("_lmSpend('_fog')")
_iDefer = s.index("_lmDefer('_fog')")
if not (_iGate < _iSpend < _iDefer):
    sys.exit('the fog spend is not between the seat-removal gate and the no-op '
             'path (gate=%d spend=%d defer=%d) (nothing written)'
             % (_iGate, _iSpend, _iDefer))
_iGateS = s.index('_snuffLane>=0&&left>1')
_iSpendS = s.index("_lmSpend('_snuff')")
_iDeferS = s.index("_lmDefer('_snuff')")
if not (_iGateS < _iSpendS < _iDeferS):
    sys.exit('the snuff spend is not between its gate and its no-op path '
             '(nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
