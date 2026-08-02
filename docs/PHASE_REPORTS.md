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

---

# Phase 2 — Totality assertions

**Status:** complete, deployed `8654acb`. Suite is now 12 probes: 11 pass,
1 fail (three known reds inside it), 0 error.

## The headline: the assertion found a bug nobody was looking for

The plan predicted one red — no relic has a `.dtype-` CSS block — and it was
there. The one that mattered was the one nobody predicted.

**`MATCOL` is missing `jade3`, `brass`, `crystal` and `ruby`.** Those four are
RETIRED materials: the master brief removed them from shop and drops. But they
are still in `DICE_TYPES`, deliberately, because the same brief promises
migration *converts* a legacy save that holds one rather than dropping it. So a
save carrying a retired die renders it **with no tint at all.**

Rare, real, and precisely the class the assertion exists for: **the domain
drifted when the materials were retired, and nothing compared the two.** No
amount of reading the tint table would have surfaced it — the table looks
complete until you ask it what it is supposed to cover.

## What the plan asked for

> *"Totality assertions on every lookup table … each is a few lines, and each
> would have caught a real bug today."*
> *"A lookup table keyed by id must assert it is total over that id's source of
> truth, in the same commit that adds it."*

## What was built

`tools/apv_table_totality.js`, six assertions, picked up automatically by the
Phase 1 runner:

| Table | Domain | Result |
|---|---|---|
| `ASPECT` | props the shipped templates reference | **38 keys / 19 needed** — green |
| card art | every live `FAM_LIVE` id | **31 / 29** — green (two are aliases needing none) |
| patron portraits | `PT_ART_POOL` | **30 / 30** — green |
| `MATCOL` | every `DICE_TYPES` id | **20 / 24** — RED, see headline |
| `FEAT_ART` | every `FEATS` id | **12 / 32** — RED |
| `.dtype-` CSS | every relic id | **0 / 8** — RED, predicted |

## What it found

**`.dtype-` blocks, 0 of 8 relics.** The predicted one. Relics draw with default
die vars anywhere the 2D renderer runs — shelf, loadout. The 3D tint landed in
P417; this is its other half, and it is the change Denis's dice-art pass will
most naturally absorb.

**`FEAT_ART`, 12 of 32 — and the assertion RECLASSIFIED it.** Before P414 the 20
artless feats took the loud full-screen overlay path, so this was a *behaviour*
bug — it is why the same feats kept interrupting the loadout screen. Since the
splash was removed, both routes are silent, so the same 12-of-32 is now purely an
*art* gap. Same number, different severity. **The assertion is what made that
distinction visible**, which is the argument for writing assertions rather than
tracking known issues in prose.

**`MATCOL` — see the headline.**

## Guideline compliance

| Requirement | Where from | Met? |
|---|---|---|
| Assert totality over the id's source of truth | Visual plan Phase 2 | **Yes** — six tables, each against its real domain |
| Additive; touch no game logic | Visual plan | **Yes** — one new file in `tools/` |
| Record known-red rather than leave it to drown new-red | Visual plan Phase 1 | **Yes** — all three reds baselined |
| Don't half-do it | Effect plan | **Yes** — the unit is the assertion set, and it is whole |
| Verify computed, never authored | Standing rule | **Partly — one row is weaker, and says so** |

**The one honest weakness.** `ASPECT` is function-scoped and cannot be read from
page scope. The choice was to change game code to expose it, or to parse it out
of the served source. **Changing the game to make a test pass is the wrong way
round**, so it is parsed from source and tagged `via:'source'` in the output.
That proves the literal in the file is total — not that the live object is. A
weaker claim, marked as weaker, rather than a strong claim quietly resting on a
weaker method.

**Repairs deliberately excluded.** Phase 2 is assertions. Fixing the three reds
inside it would have made the phase unreviewable and hidden game changes inside
an additive pass.

## What this does *not* cover

- **Six tables, not all of them.** These are the ones with a known failure
  history. `ENCH_ICONS`, `FAMILIES`, `BOSS_FAM` and the dialogue pools are
  unasserted.
- **Totality is not correctness.** `MATCOL` being total would not have caught the
  six relics whose tints were byte-identical to their family colour — that needed
  a *separation* assertion, which lives in the P417 patch script, not here.

## CORRECTION — both interpretations above were wrong, in opposite directions

Denis's review asked two empirical questions I had answered by reasoning rather
than measuring. In a report whose own standard is *verify computed, never
authored*, that is the one thing it should not have done. Both are now measured,
and both change the conclusion.

### MATCOL is NOT reachable — downgrade it

`fark_proto.html:9515` converts retired materials on load, guarded by
`S.run._diceMigrated`:

```js
var refund={brass:350,crystal:700,ruby:400,jade3:1100};
S.run[k]=S.run[k].map(function(m){ if(refund[m]){got+=refund[m];return 'bone';} return m; });
```

A legacy save holding one becomes **`bone`, refunded, before anything renders**.
So there is no state in which a player sees an untinted retired die.

**This is defensive completeness for a state nobody will ever witness, not a
rare-but-reachable bug** — exactly the distinction the review asked for, and I
had collapsed it. The table gap is real; the bug is not. Still worth the
ten-minute fix as defence-in-depth if the migration is ever bypassed, but it
carries none of the urgency the headline implied.

### FEAT_ART is WORSE than reported — the reclassification was premature

I downgraded it to "an art gap" after checking **one** consumer, the overlay path
in `_drainFeatUnlockQueue`. There are **seven**. The others are the feats wall:

```js
list=list.filter(function(f){return f&&FEAT_ART[f.id]&&!S.featsPinned[f.id];});   /* :13898 */
```

**The wall filters out every feat without art.** So the 20 artless feats are not
"text-only on the wall" — on that path they may not appear at all. That is a
behaviour consequence, and my severity downgrade moved it the wrong way.

Flagged rather than fixed here: confirming what a player actually sees on the
wall needs its own probe, and this report should not claim a second time without
measuring.

**The lesson is the report's own:** "both routes are silent since the splash was
removed" was a claim about game behaviour sourced from a changelog entry. The
standard this document sets for game code applies to statements about game code.

## What's next

**The recommendation changes because of the correction above.** Phase 3 goes
after bug classes that have already cost real time twice — `.lwho` at four
rounds, `.end-draft-slots` at two wasted attempts. MATCOL's gap is real but
currently unwitnessable. **Phase 3 first**, then the MATCOL fix as
defence-in-depth, and a probe for what the feats wall actually shows.

The original framing, kept because the reasoning is still worth reading:

- **Phase 3** — the CSSOM presence check (3a) and the selector-actually-matches
  check (3b) Denis's correction added. Catches the `.lwho` and `.end-draft-slots`
  classes of bug.
- **Fix the three reds** — `MATCOL`'s four retired materials is a ten-minute
  change and a genuine, if rare, rendering bug.

**Recommendation: the `MATCOL` fix first** (small, real, and the baseline will
prove it went green), then Phase 3.

## For the team

One decision worth having: **`FEAT_ART` at 12 of 32 is now an art question, not
an engineering one.** Twenty feats have no art. Since P414 that costs nothing
functionally. Options are to commission twenty, to cut the feat list to the
twelve that have art, or to accept that most feats are text-only on the wall.

