# -*- coding: utf-8 -*-
u"""P878 (FX BRIEF 3.2 and 3.6): `turns` is a count of ATTEMPTS, and the
refusal moves into the canonical predicate. Both are net deletions.

3.2 REVERSES HALF OF P876, and the ruling arrived after the patch.

  FOG AND SNUFF WERE ALREADY RIGHT. Their unconditional _lmSpend inside the
  due block IS miss semantics: a mark that comes due either fires or misses,
  and both cost an attempt. A Kindred fog with two attempts that misses the
  first still gets the second. What P876 called "burning a window on a no-op"
  was the miss, correctly charged. Backed out, and _lmDefer goes with it -
  under this rule nothing needs re-arming without spending, so the verb has no
  callers and no reason to exist.

  SNARE IS THE ONE THAT IS BROKEN, AND ITS OWN COMMENT SAYS SO. Directly
  above the block: "The mark then clears whether it fired or not." The code
  only retires inside the success branch, so a miss leaves live:true with
  `turn` pointing at the turn that just passed - and _lmDue tests
  turn===oppTurnCount, so it is live for ever and due never. Intent and code
  had diverged and the comment was the one telling the truth.

  P876 READ SNARE AS THE TEMPLATE. It was the patient. The comment above
  _lmRetire presented it as the considered pattern, which is what sent the fix
  to the two functions that did not need it - so that comment is rewritten
  here rather than left to mislead the next reader the same way.

3.6 MOVES THE REFUSAL TO WHERE THE RULE BELONGS. P877 put it in _splitIcons,
one reader of twelve, and P585's comment at _dieIsIcon argues the case
directly: the test belongs in the canonical predicate so it lands everywhere
at once. Two concrete divergences followed - _markLoneCast marked a refused
brand as "will cast" and then it scored 100, a visual claiming an effect that
cannot happen; and Last Stand's deliberate gate still saw an icon where there
was now a plain scoring die.

The split is one predicate into two: _iconLive is the raw fact (a live brand
on the landed face), _dieIsIcon is that AND not refused. Every one of the
twelve readers gets the rule for free, and _splitIcons keeps its `refused`
bucket by asking the only question that distinguishes the cases - live but not
an icon.
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


# ── 1. snuff: back to one attempt charged, hit or miss ───────────────
sub(u"""    _snuffLane=G._snuff.lane;
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
    u"""    _snuffLane=G._snuff.lane;
    /* P878: ONE ATTEMPT, CHARGED WHETHER IT LANDS OR NOT. `turns` counts
       attempts, not turns the mark lurks for - so a due mark that cannot take
       a seat has MISSED, and a miss costs an attempt exactly as a hit does. A
       Kindred snuff with two attempts that misses the first still gets the
       second. P876 moved this inside the guard on the reading that a no-op
       should cost nothing; the ruling says otherwise and this is the revert. */
    _lmSpend('_snuff');
    if(_snuffLane>=0&&left>1){
      left--;/* the seat itself is dropped where rungDice is built, below */
      try{setStatusMsg('THEIR '+(_snuffLane+1)+(_snuffLane===0?'ST':(_snuffLane===1?'ND':(_snuffLane===2?'RD':'TH')))+' DIE IS SNUFFED','gold');}catch(e){}
      try{famLog('SNUFF \u2014 THEY PLAY ONE SHORT');}catch(e){}
    }""",
    '1 snuff back to attempts')

# ── 2. fog likewise ──────────────────────────────────────────────────
sub(u"""          /* P876: THE SPEND MOVED IN HERE, beside the work, which is where
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
    u"""        }
        /* P878: ONE ATTEMPT, HIT OR MISS - see the snuff site. KINDRED buys a
           second ATTEMPT (#32), not a longer lurk, so a fog that finds no seat
           to take has used one of them. P876 moved this inside the branch on
           the opposite reading; the ruling settles it the other way. */
        _lmSpend('_fog');
      }""",
    '2 fog back to attempts')

# ── 3. snare gets the miss its own comment already promised ──────────
sub(u"""          _lmRetire('_snare');
          try{famLog('THE SNARE BITES \u2014 '+(_snX2?'HALVED TWICE':'HALVED'));}catch(e){}
          try{setStatusMsg('YOUR SNARE CATCHES THEM \u2014 '+(_snX2?'A QUARTER':'HALF'),'gold');}catch(e){}
        }
      }""",
    u"""          _lmRetire('_snare');
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
    '3 snare misses properly')

# ── 4. the verb with no callers, and the comment that misled ─────────
sub(u"""/* P876: THE NO-OP PATH. A third verb, and it is not a convenience - it is the
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
    u"""/* P878: _lmDefer is DELETED. It re-armed a mark without spending, which only
   makes sense if a due mark can decline to cost anything - and the ruling is
   that it cannot. Every due mark either fires or misses and both cost an
   attempt, so there is nothing left for the verb to express. Its absence also
   removes the immortal-mark case by construction: no mark can now outlive its
   count. */""",
    '4 the defer verb deleted')

sub(u"""/* CONSUMED. Distinct from _lmSpend on purpose: a marker that fired is gone
   whatever its turn count said, whereas spending a turn may re-arm. Snare is
   the only consumer today - it retires inside the branch where it actually
   halved something. */""",
    u"""/* CONSUMED - for an effect whose HIT uses the whole window at once, whatever
   its count said. Distinct from _lmSpend, which charges one attempt.
   P878: THIS COMMENT USED TO PRESENT SNARE AS THE CONSIDERED PATTERN - "it
   retires inside the branch where it actually halved something" - and that
   reading is what sent P876 to make fog and snuff match it. Snare was not the
   template; it was the one missing its miss case. A due mark ALWAYS costs an
   attempt. Snare calls this on both paths because it arms with a single
   attempt, so consuming the window and spending its last attempt coincide. */""",
    '5 the comment that misled')

# ── 6. the rule moves into the canonical predicate ───────────────────
sub(u"""function _dieIsIcon(d){return !!(d&&_isIcon(d.ench)&&d.val===d.ench.face&&!_brandSpent(d));}""",
    u"""/* P878 (brief 3.6): SPLIT IN TWO, because two different questions were being
   asked of one predicate. _iconLive is the raw fact - a live brand sitting on
   the landed face. _dieIsIcon is the one every consumer wants: a brand that
   will actually fire if kept.
   THE REFUSAL BELONGS HERE, not in a consumer. P585's own comment says why:
   this is the canonical predicate, read by _splitIcons, _iconOnTable,
   _iconRescuesRow, the bust check and _markLoneCast - so the rule lands in all
   of them at once instead of being restated per reader. P877 put it in
   _splitIcons alone, and _markLoneCast promptly marked a refused brand "will
   cast" on a die that then scored 100 - a visual promising an effect that
   cannot happen, which is the exact bug class this workstream exists to
   delete. */
function _iconLive(d){return !!(d&&_isIcon(d.ench)&&d.val===d.ench.face&&!_brandSpent(d));}
function _dieIsIcon(d){return _iconLive(d)&&!_iconRefused(d);}""",
    '6 refusal in the canonical predicate')

sub(u"""function _splitIcons(dice){
  var icons=[],rest=[],refused=[];
  (dice||[]).forEach(function(d){
    if(!_dieIsIcon(d)){rest.push(d);return;}
    /* P877: A REFUSED BRAND IS NOT AN ICON THIS TURN. _iconFire is built on
       one law - a brand banks zero BECAUSE it fired - so a refused fire must
       not take the zero with it. It joins `rest` and scores its natural face,
       which it always has: only a 1 or a 5 can be branded. */
    if(_iconRefused(d)){refused.push(d);rest.push(d);return;}
    icons.push(d);
  });
  return {icons:icons,rest:rest,refused:refused};
}""",
    u"""function _splitIcons(dice){
  var icons=[],rest=[],refused=[];
  (dice||[]).forEach(function(d){
    if(_dieIsIcon(d)){icons.push(d);return;}
    rest.push(d);
    /* P878: live but not an icon is EXACTLY the refused case, so the bucket
       costs one extra test rather than a second copy of the rule. A refused
       brand scores its natural face - it always has one, since only a 1 or a 5
       can be branded - which is the other half of _iconFire's law: a brand
       banks zero BECAUSE it fired. */
    if(_iconLive(d))refused.push(d);
  });
  return {icons:icons,rest:rest,refused:refused};
}""",
    '7 the split asks one question')

# ── post-asserts ─────────────────────────────────────────────────────
if '_lmDefer' in s.replace('_lmDefer is DELETED', ''):
    sys.exit('_lmDefer still has a reference (nothing written)')
if s.count("_lmSpend('_fog')") != 1 or s.count("_lmSpend('_snuff')") != 1:
    sys.exit('a spend was lost or duplicated (nothing written)')
if s.count("_lmRetire('_snare')") != 2:
    sys.exit('snare retires from %d places, expected 2 (hit and miss) '
             '(nothing written)' % s.count("_lmRetire('_snare')"))
if s.count('function _iconLive(') != 1 or s.count('function _dieIsIcon(') != 1:
    sys.exit('the predicate split is wrong (nothing written)')
if '_iconRefused' not in s[s.index('function _dieIsIcon('):s.index('function _dieIsIcon(')+140]:
    sys.exit('_dieIsIcon does not consult the refusal (nothing written)')
# the fog/snuff spends must now be UNCONDITIONAL inside the due block: no
# `else` branch may sit between the gate and the spend
_fs = s.index("_lmSpend('_fog')")
if '}else{' in s[s.index("_lmDue('_fog')"):_fs]:
    sys.exit('the fog spend is still behind a branch (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
