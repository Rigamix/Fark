# Phase reports

One entry per completed phase of `EFFECT_SYSTEM_PLAN.md` and
`VISUAL_INTEGRITY_PLAN.md`. Written to be circulated — each entry is
self-contained and can be pasted on its own.

Format, fixed, so entries stay comparable: **what the plan asked for → what was
built → what it found → did it follow the guidelines → what's next**.

---

# Phase 1 — The probe runner

**Status:** complete, deployed `ff368f5`. Backup tag `pre-effect-system` on
`a0aed7d`.

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
| `bust_settle_p2` | Superseded scratch that happened to contain the word "verdict" | Explicit `SUITE: exclude` marker, not deleted — it measures the second roll, which is where the rival gate failed |

**And the first baseline caught a hole in the runner itself.** `apv_bust_settle`
returned `"no bust this roll"` — a **string** — for a check whose forced bust
hadn't fired, and the `=== false` test passed it happily. An indeterminate check
reported as a pass is exactly the lying-suite failure the runner's own header
warns about. Verdict keys must now be booleans; anything else reports
INDETERMINATE and is counted apart from both pass and fail. Re-recorded clean
after the fix.

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
