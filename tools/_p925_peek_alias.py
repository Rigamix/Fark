# -*- coding: utf-8 -*-
u"""P925: the peek snapshot ALIASED the live records, and P922 made that matter.

THE HAZARD P922 INTRODUCED. saveMatchState stores

    famPeekVals:Array.isArray(G._famPeekVals)?G._famPeekVals.slice():null,

and the restore reads it back the same way. The entries are {lane,val} OBJECTS,
so .slice() copies REFERENCES. That was harmless for as long as nothing wrote
p.lane after mint - and P922's carry writes exactly that, in place, on every
vagabond reorder. So a snapshot taken at a turn boundary aliases the live
records and silently drifts with a reorder that happens after the save.

saveMatchState is called from startPTurn, so the window is every turn boundary:
snapshot, player reorders, the snapshot's lanes move too, and a resume in
between restores post-reorder lanes against a pre-reorder pool - the promise
lands on the wrong die, which is the P922 bug re-entering through the save.

THE FILE SHOWS THE INTENDED PATTERN ONE LINE ABOVE. famIllOmen, directly above,
is JSON.parse(JSON.stringify(...)). So is _tradeSwaps at 12017, so is
famPreserve at 12068, so is ftDead. _fairTrade uses {...} - a flat object whose
lane is copied BY VALUE, which is safe. famPeekVals was the only lane-bearing
record copied shallowly, and it is the only one that is an ARRAY OF OBJECTS,
which is exactly the shape .slice() fails to protect.

BOTH DIRECTIONS ARE FIXED, not just the save. The restore had the same shape, so
a restored match's live records aliased the saved snapshot and the next reorder
mutated the save. A snapshot that changes after it is taken is not a snapshot in
either direction.

FIXED AT THE COPY, NOT AT THE MUTATOR. P922's in-place write is the correct
shape - the carry has to move the live record - so the repair belongs where the
snapshot is made. That also covers every future writer of p.lane rather than
only the one that exists today.
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


sub(u"""  famPeekVals:Array.isArray(G._famPeekVals)?G._famPeekVals.slice():null,""",
    u"""  /* P925: DEEP, like famIllOmen on the line above. The entries are {lane,val}
     objects, so .slice() copied references - harmless while nothing wrote
     p.lane after mint, and P922's reorder carry writes exactly that, in place.
     A shallow copy meant the snapshot aliased the live records and drifted with
     any reorder that happened after the save; saveMatchState runs from
     startPTurn, so that window was every turn boundary. Every other
     lane-bearing record here is already deep (_tradeSwaps, famPreserve, ftDead)
     or flat-by-value (_fairTrade); this was the only array of objects. */
  famPeekVals:Array.isArray(G._famPeekVals)
    ?JSON.parse(JSON.stringify(G._famPeekVals)):null,""",
    '1 the save deep-copies')

sub(u"""  if(_rdFam.famPeekVals!==undefined)
    G._famPeekVals=Array.isArray(_rdFam.famPeekVals)?_rdFam.famPeekVals.slice():[];""",
    u"""  if(_rdFam.famPeekVals!==undefined)
    /* P925: and the restore too - the same shape in the other direction. A
       shallow restore left the LIVE records aliasing the saved snapshot, so the
       next reorder mutated the save. A snapshot that changes after it is taken
       is not a snapshot in either direction. */
    G._famPeekVals=Array.isArray(_rdFam.famPeekVals)
      ?JSON.parse(JSON.stringify(_rdFam.famPeekVals)):[];""",
    '2 the restore deep-copies')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# no shallow copy of the peek array survives, in either direction
if re.search(r'famPeekVals\s*\)\s*\?\s*\w*\.?_?famPeekVals\.slice\(\)', code) or \
   'G._famPeekVals.slice()' in code or '_rdFam.famPeekVals.slice()' in code:
    sys.exit('a shallow copy of famPeekVals survives (nothing written)')
# both sites are deep now
if code.count('JSON.stringify(G._famPeekVals)') != 1:
    sys.exit('the save is not deep exactly once (nothing written)')
if code.count('JSON.stringify(_rdFam.famPeekVals)') != 1:
    sys.exit('the restore is not deep exactly once (nothing written)')
# the neighbour that showed the pattern is untouched
if code.count('G._famIllOmen?JSON.parse(JSON.stringify(G._famIllOmen)):null') != 1:
    sys.exit('the famIllOmen neighbour was disturbed (nothing written)')
# and P922's carry still writes the live record in place - the fix is at the
# copy, not at the mutator
_loop = code.index('_carry.forEach(function(c,i){')
if code[code.rindex('var _recs=', 0, _loop):code.index('c.die.lane=L;', _loop)] \
        .count('r.lane=_slots[i]') != 1:
    sys.exit('the carry no longer writes the record in place (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
