# -*- coding: utf-8 -*-
"""Where do the five match-scoped group-2 cards actually live today?

They have no CFX entry, so their behaviour is hardcoded somewhere. Migrating
them means moving that somewhere onto the bus, which requires knowing exactly
what and where it is - not "roughly in the scoring path".

Uses cfx_bespoke's blanking so the sites reported are real code: /* */ comments
blanked (prose naming a card is not an implementation) and the FSIM harness
blanked (it re-implements scoring on purpose - `cs.ids.bloom` there is the
simulator modelling the card, not the game duplicating it). Without both, this
returns mostly noise; that was measured, not assumed.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
raw = io.open(SRC, encoding='utf-8').read()

def blank_comments(t):
    out = list(t)
    for m in re.finditer(r'/\*.*?\*/', t, re.S):
        for i in range(m.start(), m.end()):
            if out[i] != '\n':
                out[i] = ' '
    return ''.join(out)

SIM = raw.find('BALANCE SIM HARNESS')
assert SIM > 0
s = blank_comments(raw)
s = s[:SIM] + re.sub(r'[^\n]', ' ', s[SIM:])

scopes = []
for m in re.finditer(r'\bfunction\s*([A-Za-z_$][\w$]*)?\s*\(', s):
    b = s.find('{', m.end())
    if b < 0:
        continue
    d, j = 0, b
    while j < len(s):
        if s[j] == '{': d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                break
        j += 1
    scopes.append((m.start(), j, m.group(1)))

def enclosing(pos):
    best, span = None, None
    for a, b, nm in scopes:
        if a <= pos <= b and nm and (span is None or b - a < span):
            best, span = nm, b - a
    return best

FIVE = ['bloom', 'cultivate', 'vanguard_f', 'for_keeps', 'tar_pit']
for cid in FIVE:
    print('\n' + '=' * 74)
    print(cid)
    print('=' * 74)
    hits = list(re.finditer(r'(?<![\w-])' + re.escape(cid) + r'(?![\w-])', s))
    if not hits:
        print('  NO CODE SITES AT ALL - nothing implements this card.')
        continue
    for m in hits:
        ln = s[:m.start()].count('\n') + 1
        fn = enclosing(m.start()) or '(top level)'
        ls = raw.rfind('\n', 0, m.start()) + 1
        le = raw.find('\n', m.start())
        line = raw[ls:le if le > 0 else len(raw)].strip()
        kind = 'def' if ("{id:'" + cid + "'") in line else (
               'live' if re.search(r'FAM_LIVE', line) or re.search(
                   r'(?<![\w-])' + re.escape(cid) + r"\s*:\s*1\b", line) else
               'str' if re.search(r"['\"][^'\"]*(?<![\w-])" + re.escape(cid) +
                                  r"(?![\w-])[^'\"]*['\"]", line) else 'CODE')
    	# also catch the array-forEach live table
        if kind == 'CODE' and 'FAM_LIVE[id]=1' in line:
            kind = 'live'
        print('  %-5s %-6d %-22s %s' % (kind, ln, fn, line[:88]))
