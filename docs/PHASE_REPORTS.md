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

**Status:** complete, deployed `d6772fc`. Suite is 13 probes: 12 pass, 1 fail
(two known reds inside it), 0 error. `FEAT_ART` is green for the first time.

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

## Decisions needed

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

## What's next

Visual plan **Phase 5 — the asset registry**: one table mapping logical name to
path, so the previous game's `assets/` folder becomes unreachable by accident.
Highest-value remaining item and the only non-probe one.
