# -*- coding: utf-8 -*-
u"""P919b: the roster of lane-stamped ghosts becomes a function, not a phrase.

WHAT THE FIRST HALF SHIPPED WAS A SECOND COPY. The carry needs the same set of
ghosts _famRefloatGhosts reads, and it got them by repeating that reader's
expression verbatim: [].concat(window._pkGhosts||[],window._htMarks||[]). Two
copies of a roster is precisely the failure the comment beside it was written to
prevent - "every lane-stamped thing enrols here" is an instruction to a person,
and a person adding a third ghost kind would add it to the reader, see the
floats work, and never learn that the carry has its own list.

So the roster is a function. _famLaneGhosts() is the only place the kinds are
named; the reader calls it and the carry calls it, and a fourth kind is one edit
that both consumers get by construction. The comment can then say something a
mechanism cannot - WHY they enrol - instead of standing in for one.

BEHAVIOUR IS UNCHANGED IN BOTH. Same array, same order, same filter. The only
new thing is that the filter for `g && g.dataset` now guards the reader too,
which it did not before - a member without a dataset would have thrown inside
its forEach and been swallowed by the try/catch, silently stopping the refloat
for every ghost after it.
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


# ── 1. the roster gets a name, and the reader uses it ────────────────
sub(u"""function _famRefloatGhosts(){
  try{
    var byLane={};(G&&G.pool||[]).forEach(function(d){if(d.el&&!d.committed)byLane[d.lane]=d;});
    [].concat(window._pkGhosts||[],window._htMarks||[]).forEach(function(g){""",
    u"""/* P919: THE LANE-STAMPED GHOSTS, IN ONE PLACE. Every element here carries a
   dataset.lane naming the die it belongs to, which means every one of them has
   to be repaired when a vagabond reorder renumbers the lanes - see the third
   entry in _commitVagabondDrag's carry loop, which calls this. Adding a kind to
   this list is therefore the whole job; the reader and the carry both follow.
   The two had separate copies of this expression for one patch and that was
   already one copy too many: a third kind added to the reader alone would look
   correct - the floats would track their die - right up until someone dragged
   a die, and then the mark would sit on a stranger. */
function _famLaneGhosts(){
  return [].concat(window._pkGhosts||[],window._htMarks||[])
    .filter(function(g){return g&&g.dataset;});
}
function _famRefloatGhosts(){
  try{
    var byLane={};(G&&G.pool||[]).forEach(function(d){if(d.el&&!d.committed)byLane[d.lane]=d;});
    _famLaneGhosts().forEach(function(g){""",
    '1 the roster is a function and the reader calls it')

# ── 2. and the carry calls it instead of holding a copy ──────────────
sub(u"""          var _ghosts=[].concat(window._pkGhosts||[],window._htMarks||[])
            .filter(function(g){return g&&g.dataset;});""",
    u"""          var _ghosts=(typeof _famLaneGhosts==='function')?_famLaneGhosts():[];""",
    '2 the carry calls the roster')

# ── post-asserts ─────────────────────────────────────────────────────
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)

# ONE DEFINITION, TWO CONSUMERS - the whole point of the patch
if code.count('function _famLaneGhosts(') != 1:
    sys.exit('the roster is not defined exactly once (nothing written)')
if code.count('_famLaneGhosts()') != 3:   # 1 def-body ref is 0; reader + carry + typeof guard
    sys.exit('the roster does not have exactly two callers (nothing written)')
# AND NO SURVIVING COPY of the expression it replaced - it may appear exactly
# once in the whole file now, inside the definition
if code.count('window._pkGhosts||[],window._htMarks||[]') != 1:
    sys.exit('a copy of the roster expression survives (nothing written)')
# the reader's lane lookup is untouched - this patch moves the roster, not the read
_rf = code.index('function _famRefloatGhosts')
if 'byLane[+g.dataset.lane]' not in code[_rf:_rf + 700]:
    sys.exit('the reader lost its lane lookup (nothing written)')
# and the carry still writes the lane, once, in the loop
_loop = code.index('_carry.forEach(function(c,i){')
region = code[code.rindex('var _tsBefore=', 0, _loop):code.index('c.die.lane=L;', _loop)]
if region.count('g.dataset.lane=String(') != 1 or region.count('_ghBefore') != 2:
    sys.exit('the carry no longer writes the lane once (nothing written)')
# THE DEFINITION MUST PRECEDE THE READER'S USE at load time; the carry's is
# guarded by typeof because it lives forty thousand lines later and a reorder
# cannot happen before the script has finished parsing anyway.
if code.index('function _famLaneGhosts(') > _rf:
    sys.exit('the roster is defined after the reader (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: one roster, two callers')
