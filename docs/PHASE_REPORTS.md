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

### FEAT_ART, third answer, and this one is measured: TWO DIFFERENT ROSTERS

I called it an art gap, then a behaviour bug. Both wrong, because I never looked
in `Art/Assets/Feats`. There are **24 painted feats**. `FEAT_ART` maps **12**.

But the other twelve are not simply unmapped — **they do not correspond to any
shipped feat id.** Measured:

**Painted, not in the code (12):** ForKeeps, FullBloom, GreenThumb,
HisOwnMedecine, NoClaim, OmensTrue, OwnTheNight, PowderMonkey, SlowBoiled,
StickyFingers, TwiceSaved, WishGranted.

**Shipped, not painted (20):** crushing_win, lightning_round, big_turn,
no_actives, full_straight, boss_slayer, hot_hand, one_turn_wonder,
tempting_fate, brinksman_feat, boss_crusher, two_bosses, quick_climb,
five_bosses, and the six `beat_<boss>` feats.

**Those twelve painted names are the master brief's own §8 feat list** — GREEN
THUMB, FULL BLOOM, SLOW BOILED, STICKY FINGERS, TWICE SAVED, NO CLAIM, POWDER
MONKEY, WISH GRANTED, OMENS TRUE, FOR KEEPS, HIS OWN MEDICINE, OWN THE NIGHT.

So this is not a table with holes. **The art was painted for the brief's feat
roster, and the code ships a different one.** Twelve overlap; twelve paintings
have no feat; twenty feats have no painting.

That is a content decision, not a bug: which roster is real. Nothing to fix
until that is answered.

**Three wrong answers before measuring, on the same question.** The first two
were reasoned from a changelog and from one consumer; this one is counted off
the filesystem. The standing rule exists for exactly this.

### (superseded) FEAT_ART is WORSE than reported — the reclassification was premature

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

---

# Phase 3 — Does the rule exist, and does it hit anything?

**Status:** complete, deployed `2b72452`. Suite now 13 probes: 12 pass, 1 known
red (the relic `.dtype-` gap from Phase 2).

## The headline: three for three — the check found bugs in the check

Phase 1's runner caught a bug in its own verdict-checking. Phase 2's assertion
found an unpredicted red. **Phase 3's first run reported ten failures, and all
ten were wrong.**

1. **Exact-string presence flagged `.win-art` and `.win-board` as missing.** Both
   are present — as `#end-ov .win-art`, because that specificity was *raised on
   purpose* to beat `#end-ov>*{position:relative}`. **An exact-match lint fails
   precisely the rules someone took care over**, which is the worst possible bias
   a lint can have. Now matches on the token.
2. **`#playerDiceRow` was box-checked at phase `idle`**, where it legitimately has
   no size because no dice have been rolled. Asserting a box on correct
   behaviour is how a suite teaches people to ignore it.
3. **The draft selectors were checked at a fixed 3s**, before the win screen's
   animation had rendered the offer. Now waits for it.

None of the three was a game bug. All three would have been false failures — the
failure mode that costs a suite its credibility faster than missing a real bug.

**And a fourth, mine rather than the probe's:** I ran it directly instead of
through `run_probes.js`, the dev server was down, and all ten checks "failed".
That is exactly what the pre-flight built in Phase 1 exists to prevent, and I
bypassed it by not using my own tool.

## What the plan asked for

Denis's correction to the visual plan, which split a check I had conflated:

> *"3a asks whether the browser has the rule. 3b asks whether the rule found the
> thing. Two of today's bugs sat on each side of that line."*

## What was built

`tools/apv_css_live.js` — 10 checks over 3 screens.

- **3a, presence:** would have caught `.ptcard .lwho`, swallowed whole when a
  comment lost its opener and CSS error-recovery ate the following rule. Four
  rounds of "the busts are too small" were that one rule never parsing.
- **3b, matching:** would have caught `.end-draft-slots` — which parsed
  perfectly and targeted a class absent from the screen it was written for. 3a
  passes that; only asking whether it matches a live element catches it.
- **3b extended to a non-zero box:** would have caught `.win-art` collapsing to
  0×0 after losing a specificity fight.

**It drives the game** — home → patron select → match → win — and checks each
set while that screen is actually up. A match-screen selector cannot match on the
home screen, so a naive sweep reports false failures for everything off stage.

## Guideline compliance

| Requirement | Where from | Met? |
|---|---|---|
| Split 3a from 3b | Denis's correction | **Yes** — separate checks, separate verdict keys |
| Additive; no game logic | Visual plan | **Yes** — one file in `tools/` |
| Verify computed, never authored | Standing rule | **Yes** — reads the CSSOM and live boxes |
| Record known-red | Visual plan | **Yes** — baseline re-recorded at 13 probes |
| Anticipate order-of-operations | Denis's instruction | **Partly** — I anticipated the screen problem and designed for it, but not the animation-timing one, and I bypassed my own pre-flight |

## What this does *not* cover

- **10 selectors, not all of them.** These are the ones with a failure history.
- **A rule can match and still be wrong.** Same limit as Phase 2's totality: this
  proves a rule exists and hits something, never that what it does is right.

## What's next

The feat roster migration — 32 → the brief's 24, now ruled. Sized in
`FEAT_DISCREPANCIES.md` and deliberately not started at the end of a long
session: it is a content change across the whole list, and starting without room
to finish is how a half-migration happens.

`FEAT_ART` should go 12/32 → 23/23 when it lands, and the Phase 2 baseline will
prove it.

---

# Phase 4 — The feat roster migration

**Status:** complete, deployed `d6772fc`; all five open decisions ruled and the
one code change shipped in `37eff42`. Suite is 13 probes, no regressions;
`apv_table_totality` carries the two known Phase 2 reds. `FEAT_ART` is green for
the first time.

## The headline: there were three rosters, not two

`FEAT_DISCREPANCIES.md` reported 24 paintings against 32 shipped feats and
called that the discrepancy. Both numbers were right and the framing was
incomplete. Counting the code turned up a **third and a fourth** list:

| Where | Rows | Reaches the player? |
|---|---|---|
| `FEATS` — evaluated on every win | 32 | only the 12 in `FEAT_ART` |
| `_famFeats()` — granted straight into `S.featsDone` | 5 | **none** — no art, so no trinket, ever |
| `FTEXT` — authored name + description on the wall | 12 | debug viewer only |
| paintings on disk | 24 | 12 |

**Five feats were being awarded that nobody could ever see.** `_famFeats` writes
`S.featsDone` and bumps the lifetime counter, but the wall only renders ids
present in `FEAT_ART`, and none of those five were. Two of them —
`never_small` ("never a bank under eight hundred") and `ember_night` ("a night
won on three embers") — are the brief's TEETOTALLER and THREE TORCHES,
implemented in the other system, under different ids, at different numbers.

And `FTEXT` was consulted **before** the live feat, so the twelve "uncoded"
paintings carried hand-written descriptions that outranked whatever the game
actually checked. Restoring the roster without touching it would have left
NO CLAIM on the wall reading *"decline a victory draft and take the gold"* while
the code awarded it for winning without busting.

None of this was visible from the two counts in the discrepancy doc. It came out
of reading the consumers, which is the lesson: **counting a table tells you its
size, not how many tables there are.**

## What was ruled

> *"Option 1, the brief's 24. Not a coin flip between three even options — the 24
> was the original, authored scope … The 32 in code is drift."*

## What was built

**The roster.** `FEATS` is now the brief's section-8 list: **23 live, one
parked.** `FEAT_ART` is 23 entries, one painting each. The mapping is total *by
construction* — not by twelve hand-written guesses that nothing verified.

**Ten additive telemetry channels**, because a restored condition has to be
readable. Every one is a counter or a flag placed beside state the game already
keeps; none changes a score, a roll, or a branch that already existed:

| Channel | Site | Feeds |
|---|---|---|
| `_featBloom` | Bloom's commit hook | FULL BLOOM |
| `_featJade` | commit, settled at the bank | GREEN THUMB |
| `_featShatterBanked` | obsidian break, settled at the bank | POWDER MONKEY |
| `_featStarChain` | Falling Star's bank hook | WISH GRANTED |
| `_featOmenTrue` | Ill Omen resolution, hit branch | OMENS TRUE |
| `_featAmberAte` | amber immunity spend | STICKY FINGERS |
| `_featWardSaves` | the ward branch in `doBust` | TWICE SAVED |
| `_featMaxRolls` | bank **and** bust | SLOW BOILED |
| `_featMaxDeficit` | beside the existing comeback flag | THE LONG ROAD |
| `_loNight` | `_checkNightFail` | SECOND WIND |

Two of those deserve their reasoning stated. **`_featJade` and
`_featShatterBanked` are pending flags that settle at the bank**, because both
conditions are phrased *"bank a …"* — a straight the player rolled and then
busted away has not been banked, and a flag set at commit time would have paid
out for it. `_featMaxRolls` settles at **both** exits: a six-roll turn is a
six-roll turn whether it paid or not.

**`_loNight` is stamped with the tier rather than set to `true`**, so it expires
by itself when the run advances. There is no "clear the flag" path for a future
edit to forget to call.

## What it found

**Measured, live:**

```
FEAT_ART   have 23   want 23   missing []   strayKeys []
```

Both directions: every feat has a painting, and no painting entry lacks a feat.

**On the wall** — four feats seeded through the real store, loadout opened,
pixels read: four trinkets hang, all four decode (295x470, 272x441, 306x336,
438x341), all four opaque and topmost, all 23 filenames present on disk.
Screenshot confirms.

**Six of the twelve old mappings were wrong**, and they resolved as a side
effect rather than as twelve separate fixes — exactly as the ruling predicted.
Death&Taxes is Ambrose's painting and is now Ambrose's condition.

**`first_blood` was quietly wrong in a way nobody had reported.** Its painting
says *first boss badge taken*; its check awarded for the first **match** of a
run, boss or not. FirstBlood was hanging on the wall for beating a drunk at a
patron table.

## A red the migration created, and what it means

`apv_feat_splash` went red on `featsStillEarned`. It was not a bug — and that is
the point worth reporting.

The probe drives a real first-night patron match and forces a win. Under the old
32, that fired several feats immediately (Crushing Win, Lightning Round, Hot
Hand, First Blood — the batch added under *"easier renown sources … per player
feedback that perks were too hard to reach"*). **Under the brief's 24, a
first-night patron win earns nothing at all.** Most of the restored roster is
boss-scoped or needs specific play.

So the probe was measuring the roster while claiming to measure the award path.
It now arms a condition it owns (HIGH ROLLER, a pure telemetry read) and asserts
that a *met* condition still reaches the queue — which is what it always meant.

**The finding underneath it is a design one, and it is the second content loss
in this migration.** The six per-boss feats were named as a cut up front. The
early-run drip-feed is the one nobody named: the brief's roster front-loads
nothing, so a new player's first hour now produces no wall at all. That may be
correct — feats are meant to be earned — but it is a change, it came in
sideways, and it is a design call.

## Guideline compliance

| Requirement | Where from | Met? |
|---|---|---|
| Restore the brief's section-8 list | Denis's ruling | **Yes** — 23 live + BOOKKEEPER parked |
| Remap `FEAT_ART` | Ruling | **Yes** — 23/23, measured both directions |
| BOOKKEEPER stays retired | Ruling | **Yes** — parked, its painting is the one orphan |
| NO CLAIM rewritten, not cut | Ruling | **Yes** — against Ward |
| Six `beat_<boss>` cut, named | Ruling | **Yes** — named in code and here |
| `FEAT_ART` 12/32 to 23/23 | Ruling's success test | **Yes** — measured, baseline re-recorded |
| Patch via `.py`, not heredoc | Standing rule | **Yes** — `p425_feat_roster.py`, `p425b_ftext.py` |
| Parse gate must fail the chain | Standing rule | **Yes** — run after each patch, both pass |
| Verify rendered, not authored | Standing rule | **Yes** — computed styles and a screenshot, not the source |
| Probes via `run_probes.js` | Phase 1 lesson | **Yes** for the suite; `shoot.js` direct only for detail, after the runner's pre-flight had proved the server up |

## Three conditions named mechanics that no longer exist

Rewritten rather than deleted, because what each rewarded still exists. **The
first was ruled; the other two are new and need a decision:**

1. **NO CLAIM** held Insurance, now **Ward**. Ruled. Reads *win carrying a ward
   without ever busting*, and reads the owned loadout rather than the live
   table, so a die broken mid-match cannot deny a claim about the build.
2. **STICKY FINGERS** used Tar Pit, which is retired in favour of Snuff. **Not
   previously identified** — the discrepancy doc named only NO CLAIM and
   BOOKKEEPER. Written against amber's live break-trigger (*win a match in which
   the amber held and ate a bust*). The name still fits — the tar holds — but
   the wording is a design call.
3. **BOOKKEEPER** needed Bookends, collapsed into Vanguard. Parked per the
   ruling. Its painting is the single orphan.

**Badges do not exist in this build** — tells replaced them. FIRST BLOOD, HIS
OWN MEDICINE and THE COLLECTOR are stated against tells. The discrepancy doc
quoted the brief's badge wording without noticing the mechanic had been renamed
underneath it.

## What this does *not* cover

- **The totality assertion still cannot see a painting with no feat.** Its
  domain is `FEATS`, so `Bookkeeper.png` sitting unused is invisible to it. The
  orphan is tracked here and in the code comment, not by the suite.
- **Totality is not correctness.** Same limit as Phase 2. Every feat has art;
  nothing proves the art *means* the condition. That check is a human reading
  24 pictures against 24 sentences.
- **The conditions are unplayed.** They parse, they read real state, and the
  wall renders — but only HIGH ROLLER has been fired through a live match. The
  narrow ones (WISH GRANTED's two chained extra turns, TWICE SAVED's two ward
  saves) want a sim pass or a playtest before anyone trusts the numbers.
- **`_famFeats` still grants three invisible feats** — `three_lucky`,
  `own_reckoning`, `keg_triple`. They have no art and cannot be seen. Left in
  place: deleting drift is a separate decision from restoring a roster.
- **Old saves keep dead ids.** A save holding `beat_corvus` simply stops
  rendering it. No migration written; the wall filters on `FEAT_ART` already.

## Decisions needed (all five ruled — see the section after next)

1. **STICKY FINGERS' wording** — the amber rewrite above, or something else.
2. **NO CLAIM's exact wording** — ruled as "rewrite against Ward"; this is the
   first draft of that sentence.
3. **The early-run drip-feed.** Restoring the 24 removes every feat that fired
   in a new player's first hour. Intended, or does the roster want one or two
   early ones?
4. **DEATH AND TAXES vs OWN THE NIGHT.** The brief defines them as *beat
   Ambrose* and *win the run* — and Ambrose is the final boss, so both fire on
   the same act. That overlap is in the brief, not introduced here, but two pins
   for one moment is probably not what was meant.
5. **Bookkeeper's painting** — leave it unused, or retarget it.

## One note on the suite

`apv_bust_settle` **flapped** during this phase: red in one full run, green
twice in isolation immediately after, with nothing changed between. The runner's
own header calls this out as failure mode 5 — *"any probe that flaps between
runs belongs in the measure pile, not here"*. It is a timing probe over real
dice physics. Recorded green in the baseline; it needs hardening or demoting,
and it should not be trusted as a regression signal until then.

## RULED — all five, and one of them changed the code (`37eff42`)

**1. STICKY FINGERS — not the amber rewrite. Back to Vagabond.** The draft was
wrong on the name, and the reasoning is worth keeping: *sticky fingers* is a
thief, not something that holds. Tar Pit was Vagabond-flavoured to begin with,
so moving the feat to amber relocated it to a different family for a reason
having nothing to do with the name.

Now written against **Vagabond's break row**, which takes what the rival banked
— a hand in someone else's purse. Same family the condition always belonged to,
and the name finally describes the mechanic.

Implemented: the hook sits inside the `steal>0` branch, so **only a steal that
actually took something counts.** The row still fires when the rival busted
their turn away and left nothing to lift, and a feat that paid out for reaching
into an empty purse would be the same class of bug this whole phase exists to
remove. The amber counter went with the draft — it existed only for it.

**2. NO CLAIM — confirmed as written, shipped unchanged.** *No claim* is
insurance language for a policy you carried and never had to use: Ward present,
the bust-save never triggered because there was never a bust. The condition
already reads exactly that.

**3. The early-run drip-feed — nothing goes back into the feat list.** Adding
early feats to patch an onboarding gap is the exact drift this migration just
removed; re-diluting the wall on day one would undo the fix.

Treated instead as a **separate problem with a separate answer**. Circles, gold
and first-badge progress already work as early reward loops independent of the
wall, and if the early game isn't landing, that is where it gets fixed.

**Still open, and deliberately not resolved here.** This is a real tension
between the design law (feats are rare, meaningful, never for sale) and real
prior playtest feedback that progression was too slow. It wants a direct call
rather than a unilateral one in either direction — and "don't touch the feat
list" settles what *not* to do without settling what to do instead.

**4. DEATH AND TAXES vs OWN THE NIGHT — not a bug, both fire.** They recognise
different scopes of the same moment: one the specific fight, one completing the
run. Several achievements landing on one climactic beat is an ordinary pattern.
Cutting either would lose a real distinction to fix a coincidence that is not a
problem. No change.

**5. Bookkeeper's painting — leave it unused.** None of the 23 restored feats
is ledger or counting content, so retargeting it now would recreate exactly the
picture-doesn't-match-meaning problem this migration exists to fix. Corvus's
identity is economy-adjacent, so a future economy-flavoured feat is its natural
home. Forcing a mismatch today to avoid one idle asset is the worse trade.

## And a gate that was not gating

Caught while applying the STICKY FINGERS patch: **`zv_trade_parsegate.js` had
been passing vacuously.** Its default argument was
`tools/_zv_trade_scratch.html` — an untracked scratch build frozen since 31 July
— so every bare `node tools/zv_trade_parsegate.js` compiled *that* file and
reported PASS regardless of what had just been edited.

The rule it enforces is *the parse gate must fail the chain*. It could not fail
anything: this whole session's patches to `fark_proto.html` were gated against a
file none of them touched.

**Nothing was damaged** — the live file compiles clean, and the probe suite runs
against the real served page, which is a stronger check that was passing all
along. But the cheap check was worthless, and it was worthless silently.

**Found by noticing the reported char count never moved across three different
edits.** Not by reading the script — by a number that should have changed and
did not.

Fixed: the default is the game, a missing file exits 1, and **the file actually
read is printed with its mtime**, so a stale input appears in the output instead
of hiding behind the word PASS. Verified three ways — bare invocation gates
`fark_proto.html`, a missing path fails, and an injected syntax error fails with
exit 1.

## What's next

Visual plan **Phase 5 — the asset registry**: one table mapping logical name to
path, so the previous game's `assets/` folder becomes unreachable by accident.
Highest-value remaining item and the only non-probe one.

---

# Phase 4b — The badge remap

**Status:** complete, deployed `9082bf1`. Suite is 14 probes: 13 pass, 1 fail
(the two known Phase 2 reds), 0 error.

## The headline: a rule can be live through one door and dead through the other two

A table rule is reachable three ways — a boss's **badge**, a **sleeve** the
player wears, and a **sealed seat**. They are three doors to one rule, and this
remap turned up two rules that only worked through some of them.

**ZERO HOUR was live as Grog's badge and dead through a sleeve and a sealed
seat.** The brief's "Grog: Last Call → Zero Hour" had shipped by *recycling the
id* rather than minting a new one, so `last_call` the id carried Zero Hour the
rule. `_RETIRED_RULES={last_call:1}` then switched that id off everywhere
`_ruleActive` is consulted — which is every door except the badge, because
`_iconFire` reads `G._tell.id` directly and bypasses it.

**Zero Hour is claimable as boss spoils.** A player could win it and have it do
nothing. The code comment at `_RETIRED_RULES` names this exact trap and states
it is not fixed; giving the two rules honest ids (`last_call` / `zero_hour`)
removes the reason the guard existed, and the table is now empty.

**Steeped had the same split, pointing the other way** — and parking it is what
exposed it. The bonus **accrues** through `_ruleActive`, which sees all three
doors. It **paid out, displayed, and reset** through `G._tell.id === 'steeped'`,
which sees only a badge. Those two agreed for exactly as long as Mabel wore it.
Parked, a cursed seat rolling Steeped would have accrued a bonus every roll and
paid none of it, forever. Four sites moved to `_ruleActive`.

That is the same bug this phase set out to fix, reappearing in the same commit
that fixed it. Which is why the new probe asserts the shape rather than the
instances.

## What was ruled

- **Zero Hour → Mabel, by name.** The position framing ("last slot before
  Ambrose") is dropped: it never checked against existing assignments, and
  there is no confirmed order for the middle six anyway. Aldric already carries
  enchant suppression (Still Waters) and Brutus a turn-length constraint (Drill
  Order), so either would have doubled a theme that boss already owns.
- **Grog keeps LAST CALL, retuned to 800.** Not a fresh number — it is the bar
  TEETOTALLER already uses for "never a bank under X", so the game states one
  threshold instead of two arbitrary ones. 500 read weak because most ordinary
  turns clear it without trying.
- **Steeped is parked, not deleted.** Every other candidate boss already carried
  a rule, so *something* was displaced whichever name was picked; once
  displacement is unavoidable, throwing away tested, shipped work is the worse
  trade.
- **Boss counters are per-run.**

## A correction I owe on the question I asked

I reported Last Call as *"dead code in an `if(false)` block, so reviving is
cheap."* Half right, and the wrong half mattered: the **mechanic** was indeed
sitting in `if(false)` at 500 — but the **id had been reused for Zero Hour**,
so reviving it was never a one-line flag flip. It needed a new id, a rule moved
off another boss, and the retired-rules guard untangled. The design ruling was
unaffected; the cost estimate was wrong.

## What was built

| Change | Why it is not just a rename |
|---|---|
| Grog → `last_call` / **LAST CALL** / `minBank:800` | the rule did not exist; the id was occupied |
| Mabel → `zero_hour` / **ZERO HOUR** | frees `last_call`, and gives the rule an id that means it |
| `PARKED_TELLS` | `_tellById` **scans RUNGS** — a rule existed only while a boss carried it, so "keep the rule, drop the badge" was not expressible |
| `_RETIRED_RULES` → `{}` | kept as an empty table, not deleted: the mechanism is right, its one entry was not |
| `_SEAL_POOL` + `zero_hour` | a parked rule stays playable as a cursed seat, which is the point of parking it |
| `_iconFire` → `_ruleActive('zero_hour','p')` | the direct read *was* the bug |
| bank-void back on, threshold read from the rule | `G._tell` is null for a sleeved or sealed Last Call — the same direct-read mistake |
| `S.npcState={}` at run start | streak and carryover lived on `S`, so they persisted across runs |

**The voice moves with the rule.** Grog's Zero Hour line was a bar-closing line
and read wrong in Mabel's mouth. Hers is stitchwork, which is also what her
cards are made of. This was Denis's check, and it was the right one to make:
there is no separate bark file, so **the tell's `desc` and `icon` ARE the
flavour** — nothing else keys off a tell id for dialogue.

## What it found that nobody asked about

**Three more badges still carry recycled ids.** Measured off the live roster:

| Boss | Rule shown | Id underneath |
|---|---|---|
| Corvus | FIRST STRIKE | `in_arrears` |
| Aldric | STILL WATERS | `confession` |
| Whisper | KINDRED | `counterfeit` |

Harmless **today**, because `_RETIRED_RULES` is empty. But it is the same
divergence that produced the Zero Hour bug, and any future "retire the old rule
ahead of its replacement" entry re-arms the identical trap on whichever of the
three it names. Left alone deliberately — renaming touches many sites and is a
call to make on purpose, not in passing.

## The check that caught me

`apv_terminology` went red within a minute of the Mabel line being written: I
wrote *"Touch a **marked** die at my table"*, and the rule is that a mark on a
die is an **enchant** now — a rule Grog's original text had already been
corrected for. I inherited the wrong word from the line I was replacing.

Worth recording because I had already recorded a baseline with that red in it.
Fixed and re-recorded before the commit; a baseline that blesses a bug you just
introduced is worse than no baseline.

## Guideline compliance

| Requirement | Where from | Met? |
|---|---|---|
| Zero Hour to Mabel by name | Ruling | **Yes** |
| Last Call at 800 | Ruling | **Yes** — read from the rule, not hard-coded at the call site |
| Steeped parked, not deleted | Ruling | **Yes** — `PARKED_TELLS`, still in the seal pool, still paying out |
| Check Mabel's bark for Steeped flavour | Denis's added check | **Yes** — no separate bark exists; the tell `desc` is the flavour and both moved rules were rewritten in voice |
| Boss counters per-run | Ruling | **Yes** |
| Patch via `.py`, not heredoc | Standing rule | **Yes** |
| Parse gate must fail the chain | Standing rule | **Yes — and it did.** Caught a brace-arithmetic slip that emitted `}}},`. That is the first time this gate has failed anything; it had been reading a stale scratch file until an hour earlier |
| Verify measured, not reasoned | Standing rule | **Yes** — new probe drives each rule through all three doors |

## What this does *not* cover

- **`minBank:800` is unplayed.** The rule fires from real state and the void
  path is restored, but no live match has yet banked under 800 against Grog.
  Wants a playtest before the number is trusted.
- **The three recycled ids above** are named, not fixed.
- **`last_call` is also a handicap id** — an unrelated system that raises the
  target 1.5x. Now that the tell of the same name is live again, the collision
  is genuinely confusing to read even though the two never interact.
- **Per-run `npcState` is untested across a run boundary.** It resets where the
  run resets; nothing has yet played two runs to watch a streak not carry.

## What's next

Visual plan **Phase 5 — the asset registry**.

---

# Phase 5 — The asset registry

**Status:** complete, deployed `31adddd`. Suite is 17 probes: 16 pass, 1 fail
(the two known Phase 2 reds), 0 error.

## The headline: the plan's premise was wrong, and measuring it first is the whole story

The visual plan says this, and it is the reason Phase 5 was ranked highest:

> *"`assets/` is the **previous game's** art. `Art/Assets/` is current. Nothing in
> the code says so, so every lookup is a chance to reach into the wrong one — and
> I did it three times today (font, coin, diamond)."*
> *"A registry … makes the old folder **unreachable by accident** rather than
> merely discouraged."*

Measured before building anything:

| | |
|---|---|
| static asset paths that resolve | 77 (28 current tree, 49 old tree) |
| static asset paths that **do not** resolve | **0** |
| old-tree paths with a replacement in the current tree | **2** — and one is a `.psd` |
| old-tree paths with **no** replacement anywhere | **47** |

**`assets/` is not a graveyard being wrongly referenced. It is a live
dependency.** Those 47 are every font in the game, all the audio, the nine
character portraits, the eight match frames and the whole Night_Art UI set.

**A registry that made the folder unreachable would have broken the page** — and
would have taken `'JMH Beda'` with it, the family this project keeps calling
"the game's font", which loads from `assets/_mockups/new_main/`.

The three mistakes that motivated the plan were real. But they were about
**reaching for the wrong source when writing new code**, not about the code
pointing at stale files. Only two paths do that, and one of them resolves to a
Photoshop document nothing can display. So the registry **names** rather than
**bans**, and that is a different artefact than the one specified.

## What was built

**`FK_ART`, 21 entries**, in its own script block ahead of everything that reads
it:

- **Directories in the current tree** (13) — homescreen, buttons, icons, new
  run, store, patron frames, patron characters, traits, props, last orders,
  hearts, boss backgrounds, feats, win plates.
- **Directories in the OLD tree** (3) — mockups, enchant icons, fonts. Marked
  **deliberate, measured, not stale**, so the next person does not "fix" them.
- **Single files this project has picked wrong before** (3) — the coin, the
  diamond, the shelf background.
- **The font family.** Not a path. The entry most likely to actually save
  someone: `--font-px` is `'Alagard','Press Start 2P'`, the previous game's
  pixel font, and it reads as the obvious choice right up until Denis points out
  the score is in the wrong typeface.

**A registry nobody calls is a comment.** The thirteen prefix constants
scattered across 22,000 lines are now *redefined from it* — `var
PT_P=FK_ART.patronFrames;` — so every call site is untouched (zero blast radius)
while there is exactly one place the strings live. Two of them, `BT` and `BTP`,
were the same directory declared twice 20k lines apart; now one entry.

**`apv_asset_registry` gives it teeth.** Three ways a registry dies, one check
each:

| Failure | Check |
|---|---|
| an entry rots — art moves, the registry keeps the old path, and the one place people trust becomes the one place that lies | every entry **fetched**, directories included, so a deleted folder cannot hide behind "it's only a prefix" |
| the font entry is declared but nothing uses it | checked **as a font** — declared *and* first-choice for some element. That is the Metamorphous test |
| someone re-hardcodes a path and the registry quietly stops being read | the served source is grepped for `var NR='Art/…'` — the values would still match, so comparing values alone would pass |

## What it found

**528 image loads across six screens, zero dead** (`apv_asset_404`). That probe
covers what a static scan cannot: 54 of the file's asset paths are built at
runtime from a prefix plus a name, and the join is where a 404 hides —
`Death&Taxes.png` needs URL-encoding at one call site and not another.

**One genuinely dead font, not fifty-eight references.** This one is a
correction to my own earlier report, and the mistake is worth stating: I read
`document.fonts.status === 'unloaded'` as *unreferenced*. It is not. **Unloaded
means the browser never fetched it**, which happens whenever no rendered text
has resolved to it *yet*. Measured properly — all nine screens, counting
elements whose **computed** `font-family` names each family *first*:

| Family | Elements | |
|---|---|---|
| Uncial Antiqua | 270 | live |
| IM Fell English | 61 | live |
| Jacquard 24 | 9 | live |
| Macondo | 7 | live |
| **Metamorphous** | **0** | dead — one `@font-face`, zero uses |
| Press Start 2P | 0 primary | kept — it is the fallback inside `--font-px` |

One declaration deleted. **Had I acted on my own earlier claim, five live fonts
would have gone with it.**

## Guideline compliance

| Requirement | Where from | Met? |
|---|---|---|
| One table, logical name → path | Visual plan Phase 5 | **Yes** — 21 entries |
| Make the wrong folder hard to reach by accident | Visual plan Phase 5 | **Reinterpreted, and said so.** Unreachable was measured impossible; the registry names both trees and marks the old-tree entries deliberate |
| Give Phase 2 something to assert against | Visual plan Phase 5 | **Yes** — `apv_asset_registry`, three failure modes |
| Additive; no behaviour change | Visual plan | **Yes** — constants redefined, call sites untouched |
| Verify measured, not reasoned | Standing rule | **Yes** — every entry fetched; match screen re-shot after the rewire (106 images, 0 dead) |
| Patch via `.py`, not heredoc | Standing rule | **Yes** |
| Parse gate must fail the chain | Standing rule | **Yes** — 3 scripts now, all pass |

## Two probe bugs found by writing the probes

Both worth recording, because both would have sent someone hunting a bug that
does not exist:

1. **`NR` reported as "not reading the registry".** Seven of the thirteen
   rewired constants are `var`s **inside a function** and are simply not in
   scope for a page-scope `eval`. "Cannot be seen from here" is a different fact
   from "is wrong". The source-grep covers those seven instead.
2. **The rule-migration test reported a working migration as broken** (Phase 4b
   / P428). The migration lives inside `if(!S){…}` in `_getS` — correct, that is
   run-load — so calling `_getS()` twice on a warm page skips it entirely. The
   test has to reproduce a **cold start**.

## And a flake finally fixed rather than recorded around

`apv_bust_settle` had been flapping red/green for three phases. Its
`pauseLooksRight` key asserted a hand-picked **400–1600ms window** on a gap
produced by a physics solve over real dice — a guess about a duration nobody
specified, dressed as an assertion.

Demoted to a reported number. **The ordering is the real claim** — the bust
verdict must not reach the player before the dice stop — and that stays an
assertion, true or false regardless of how long the solve took. The duration is
still measured, so if it ever needs a bound, the number to bound it with is in
the output.

I had already recorded a baseline with that red in it, twice this session
(the other was the terminology red). Both re-recorded before committing: **a
baseline that blesses a red you just introduced is worse than no baseline.**

## What this does *not* cover

- **The registry is not enforced at new call sites.** Nothing stops someone
  writing a raw path tomorrow; the probe catches a re-hardcoded *constant*, not
  a fresh literal in a new function. Making that impossible needs a lint over
  the source, which is a bigger and separate tool.
- **`assets/` still has no owner.** 47 live dependencies with no replacement is
  a fact, not a plan. Whether the character portraits and match frames should be
  redrawn into the current tree is an art decision nobody has made.
- **Two stale paths remain**, named and not touched: `Environment_ART/gameover.png`
  (its twin is a `.psd`) and `Menu_Art/Settings.png` (twin exists at
  `Art/Assets/Panels/Settings/settings.png`). Swapping them is a look change.
- **Nine screens, not every state.** The font reachability sweep covers the
  screens the game can be driven to; modal states inside them were not
  enumerated.

## What's next

Effect plan **Phase 1 — the inventory**: decompose ~50 cards, enchants and
badges into trigger / condition / effect. The *misfits* are the valuable output.

---

# Effect plan Phase 1 — The inventory

**Status:** complete, deployed `1850e3c`. Full decomposition in
`docs/EFFECT_INVENTORY.md`; this is the summary and the re-plan it triggers.
No game code was touched.

## The headline: the trigger bus already exists, and it is 69% done

The plan is written as though the bus has to be designed. **`CFX` is shipped.**
It dispatches on seven hooks — `canUse`, `use`, `roll`, `bank`, `bankBonus`,
`turnStart`, `bust` — and **20 of the 29 live family cards already route through
it.**

That is the vocabulary Phase 3 was going to spend its time inventing, already in
the codebase, already carrying two thirds of the content.

**The nine that do not route through it are the finding underneath.** `bloom`,
`cultivate` and `vanguard_f` live inside `famCommitBonus`; `for_keeps` and all
five tavern cards are wired wherever they happen to act. They have no `CFX`
entry, so **a migration that starts from the effect table cannot see them** —
which is precisely where a half-migration would leave a hole, and the plan does
not mention them at all.

## What the plan asked for

> *"Decompose all ~50 cards, enchants, badges and relics into
> trigger / condition(s) / effect(s)."*
> *"**The valuable output is the rows that DON'T fit.** A clean table proves
> nothing except that the vocabulary was written by someone who'd seen the
> content."*

**69 items, not ~50** — 8 enchants, 6 Break death rows, 29 live family cards,
9 table rules, 8 relics, 9 material traits. Read out of the running game via
`tools/effect_inventory.js`, not off a document, because every wrong answer this
project has produced came from the other way round.

## What it found

**All three predicted misfits confirmed** — Jade's Break row (a re-entrancy rule
about a roll already in flight), Fair Trade (a lease with its own clock), and
Honeytrap (a constraint on generation, not an effect on a result).

**Six more, and one of them changes a planned decision:**

- **Kindred is not a multiplier.** Its "double strength" means something
  *structurally different* for each of the five whitelisted enchants: Tithe pays
  2× gold, Ward saves **two-thirds instead of a half**, Snare halves **twice on
  the same shot** rather than watching a longer window, Snuff and Fog hold their
  seat for **two turns rather than two lanes**. Break and Trade are excluded
  because no coherent 2× exists.

  Phase 3 says *"decide the multiplier rule now even though nothing multiplies
  yet — this is the one that silently changes numbers later."* Measured,
  **nothing multiplies and nothing will.** The only doubling in the game is five
  bespoke rules sharing a badge. Settling an arithmetic rule for it would be
  inventing a requirement rather than answering one.

- **Quicksilver is a permission, not an effect** — it grants an option, and the
  player is the trigger. It already sits in a different table from the other
  seven, which is a shape finding rather than bookkeeping.
- **Silver's weighted face table is the die's base geometry**, not an effect at
  all — the brief exempts it explicitly, and the bus needs somewhere else to put
  "this die's distribution differs".
- **Still Waters operates ON the system** — it changes whether other things
  fire. Tier-2, and the one rule that needs the bus to exist first.
- **Zero Hour triggers on another effect firing**, not on a game event.
- **Four enchants are markers with a lifetime, not effects with a moment.**
  Snare, Snuff, Fog and Trade each mark a lane, wait, resolve on the opponent's
  next turn, then clear. Snare's whole design correction was *shortening the
  window* — a statement about lifetime, which "effect" does not carry.

**And two whole groups may not belong on a match-scoped bus at all:** the five
tavern cards act on the RUN (`the_tab` is a debt with a due date;
`hair_of_the_dog` fires next match), and `for_keeps` is a stake whose effect is
a change to the reward screen.

## Two simplifications, worth as much as the misfits

- **Relics are not a category.** Six of the eight reuse a material's mechanic —
  `grogs_tooth`/`obsidian` both `shatter_bonus`, `mabels_thimble`/`amber` both
  `triple_bonus`, `corvus_ledger_d`/`starstone` both `starstone_bonus`. A
  seventh is a die born carrying an enchant. **They need the material
  vocabulary plus a numeric override, not one of their own.**
- **Last Call and The Reckoning are one rule.** Both void a bank under a
  threshold; only the source of the threshold differs.

## A dividing line nobody had drawn

Of the nine table rules, **four carry a numeric field and five carry none**:
`last_call`/`minBank`, `drill_order`/`maxRolls`, `pickpocket`/`chance`,
`steeped`/`perRoll` — versus `zero_hour`, `first_strike`, `still_waters`,
`kindred`, `reckoning`.

The four are **data**. The five are **code** — and every one of them is either a
misfit above or acts on the system itself. That split predicts the migration
cost almost exactly, and nobody had noticed it because the rules are declared
inline on eight different bosses.

## Guideline compliance

| Requirement | Where from | Met? |
|---|---|---|
| Decompose all content into trigger/condition/effect | Effect plan Phase 1 | **Yes** — 69 items, `docs/EFFECT_INVENTORY.md` |
| The misfits are the output | Effect plan Phase 1 | **Yes** — 3 predicted + 6 new + 2 whole groups |
| Touch no game code | Effect plan Phase 1 | **Yes** — one extraction tool, one doc |
| Measure, don't reason | Standing rule | **Yes** — read out of the running game; corrected my own arithmetic before shipping (18→20, 11→9) |
| Start with Phase 1 alone and re-plan | Plan's own closing instruction | **Yes — see below** |

## THE RE-PLAN — what Phase 1 says to change

The plan's own last line: *"I'd start with Phase 1 alone and re-plan after it.
It's the only thing that can tell us whether the rest of this plan is the right
shape."* It has, and three things change:

1. **Phase 3 loses the multiplier decision.** There is nothing to multiply.
   What Phase 3 should settle instead is **effect lifetime** — four enchants are
   markers with a placement, a window and an expiry, and nothing in the plan's
   vocabulary expresses that.
2. **Phase 4's first group is wrong.** It says enchants first, "newest, best
   understood". True, but four of seven are lifetime-markers and one is a
   permission — enchants are where the vocabulary needs its *hardest* new
   concept. **The 20 cards already on `CFX` are the honest first group**: the
   ones the existing vocabulary already fits.
3. **A new group exists that the plan does not list:** the nine hardcoded cards.
   They are not on the effect table, so they will not appear in any migration
   that enumerates it.

**None of this is a decision I should make alone** — it re-scopes two phases of
a plan Denis approved. The recommendation is above; the call is his.

## What this does *not* cover

- **Decomposition by shape, not by reading every implementation.** A card whose
  hooks look ordinary may still do something structural inside them. Slow Cook
  (four hooks) is the most likely to be under-described.
- **No decision, no code.** This is the map.
- **Opponent-side effects do not exist**, so every "affects the opponent" row is
  one-directional today. The brief defers that deliberately, and it will change
  the vocabulary when it lands.
