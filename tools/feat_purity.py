# -*- coding: utf-8 -*-
"""Phase 5 groundwork - do any feats actually grant power?

Phase 5's stated goal: "feats must never grant power - currently a rule we
remember, afterwards a thing the architecture won't allow."

BEFORE BUILDING THE ENFORCEMENT, MEASURE WHETHER THE RULE HOLDS TODAY. Every
phase here started with a reading rather than a design, and twice that reading
changed what got built (Trade out of the lane markers, endMatch out of the
run-scoped seams). The question is not "how do we enforce purity" but "is it
pure now, and where isn't it".

A feat is `{id, label, desc, renown, check:function(G){...}}`. `check` receives
the WHOLE game state, so nothing structurally prevents
`check:function(G){G.pPts+=1000;return true;}`. The rule is held by discipline
alone; this finds out whether discipline has held.

A WRITE IS TO GAME STATE, NOT TO A LOCAL. The first pass of this file matched
any `=` and flagged three feats whose bodies open with `var md=...` /
`var n=...` - local declarations, which are how a check reads anything at all.
All three were false positives of my own regex. So the pattern targets
assignments whose LEFT SIDE is G.something or S.something.

WHAT IT CANNOT SEE, stated so a clean run is not over-read: a check that calls
a helper which mutates. Direct writes and a short list of known state-changers
are covered; a feat calling something innocent-looking that writes inside would
pass. Clean here means clean of DIRECT writes, not proven pure.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

m = re.search(r'\nconst FEATS\s*=\s*\[', s)
assert m, 'FEATS not found'
i = s.index('[', m.end() - 1)
d, j = 0, i
while j < len(s):
    if s[j] == '[':
        d += 1
    elif s[j] == ']':
        d -= 1
        if d == 0:
            break
    j += 1
body = s[i:j + 1]

feats = []
for fm in re.finditer(r"\{id:'([a-z0-9_]+)'", body):
    k = fm.start()
    d2, e = 0, k
    while e < len(body):
        if body[e] == '{':
            d2 += 1
        elif body[e] == '}':
            d2 -= 1
            if d2 == 0:
                break
        e += 1
    feats.append((fm.group(1), body[k:e + 1]))

MUTATORS = ('save(', 'famLog(', 'setStatusMsg(', 'spawnPop(', 'updHUD(',
            '_famPop(', 'triggerCard(', 'famBurn(', '_rubOutCircles(')
TARGET = r'[GS]\.[A-Za-z_$][\w$.]*(?:\[[^\]]*\])?'
WRITE = re.compile(TARGET + r'\s*(?:=(?!=)|\+\+|--|\+=|-=|\*=)'
                   r'|delete\s+' + TARGET)

print('feats: %d\n' % len(feats))
dirty, nocheck = [], []
for fid, blob in feats:
    cm = re.search(r'check\s*:\s*function\s*\([^)]*\)\s*\{', blob)
    if not cm:
        nocheck.append(fid)
        continue
    b = blob.index('{', cm.end() - 1)
    d3, e = 0, b
    while e < len(blob):
        if blob[e] == '{':
            d3 += 1
        elif blob[e] == '}':
            d3 -= 1
            if d3 == 0:
                break
        e += 1
    cbody = re.sub(r'/\*.*?\*/', '', blob[b + 1:e], flags=re.S)
    writes = WRITE.findall(cbody)
    calls = [x for x in MUTATORS if x in cbody]
    if writes or calls:
        dirty.append((fid, writes[:4], calls, re.sub(r'\s+', ' ', cbody)[:76]))

if nocheck:
    print('feats with NO check function: %s\n' % ', '.join(nocheck))

if not dirty:
    print('NO FEAT WRITES GAME STATE in its check body.')
    print('The rule has held on discipline alone across %d feats.\n' % len(feats))
    print('So Phase 5 is not a REPAIR. It makes an invariant that is currently')
    print('TRUE impossible to break later - a different and easier job than')
    print('fixing violations, and worth knowing before designing for violations')
    print('that do not exist.')
else:
    print('FEATS THAT WRITE GAME STATE (%d):' % len(dirty))
    for fid, w, c, snip in dirty:
        print('  %-22s writes=%s calls=%s' % (fid, w, c))
        print('      %s' % snip)

print('')
print('LIMIT: direct writes and known mutator calls only. A check calling a')
print('helper that mutates would pass this. Clean means clean of DIRECT writes.')
