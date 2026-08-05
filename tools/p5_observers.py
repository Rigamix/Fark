# -*- coding: utf-8 -*-
u"""Phase 5 - Observers. How much of the layer is actually structurally gated?

THE PLAN'S CLAIM: "Structurally enforces 'feats must never grant power' -
currently a rule we remember, afterwards a thing the architecture won't allow."

_featView(G) already exists: a facade over G that a Proxy makes throw on set and
delete. So the mechanism is built. The question Phase 5 actually turns on is
COVERAGE - a guard that one caller bypasses enforces nothing, and the rule goes
back to being remembered.

THREE THINGS MEASURED, and the third is the one that decides the phase:

  1. FEATS      does every feat `check:` receive the view, or does any get raw G?
  2. DIALOGUE   the trait-reaction layer is the plan's other half. Does it read
                state through anything comparable, or straight off G?
  3. THE HOLES  _featView copies a fixed field list. A field NOT copied reads
                undefined inside a check - which is not a throw, it is a silent
                false. That is worse than an ungated read, because the feat
                simply never fires and nothing says why.

POINT 3 IS THE TRAP. The Proxy protects against WRITES. Nothing protects against
a check reading a field the facade forgot, and the failure looks exactly like a
feat whose condition was not met - the same shape as the try/catch swallowing
deadRoll and the null-resolving card id.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# ── the view itself: which fields does it carry? ──
m = re.search(r'function\s+_featView\s*\(', s)
view_fields = set()
if m:
    b = s.index('{', m.end() - 1)
    d, j = 0, b
    while j < len(s):
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                break
        j += 1
    vbody = s[b:j + 1]
    # THE FIELDS ARE A STRING ARRAY WALKED BY forEach, not `key: G.x` pairs.
    # A first version regexed for the pair form, found ONE field, and duly
    # reported 19 of 23 checks reading something the view "does not carry" -
    # every one of which was in the list. A missing-field count computed from a
    # field list of size one is not a finding.
    view_fields = set(re.findall(r"'(\w+)'", vbody))
    view_fields |= set(re.findall(r'v\.(\w+)\s*=', vbody))
print('_featView carries %d fields:' % len(view_fields))
print('   ' + ', '.join(sorted(view_fields)) or '   (none found)')

# ── every feat check, and what it reads off its argument ──
checks = []
for cm in re.finditer(r'check\s*:\s*function\s*\(\s*(\w+)\s*\)\s*\{', s):
    arg = cm.group(1)
    b = s.index('{', cm.end() - 1)
    d, j = 0, b
    while j < len(s):
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                break
        j += 1
    body = s[b:j + 1]
    reads = set(re.findall(re.escape(arg) + r'\.(\w+)', body))
    head = s[max(0, cm.start() - 300):cm.start()]
    ids = re.findall(r"id\s*:\s*'([a-z_0-9]+)'", head)
    checks.append((ids[-1] if ids else '?', arg, reads))

print('\nFEAT CHECKS: %d' % len(checks))
missing = {}
for fid, arg, reads in checks:
    gap = sorted(r for r in reads if view_fields and r not in view_fields)
    if gap:
        missing[fid] = gap
print('   reading a field the view does NOT carry: %d' % len(missing))
for fid, gap in list(missing.items())[:12]:
    print('     %-22s %s' % (fid, ', '.join(gap)))

# ── who calls the checks, and with what ──
print('\nHOW CHECKS ARE INVOKED:')
for cm in re.finditer(r'\.check\s*\(([^)]*)\)', s):
    ls = s.rfind('\n', 0, cm.start()) + 1
    line = re.sub(r'\s+', ' ', s[ls:s.find('\n', cm.start())]).strip()
    gated = '_featView' in cm.group(1)
    print('   %-9s %s' % ('VIEW' if gated else 'RAW G', line[:88]))

# ── the dialogue layer ──
print('\nDIALOGUE TRAIT-REACTION LAYER:')
dlg_reads = len(re.findall(r'DLG\.\w+', s))
dlg_view = len(re.findall(r'_featView\s*\([^)]*\)\s*\)?\s*;?\s*/\*\s*DLG', s))
print('   DLG call sites: %d' % dlg_reads)
print('   any equivalent read-only facade: %s'
      % ('yes' if dlg_view else 'NO - reads state directly'))

print("""
A GUARD ONE CALLER BYPASSES ENFORCES NOTHING. If any invocation passes raw G,
the architecture does not forbid a feat granting power - it just makes it
awkward, which is the same as the rule being remembered.""")
