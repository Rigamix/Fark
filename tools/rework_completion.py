# -*- coding: utf-8 -*-
"""Rework completion, counted per category against the Phase 1 inventory.

The 69-item denominator is unchanged; only classifications have moved. Counted
here per category, never as one blended number - and if a blend is wanted the
arithmetic is printed so it can be checked rather than trusted.

WHAT COUNTS AS "ON SHARED MACHINERY", stated per category because it is not the
same mechanism for each, and pretending it is would be the mistake this whole
rework has been removing:

  family cards   a CFX[id] entry - the effect bus, plus the commit hook
  enchants       state managed through _lm* (arm/due/spend/retire)
  break rows     an entry in BREAK_TRIGGERS, which is ONE keyed table with ONE
                 dispatch site
  table rules    reached through _ruleActive(id,side) rather than by reading
                 G._tell.id directly
  relics         effect.mechanic dispatched by a shared handler
  materials      same

AND THE TEST FOR "SHARED" IS NOT "A TABLE EXISTS". A 50-arm switch in one
function is a dispatcher; fifty `if(mechanic===...)` checks scattered across
twenty functions is bespoke wearing a data field. So mechanic dispatch is
measured the same way the seams were: how many DISTINCT enclosing functions
contain the branches. One or two is a dispatcher. Twenty is not.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

scopes = []
for m in re.finditer(r'\bfunction\s*([A-Za-z_$][\w$]*)?\s*\(', s):
    b = s.find('{', m.end())
    if b < 0:
        continue
    d, j = 0, b
    while j < len(s):
        if s[j] == '{':
            d += 1
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

def block(txt, start):
    b = txt.index('{', start)
    d, j = 0, b
    while j < len(txt):
        if txt[j] == '{':
            d += 1
        elif txt[j] == '}':
            d -= 1
            if d == 0:
                return txt[b:j + 1]
        j += 1
    return ''

# ── is mechanic dispatch shared or scattered? ──
fns = collections.Counter()
for m in re.finditer(r"mechanic\s*===\s*'([a-z_]+)'", s):
    fns[enclosing(m.start()) or '(top)'] += 1
print('MECHANIC DISPATCH: %d branches across %d functions' % (sum(fns.values()), len(fns)))
for f, n in fns.most_common(6):
    print('   %-28s %d' % (f, n))
shared_mech = len(fns) <= 2
print('   -> %s\n' % ('ONE DISPATCHER (shared)' if shared_mech
                      else 'SCATTERED across %d functions - bespoke' % len(fns)))

# ── per category ──
cfx = set(re.findall(r'\bCFX\.([A-Za-z_][\w]*)\s*=\s*\{', s))
# THE FAMILY-CARD ROW COMES FROM THE PAGE, NOT FROM THIS FILE. Parsing FAM_LIVE
# statically gave 22 live cards against the inventory's 29, and included
# anchor_f and bookends_f - FAM_LIVE keys for cards CUT from FAM_CARDS, so they
# are live flags pointing at nothing. The game's own answer is
# FAM_CARDS.filter(d => FAM_LIVE[d.id]), evaluated in-page:
#     live 29, on CFX 23, off 6
# and the six off are exactly the run-scoped six ruled off the match bus.
# Reporting the static number would have understated the denominator by 7 AND
# named two cut cards as unmigrated work.
FAM_LIVE_COUNT, FAM_ON_BUS = 29, 23
FAM_OFF = ['for_keeps', 'double_stakes', 'the_tab', 'hair_of_the_dog',
           'marked_table', 'high_table']
STALE_FAM_LIVE = ['anchor_f', 'bookends_f']

ENCH = ['tithe', 'ward', 'snare', 'break', 'trade', 'snuff', 'fog', 'quicksilver']
lm_backed = set()
for e in ENCH:
    if re.search(r"_lmArm\('_" + e + r"'", s) or re.search(r"_lm(Due|Spend|Retire)\('_" + e + r"'", s):
        lm_backed.add(e)

RULES = ['last_call', 'zero_hour', 'pickpocket', 'first_strike', 'drill_order',
         'still_waters', 'kindred', 'reckoning', 'steeped']
rule_shared = {r for r in RULES if re.search(r"_ruleActive\('" + r + r"'", s)}

bt = re.search(r'\bvar BREAK_TRIGGERS\s*=\s*\{', s)
break_rows = re.findall(r"([a-z0-9_]+)\s*:\s*\{", block(s, bt.end() - 1)) if bt else []
bt_sites = len(re.findall(r'BREAK_TRIGGERS\[', s))

RELICS = ['grogs_tooth', 'mabels_thimble', 'finnicks_palm', 'corvus_ledger_d',
          'brutus_shield', 'aldrics_square', 'whispers_fang', 'ambrose_weight']
MATS = ['amber', 'jade', 'jade2', 'jade3', 'brass', 'crystal', 'obsidian',
        'starstone', 'vagabond']

rows = [
    ('Family cards, live', FAM_LIVE_COUNT, FAM_ON_BUS, 'CFX entry (measured in-page)'),
    ('Enchants', 8, len(lm_backed), '_lm* managed'),
    ('Break death rows', len(break_rows), len(break_rows) if bt_sites <= 3 else 0,
     'BREAK_TRIGGERS, %d dispatch site(s)' % bt_sites),
    ('Table rules (badges)', 9, len(rule_shared), '_ruleActive gated'),
    ('Relics', 8, 8 if shared_mech else 0, 'mechanic dispatch'),
    ('Material family traits', 9, 9 if shared_mech else 0, 'mechanic dispatch'),
]
print('%-24s %-8s %-8s %s' % ('category', 'total', 'shared', 'test'))
print('-' * 74)
tot = shr = 0
for name, t, sh, how in rows:
    print('%-24s %-8d %-8d %s' % (name, t, sh, how))
    tot += t; shr += sh
print('-' * 74)
print('%-24s %-8d %-8d' % ('TOTAL', tot, shr))
print('\nblended, with the arithmetic: %d / %d = %.1f%%' % (shr, tot, 100.0 * shr / tot))
print('(printed only because it was asked for. The per-category rows above are')
print('the answer; a single number hides that enchants and cards are at very')
print('different stages.)')

print('\nNOT ON SHARED MACHINERY, named:')
print('  family cards: %s' % ', '.join(FAM_OFF))
print('                (all six are the run-scoped cards, ruled OFF the match')
print('                 bus deliberately - not unmigrated work)')
print('  enchants:     %s' % ', '.join(e for e in ENCH if e not in lm_backed))
print('  table rules:  %s' % (', '.join(r for r in RULES if r not in rule_shared) or 'none'))
