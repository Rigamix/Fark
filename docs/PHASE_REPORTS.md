# Phase reports

One entry per completed phase of `EFFECT_SYSTEM_PLAN.md` and
`VISUAL_INTEGRITY_PLAN.md`. Written to be circulated — each entry is
self-contained and can be pasted on its own.

Format, fixed, so entries stay comparable: **the headline → what the plan asked
for → what was built → what it found → did it follow the guidelines → what's
next**.

**Self-contained means self-contained.** Any reference to a past bug, a probe or
a code path has to carry enough of its own context to land on someone who was
not there — a Phase 1 draft failed this by justifying a kept probe with "it
measures the second roll, which is where the rival gate failed", which is
meaningless without the rival-gate story. If an entry names something, it
explains it.

---

# Phase 1 — The probe runner

**Status:** complete, deployed `ff368f5`. Backup tag `pre-effect-system` on
`a0aed7d`.

## The headline: the suite caught itself lying, on its first run

Before it was ever pointed at game code, the runner found a bug **in its own
verdict-checking**.

It tested each verdict key with `=== false`. One probe, `apv_bust_settle`,
returned the **string** `"no bust this roll"` for a check whose forced bust
hadn't fired — a leftover status message where a boolean belonged. `"no bust
this roll" === false` is `false`, so **the check passed, and the probe was
reported green.**

That is exactly the "lying suite" failure the runner exists to prevent: an
indeterminate result presented as a confirmed pass. It surfaced on run one,
against the verification tooling itself.

**Why this is the finding and not a footnote:** the project's standing rule is
*verify computed, never authored* — don't trust what the code says, measure what
it does. This is that rule applied **recursively, to the verifier**. The runner
was not trusted to be correct because it had been written carefully; it was
measured, and it was wrong. Verdict keys must now be booleans, and anything else
reports INDETERMINATE, counted apart from both pass and fail.

**Read the clean result below in that light.** "11 pass, 0 fail, 0 error" is
true, but it is the number *after* a bug in the test infrastructure was found
and fixed. The first run of this suite was not green.

## What the plan asked for

Both plans named the same Phase 1 and said to build it once:

> *"There are ~20 `tools/apv_*.js` probes now and no way to run them all. One
> runner, one pass/fail report. This is shared infrastructure between both plans."*

And the effect plan called it the prerequisite:

> *"The real risk isn't the migration, it's that there's no way to tell whether
> it broke something."*

## What was built

`tools/run_probes.js`.

```bash
node tools/run_probes.js            # run, compare to baseline
node tools/run_probes.js --record   # set the baseline
node tools/run_probes.js --only x   # run a subset
```

**Result: 11 assertion probes, 11 pass, 0 fail, 0 indeterminate, 0 error.**
Baseline recorded in `tools/probe_baseline.json`. **No game code was touched.**

Of 45 `apv_*.js` files, 31 are one-off diagnostics from single investigations —
they measure, they don't claim. Adopting them would report noise, so the runner
only picks up probes carrying a `verdict` object.

## What it found

**Three probes errored on the first full run, and all three were problems with
the probes rather than the game.** That is the honest headline: the suite's first
act was to audit itself.

| Probe | Problem | Fix |
|---|---|---|
| `break_borrowed` | Needs ≥3 free dice; the roll decides | A probe that **declines** is not a probe that **failed** — `{err\|skip}` with no verdict is now a SKIP |
| `harness_trade` | Needed `FSIM`, absent from the page — only ever worked inside a bespoke wrapper | Loads its own dependency. A probe the suite can't run standalone isn't in the suite |
| `bust_settle_p2` | Superseded scratch that happened to contain the word "verdict" | Explicit `SUITE: exclude` marker, not deleted — see below |

**Why `bust_settle_p2` was kept rather than deleted.** The bust-timing bug had
two halves. The player's was a flat 1,100ms budget. The rival's was subtler: the
gate that waited for the dice tested `d.roll`, the physics playback tape, which
only exists once the solve has *started* — and the start can be deferred by up to
a second. On the **first** throw of a match the tape happened to start in time
and the gate looked correct; on the **second** it hadn't, so "not thrown yet" was
read as "finished" and the rival busted over four dice that hadn't been rolled.
`bust_settle_p2` is the probe that isolates that second throw specifically. The
shipped assertion (`apv_bust_settle`) covers the fixed behaviour, but if this
ever regresses, the second-throw case is where it will show, and re-deriving that
setup from scratch would cost an hour. It measures; it doesn't claim; it stays.

(The runner's own bug — the string verdict — is covered in **The headline**
above.)

## Guideline compliance

Checked against the two plans' own stated requirements, not against a general
sense of doing well:

| Requirement | Where from | Met? |
|---|---|---|
| Build the runner once, serve both plans | Both plans, Phase 1 | **Yes** — one tool, no duplication |
| Touch no game logic | Visual plan: "additive" | **Yes** — only `tools/`, plus two probe fixes |
| Record a baseline so known-red doesn't drown new-red | Visual plan Phase 1 rationale | **Yes** — `probe_baseline.json`, and deliberately recorded only *after* the suite was honest |
| Verify computed/measured, never authored | Standing rule | **Yes** — every probe drives a live page |
| Don't half-do it | Effect plan | **Yes** — the unit here is the runner, and it is whole |
| Anticipate order-of-operations breakage | Denis's instruction | **Yes, and it paid** — see below |

**Two order-of-operations calls that mattered:**

1. **Pre-flight before anything.** The dev server was down when I started. Without
   the check that arrives as eleven identical false failures — the most
   misleading output available. It now fails fast with an explanation.
2. **Baseline only after the suite was honest.** Recording first would have
   enshrined a broken probe and a string-valued verdict as "expected".

## What this does *not* yet cover

Stated so the team isn't misled about the size of the net:

- **11 probes for ~50 pieces of content.** This is a seed, not coverage. Most
  cards, all badges, and most enchants have no probe at all.
- **Non-determinism is surfaced, not solved.** These drive live dice. A probe
  whose verdict depends on the roll will skip or go indeterminate rather than
  flap — visible, but not fixed.
- **No CI.** It runs when someone runs it.

## What's next — Phase 2

Totality assertions per lookup table: `ASPECT` over `Props/`, `MATCOL` over
`DICE_TYPES`, `FEAT_ART` over `FEATS`, `PT_ART_POOL` over the portrait files,
card art over `FAM_LIVE`.

**One is already known to fail** — no relic has a `.dtype-` CSS block, so relics
draw with default die vars anywhere the 2D renderer is used. That known-red is
precisely why the baseline went in first.

## For the team

Nothing here needs a decision. One thing worth knowing: the runner takes roughly
8–12 minutes for a full pass, because each probe gets its own browser to avoid
the shared-state problem. That's the cost of the six probes that stub globals,
and it's not negotiable without giving up the isolation.
