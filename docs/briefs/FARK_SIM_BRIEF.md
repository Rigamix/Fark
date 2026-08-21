# FARK — SIM BRIEF FOR CODE

> **STATUS 2026-08-21:** the receipts below are outdated — Break's
> restore, the Ward cap and live Preserve all shipped since. The
> harness lineage moved twice: `tools/sim_harness.js` (FSIM) replaced
> agents.js, and `tools/ladder_real.js` replaced the sim for DIFFICULTY
> after OPEN.md §1 measured the sim's rival as unfaithful (understates
> by 23-51%). The acceptance targets here are under revision by the
> ladder rebuild. The four-lens program (FUN/POWER/ELEGANCE/Scavenger)
> was deferred and never run end-to-end — that ask now lives in
> AUDIT_BACKLOG.md's RE-HOMED section. The brief's METHOD remains the
> reference; its numbers do not.

Why this is yours to run, not mine: everything shipped since the enchant/
badge rework (Silver's new identity, all eight enchants, four rescoped
badges, Break's timing mechanic) has never been through run-level
simulation. The original harness (agents.js/agents2.js) was built by
extracting real functions from an uploaded build into a Node/DOM-stub
sandbox — that only stays trustworthy against a build that's actually
current, and the last several rounds of audit found the brief and the
live code disagreeing often enough that I can't responsibly guess my way
to a current extraction anymore. You have direct access to the real
functions, the real data, and (per the throw-physics tooling already
built) existing precedent for exactly this kind of measurement work.
This is the methodology — the acceptance targets, the agent roster, and
critically the four evaluation lenses beyond raw win-rate — so you're not
starting from zero.

## The four things being tested, not just "does it work"

A game can be numerically balanced and still fail. Test all four:

1. **FUN** — no dominant, solved strategy. The original finding was that
   skill lives almost entirely in DRAFTING and BUILD DECISIONS (~45
   points of win-rate spread between a random-drafting floor agent and a
   deliberate one), while moment-to-moment execution (banking thresholds,
   keep choices) is nearly flat (~2 points). That's the intended shape —
   verify it still holds. If the spread has collapsed (everyone's
   win-rate converges regardless of build) or inverted (one specific
   enchant/badge/family combo dominates regardless of skill), that's a
   fun failure even if the aggregate numbers look fine.
2. **SENSE OF POWER** — a maxed-out late-game build should CRUSH what an
   early-game build could only just survive, and the player should FEEL
   that escalation. Concrete metric below.
3. **ELEGANCE** — the specific interactions this project spent real
   effort reconciling (Break's timing asymmetry, Trade's match-scoped
   reversion, Still Waters suppressing Break's Obsidian trigger, Ward's
   loadout cap, the 1/5 restriction closing the bust-insurance exploit)
   need to behave EXACTLY as specified, verified as targeted pass/fail
   checks, not inferred from aggregate stats.
4. **NO CHEAT AROUND POSSIBLE** — an agent whose whole job is hunting for
   degenerate combos should not find one that dramatically outperforms
   honest play. This needs its own agent archetype, described below —
   don't rely on the "normal" agents to stumble into an exploit by
   accident the way a human eventually would.

## Method

Drive the REAL functions directly — scoring, bank/keep resolution, enchant
effect resolution, badge rule application, patron/boss generation — not a
reimplementation of what they're supposed to do. The entire value of this
kind of testing is that bugs in the real implementation surface instead of
being quietly modeled away. If a function's behavior doesn't match what a
brief says, that's a finding to report, not something to paper over by
coding the harness to match the brief instead of the code.

Track and report: run-win rate, patron/boss win rate at intended gear,
median banked turns per side, bust rates, gold curve health, per-enchant
and per-badge usage/impact, and the four targeted checks below. Use seeded
RNG for exact reproducibility. Report confidence intervals at your sample
size — don't let noise get reported as a finding (a 3-4 point win-rate gap
between two agents at n=400 is very likely nothing).

## Agent roster

Extend the original five with two new ones this system specifically needs.
Personalities should extend naturally into build/enchant/badge choices,
not just banking thresholds:

- **CAUTIOUS CARL** — low bank threshold, defensive leanings (Silver,
  Ward). Historically a trap (4-5% win rate stacking full defense) —
  RE-CONFIRM this still holds under Silver's new odds-skew identity;
  don't assume the old finding transfers automatically.
- **BALANCED BEA** — mid threshold, drafts toward owned families. Should
  be the one agent that actually uses PRE-MATCH LANE PLANNING —
  reordering her loadout at the peek to line up Snare/Trade/Fog-branded
  dice against whatever the opponent's peek reveals. If Bea can't
  meaningfully benefit from this, the pre-match planning system isn't
  pulling its weight.
- **GAMBLER GREG** — high threshold, obsidian/volatility leaning, uses
  Break aggressively. This is the agent that tests the TIMING question
  directly: give Greg a policy that fires Break the moment it's
  available (naive) and a second variant that only fires it when no
  future turns remain this match (informed), and compare. If naive-Greg
  and informed-Greg perform similarly, the timing mechanic isn't
  actually teaching anything and the finding from section 4 isn't
  translating into real decision-making.
- **NEWBIE NED** — near-random, low sophistication. The control: is
  drafting/build skill still worth ~45 points over doing nothing smart?
- **RUSHER RITA** — minimal seats, rushes the boss, low system
  investment.
- **RANDOM RANDY** — the floor. Fully random across dice purchases,
  drafts, enchant choices, badge wear, lane reordering.
- **ORACLE OTTO** — the ceiling. EV-optimal banking (as before), EXTENDED
  to be EV-optimal about drafting, enchanting, and lane-reading too —
  the old Otto only optimized turn-level decisions; this system has
  build-level depth now and the skill ceiling reference should reflect
  that.
- **NEW — SCAVENGER (exploit hunter).** Not trying to play well in the
  normal sense — trying to find a sequence that produces runaway value.
  Specifically attempt, at minimum: Fair Trade + Break on the same die
  in sequence (should now correctly cost the die, confirm it does);
  stacking multiple Ward-branded dice if the loadout cap has any gap;
  branding faces outside {1,5} if the shipped restriction has any hole;
  wearing Kindred while intentionally maximizing enchant count to see if
  the doubling produces an outsized effect anywhere it isn't cleanly
  defined (Ward, Snare, Break, Trade, Snuff, Fog — all currently
  undefined for "double," per the open item — if Scavenger finds ANY of
  these already implemented with a guessed default, report exactly what
  that default is, since nobody signed off on one); firing Trade
  specifically to acquire an opponent's enchanted die and checking
  whether it correctly reverts at match end or whether anything leaks
  into the next match. Scavenger's win rate/value-per-turn should NOT be
  a dramatic outlier next to Bea/Otto — if it is, that's the headline
  finding, report it first.

## Concrete metrics for the four lenses

- **Fun** — win-rate spread across the roster, same shape as before
  (deliberate agents should separate meaningfully from Ned/Randy; the
  top cluster of deliberate agents should stay close together, since
  execution skill is supposed to be compressed). Flag if any single
  build/combo dominates independent of which agent is running it.
- **Power** — compare a night-1-gear loadout's win rate against a
  night-8, fully-built loadout (enchants + a worn badge) at the SAME
  opponent tier. The delta should be large and unambiguous. If a maxed
  build barely outperforms a starting one, power fantasy isn't landing
  regardless of what the aggregate run-win number says.
- **Elegance** — pass/fail, not statistical, on each of these:
  - Break destroys the targeted die for the rest of THIS match only;
    fully restored at the start of the agent's next match.
  - Trade's whole die (material + enchant) swaps for the match only;
    both sides' true loadouts are bit-for-bit restored at match end.
  - Still Waters suppresses Break's guaranteed Obsidian payout, not just
    the passive 6% check — confirm the guaranteed version is ALSO
    silenced, not just reduced to the passive rate.
  - A loadout cannot contain two Ward-branded dice under any purchase
    sequence.
  - A branded icon face can only ever land on a die's natural 1 or 5;
    verify no purchase or relic path produces a 2/3/4/6 brand.
  - A Preserved die is never a legal Break target.
  - Zero Hour ends the acting side's turn immediately on any icon keep,
    with no hot-dice exception carved out.
- **No-cheat** — Scavenger's results per above. Report any sequence that
  produces value clearly above what Bea/Otto achieve through honest play.

## Acceptance targets (restate, re-validate, don't assume)

Patron win 60-70% at intended gear, boss 45-55%, median 5-7 banked turns
per side. Run-level: 25-35% full-run win rate for a competent build-
focused player. These were validated against a pre-rework build — if the
current numbers land meaningfully outside these bands, that's not
automatically wrong, but it needs a decision (tune targets, or tune the
new systems) rather than being reported as a pass/fail against stale
numbers.

## Reporting format

Lead with the headline verdict on each of the four lenses, THEN supporting
numbers, THEN flagged uncertainties — matches how findings have been
reported throughout this project so far. Don't bury a "Scavenger broke
the game" finding under a wall of otherwise-healthy win-rate tables.

---

## Note added on receipt — read before running this

The brief was written without access to the current build, and several of
its ELEGANCE checks describe behaviour the shipped code does NOT have yet.
Running them today produces failures that are correct-as-measured but read
as regressions. Which is which, as of this commit:

- **Break restores at the start of the next match** — NOT BUILT. The
  match-scoped ruling arrived in AUDIT_RESOLUTIONS.md and reverses what
  P365 shipped. See that doc's final section; P365's permanent splice out
  of `S.run.diceInv` has to be reverted first or this check fails by
  design.
- **Trade restores both loadouts bit-for-bit at match end** — PARTIAL.
  P365 handles the loan end but under the superseded run-scoped reading.
- **Branded faces restricted to 1 or 5** — NOT BUILT. The code ships a
  different system deliberately and documents why; resolution items 13/14
  adopt the restriction (Phase A only, picker skipped permanently).
- **No two Ward-branded dice** — NOT BUILT. `_wardOwned` does not count
  Brutus's relic at all (measured false with the relic in the loadout).
- **Still Waters suppresses Break's guaranteed Obsidian payout** — NOT
  BUILT, and resolution item 5 marks the ruling itself UNVALIDATED and
  wanting its own sim pass.
- **A Preserved die is never a legal Break target** — Preserve as a
  visible die is not applied at all.
- **Zero Hour ends the turn on any icon keep, no hot-dice exception** —
  BUILT (P341) and verified by play.

So the honest order is: land the resolutions first, then run the sim
against a build that actually implements what the checks assert.
Otherwise the ELEGANCE section reports seven failures that are really one
finding — "this hasn't been built yet" — and buries whatever the FUN,
POWER and NO-CHEAT lenses have to say, which are the parts that can be
measured against the build as it stands today.
