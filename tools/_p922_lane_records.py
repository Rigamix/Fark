# -*- coding: utf-8 -*-
u"""P922: P919 was HALF-APPLIED, which is worse than not applied. The records
carry too, and the roster stops being four hand-written special cases.

THE REGRESSION P919 SHIPPED. The stargazer promise lives in two places that must
agree: G._famPeekVals[i] = {lane, val}, the record that decides which die
RECEIVES the promised face, and a DOM float whose dataset.lane is copied from it
two lines later (17945-17946). The consume at 17548 is lane-keyed -
_pk[p.lane]=p.val, then `if(_pk[d.lane]!==undefined) d.val=_pk[d.lane]`.

Before P919 both were stale together after a reorder, so the float sat on
exactly the die that was about to receive its value: wrong relative to mint
time, but never observably contradictory. P919 taught the float to follow its
die and left the record behind, so THE FLOAT PROMISING A 5 NOW SITS ON A DIE
THAT ROLLS 6. Fixing one half of a two-part invariant is worse than fixing
neither, because the disagreement is on screen.

HOW IT WAS MISSED, exactly. The patch censused lane-stamped DOM ELEMENTS and
concluded it had found every lane-stamped THING - missing the state record that
mints those very elements, two lines apart. A census of markers is not a census
of mechanics, one level up from where that rule is usually applied.

AND THE COMMENT VOUCHED FOR IT. "EVERY LANE-STAMPED THING ENROLS HERE" was
written into the loop while two lane-stamped things did not. A comment asserting
coverage the code lacks is worse than no comment: it answers the question a
reader would otherwise go and check.

SO THE ROSTER BECOMES REAL. _famLaneRecords() names every lane-stamped state
record in one place, the way _famLaneGhosts() names the DOM ones, and the carry
loop iterates the two rosters instead of holding a hand-written branch per
record. That collapses G._fairTrade (P530), G._tradeSwaps[] (P531),
G._famPeekVals[] and G._famPreserve into one mechanism, and a fifth record is
one line in the roster rather than a fourth branch someone has to remember to
add. The rule is now enforced by the shape rather than asserted by the prose.

BEHAVIOUR IS PRESERVED FOR THE TWO EXISTING ENTRIES. The old branches used -1
sentinels for absent lanes; the roster simply excludes non-numeric lanes, which
is equivalent because the _slots gate above already rejects any pool containing
a non-numeric or negative lane, so c.die.lane can never be -1. The legacy
bare-number _famPeekVals save shape (17542) has no .lane and is excluded for the
same reason - correctly, since that branch is index-keyed rather than lane-keyed.
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


# ── 1. the record roster, beside the element roster ─────────────────
sub(u"""function _famLaneGhosts(){
  return [].concat(window._pkGhosts||[],window._htMarks||[])
    .filter(function(g){return g&&g.dataset;});
}""",
    u"""function _famLaneGhosts(){
  return [].concat(window._pkGhosts||[],window._htMarks||[])
    .filter(function(g){return g&&g.dataset;});
}
/* P922: AND THE LANE-STAMPED STATE RECORDS, which is the half P919 missed.
   _famLaneGhosts names the DOM elements; these are the objects those elements
   are drawn FROM, and they are the half that decides what actually happens.
   G._famPeekVals[i] is {lane,val} and the peek float's dataset.lane is copied
   straight off it (17946), so teaching the float to follow its die while the
   record stayed behind put a float promising 5 over a die that rolls 6.
   EVERY LANE-STAMPED RECORD GOES IN THIS LIST, and _commitVagabondDrag's carry
   loop iterates it - so a new one is a line here rather than a branch someone
   has to remember to add to the reorder. That is the difference between the
   rule being enforced and the rule being asserted in a comment, which is what
   P919 did while two records sat outside it.
   `lane` ONLY, NEVER `oLane` (P531): lane indexes the player's board, oLane the
   rival's, and a player reorder renumbers only the player's seats.
   A non-numeric lane is excluded rather than sentinelled - the _slots gate in
   the carry rejects any pool with a non-numeric or negative lane, so a real
   die's lane can never match a sentinel anyway. That also correctly excludes
   the legacy bare-number _famPeekVals save shape (17542), which is index-keyed
   rather than lane-keyed. */
function _famLaneRecords(){
  var out=[];
  if(typeof G==='undefined'||!G)return out;
  try{
    if(G._fairTrade&&typeof G._fairTrade.lane==='number')out.push(G._fairTrade);/* P530 */
    (G._tradeSwaps||[]).forEach(function(t){
      if(t&&typeof t.lane==='number')out.push(t);});                            /* P531 */
    (G._famPeekVals||[]).forEach(function(p){
      if(p&&typeof p.lane==='number')out.push(p);});                            /* P922 */
    if(G._famPreserve&&typeof G._famPreserve.lane==='number')out.push(G._famPreserve);
  }catch(e){}
  return out;
}""",
    '1 the record roster')

# ── 2. the carry loop iterates two rosters, not four special cases ──
sub(u"""          /* P530: THE LOAN'S SEAT MOVES TOO. P520 permuted matchDice, _enchArr
             and d.lane and left G._fairTrade.lane behind, so after a reorder the
             loan protected whichever die had moved INTO the seat it used to
             hold - which is S7(b)'s real mechanism, the lane gate having already
             ruled out the material test on its own. */
          var _ftBefore=(G._fairTrade&&typeof G._fairTrade.lane==='number')?G._fairTrade.lane:-1;
          /* P531: AND THE TRADE LEDGER'S PLAYER-SIDE SEAT. P530 taught this loop to
             carry the loan and left its sibling behind - measured, the die moved
             from seat 0 to seat 3, the loan followed and the ledger stayed at 0.
             ONLY `lane` MOVES, NEVER `oLane`: lane indexes the player's board,
             oLane the rival's, and a player reorder renumbers only the player's
             seats. Carrying both would repair the wrong die on the rival's board,
             which is the error P527 caught in its own first draft.
             Snapshotted before the loop writes anything, like the pairs beside it,
             or an entry that has already moved gets matched a second time. */
          var _tsBefore=(G._tradeSwaps||[]).map(function(t){
            return (t&&typeof t.lane==='number')?t.lane:-1;});""",
    u"""          /* P922: EVERY LANE-STAMPED THING FOLLOWS ITS DIE, and this loop no
             longer holds a hand-written branch per kind. Two rosters -
             _famLaneRecords() for the state objects, _famLaneGhosts() for the
             DOM elements they are drawn from - and the loop repairs whatever is
             in them.
             THE HISTORY IS WHY THE SHAPE CHANGED. P520 permuted matchDice,
             _enchArr and d.lane and left G._fairTrade.lane behind, so a reorder
             left the loan protecting whichever die had moved INTO its seat.
             P530 carried the loan and left G._tradeSwaps[].lane behind -
             measured: the die moved seat 0 to seat 3, the loan followed, the
             ledger stayed at 0. P531 carried the ledger. P919 carried the DOM
             floats and left G._famPeekVals[].lane behind, which was worse than
             all of them, because the float and the record disagreed ON SCREEN:
             a float promising 5 sitting over a die that rolls 6. Four patches,
             each finding the previous one's leftover.
             A branch per kind is what made that possible, so there is no longer
             a branch per kind. Add a record to _famLaneRecords and it is
             carried; nothing here needs editing.
             SNAPSHOT BEFORE THE LOOP WRITES, or an entry that has already moved
             is matched a second time. `lane` only, never `oLane` - P531's rule,
             now enforced in the roster rather than repeated here. */
          var _recs=(typeof _famLaneRecords==='function')?_famLaneRecords():[];
          var _recBefore=_recs.map(function(r){return r.lane;});""",
    '2 the roster replaces the special cases')

sub(u"""          var _ghosts=(typeof _famLaneGhosts==='function')?_famLaneGhosts():[];
          var _ghBefore=_ghosts.map(function(g){
            var L=parseInt(g.dataset.lane,10);
            return isFinite(L)?L:-1;});
          _carry.forEach(function(c,i){
            if(_ftBefore>=0&&c.die&&c.die.lane===_ftBefore)G._fairTrade.lane=_slots[i];
            if(c.die&&typeof c.die.lane==='number')(G._tradeSwaps||[]).forEach(function(t,ti){
              if(t&&_tsBefore[ti]===c.die.lane)t.lane=_slots[i];
            });
            if(c.die&&typeof c.die.lane==='number')_ghosts.forEach(function(g,gi){
              if(_ghBefore[gi]===c.die.lane)g.dataset.lane=String(_slots[i]);
            });""",
    u"""          var _ghosts=(typeof _famLaneGhosts==='function')?_famLaneGhosts():[];
          var _ghBefore=_ghosts.map(function(g){
            var L=parseInt(g.dataset.lane,10);
            return isFinite(L)?L:-1;});
          _carry.forEach(function(c,i){
            if(c.die&&typeof c.die.lane==='number'){
              _recs.forEach(function(r,ri){
                if(_recBefore[ri]===c.die.lane)r.lane=_slots[i];});
              _ghosts.forEach(function(g,gi){
                if(_ghBefore[gi]===c.die.lane)g.dataset.lane=String(_slots[i]);});
            }""",
    '3 the loop body repairs both rosters')

# ── the P919 comment claimed coverage it did not have ───────────────
sub(u"""          /* P919 (brief 3.8): AND THE LANE-STAMPED GHOSTS - the pickpocket
             floats and the honeytrap marks. P844 already stated the behaviour,
             "the floats just follow their dice", and this loop is why they did
             not: the reorder renumbers d.lane while a ghost's dataset.lane
             keeps the stamp from mint, and _famRefloatGhosts runs AFTER the
             renumbering, so it reads a fresh lane against a stale stamp and
             floats the ghost onto whichever die moved into that seat. Nothing
             in _famRefloatGhosts changes; the lane is just correct when it runs.
             EVERY LANE-STAMPED THING ENROLS HERE. That is the rule, written
             once instead of the history: P530 carried the loan, P531 carried
             the ledger and recorded that P530 "left its sibling behind", and
             these were the next straggler for as long as P844 has existed. A
             fourth one goes in this loop on the day it is created, not on the
             day somebody notices the float landed on the wrong die.
             Snapshot before the loop writes, like the pairs above, or an entry
             that has already moved is matched a second time. `lane` only: a
             ghost has no oLane, and a player reorder renumbers only the
             player's seats. */
""",
    u"""          /* P919 + P922: the DOM half. _famRefloatGhosts is unchanged - it
             reads a fresh lane against a stamp that is now correct. */
""",
    '4 the overclaiming comment goes')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

_loop = code.index('_carry.forEach(function(c,i){')
region = code[code.rindex('var _recs=', 0, _loop):code.index('c.die.lane=L;', _loop)]

# the hand-written branches are GONE, not merely joined by a third
for gone in ('_ftBefore', '_tsBefore'):
    if gone in code:
        sys.exit('%s survives - the special cases were not replaced (nothing written)' % gone)
# and the records they carried are still carried, via the roster
for need in ('G._fairTrade', 'G._tradeSwaps', 'G._famPeekVals', 'G._famPreserve'):
    if need not in code[code.index('function _famLaneRecords'):
                        code.index('function _famLaneRecords') + 900]:
        sys.exit('%s is not in the record roster (nothing written)' % need)
# one roster definition, and the carry is its only writer of .lane
if code.count('function _famLaneRecords(') != 1:
    sys.exit('the record roster is not defined once (nothing written)')
if region.count('r.lane=_slots[i]') != 1:
    sys.exit('the records are rewritten other than once (nothing written)')
if region.count('g.dataset.lane=String(') != 1:
    sys.exit('the ghosts are rewritten other than once (nothing written)')
# snapshot before write, for both rosters
for snap, write in (('var _recBefore=', 'r.lane=_slots[i]'),
                    ('var _ghBefore=', 'g.dataset.lane=String(')):
    if region.index(snap) > region.index(write):
        sys.exit('%s is taken after its write (nothing written)' % snap)
# and both snapshots are taken before the loop opens
_open = region.index('_carry.forEach(function(c,i){')
if region.index('var _recBefore=') > _open or region.index('var _ghBefore=') > _open:
    sys.exit('a snapshot is taken inside the loop (nothing written)')
# oLane is never touched here - P531's rule
if 'oLane' in region:
    sys.exit('the carry touches oLane (nothing written)')
# the mint sites are undisturbed
if code.count('g.dataset.lane=String(') != 3:
    sys.exit('a ghost mint site was disturbed (nothing written)')
# and the claim that outran the code is gone
if 'EVERY LANE-STAMPED THING ENROLS HERE' in s:
    sys.exit('the overclaiming comment survives (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
