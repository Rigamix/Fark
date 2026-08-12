# -*- coding: utf-8 -*-
"""Do the eight enchantments say anything when they fire?

ENCH_GRID is the roster. For each, find every site that tests it firing -
ench.t==='<id>' or a case '<id>' - and look for a call that puts words on the
table within the surrounding block. Reported per SITE, not as a yes/no, because
an enchant can announce on one path and be silent on another and a single
boolean would hide that.
"""
import io, re

s = io.open('fark_proto.html', encoding='utf-8').read()
lines = s.split('\n')
SPEAKS = ('famLog(', 'setStatusMsg(', '_famPop(', 'triggerCard(', 'spawnPop(')

m = re.search(r"var ENCH_GRID=\[([^\]]*)\]", s)
ids = re.findall(r"'([a-z_]+)'", m.group(1)) if m else []
print('%d enchantments: %s\n' % (len(ids), ', '.join(ids)))

for eid in ids:
    pats = ["ench.t==='%s'" % eid, "ench&&x.ench.t==='%s'" % eid,
            "case '%s'" % eid, "'%s'" % eid]
    sites = []
    for i, l in enumerate(lines):
        if ("'%s'" % eid) not in l:
            continue
        # only sites that look like the enchant FIRING, not table/art/label rows
        if not re.search(r"ench|ENCH|case\s*'%s'" % eid, l):
            continue
        if re.search(r"ENCH_ICONS|ENCH_GRID|ENCH_LABEL|ENCH_ICON_DIR", l):
            continue
        window = '\n'.join(lines[max(0, i - 6):i + 14])
        sites.append((i + 1, any(k in window for k in SPEAKS)))
    if not sites:
        print('   ?? %-12s no firing site matched — check by hand' % eid)
        continue
    speaks = sum(1 for _, sp in sites if sp)
    flag = '  ' if speaks == len(sites) else ('!!' if speaks == 0 else ' ~')
    print('   %s %-12s %d firing sites, %d announce   %s'
          % (flag, eid, len(sites), speaks,
             ' '.join(('%d%s' % (ln, '' if sp else '*')) for ln, sp in sites[:8])))
print('\n(* = that site has no announcement in its block)')
