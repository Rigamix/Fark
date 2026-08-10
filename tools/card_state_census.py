# -*- coding: utf-8 -*-
"""Does the CARD layer lose state across a save/resume, the way the DICE layer did?

THE QUESTION. The dice-lane sweep found the same bug four separate times: a
field added to the live game and never added to the snapshot, so a resume either
dropped it or regenerated it at full strength. P511 (family charges refunded
4 -> 2 -> 4), P532 (`oLane`/`seatGone` silently un-shipped P527), P537 (the
preserve nulled before the snapshot read it), P540 (`sealRule`). The card layer
was never swept for it, and the integrity plan calls that the largest gap.

WHY A TOOL AND NOT A HAND LIST. The plan's own standing ask. A hand list of
"the fields I thought of" is the instrument that produced four separate misses;
this enumerates from the source and reports the whole domain with its
denominator, so a field added tomorrow shows up as uncovered rather than as
nothing at all.

WHAT IT WILL NOT TELL YOU, stated because a clean row here is not a clean bill:

  * TURN-SCOPED IS NOT A BUG. A field that startPTurn or doBust resets is
    SUPPOSED to be absent from the snapshot - carrying it would restore a stale
    value into a fresh turn. The column says which, it does not judge.
  * A WRITE IS NOT ONLY `=`. `G._oTarPit--` is a write, and a census that
    matched assignment alone reported that field as never written, which is a
    finding-shaped artifact. Every mutation form is matched here.
  * A FIELD WITH NO WRITER MAY BE DELIBERATE. G._oTarPit and G._famTarPit have
    no writer because Tar Pit is RETIRED, and the code says so in a comment at
    the arming site. Read the site before calling it dead.

Run: python tools/card_state_census.py
"""
import io, re, sys, json

SRC = io.open('fark_proto.html', encoding='utf-8', newline='').read()
LINES = SRC.split('\n')


def line_of(pos):
    return SRC.count('\n', 0, pos) + 1


def body_of(start_line, max_lines=900):
    """Text of a function from its `function NAME` line to its closing brace,
    tracked by depth rather than by a blank-line or indentation guess - the
    file has both inside these functions."""
    i = start_line - 1
    depth, started, out = 0, False, []
    while i < len(LINES) and i < start_line - 1 + max_lines:
        out.append(LINES[i])
        for ch in LINES[i]:
            if ch == '{':
                depth += 1
                started = True
            elif ch == '}':
                depth -= 1
        if started and depth <= 0:
            break
        i += 1
    return '\n'.join(out)


def find_fn(name):
    m = re.search(r'^function\s+' + re.escape(name) + r'\s*\(', SRC, re.M)
    return line_of(m.start()) if m else None


# ── the three regions a field's fate is decided in ────────────────────────
SNAP_START = None
m = re.search(r'\n(\s*)_resumeData\s*:\s*snap', SRC)
if m:
    # walk back to the start of the object literal this sits in
    SNAP_START = line_of(m.start())
snap_fn = find_fn('_snapshotMatch') or find_fn('snapshotMatch')
# the snapshot is built as `var snap = {...}` before _resumeData:snap - take a
# generous window ending there and let the field search be exact
SNAP_TEXT = '\n'.join(LINES[max(0, (SNAP_START or 1) - 400):(SNAP_START or 1) + 5])

# the resume side: every `params._resumeData` reader, widened to the block
RESUME_TEXT = '\n'.join(LINES[32980:33240])

NEWG_TEXT = body_of(find_fn('newG')) if find_fn('newG') else ''

# ── WHICH FUNCTION DOES EACH WRITE LIVE IN ────────────────────────────────
# The first version of this census hard-coded the turn-reset functions as
# startPTurn / _turnTableClear / doBust and reported 37 of 48 fields as
# match-scoped and unsaved. That number was an artifact: most of them are the
# RIVAL's, and the rival's per-turn state is reset at the top of runOppTurn,
# which the list did not contain. A hand-listed set of "the functions I thought
# of" is the same instrument that produced the misses this sweep exists to find.
# So the enclosing function is DERIVED per write site, and turn-scope is decided
# from that rather than from a list.
FN_STARTS = [(line_of(m.start()), m.group(1))
             for m in re.finditer(r'^function\s+([A-Za-z0-9_$]+)\s*\(', SRC, re.M)]
FN_STARTS.sort()


def enclosing(line):
    lo, name = 0, '(top level)'
    for ln, nm in FN_STARTS:
        if ln <= line:
            lo, name = ln, nm
        else:
            break
    return name


# a write inside one of these is a per-turn reset, not carried state
TURN_FNS = set()
for nm in ('startPTurn', '_turnTableClear', 'doBust', 'runOppTurn', 'finOpp',
           'startOTurn', 'endPTurn', 'oppTurn'):
    if any(n == nm for _, n in FN_STARTS):
        TURN_FNS.add(nm)

# ── the domain: every G._field the card/family layer touches ──────────────
FIELDS = sorted(set(re.findall(r'G\.(_(?:fam|f[A-Z]|o[A-Z]|rs|npcCard)[A-Za-z0-9_]*)', SRC)))

WRITE = r'G\.%s\s*(?:=[^=]|\+\+|--|\+=|-=|\|\|=)|G\.%s\s*=\s*$|delete\s+G\.%s\b'


def writes(f):
    pat = re.compile(r'G\.' + re.escape(f) + r'\s*(?:=(?!=)|\+\+|--|\+=|-=)')
    return [line_of(m.start()) for m in pat.finditer(SRC)]


def refs(f):
    return [line_of(m.start()) for m in re.finditer(r'G\.' + re.escape(f) + r'\b', SRC)]


rows = []
for f in FIELDS:
    w, r = writes(f), refs(f)
    wfns = sorted(set(enclosing(x) for x in w))
    in_snap = (f in SNAP_TEXT) or (f.lstrip('_') in SNAP_TEXT)
    in_resume = f in RESUME_TEXT
    # reset every turn somewhere => a resume is SUPPOSED to lose it
    turn_cleared = any(fn in TURN_FNS for fn in wfns)
    # and the sharper question: is there a write OUTSIDE the reset functions?
    # a field only ever written by its own reset carries nothing across a turn.
    live_writes = [x for x in w if enclosing(x) not in TURN_FNS]
    born_in_newg = bool(re.search(r'\b' + re.escape(f.lstrip('_')) + r'\s*:', NEWG_TEXT))
    rows.append(dict(field=f, writes=len(w), refs=len(r), writeLines=w[:6],
                     writeFns=wfns, liveWrites=live_writes,
                     inSnapshot=in_snap, inResume=in_resume,
                     turnCleared=turn_cleared, inNewG=born_in_newg))

# ── report ───────────────────────────────────────────────────────────────
print('card/family state fields: %d' % len(rows))
print('%-26s %5s %5s %5s %5s %5s %5s' % ('field', 'wr', 'rd', 'snap', 'resum', 'turn', 'newG'))
for x in rows:
    print('%-26s %5d %5d %5s %5s %5s %5s' % (
        x['field'], x['writes'], x['refs'],
        'Y' if x['inSnapshot'] else '.', 'Y' if x['inResume'] else '.',
        'Y' if x['turnCleared'] else '.', 'Y' if x['inNewG'] else '.'))

# THE ONES THAT MATTER: written somewhere, not reset each turn, not in the
# snapshot. Those are the ones a resume silently changes.
at_risk = [x for x in rows if x['liveWrites'] and not x['turnCleared'] and not x['inSnapshot']]
print('\nMATCH-SCOPED AND NOT SNAPSHOTTED (%d of %d):' % (len(at_risk), len(rows)))
for x in at_risk:
    print('  %-26s written in %s  (lines %s)'
          % (x['field'], ','.join(x['writeFns']), x['liveWrites'][:5]))

carried = [x for x in rows if x['turnCleared'] and x['liveWrites'] and not x['inSnapshot']]
print('\nRESET EACH TURN *AND* WRITTEN ELSEWHERE (%d) - the mixed ones, read these:' % len(carried))
for x in carried:
    print('  %-26s reset in %s; also written at %s'
          % (x['field'],
             ','.join(fn for fn in x['writeFns'] if fn in TURN_FNS),
             x['liveWrites'][:5]))
print('\nA row here is a CANDIDATE, not a defect - confirm each by reading the')
print('write site and by driving a real save/resume. Fields with no writer may')
print('be retired on purpose (G._oTarPit is, and says so at its arming site).')
io.open('docs/CARD_STATE_CENSUS.json', 'w', encoding='utf-8').write(json.dumps(rows, indent=1))
