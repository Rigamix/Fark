# -*- coding: utf-8 -*-
"""What do the 23 feat checks actually READ?

The enforcement shape for Phase 5 depends on this and nothing else. Three
candidates, and the measurement picks between them rather than taste:

  A NARROW FACADE - an object exposing only the fields feats use, getters only.
    Right if the reads are a small, stable set. Strongest guarantee: a feat
    cannot even NAME anything else, so the invariant holds by vocabulary.
  A FROZEN SNAPSHOT - Object.freeze over a shallow copy.
    Right if the reads are wide but flat. Weaker: freeze is shallow, so a
    nested object stays mutable and the guarantee quietly does not hold.
  A PROXY that throws on set.
    Right if reads are unpredictable. Weakest to reason about and the only one
    that fails at RUNTIME rather than at authoring time.

The direct-write scan (feat_purity.py) says no check writes state today, but it
also says what it cannot see: a check calling a helper that mutates. A facade
closes that gap by construction - a helper cannot be called with state the
check never received. Freeze and proxy do not close it at all, because the
check could still reach the real G through a closure or a global.

That is the argument for the facade, and this file tests whether the content
allows it.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

m = re.search(r'\nconst FEATS\s*=\s*\[', s)
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

gfields, sfields, globals_used, calls = {}, {}, {}, {}
KNOWN_GLOBALS = ('DICE_TYPES', 'FAM_CARDS', 'TIERS', 'CARDS', 'FEATS',
                 'DICE_MAP', 'FAMILIES')
for fid, blob in feats:
    cm = re.search(r'check\s*:\s*function\s*\([^)]*\)\s*\{', blob)
    if not cm:
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
    cb = re.sub(r'/\*.*?\*/', '', blob[b + 1:e], flags=re.S)
    for f in re.findall(r'\bG\.([A-Za-z_$][\w$]*)', cb):
        gfields.setdefault(f, set()).add(fid)
    for f in re.findall(r'\bS\.([A-Za-z_$][\w$]*)', cb):
        sfields.setdefault(f, set()).add(fid)
    for g in KNOWN_GLOBALS:
        if re.search(r'\b' + g + r'\b', cb):
            globals_used.setdefault(g, set()).add(fid)
    for c in re.findall(r'\b([A-Za-z_$][\w$]*)\s*\(', cb):
        if c in ('function', 'if', 'for', 'while', 'return', 'typeof'):
            continue
        calls.setdefault(c, set()).add(fid)

def show(title, dct):
    print('\n%s (%d)' % (title, len(dct)))
    for k, v in sorted(dct.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        print('  %-26s %2d feat(s)  %s' % (k, len(v), ', '.join(sorted(v))[:52]))

show('G FIELDS READ', gfields)
show('S FIELDS READ', sfields)
show('MODULE GLOBALS REACHED', globals_used)
show('FUNCTIONS CALLED', calls)

print('\n' + '=' * 74)
print('VERDICT INPUT: %d distinct G fields, %d S fields, %d globals, %d calls.'
      % (len(gfields), len(sfields), len(globals_used), len(calls)))
print('A facade is viable if the G/S sets are small and stable. Anything a')
print('check REACHES PAST its argument - a module global, a called helper - is')
print('a hole a facade cannot close on its own, and has to be listed here')
print('rather than discovered later.')
