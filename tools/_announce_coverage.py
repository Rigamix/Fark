# -*- coding: utf-8 -*-
"""Which effect families announce themselves, and which are silent?

Denis: "This text should also be part of the audit for card and dice, enchant
effects. It should all follow the same pipeline. Same with badge effects in boss
matches or cursed matches."

famLog -> _famAnnounce -> setStatusMsg is the pipeline. The question is which
families reach it. For each family, find where its effects live and count the
ones whose body contains a call that puts words on the table.
"""
import io, re

s = io.open('fark_proto.html', encoding='utf-8').read()
lines = s.split('\n')

SPEAKS = ('famLog(', 'setStatusMsg(', '_famPop(', 'triggerCard(', 'spawnPop(')


def body_of(start_idx, stop_re):
    """lines from start until the next line matching stop_re (or +90)"""
    out = []
    for j in range(start_idx, min(start_idx + 90, len(lines))):
        if j > start_idx and stop_re.match(lines[j]):
            break
        out.append(lines[j])
    return '\n'.join(out)


def report(title, entries):
    silent = [e for e in entries if not e[1]]
    print('%s  —  %d entries, %d silent' % (title, len(entries), len(silent)))
    for name, spoke in entries:
        print('   %s %s' % ('  ' if spoke else '!!', name))
    print()


# ── family cards: CFX.<id> ───────────────────────────────────────────────
stop = re.compile(r'^CFX\.[a-z_0-9]+\s*=')
cfx = []
for i, l in enumerate(lines):
    m = re.match(r'CFX\.([a-z_0-9]+)\s*=', l)
    if m:
        b = body_of(i, stop)
        cfx.append((m.group(1), any(k in b for k in SPEAKS)))
report('FAMILY CARDS (CFX)', cfx)

# ── enchantments ─────────────────────────────────────────────────────────
# find the enchant table and the sites that apply one
ench_ids = sorted(set(re.findall(r"ench\s*:\s*\{\s*t\s*:\s*'([a-z_]+)'", s)))
print('ENCHANT ids seen in code: %s' % (', '.join(ench_ids) or '(none found)'))
for eid in ench_ids:
    hits = [i for i, l in enumerate(lines) if eid in l]
    spoke = any(any(k in lines[i] for k in SPEAKS) for i in hits)
    near = any(any(k in lines[max(0, i - 3):i + 4][j] for k in SPEAKS)
               for i in hits for j in range(len(lines[max(0, i - 3):i + 4])))
    print('   %s %-14s %d sites, speaks near a site: %s'
          % ('  ' if near else '!!', eid, len(hits), near))
print()

# ── tell / badge rules ───────────────────────────────────────────────────
pool = re.search(r"var _SEAL_POOL=\[([^\]]*)\]", s)
ids = re.findall(r"'([a-z_]+)'", pool.group(1)) if pool else []
print('TELL/BADGE rules in _SEAL_POOL: %d' % len(ids))
for rid in ids:
    hits = [i for i, l in enumerate(lines) if "'" + rid + "'" in l]
    near = False
    for i in hits:
        w = '\n'.join(lines[max(0, i - 4):i + 8])
        if any(k in w for k in SPEAKS):
            near = True
            break
    print('   %s %-14s %d sites' % ('  ' if near else '!!', rid, len(hits)))
