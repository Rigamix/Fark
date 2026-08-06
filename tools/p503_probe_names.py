# -*- coding: utf-8 -*-
u"""P503 - the five structural checks say what they verify.

PROBE_AUDIT.md filed these rather than patching them under pressure, and the
right resolution turned out to need one fact that had not been established:
IS THE STRUCTURAL CHECK THE ONLY GUARD, OR A SECOND ONE?

Counted, and in every case the behaviour is separately covered:

  apv_bank_fx      8 behavioural (flatBonus, doubleBank, halveEven/Odd, gain*,
                   rowsArePure, defaults) + bothSeatsWired
  apv_bust_fx      6 behavioural (gainPtsCard, punishCard, defaults,
                   survivesUndefined, noStaleFallbacks, earlierTablesIntact)
                   + bothSeatsWired
  apv_commit_seam  4 behavioural (bothSeatsRaise, actorsAreRight,
                   sameDerivation, tripleDetected) + wiredAfterReroll
  apv_fog_index    5 behavioural, incl. a 4,746-case sweep + reExpansionIsWired
  apv_deadroll_opp raisesWithArray + ungatedNothing behavioural,
                   wiredInStep + placedCorrectly structural

So these are NOT weak substitutes for behavioural tests. They are refactor
guards - they catch wiring being moved or deleted even when the behavioural
checks happen to still pass - and that is a real job worth keeping.

Which makes renaming the correct repair rather than the lazy one. From
PROBE_AUDIT.md: "either the check verifies what the name says, or the name says
what the check verifies". Adding a duplicate behavioural assertion beside an
existing one would be noise; what was actually wrong is that a source-position
check was reporting a verdict that sounded like proven behaviour.

`placedCorrectly` was the worst of them and is the one that motivated the audit:
it infers CORRECTNESS OF PLACEMENT from substring offsets, the identical
inference that let straightsProtectsAFive stay green while a complete six-run
was traded away. It now names the ordering it actually checks.

Each also gains a comment pointing at the sibling that covers the behaviour, so
a future reader can see the structural check was never meant to stand alone.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))

RENAMES = [
    ('apv_deadroll_opp.js', 'placedCorrectly', 'raiseSitsAfterEncoreAndBeforeBustSave',
     u'/* SOURCE-ORDER check, not a behavioural one. It compares indexOf offsets\n'
     u'   inside runOppTurn to confirm the raise sits between the encore branch and\n'
     u'   the bust-save. Named `placedCorrectly` until P503, which inferred\n'
     u'   CORRECTNESS from a substring offset - the same inference that let\n'
     u'   straightsProtectsAFive stay green through a real bug.\n'
     u'   The behaviour is covered by raisesWithArray and ungatedNothing below;\n'
     u'   this exists to catch the raise being MOVED by a refactor. */\n'),
    ('apv_bank_fx.js', 'bothSeatsWired', 'bothSeatsReferenceTheTable',
     u'/* SOURCE check: both seats mention the BANK_FX rows. "Wired" claimed more\n'
     u'   than that. The eight behavioural checks above (flatBonus, doubleBank,\n'
     u'   halveEven/Odd, gain*, rowsArePure) are what prove it works; this catches\n'
     u'   a seat losing its reference in a refactor. */\n'),
    ('apv_bust_fx.js', 'bothSeatsWired', 'bothSeatsReferenceTheTable',
     u'/* SOURCE check: doBust and runOppTurn both mention BUST_FX. "Wired" claimed\n'
     u'   more. gainPtsCard, punishCard, defaults and survivesUndefined are the\n'
     u'   behavioural proof; this catches a seat losing its reference. */\n'),
    ('apv_commit_seam.js', 'wiredAfterReroll', 'commitCallSitsAfterTheRerollBlock',
     u'/* SOURCE-ORDER check, and the ordering genuinely matters: the player-armed\n'
     u'   reroll can un-keep every die and zero `total`, so committing before it\n'
     u'   would raise a selection the player then destroyed. bothSeatsRaise and\n'
     u'   actorsAreRight prove the behaviour; this pins the position. */\n'),
    ('apv_fog_index.js', 'reExpansionIsWired', 'reExpansionPresentInSource',
     u'/* SOURCE check. The 4,746-case sweep above is the behavioural proof that\n'
     u'   the keep now matches; this only confirms the re-expansion line is still\n'
     u'   in runOppTurn, so a refactor cannot silently drop it. */\n'),
]

for fname, old, new, note in RENAMES:
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding='utf-8').read()
    tok = u'v.' + old
    assert s.count(tok) == 1, '%s: %s matched %d' % (fname, tok, s.count(tok))
    assert (u'v.' + new) not in s, '%s: %s already present' % (fname, new)
    s = s.replace(tok, note + u'v.' + new)
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('%-22s %s -> %s' % (fname, old, new))

# ── gates: the old names are gone, the new ones exist exactly once ──
for fname, old, new, _ in RENAMES:
    s = io.open(os.path.join(HERE, fname), encoding='utf-8').read()
    assert (u'v.' + old) not in s, '%s still has %s' % (fname, old)
    assert s.count(u'v.' + new) == 1, '%s: %s count wrong' % (fname, new)
print('all five renamed, old names gone')
