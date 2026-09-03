# -*- coding: utf-8 -*-
u"""P919 (brief 3.8): the lane-stamped ghosts enrol in the reorder's carry loop.

NOT A NEW ANCHOR - THE EXISTING ONE, MADE TRUE. P844 already said what should
happen: "the floats just follow their dice". The mechanism contradicted it. A
vagabond reorder renumbers d.lane on the die objects while a ghost's
dataset.lane keeps the stamp it was minted with, and _famRefloatGhosts runs
AFTER the renumbering - so it reads a fresh lane against a stale stamp and
floats the ghost onto whichever die moved into that seat. Identical until a
reorder, and then not.

NOTHING IN _famRefloatGhosts CHANGES. The lane is simply correct when it runs.

THE THIRD SIBLING, and the loop should say so. P530 taught this loop to carry
G._fairTrade.lane; P531 added G._tradeSwaps[].lane and recorded the shape of the
mistake in its own comment - "P530 taught this loop to carry the loan and left
its sibling behind". The ghosts have been the next straggler since P844. A loop
extended three times by someone finding a leftover is a loop that needs the rule
written in it rather than the history: EVERY LANE-STAMPED THING ENROLS HERE.

SAME DISCIPLINE AS THE TWO BESIDE IT. Snapshotted before the loop writes
anything - _tsBefore exists because an entry that has already moved gets matched
a second time - and `lane` only. A ghost has no oLane, and P531's note is exact
about why that matters: a player reorder renumbers only the player's seats, so
carrying the rival's index would repair the wrong die on the wrong board.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]


sub(u"""          var _tsBefore=(G._tradeSwaps||[]).map(function(t){
            return (t&&typeof t.lane==='number')?t.lane:-1;});
          _carry.forEach(function(c,i){
            if(_ftBefore>=0&&c.die&&c.die.lane===_ftBefore)G._fairTrade.lane=_slots[i];
            if(c.die&&typeof c.die.lane==='number')(G._tradeSwaps||[]).forEach(function(t,ti){
              if(t&&_tsBefore[ti]===c.die.lane)t.lane=_slots[i];
            });""",
    u"""          var _tsBefore=(G._tradeSwaps||[]).map(function(t){
            return (t&&typeof t.lane==='number')?t.lane:-1;});
          /* P919 (brief 3.8): AND THE LANE-STAMPED GHOSTS - the pickpocket
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
          var _ghosts=[].concat(window._pkGhosts||[],window._htMarks||[])
            .filter(function(g){return g&&g.dataset;});
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
    'the ghosts enrol in the carry')

# ── post-asserts, comments stripped so a comment cannot satisfy one ──
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)

# EVERY POSITIONAL ASSERT IS SCOPED TO THE CARRY, and the first draft was not.
# `g.dataset.lane=String(` already exists TWICE in this file - it is how both
# ghost kinds are stamped at mint - so a file-wide count of it was counting
# mentions rather than the thing, and `code.index` of it returned a mint site
# forty thousand lines above the loop, which would have made the
# snapshot-before-write check compare two unrelated positions. The region is
# the unit; the string is not.
_loop = code.index('_carry.forEach(function(c,i){')
_regionStart = code.rindex('var _tsBefore=', 0, _loop)
_regionEnd = code.index('c.die.lane=L;', _loop)
region = code[_regionStart:_regionEnd]

if region.count('_ghBefore') != 2:
    sys.exit('the ghost snapshot is not taken once and read once (nothing written)')
if region.count('g.dataset.lane=String(') != 1:
    sys.exit('the ghost lane is not rewritten exactly once in the carry (nothing written)')
# and the mint sites are untouched - two before, two after
if code.count('g.dataset.lane=String(') != 3:
    sys.exit('a ghost mint site was disturbed (nothing written)')
# SNAPSHOT BEFORE WRITE, the discipline _tsBefore exists to document
if region.index('var _ghBefore=') > region.index('g.dataset.lane=String('):
    sys.exit('the ghost snapshot is taken after the write (nothing written)')
# and the snapshot is taken BEFORE the loop opens, not inside it
if region.index('var _ghBefore=') > region.index('_carry.forEach(function(c,i){'):
    sys.exit('the ghost snapshot is taken inside the loop (nothing written)')
# and the write sits INSIDE that loop with its two siblings
if region.index('_carry.forEach(function(c,i){') > region.index('g.dataset.lane=String('):
    sys.exit('the ghost carry is not inside the carry loop (nothing written)')
# lane only, never oLane - P531's rule
if 'oLane' in region:
    sys.exit('the ghost carry touches oLane (nothing written)')
# all three siblings still carried
for sib in ('G._fairTrade.lane=_slots[i]', 't.lane=_slots[i]'):
    if sib not in code:
        sys.exit('%s was lost (nothing written)' % sib)
# _famRefloatGhosts is untouched - the lane is fixed, not the reader
_rf = code.index('function _famRefloatGhosts')
if 'byLane[+g.dataset.lane]' not in code[_rf:_rf + 700]:
    sys.exit('_famRefloatGhosts changed - it should not have (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: the ghosts are the third carry')
