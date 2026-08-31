# -*- coding: utf-8 -*-
u"""P890b: withdraw the full-silver stacking verdict from the master brief, and
correct the two die descriptions that still promise a retired bust-save.

THE VERDICT CANNOT BE RE-RUN, ONLY WITHDRAWN, for three independent reasons:
  - Its instrument GRANTED the immunity it was used to judge. _runBalanceSim's
    simTurn hard-coded one free bust-save per turn for owning a silver die,
    plus one per ward charge - the exact stack the finding is about. It did not
    measure the stack, it granted it and measured the consequence.
  - No harness that touches _runBalanceSim can produce a run-win number at all.
    It is match-level: one cell is N independent playMatch calls with no night
    loop, no hearts, no gold and no carry-over. Nothing in it can fail a RUN.
    _runEconomySim is run-level but rolls no dice - it takes win rates as
    hard-coded constants copied out of the same silver-bearing rows.
  - Two of the three named components do not exist as modellable things.
    famDef('ward') is false, so the ward charge could never be non-zero; and
    insurance is retired, which bust() says in its own comment.

WHAT REPLACES IT IS SMALLER AND FIRMER. Measured on the fixed sim, 2,000
matches per cell, noise floor 2.1pp patron / 2.5pp boss: six-silver is
INDISTINGUISHABLE from the shipped G2-mid gear and +22 to +25pp over all-bone.
Not a trap, not a menace.

AND THE PREMISE FAILS FROM A SECOND DIRECTION: six silver is not a build the
game can produce. DICE_STORE stocks silver at 1 per run, every purchase path
guards on the stock, and the starter draft adds at most one more - so the
ceiling is two, three with Brutus's Shield. The buildable two-silver stack
beats two IRONS by +0.8 to +1.3pp, inside noise. A 580g die performing like a
100g one is a PRICING question, and it is the one this line should have been
about.

The two die descriptions are corrected because they describe a mechanic that
was deleted: DICE_TYPES silver is effect:null with a weighted rollTable, and
Brutus's Shield is effect:null with a born ward. The TWICE SAVED feat is left
alone - it was flagged as possibly unreachable and it is not: _featWardSaves is
incremented where a ward halves a busted turn, so the feat reads on ward saves,
which still exist.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'docs', 'briefs', 'FARK_MASTER_BRIEF.md')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


sub(u"""cross-family bust-immunity stacks (run-sim verdict: full silver
   stacking is a TRAP at 4% run wins, not a menace - low priority; the
   real risk is defense-only builds lacking any win condition)
  (Silver die + Ward + Insurance)""",
    u"""cross-family bust-immunity stacks.
  **VERDICT WITHDRAWN, not re-run.** The "TRAP at 4% run wins" number came
  from a sim whose match layer hard-coded the very immunity under test - one
  free bust-save a turn for owning a silver die, plus one per ward charge
  (fixed P888). It did not measure the stack, it granted it. It also cannot
  be repaired by re-running: `_runBalanceSim` is MATCH-level and nothing in
  it can fail a run, and two of the three named components no longer exist -
  Insurance is retired and Ward halves rather than rescues.
  **Re-measured on the fixed sim** (2,000 matches/cell, tiers 1 and 4, two
  policies, noise floor 2.1pp patron / 2.5pp boss): six-silver is
  INDISTINGUISHABLE from the shipped G2-mid gear (-0.6 to +2.4pp patron,
  -0.6 to +0.8pp boss) and +22 to +25pp over all-bone. Not a trap, not a
  menace.
  **And six-silver is unbuildable:** DICE_STORE stocks silver at 1 per run
  and the starter draft adds at most one more, so the ceiling is two (three
  with Brutus's Shield). The buildable two-silver stack beats two IRONS by
  +0.8 to +1.3pp - inside noise. **The live question is Silver's 580g price,
  not bust-immunity stacking.**
  **RUN-level impact is still unmeasured.** `tools/sim_power_e.js` is the
  only harness that can answer it and has never been pointed here.""",
    '1 the withdrawn verdict')

sub(u"""- Silver (white), 580g: saves you from one bust per match.""",
    u"""- Silver (white), 580g: weighted to 1s and 5s (rollTable
  [1,5,1,5,2,3,4,6]), so it busts far less often - but never safely. *(The
  bust-save this line used to describe was retired; the die's `effect` is
  null. Measured: about a third of bone's per-turn bust rate.)*""",
    '2 silver is not a bust save')

sub(u"""- Brutus's Shield (silver): two bust saves per match.""",
    u"""- Brutus's Shield (silver): silver's weighted table plus a born Ward on the
  5 face. *(Not two bust saves - its `effect` is null and Ward halves a
  busted turn rather than rescuing it.)*""",
    '3 the shield is not two saves')

# ── post-asserts ────────────────────────────────────────────────────
if 'is a TRAP at 4%' in s:
    sys.exit('the withdrawn verdict survives (nothing written)')
if 'saves you from one bust per match' in s:
    sys.exit('the stale silver description survives (nothing written)')
if 'two bust saves per match' in s:
    sys.exit('the stale shield description survives (nothing written)')
if s.count('VERDICT WITHDRAWN') != 1:
    sys.exit('the replacement is not present exactly once (nothing written)')
# the checklist item itself must survive - this withdraws a verdict, not a task
if 'cross-family bust-immunity stacks' not in s:
    sys.exit('the checklist item was deleted with its verdict (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
