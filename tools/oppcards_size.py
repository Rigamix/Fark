# -*- coding: utf-8 -*-
u"""Sizing the generateOppCards stub lift. Measured before building.

RULED: lift it. The body below `return [];` is already written - 22 lines that
build a pool, shuffle, pick n, and guarantee a boss's signature card. So the
question is NOT "how do we write this". It is:

  DOES THE DEAD CODE STILL REFERENCE A WORLD THAT EXISTS?

It predates the P1 cutover and everything since. Three ways it can be stale, all
silent:

  1. EVERY id IN EVERY cardPool must resolve. getNpcCard returning undefined
     means the deal succeeds and the card does nothing - every consuming loop
     starts `var npc=getNpcCard(cid);if(!npc)return;`. A retired id in a pool is
     a card the boss "holds" that cannot ever act, and nothing logs it.
  2. THE FIELDS IT READS must still be there - rung.key, rung.cardCount,
     rung.cardChance, S.npcWonCards.
  3. THE MECHANICS THOSE CARDS CARRY must still have a dispatch branch. A card
     that resolves but whose mechanic no branch tests is the same silence one
     layer down.

Point 1 is the one that would bite hardest and looks like nothing. Point 3 is
where tonight's mechanic tables meet this: those tables are the branches, and
this measures whether the pooled cards actually reach them.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# ── every cardPool and the rung it belongs to ──
pools = []
for m in re.finditer(r'cardPool\s*:\s*\[([^\]]*)\]', s):
    ids = re.findall(r"'([a-z_0-9]+)'", m.group(1))
    head = s[max(0, m.start() - 700):m.start()]
    keys = re.findall(r"key\s*:\s*'([a-z_0-9]+)'", head)
    names = re.findall(r"name\s*:\s*'([^']+)'", head)
    pools.append((keys[-1] if keys else '?', names[-1] if names else '?', ids))

allids = sorted({i for _, _, ids in pools for i in ids})

# ── what the NPC card registry actually defines ──
defined = set()
for m in re.finditer(r"\{\s*id\s*:\s*'([a-z_0-9]+)'", s):
    defined.add(m.group(1))

missing = [i for i in allids if i not in defined]

print('CARD POOLS: %d rungs, %d distinct ids\n' % (len(pools), len(allids)))
print('%-18s %-22s %s' % ('rung key', 'name', 'pool'))
print('-' * 88)
for key, name, ids in pools:
    bad = [i for i in ids if i not in defined]
    mark = ('  <-- MISSING: ' + ', '.join(bad)) if bad else ''
    print('%-18s %-22s %s%s' % (key, name[:22], ', '.join(ids)[:40], mark))

print('\n' + '=' * 88)
print('1. UNRESOLVABLE IDS: %d of %d' % (len(missing), len(allids)))
if missing:
    print('   ' + ', '.join(missing))
else:
    print('   none - every pooled id has a definition')

# ── 2. the fields the dead code reads ──
print('\n2. FIELDS THE DEAD CODE READS:')
for field, pat in [('rung.key', r"key\s*:\s*'"), ('rung.cardCount', r'cardCount\s*:'),
                   ('rung.cardChance', r'cardChance\s*:'), ('S.npcWonCards', r'npcWonCards')]:
    n = len(re.findall(pat, s))
    print('   %-18s %s' % (field, ('%d occurrence(s)' % n) if n else 'ABSENT - dead code would break'))

# ── 3. do the pooled cards' mechanics have live branches? ──
print('\n3. MECHANICS THE POOLED CARDS CARRY, and whether a branch tests them:')
mechs = collections.Counter()
for cid in allids:
    m = re.search(r"\{\s*id\s*:\s*'" + cid + r"'", s)
    if not m:
        continue
    seg = s[m.start():m.start() + 900]
    for mm in re.finditer(r"mechanic\s*:\s*'([a-z_0-9]+)'", seg[:400]):
        mechs[mm.group(1)] += 1
        break
have = {m for m in re.findall(r"mechanic\s*===\s*'([a-z_0-9]+)'", s)}
orphan = [m for m in mechs if m not in have]
print('   %d distinct mechanics across the pools' % len(mechs))
print('   with a dispatch branch:    %d' % len([m for m in mechs if m in have]))
print('   WITHOUT one (orphans):     %d%s' % (len(orphan), ('  ' + ', '.join(orphan)) if orphan else ''))

print("""
READ 1 AND 3 TOGETHER. An unresolvable id is a card the boss holds that cannot
act. An orphan mechanic is a card that resolves and then does nothing. Both look
identical from a match - the boss simply plays worse than its card list claims -
and neither logs anything.""")
