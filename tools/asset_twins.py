# -*- coding: utf-8 -*-
"""PHASE 5, step two — which legacy paths already have a replacement?

asset_inventory.js proves every static path RESOLVES. That is a different
question from whether it points at the RIGHT file. A path into the previous
game's tree is not broken; it is stale, and stale is invisible — the picture
loads, it is just the wrong picture, or an older one nobody meant to ship.

This matches every live `assets/...` reference against the current tree by
filename stem (ignoring an `_opt` suffix, since the optimizer appends it), and
reports the ones that have a twin. Those are the candidates for rewiring — a
LIST FOR DENIS, not something to rewrite unattended: swapping a background is a
look change, not a refactor.

  python tools/asset_twins.py
"""
import io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

inv = json.loads(subprocess.check_output(
    ['node', 'tools/asset_inventory.js', '--json']).decode('utf-8'))

# index the current tree by lowercase stem
idx = {}
for root, dirs, files in os.walk(os.path.join(ROOT, 'Art', 'Assets')):
    for f in files:
        stem = re.sub(r'(_opt)?\.[a-z0-9]+$', '', f.lower())
        rel = os.path.relpath(os.path.join(root, f), ROOT).replace(os.sep, '/')
        idx.setdefault(stem, []).append(rel)

twins, orphans = [], []
for r in inv['legacy'] + inv['broken']:
    raw = r['raw']
    stem = re.sub(r'\.[a-z0-9]+$', '', os.path.basename(raw).lower())
    hit = idx.get(stem)
    (twins if hit else orphans).append((raw, r['count'], r['lines'][0], hit))

print('LEGACY PATHS WITH A TWIN IN THE CURRENT TREE — %d' % len(twins))
print('(the code points at the old file; a same-named file exists in Art/Assets)\n')
for raw, n, line, hit in sorted(twins):
    print('  %-46s x%-2d line %-6d -> %s' % (raw, n, line, hit[0]))

print('\nLEGACY PATHS WITH NO TWIN — %d' % len(orphans))
print('(nothing in the current tree answers to this name; these are the real')
print(' dependencies on the old folder, and fonts are most of them)\n')
groups = {}
for raw, n, line, _ in orphans:
    groups.setdefault('/'.join(raw.split('/')[:2]), []).append(raw)
for g in sorted(groups):
    print('  %-30s %d' % (g, len(groups[g])))
    for raw in sorted(groups[g])[:40]:
        print('      ' + raw)
