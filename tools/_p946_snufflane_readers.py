# -*- coding: utf-8 -*-
u"""P946: P945 renamed a variable and left three readers behind.

THE CRASH. `step()` inside runOppTurn read `_snuffLane`, a local P945 renamed
to `_snuffLanes` 155 lines earlier. The read is UNGUARDED - `if(_snuffLane>=0`
- so it threw ReferenceError on every rival turn, snuffed or not, and took
runOppTurn down with it. The rival's row is never dealt and the turn never
returns.

HOW IT WAS FOUND, because that is the part worth keeping: not by looking for
it. A reachability probe for build step 9 asked whether a rival die exists
during the arm window, drove a turn to phase=opp, and the page error came out
in the run log. The census question was answered too (it does not), but the
crash outranks it.

WHAT IT ALREADY COST. Today's boss-drain probe reported
stalled="deadline at phase=opp" and I recorded it in OPEN.md as a defect in
fark_driver.js's boss path, with G._ffMult offered as the lead. That
attribution is wrong: the driver stalls because the rival turn it is waiting
for is throwing. A void measurement invented a defect in the instrument, and
the real fault was in the game and was mine. (The ladder's boss 0/30 is NOT
affected - ec70d3b landed before P945's ee7e11a.)

AND THE SAME RENAME LEFT TWO MORE. Counted rather than spot-fixed, which is
the rule this file already carries:
  G._oSnuffLane, the singular, is written at the publish site and re-keyed by
  _oRemoveOppDieAt, and read by NOTHING - _lmSnuffed and _oHandAfterSweep both
  read the list. P945's comment kept it for "a reader outside this file's
  census", a reader it never named and that does not exist.
  G._oSnuffLanes, the list that IS read, is not re-keyed at all. So removing an
  opposing die maintained the dead copy and left the live one stale: every
  published snuff lane above the removal points one seat too high.
Two homes for one fact, and the removal was keeping the wrong one correct. The
dead field goes rather than being maintained alongside.
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


# 1 ── THE CRASH ────────────────────────────────────────────────────
sub(u"""    if(_snuffLane>=0&&_rungMats.length>1){
      _rungMats.splice(_snuffLane,1);rungLanes.splice(_snuffLane,1);
    }""",
    u"""    /* P946: EVERY SNUFFED SEAT - and this line is where the rival's turn
       died. P945 renamed the local to `_snuffLanes` and published a list; this
       reader, a closure inside step() declared 155 lines below it, kept the old
       name. Unguarded, so it threw ReferenceError on EVERY rival turn rather
       than only a snuffed one.
       DESCENDING, for the reason the fog site carries: each splice shifts the
       indices the next was computed against. The one-die floor is re-tested per
       cut instead of once, because two snuffs on a two-seat hand must take one
       seat, not both - the same floor _snuffLanes itself applies when it is
       built. */
    var _snCuts=(_snuffLanes||[]).filter(function(L){
      return typeof L==='number'&&L>=0&&L<_rungMats.length;
    }).sort(function(a,b){return b-a;});
    _snCuts.forEach(function(L){
      if(_rungMats.length>1){_rungMats.splice(L,1);rungLanes.splice(L,1);}
    });""",
    '1 the dangling _snuffLane read')

# 2 ── THE DEAD SINGULAR GOES ───────────────────────────────────────
sub(u"""  /* P945: a LIST now - see _lmSnuffed. The old scalar is still assigned so a
     reader outside this file's census keeps working, and it carries the first
     lane, which is exactly what it carried when only one could exist. */
  G._oSnuffLanes=_snuffLanes.slice();
  G._oSnuffLane=_snuffLanes.length?_snuffLanes[0]:-1;""",
    u"""  /* P945: a LIST now - see _lmSnuffed.
     P946: AND ONLY THE LIST. The scalar was kept here for "a reader outside
     this file's census" - a reader never named and never found; _lmSnuffed and
     _oHandAfterSweep are the readers and both take the list. It survived as a
     second home for one fact, and _oRemoveOppDieAt was re-keying THAT one
     while leaving this one stale, so the removal kept the dead copy correct.
     A flagged assumption that is never closed is still a guess. */
  G._oSnuffLanes=_snuffLanes.slice();""",
    '2 the unread scalar is not published')

# 3 ── THE REMOVAL RE-KEYS THE LIST THAT IS READ ────────────────────
sub(u"""  if(typeof G._oSnuffLane==='number'){
    if(G._oSnuffLane===L)G._oSnuffLane=-1;
    else if(G._oSnuffLane>L)G._oSnuffLane--;
  }""",
    u"""  /* P946: RE-KEY THE LIST, WHICH IS THE ONE ANYTHING READS. This maintained
     the scalar P945 left behind, so a removal kept a field nobody consults
     correct and let G._oSnuffLanes - read by _lmSnuffed and _oHandAfterSweep -
     go stale: every published snuff lane above the removal pointed one seat
     too high, which is the off-by-one-per-seat error the snuff seat machinery
     exists to prevent. A lane that WAS the removed die drops out rather than
     being kept as -1: _lmSnuffed does indexOf, and a -1 in the list would
     answer true for any caller that passed one. */
  if(G._oSnuffLanes&&G._oSnuffLanes.length){
    G._oSnuffLanes=G._oSnuffLanes.map(function(n){
      if(typeof n!=='number')return n;
      return (n===L)?-1:((n>L)?n-1:n);
    }).filter(function(n){return n>=0;});
  }""",
    '3 the removal re-keys _oSnuffLanes')

# 4 ── the stale comment that names the dead field ──────────────────
sub(u"""   A sweep clears the held dice but NOT the snuff: _snuffLane is set once and
   never cleared for the turn, which is the whole reason P521 stopped assigning
   the literal 6. G._oSnuffLane is published by runOppTurn so this and _oSeats
   read the same source rather than two copies of the same idea. */""",
    u"""   A sweep clears the held dice but NOT the snuff: _snuffLanes is set once and
   never cleared for the turn, which is the whole reason P521 stopped assigning
   the literal 6. G._oSnuffLanes is published by runOppTurn so this and _oSeats
   read the same source rather than two copies of the same idea. */""",
    '4 the comment names the live field')

# ── post-asserts, against CODE with the comments stripped ──────────
# (a comment quoting the old name is exactly what made four earlier asserts
#  fail on correct code)
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

if re.search(r'\b_snuffLane\b', code):
    sys.exit('the singular local survives in code (nothing written)')
if re.search(r'_oSnuffLane\b', code):
    sys.exit('the dead scalar survives in code (nothing written)')
# the list must still have its writer and its two readers
if code.count('G._oSnuffLanes=') != 2:
    sys.exit('expected exactly 2 writers of _oSnuffLanes, found %d '
             '(publish + re-key) (nothing written)'
             % code.count('G._oSnuffLanes='))
for reader, where in ((u'_lmSnuffed', u'the shared predicate'),
                      (u'_oHandAfterSweep', u'the sweep hand size')):
    if reader not in code:
        sys.exit('%s (%s) is gone (nothing written)' % (reader, where))
# the crash site now iterates
if 'var _snCuts=' not in code:
    sys.exit('the seat cut does not iterate (nothing written)')
if 'return b-a;' not in code:
    sys.exit('the descending sort was lost (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
