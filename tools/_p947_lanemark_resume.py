# -*- coding: utf-8 -*-
u"""P947: a lane mark does not survive a save, and never has.

(P947b folded in: the restore copied, it did not alias. See the comment in
edit 3 - the first version handed S.pendingMatch's own object to G.)

THE BUG. G._laneMark is not in saveMatchState's field list, nor in the mid-turn
snapshot at 25365, nor in the restore. So: brand a snare for 400g, keep it, quit
the match, resume - and the snare is gone. Same for fog and snuff. The player
paid for an effect the save silently drops. This predates P945 (the old
G._fog/_snuff/_snare keys were not carried either); the re-key inherited it.

WHY IT IS THE SAME SHAPE THE FILE ALREADY DOCUMENTS. _tradeSwaps sits two lines
above the gap with this comment: "A Trade fires MID-turn and this snapshot is
rewritten whole at every turn boundary, so without the field a resumed match
held a rival's die in a lane with no record it had ever been borrowed." A lane
mark arms mid-turn (inside _iconFire, on the KEEP path) and resolves on the
rival's next turn. Identical lifetime, identical hole.

THE TRAP, AND IT IS WHY THE MARKS ARE REBASED RATHER THAN JUST CARRIED.
A mark's due-ness is `m.turn === G.oppTurnCount` (24918), and G.oppTurnCount is
NOT saved either - it is initialised to 0 at 31590/31619 and restarts there on
every resume. Carrying _laneMark alone would restore marks stamped for a turn
number that never arrives: they would never fire, never be swept by the
`oppTurnCount > m.turn+1` rule at 37690, and would hold their lanes forever
against _lmArm's occupancy refusal. **That is strictly worse than dropping
them** - the player would lose the effect AND the seat. Carrying the cost
without the effect.

Saving oppTurnCount instead was rejected: four other consumers key their cadence
off it - the Jinx (%2, 37663), Whisper's Veil (%2, 37666), Leaky Cup (%4, 37830)
and The Sting (%4, 37693) - so restoring the true count would change those
mechanics on a resumed match, which is a balance change and not mine to make.

So the marks are REBASED on the way in: a live mark becomes due on the rival's
next turn, whenever that is. That preserves what the mark means - "their next
turn" - without touching a single other reader of oppTurnCount.
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


# 1 ── the turn-boundary snapshot ───────────────────────────────────
sub(u"""    _tradeSwaps:G._tradeSwaps?JSON.parse(JSON.stringify(G._tradeSwaps)):null,
    originalPlayerDice:[...G.originalPlayerDice],""",
    u"""    _tradeSwaps:G._tradeSwaps?JSON.parse(JSON.stringify(G._tradeSwaps)):null,
    /* P947: THE LANE MARKS, for exactly the reason stated above them. A fog,
       snuff or snare arms MID-turn - inside _iconFire, on the keep path - and
       resolves on the rival's next turn, so it has the same lifetime as the
       trade ledger and had the same hole: none of the three was ever carried,
       before or after P945's re-key. A player who branded a snare for 400g,
       kept it and resumed the match got nothing. */
    _laneMark:G._laneMark?JSON.parse(JSON.stringify(G._laneMark)):null,
    originalPlayerDice:[...G.originalPlayerDice],""",
    '1 the turn-boundary snapshot carries the marks')

# 2 ── the mid-turn snapshot ────────────────────────────────────────
sub(u"""    try{S.pendingMatch._tradeSwaps=G._tradeSwaps?JSON.parse(JSON.stringify(G._tradeSwaps)):null;}catch(e){}""",
    u"""    try{S.pendingMatch._tradeSwaps=G._tradeSwaps?JSON.parse(JSON.stringify(G._tradeSwaps)):null;}catch(e){}
    /* P947: and the marks, because THIS is the writer that matters for them -
       they are armed mid-turn, so the turn-boundary snapshot alone would miss
       every mark placed after it. */
    try{S.pendingMatch._laneMark=G._laneMark?JSON.parse(JSON.stringify(G._laneMark)):null;}catch(e){}""",
    '2 the mid-turn snapshot carries the marks')

# 3 ── the restore, with the rebase ─────────────────────────────────
sub(u"""        seatGone:!!t.seatGone};})
      :null;
  }""",
    u"""        seatGone:!!t.seatGone};})
      :null;
    /* P947: THE LANE MARKS COME BACK REBASED, NOT AS THEY WERE.
       A mark is due when `m.turn === G.oppTurnCount` (24918), and oppTurnCount
       is NOT carried across a resume - it restarts at 0 (31590/31619). A mark
       restored with its original stamp would therefore never come due, never be
       swept by the `oppTurnCount > m.turn+1` rule (37690), and would hold its
       lane for the rest of the match against _lmArm's occupancy refusal: the
       player loses the effect AND the seat, which is worse than dropping the
       mark outright. Saving oppTurnCount instead would move the Jinx (37663),
       Whisper's Veil (37666), Leaky Cup (37830) and The Sting (37693), all of
       which key their cadence off it - a balance change, not a repair.
       So each live mark is re-stamped for the rival's NEXT turn, which is what
       the mark has always meant. Dead marks are dropped rather than carried:
       they hold no lane and answer no question. */
    var _rdLM=params._resumeData._laneMark;
    if(_rdLM&&typeof _rdLM==='object'){
      var _lmOut={},_lmBase=(G.oppTurnCount||0)+1;
      for(var _lmK in _rdLM){
        if(!_rdLM.hasOwnProperty(_lmK))continue;
        var _lmSrc=_rdLM[_lmK];
        if(!_lmSrc||!_lmSrc.live)continue;
        var _lmL=+_lmK;
        if(!isFinite(_lmL)||_lmL<0)continue;
        /* P947b: A COPY, NEVER THE SNAPSHOT'S OWN OBJECT. The first version put
           _rdLM[k] straight into G._laneMark, and _rdLM IS S.pendingMatch's map
           - so the restored mark and the saved mark were ONE object and live
           play wrote through into the save. Measured: a mark snapshotted
           live/turn 5/1 attempt read back dead/turn 1/0 attempts once it fired,
           because _lmSpend had mutated the snapshot. Every other record
           restored here builds fresh objects - _tradeSwaps maps to a literal -
           and this is the reason why. */
        var _lmM={};
        for(var _lmF in _lmSrc)if(_lmSrc.hasOwnProperty(_lmF))_lmM[_lmF]=_lmSrc[_lmF];
        _lmM.lane=_lmL;_lmM.turn=_lmBase;
        _lmOut[_lmL]=_lmM;
      }
      G._laneMark=_lmOut;
    }
  }""",
    '3 the restore rebases the marks')

# ── post-asserts, against code with comments stripped ──────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# both writers and the reader exist
if code.count('_laneMark:G._laneMark?JSON.parse') != 1:
    sys.exit('the turn-boundary writer is not there exactly once (nothing written)')
if code.count('S.pendingMatch._laneMark=G._laneMark?JSON.parse') != 1:
    sys.exit('the mid-turn writer is not there exactly once (nothing written)')
if 'params._resumeData._laneMark' not in code:
    sys.exit('the restore does not read the field (nothing written)')
# THE REBASE IS THE POINT - a plain carry is the bug this patch exists to avoid
if '_lmM.turn=_lmBase' not in code:
    sys.exit('the restore does not rebase the turn stamp (nothing written)')
# and dead marks must not be carried, or they hold lanes
if '!_lmSrc.live)continue' not in code:
    sys.exit('the restore carries dead marks (nothing written)')
# AND IT MUST COPY, NOT ALIAS. The first version handed S.pendingMatch's own
# mark object to G, so _lmSpend wrote through into the save when the mark
# fired - the probe measured a snapshot changing under it. Caught only because
# the probe PRINTED the saved object instead of asserting a field on it.
if '_lmM[_lmF]=_lmSrc[_lmF]' not in code:
    sys.exit('the restore aliases the snapshot instead of copying '
             '(nothing written)')
# the paired fact: oppTurnCount must still NOT be saved, or the rebase is
# reasoning about a world that no longer exists
if re.search(r'oppTurnCount:G\.oppTurnCount', code):
    sys.exit('oppTurnCount is now saved - the rebase rationale is stale '
             '(nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
