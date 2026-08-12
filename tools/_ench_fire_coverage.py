# -*- coding: utf-8 -*-
"""Does each icon enchant's fire() handler say anything?

The previous pass guessed at firing sites by grepping the enchant's id and
missed six of eight, then called zero_hour silent when it announces loudly from
_zeroHourClose - a function whose name contains none of the strings searched.
That was a broken instrument reporting findings, so this one reads the actual
handlers instead.

ENCH_ICONS is the table and every icon enchant resolves through its own
`fire:function(c){...}`. Slice each handler by brace-matching from `fire:` and
look inside it for a call that puts words on the table.
"""
import io, re

s = io.open('fark_proto.html', encoding='utf-8').read()
SPEAKS = ('famLog(', 'setStatusMsg(', '_famPop(', 'triggerCard(', 'spawnPop(')

start = s.index('var ENCH_ICONS={')
# brace-match the whole table
i, depth = s.index('{', start), 0
for j in range(i, len(s)):
    if s[j] == '{':
        depth += 1
    elif s[j] == '}':
        depth -= 1
        if depth == 0:
            table = s[i:j + 1]
            break

print('ENCH_ICONS table: %d chars\n' % len(table))

# each entry starts at "<id>:{" at depth 1
entries = []
depth = 0
for m in re.finditer(r'([a-z_]+)\s*:\s*\{', table):
    # depth of this match
    d = table[:m.start()].count('{') - table[:m.start()].count('}')
    if d == 1:
        entries.append((m.group(1), m.start()))

print('%d enchants in the table\n' % len(entries))
for k, (eid, pos) in enumerate(entries):
    end = entries[k + 1][1] if k + 1 < len(entries) else len(table)
    body = table[pos:end]
    fm = re.search(r'\bfire\s*:\s*function', body)
    if not fm:
        print('   ?? %-12s no fire() handler in its entry' % eid)
        continue
    b = body.index('{', fm.end() - 1)
    d2 = 0
    for j in range(b, len(body)):
        if body[j] == '{':
            d2 += 1
        elif body[j] == '}':
            d2 -= 1
            if d2 == 0:
                fire = body[b:j + 1]
                break
    hits = [k2 for k2 in SPEAKS if k2 in fire]
    print('   %s %-12s fire() %4d chars   %s'
          % ('  ' if hits else '!!', eid, len(fire), ', '.join(hits) or 'SILENT'))
