# -*- coding: utf-8 -*-
"""P437 - the sim harness catches up to the rule-id renames.

FOUND BEFORE RUNNING ANYTHING, which is the only reason it is a fix rather
than a set of published numbers that were quietly wrong.

P427 and P428 renamed the table-rule ids so each matches the rule it carries.
The harness still holds the old map, and it is wrong in TWO different ways:

  SILENTLY NO-OP. `kindred:'counterfeit'`, `still_waters:'confession'`,
  `first_strike:'in_arrears'` - none of those ids resolves any more, so
  _tellById returns null and the badge simply is not applied. GEAR.night8
  carries badge:'counterfeit', so every night-8 run would have gone out BARE
  while reporting itself as a Kindred build.

  SILENTLY WRONG. `zero_hour:'last_call'` is worse than a no-op. After P427
  `last_call` is a REAL, LIVE rule again - Grog's LAST CALL, which voids a bank
  under 800 - and `zero_hour` is its own id on Mabel. So a harness asking for
  Zero Hour would have got a bank-void rule instead and measured it as Zero
  Hour. Not nothing: the wrong thing, with a plausible number attached.

The map becomes an identity now, and that is the point: it existed only to
paper over a divergence between rule names and rule ids, and that divergence is
what P428 removed. Kept as a table rather than deleted so agents keep one place
to name a rule.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
RENAME = {'counterfeit': 'kindred', 'confession': 'still_waters',
          'in_arrears': 'first_strike'}

# ── sim_harness.js ────────────────────────────────────────────────────
p = os.path.join(HERE, 'sim_harness.js')
s = io.open(p, encoding='utf-8').read()
orig = s

OLD_MAP = ("""/* Badge ids are the RULE ids the engine still keys on, not the new names:
   last_call = ZERO HOUR, counterfeit = KINDRED, confession = STILL WATERS,
   in_arrears = FIRST STRIKE. Named here once so no agent has to re-derive it. */
F.BADGE={zero_hour:'last_call',kindred:'counterfeit',still_waters:'confession',
         first_strike:'in_arrears',steeped:'steeped',pickpocket:'pickpocket',
         drill_order:'drill_order',reckoning:'reckoning'};""")
NEW_MAP = ("""/* THE IDS AND THE RULES MATCH NOW (P427/P428), so this map is an identity -
   and that is the point. It existed only to paper over a divergence where a
   badge showed one rule name and keyed on another, which is what got removed.
   Kept as a table, not deleted, so an agent still has one place to name a rule.

   IT WAS WRONG IN TWO WAYS BEFORE THIS, both silent:
     kindred/still_waters/first_strike pointed at counterfeit/confession/
     in_arrears, none of which resolves any more - _tellById returns null and
     the badge is simply not applied. GEAR.night8 asks for Kindred, so every
     night-8 batch would have run BARE while reporting itself as a Kindred build.
     zero_hour pointed at 'last_call', which is worse than a no-op: after P427
     that is a LIVE rule again (Grog's LAST CALL, voids a bank under 800). The
     harness would have measured a bank-void rule and labelled it Zero Hour. */
F.BADGE={zero_hour:'zero_hour',kindred:'kindred',still_waters:'still_waters',
         first_strike:'first_strike',last_call:'last_call',
         steeped:'steeped',pickpocket:'pickpocket',
         drill_order:'drill_order',reckoning:'reckoning'};""")
assert s.count(OLD_MAP) == 1, 'badge map anchor missed'
s = s.replace(OLD_MAP, NEW_MAP)
s = s.replace("badge:'counterfeit'", "badge:'kindred'")
assert "badge:'counterfeit'" not in s
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('sim_harness.js: badge map + night8 gear')

# ── the two tails that hardcode ids ───────────────────────────────────
for name in ('sim_fun_d2.js', 'sim_l3_elegance.js'):
    q = os.path.join(HERE, name)
    t = io.open(q, encoding='utf-8').read()
    before = t
    for old, new in RENAME.items():
        t = t.replace("'" + old + "'", "'" + new + "'")
    t = t.replace("/* 'confession' */", "/* 'still_waters' */")
    if t != before:
        io.open(q, 'w', encoding='utf-8', newline='').write(t)
        print('%s: ids updated' % name)

# ── prove no stale id survives anywhere in tools/ ─────────────────────
stale = []
for f in sorted(os.listdir(HERE)):
    if not f.endswith('.js'):
        continue
    body = io.open(os.path.join(HERE, f), encoding='utf-8').read()
    for old in RENAME:
        if "'" + old + "'" in body:
            stale.append(f + ':' + old)
assert not stale, 'stale rule ids remain: %r' % stale
print('no stale rule ids remain in tools/')
