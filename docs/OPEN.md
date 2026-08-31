# OPEN — questions and blockers

The only file you need to read. Everything has my recommendation, so **"yours"
is a valid answer.** Answered items are deleted, not marked — this stays short.

---

## `window.G` — ALL THREE FIXED (P886). One residual, and it is a real question.

`G` is a `let`, so `window.G` was undefined for the life of the page and every
`window.G&&` guard was dead. All three are now on the binding, driven 18/18:

- **The bank sound pitches again.** Measured 520/660/900 at 20% of target,
  598/759/1035 at 70%, 676/858/1170+**1287** at 88%, 780/990/1350+**1485** at
  98%. The hot harmonic had never played.
- **Tap-to-fast-forward works.** A real pointerdown on the board takes
  `_ffMult` 1 → 0.15 and `_oppDelay(1900)` from 1900ms to 285ms; off the board,
  on a button, and outside a rival turn all correctly do nothing.
- **The sim really isolates `oppShouldBank` now.** 10,733 calls during a sim,
  not one of which saw a live `G` or an active sealed rule, and a forced throw
  still restores the binding through the `finally`. **Safe for the ladder
  re-run.**

**THE RESIDUAL — yours, because it is a judgement about feel, not a bug.**
With the tap live, `_afterOppSettle`'s `MIN = _oppDelay(260)` drops from 260ms
to **40ms**. That window exists to cover the 3D layer picking the dice up. It is
a pre-existing shape — the shipped `fastRival` setting already takes it to
104ms — and I could not time it honestly on a ~1fps harness, so I changed
nothing and am telling you instead of guessing. If a fast-forwarded rival turn
ever looks like it skips a beat rather than running fast, this is the line:
flooring it (`Math.max(160, _oppDelay(260))`) keeps the pickup window while
still accelerating everything else. *Recommendation: ship as-is and watch for
it; the floor is a one-line change if you see it.*

**The flat `bustsPerMatch` is found, fixed and measured (P888) — and it was
not a metric bug.** `simTurn` gave a free bust save to any loadout containing a
silver die: a per-turn counter, spent by returning `bank()` instead of
`bust()`, and a turn reaches that check at most once. So **one silver die was
100% bust immunity every turn for the whole run**, on the rival's seat as well
as yours, and it did not even need to still be in hand.

Silver's own definition says the save was retired — *"the old bust-save is
gone… it never removes the zero"* — and its `effect` is `null`. It pays through
its weighted roll table, which the sim already gets for free, so the line was
counting a retired mechanic twice.

Measured, 100 tier-0 matches, one bone swapped for one silver: 91 busts with
bone, **zero** with silver and 84 saves consumed, 80 with a clone of silver's
roll table under a different id. After the fix: bone 0.78, silver 0.62, clone
0.58. The persona path went from exactly 0.000 on all six personas to
0.13–0.247.

**This is a balance-measurement defect, not a display one.** Every `patronWin`
and `bossWin` ever produced for a silver-bearing loadout is inflated — at tier
0, patronWin ran 18% / 24% / 22% across none / silver / clone, so about half of
silver's apparent gain was the retired save. It lands before the ladder re-run,
alongside the sim's `G` isolation.

**Correction to what I told you.** I said every row read `bustsPerMatch: 0`. It
did not — it was zero exactly when the gear contained silver, which is G2-mid
and G3-late, half the default table, and normal for G0-bone and G1-early. The
rows I was looking at came through callers that pin a silver-bearing gear, so I
generalised from a filtered view.

### SILVER: WHAT THE RE-DERIVATION LEFT OPEN

The full-silver verdict in `FARK_MASTER_BRIEF.md` is **withdrawn, not
re-run** — its instrument granted the immunity it was used to judge, and no
harness that touches `_runBalanceSim` can produce a run-win number at all.
Re-measured (2,000 matches/cell): six-silver is indistinguishable from the
shipped G2-mid gear and +22–25pp over all-bone. **Not a trap, not a menace.**

Two things fell out that are more useful than the verdict was:

**Six silver is unbuildable.** `DICE_STORE` stocks silver at 1 per run, every
purchase path guards on the stock, and the starter draft adds at most one more
— ceiling of two, three with Brutus's Shield. **The buildable two-silver stack
beats two 100g IRONS by +0.8 to +1.3pp, which is inside noise.** A 580g die
performing like a 100g one is the live question, and it is a pricing one.
*Recommendation: yours — either Silver's price comes down or its weighting goes
up. I have not touched either.*

**The bug's leverage ran backwards from the intuition.** The free save was
worth 4.8pp of a 7.2pp apparent gain for ONE silver among bones (67% of it),
and +0.2pp for six. It inflated *thin* silver builds, not stacked ones — so the
defect cannot by itself explain a "stacking is a trap" verdict.

**Still carrying the same contamination, not yet re-derived:**

1. **`_runEconomySim`'s `PWIN`/`BWIN` constants.** It is run-level but rolls no
   dice — it takes win rates as hard-coded numbers copied from the balance
   sim's gear-band rows, which were silver-bearing. Every `runsWon` and pity
   number it has produced rests on them, and **this is the most likely ancestor
   of the "4% run wins" figure.**
2. **`G3-late` is untested.** It carries silver plus `bankAdd:500` and
   starstone. `G2-mid` measured as unmoved by the fix (inside noise), but G3
   has not been checked and it is an "intended gear" row in the acceptance
   targets.
3. ~~**A cross-harness discrepancy.**~~ **RESOLVED — and the archive had
   already answered it before I raised it.** I measured a per-turn silver/bone
   bust ratio of **0.33–0.40** against the **0.54–0.58** anchor and flagged it
   as a lead. Ruling #24 in `docs/archive/SIM_RESULTS_2026-07-31.md` had
   already swept that ratio across **seventeen policy cells** and found it runs
   **0.126 → 0.864**, monotone in how deep the turn pushes, and is explicitly
   **not policy-invariant**. My number sits inside that sweep. It is the
   documented policy dependence, not a discrepancy — and those figures came
   through FSIM, whose compat bust-save is off by default, so they were never
   contaminated. **No action.** What the anchor is missing is the caveat that
   it holds at one policy only, which Ruling #24 already says.

**Fixed on the way (P890), because my own P888 broke it:** FSIM's
`__shippedCompat` emulated two differences from the shipped sim, one of which
was the free bust-save P888 deleted. Left alone, `sim_verify`'s control would
have been inverted — the compat arm granting a save the thing it models no
longer has, reporting a gap *in FSIM's favour*, which is the worst direction
for a check whose job is to catch FSIM being wrong. The save half is deleted;
the hot-dice half is untouched and still real.

**Checked and cleared, so you don't have to:** the `_runCowardiceGate` verdict
survives (PUSH PAYS, margin ~18.5 against a threshold of 5; the bug inflated it
by ~2.5pp). The **TWICE SAVED** feat is reachable — it reads `_featWardSaves`,
which is incremented where a ward halves a busted turn, so it tracks ward saves
and those still exist.

---

## BOSS REWARD BRIEF — BUILT (P860-P866). Six things need you.

All five sections shipped in §8's order and every §9 check is driven. Items 1
and 2 below are now CLOSED — kept visible so the corrections are on the record
rather than silently deleted. The rest is what I could not decide.

**1. Night 8 renown — FIXED (P867), no longer a question.** Lifted the
payout out of the if/else chain into an unconditional block above it, keyed
with `_bossKey`; deleted the split so Ambrose falls through to the ordinary
spoils branch with his three tiles; his line is now a header above them.
The trophy grant moved up with it, so the shelf has ONE writer covering all
eight bosses rather than two. Driven: first win pays (delta 255 — the +150
plus other renown a boss win already pays), the latch holds it to once per
run, a cleared latch pays exactly 150, Brutus pays none but still takes his
trophy, and Ambrose keeps three unclipped tiles.

**2. ~~Actives are now boss-only~~ — MY QUESTION WAS WRONG, withdrawn.**
Denis: *"Patrons should have regular family cards, some passive, some
active. And I can win active cards from the start like I currently do?
Only limitation is boss cards, limited to boss encounters."* That is
already what the brief does, and I conflated two tables. §2 deletes
CARDS-table actives, which the player has never been able to hold; the
cards a player drafts are FAM_CARDS. `famOffer` filters on `_famDraftable`
and tier only — no `kind` test. Driven to be sure: **647 of 1200 night-1
offers are active family cards (53.9%, against a 58.6% share of the table),
15 distinct ones**. Nothing to change; the patron draft was never narrowed.

**3. §6's census was wrong in both directions; the assertion is narrower than
the brief asked.** Driven at runtime against the real arrays: **6 collisions,
not 23**, and one at depth three, not three. Five of your 23 were test
fixtures (`{id:'steady_hand',tier:1}` at 22510 and 45590) counted as table
rows. Ten more you missed are *foreign keys doing their job* — an NPC_RESCUES
row is named for the card whose effect it runs, and `_RELIC_FAM` is keyed by
DICE_TYPES id on purpose. An assertion over "any id in two arrays" would have
shouted ~20 times per boot on correct code. It checks definition tables only,
and reports unresolvable REFERENCES as a second, separate failure. §2 retired
two of the six; four remain, all harmless: `the_collector`, `high_roller`,
`second_wind` (CARDS vs FEATS) and `pickpocket` (the Vagabond family card vs
Finnick's badge). Rename any of them, or leave them grandfathered?

**4. Four dead blocks left in the bust and bank paths.** Deleting the twenty
handlers stranded `stitchActive`, `vowActive`, `ledgerActive` and
`allInActive` — their only writers were those handlers, so four blocks now
test a flag nothing can set. Removing them is surgery in the two riskiest
paths in the file for zero behaviour change, so I marked them in place instead
and stopped. Want them out in a patch of their own?

**5. §5 Pass B and Pass C not done, deliberately.** Pass A shipped (12
player-facing strings). Pass B renames the persisted `S.run.tells` /
`S.run.sleeve`, which needs a migration and buys nothing a player can see —
your own brief says only do it "if the rename actually buys something". Pass C
you already called "probably never". Say if you want either.

**6. §10's two recorded items, answered.**
- **Steeped has three disagreeing numbers for one value**: 100 in the record,
  `G._tell.perRoll||50` in the player fallback, and a hardcoded 100 on the
  rival side. It is parked so this is dormant, but it is one retune away from
  paying three different amounts.
- **Relics post-P834**: inert *by starvation*, not by deletion. `_RELIC_FAM`
  has one live reader (`_matFam`) and the `effect:{}` readers are all live
  code — nothing hands them a relic material any more. One route survives: a
  PRE-P834 save with a relic still in `S.run.diceInv`, which `famDiceSwapIn`
  will seat and no migration strips. Three of the effect blocks are dead even
  if seated (`palm_adjacent`, `fang`, `weight_bank` are implemented by
  hardcoded material checks, not by the block).

**§11 IS BUILT (P868-P870), SPLIT ACROSS TWO MEASURED RUNS.** All three parts
are difficulty levers, and they do not point the same way — §11.1 and §11.2
make nights 6-8 easier, §11.3 makes every NPC harder, patrons included. Run
them together and the two directions net out to noise.

- **Run one — the corrections, LIVE.** §11.1's cap and §11.2's reorder. Both
  are fixes to things plainly wrong rather than tuning. The cap is now
  structural (`NPC_CARD_CAP` in the function, not eight rows that have to
  agree) and the match-the-player lift is deleted; driven at player hand
  sizes 0-4 for all eight bosses plus a patron, worst hand seen is 3 where it
  used to become 4. **This branch is what to freeze and run the ladder
  against.**
- **Run two — the synergy, SHIPPED DARK.** `NPC_SYN_WEIGHTING` is `false`.
  Flip that one boolean and re-run the ladder; the delta is attributable
  entirely to §11.3. Proven dark, not assumed: the flag-off distribution was
  diffed against a build from the previous commit at 6000 draws per boss and
  the worst per-card delta is 0.0070 — sampling noise. The old shuffle is
  preserved as the same lines, not an equivalent rewrite.

  Fourteen starter tags are in, all on non-signature cards (a guaranteed card
  cannot be up-weighted). With the flag on, tagged cards draw ~0.21 against
  untagged ~0.08, every pool member is still drawn across 4000 draws per boss
  — a zero would mean the weighting had become a filter — and a genuinely
  untagged pool draws identically on and off. Tag more pools whenever; it
  degrades to today's behaviour with none.

**THE VOICE PASS IS COMPLETE (P874 + P875).** The two stranded moments have
triggers now, so all 91 rows that could not fire are live. Nothing in the
patron tables is unreachable — driven, and the probe asserts it as
`nothingStranded` rather than as a count.

- **preroll** rides the head of `runOppTurn`, which runs exactly once per
  rival turn (its internal `step()` is the per-roll loop), at probability
  **.3** — matching the hesitation dial, for the reason that dial's own
  comment gives: a rival turn already holds three or four beats.
- **waiting** is a `setTimeout`, not a poll: **9 seconds** of no input on
  the player's turn, **once per turn**, probability 1 because the threshold
  and the latch are already the gate. Re-armed by a single capture-phase
  pointerdown listener, so every interaction counts as “still there”
  without instrumenting any of them.

**Two numbers are mine, not the brief's** — `DLG_IDLE_MS = 9000` and
`OPP_TURN_START = .3`. They are one-line dials; say the word if either
feels wrong in play. Bosses stay silent on both beats, which is a
consequence rather than a choice: they resolve through the trait pools and
the voice brief wrote patron lines only. Boss lines for these two moments
are a separate ask.

Still true from the same pass: `nv:1` on Golgoth's rows has no reader
(inert, kept); and `_dlgOutcome` still passes `null` where the skip map
goes, deliberately — win/loss fire once per match, so a per-match de-dup
could not do anything there.

**THE FX WORK — VERIFIED BEFORE BUILDING, AND SIX CLAIMS DID NOT HOLD.**
Nothing built yet. I checked both docs against the live file first, because
the design doc opens by correcting the audit and that is a warning about the
class of error. Six findings change the build order:

1. **The “missing layer” premise is refuted.** A per-die layer above the
   dice already ships — `.fog-float`/`.peek-float`/`.honey-float`/`.vang-float`
   at z-60, with `_famRefloatGhosts` re-anchoring them per die. And
   `D3X._slaveHost` already translates each die's chip under the drawn 3D die
   **every frame**. So a chip-anchored overlay tracks the settled die for
   free, and the audit's “a DOM chip is not where the die is” is no longer
   true. Route through these rather than adding a sixth layer.
2. **Only ONE of FKFX's primitives reaches a settled die**, not three.
   `_spray` works. `_glow` is completely dead (drop-shadow on an element with
   zero opaque pixels). And `_motion dx/dy` — which the design doc lists as
   working — animates `translate`, *the exact property `_slaveHost` writes
   inline every frame*. A comment at that site documents fixing this very
   bug; FKFX reintroduces it. STRIKE's shake moves the invisible hit box and
   the die zero pixels.
3. **Eight classes paint in 3D, not thirteen.** L2811 kills box-shadow/border;
   **L2812 kills every pseudo-element**. So the ❤ glyph, the `?`, dampened,
   combo-glow and die-kindred are already suppressed. The census is right
   about the mistake and roughly 40% over on the count.
4. **Two brands per die is a turn DEADLOCK, not a cosmetic issue.**
   `brand-spent`/`_spentLook` are per-die: a die that cast its 1-brand still
   has a live 5-brand, so `anyScoring` calls the roll non-bust while the die
   is dimmed and untappable. Not a bust, no legal move. Also the cap is
   enforced in **four** places, not one, and `_iconFaceRoll` *cannot* avoid a
   taken face — it has no die index at all, so “two lines” is an argument
   threaded through two callers.
5. **The flat 2D path is dead in the page.** `D3_MATCH` is read in four places
   and assigned in none. Deleting the CSS geometry costs players nothing — but
   three probes set it on a `#flat` hash and would need cutting in the same
   patch.
6. **Two lane-mark bugs the docs missed:** fog and snuff both call `_lmSpend`
   outside the branch that did anything, so a window turn is burned on a
   no-op. And Break was explicitly fixed for this exact overwrite shape
   (P526, “PUSH, not assign”) — the three lane markers were left with the
   un-fixed version.

**HARNESS CONSTRAINT, and it decides how any of this gets verified.** The
headless probe runs the 3D layer at **~1 fps**: `D3X._rolling()` takes ~19s
to clear against ~700ms real, and `_drawGlow` skips the entire pass while it
is true, so the glow canvas is never even created inside a normal probe
window. Part Six's tests — centroid across a re-throw, per-frame gap
assertions, idle-motion pixel diffs, 400ms budgets — are all frame-timed and
cannot run as written. They need to become state-polled with forced draws.
Worth knowing before building the thing they are meant to check.

**Also found, not acted on:** `getDie()` never returns null — it falls back to
`DICE_TYPES[0]`, so a card id fed to the die namespace silently yields the
*wrong die* rather than an error. That is the mechanism behind the
`corvus_ledger` / `corvus_ledger_d` bug the file already documents. And the
tell badge sits at opacity 0 for the whole of the FIRST boss match after a
cold boot — drill_order too, so it is not new — which needs a real-play check
before it is called a player-facing bug.


**The 2026-08-20 ruling batch is EXECUTED** (P832-P838): Corvus orderly,
boss :open pool wired (your 80 greeting lines shipped in P839),
DLG.triggerCard deleted, the additive resolver + all 22 patrons' growth
lines live, Seven Dice redesigned (free one-die reroll), relics are
trophies, committed dice sit out the vagabond drag (+ one real drag
canceller), the cardHit rule is complete (20 new dock fires, both
directions), all four leveling rulings (rival obsidian shatters through
a new rival-side removal path, no raw patron tier-III, the name IS the
character via S.run._artPersona, the recognition beat), and 155
unreferenced legacy files are out of the repo (psd masters and your
live-edited files kept). §8's Last Orders layout was VERIFIED already
in its ruled shape — your P804-P808 mockup round had resolved it;
nothing changed. Every item probe-driven; probes in tools/apv_*.js.

**§1's ladder rebuild: the instrument is BUILT and measuring.**
tools/ladder_real.js drives full real matches on both seats (tap-driven,
the harness's own carl/rita policies over F.legalKeeps, modal night
loadouts, bare gear — stated convention). Calibrated: ~75-130s per real
match; Brutus crushed carl 9900-5750 and 13200-4950 in the calibration
pair, consistent with the model-understates-the-rival finding.
**FOUR REAL CELLS MEASURED (2026-08-21, stopped again on your word):
ALDRIC carl 0/18 · ALDRIC rita 0/16 · WHISPER carl 0/20 · WHISPER rita
0/20 — 0 wins in 74 real matches.** The sim's 9-12% for those nights was
OPTIMISTIC; the real rival is stronger still. AMBROSE and FINNICK cells
not reached. Resume (tier is 0-INDEXED: night = tier+1, so nights
6,7,8,3 = tiers 5,6,7,2):
  node tools/shoot.js --url <dev>/fark_proto.html#lad=<tier>,<carl|rita>,<n> --eval-file tools/ladder_real.js

§2–§4 still need you or a playtest.

Rebuilt 2026-08-06 — it had reached 960 lines with four `CLOSED` sections still
in it, which defeated the point of the file. Deleted items live in git history.

---

## PATRONS ARE THIN BY RULING, AND IT'S YOUR OWN (measured 2026-08-21)

You asked: "patrons still don't have cards or decent dice even at
Finnick's level?" Measured, 12 generated patrons per tier plus a live
night-3 table:

**Cards.** Patrons get FAMILY cards only — night 3 averages **1.2**
(mostly tier I, 30% roll tier II), rising to ~2.4 by night 6. They get
**ZERO tavern cards, at every tier** — `pCardCount=0`, and that is
**P507, your own ruling**: the old code built patron hands out of the
retired 133-card legacy roster (17 distinct dead ids measured in real
matches), and the fix switched the layer off rather than repoint it,
because "a fresh patron card layer is unscoped design work." The
comment even predicted this conversation: *"NOTE: this makes nights 3-8
easier — a correctness fix, not a balance call."* So the thinness is
real, deliberate, and was always meant to come back as designed work.

**Dice.** Night 3 (tier 2) draws from bone/iron/lead + one lucky die —
measured across 12 patrons: lead 23, iron 19, bone 17, lucky 10, amber
3 (the 35% next-tier splash). **Family dice only enter at night 4**
(P822). So at Finnick's night a patron holds five plain dice, one
lucky, and about one tier-I family card — against a player with three
card slots, drafted cards and enchants.

**This is the other half of the ladder finding.** The measured cells
say bosses at nights 6-7 win ~100% (0 wins in 74). Patrons at nights
1-5 are the opposite. **The curve is bimodal: trivial seats, impossible
bosses** — which is exactly the shape a player would describe as "the
patrons don't do anything and then the boss is a wall."

**RULED AND SHIPPED (P851/P851b):** "patrons should get cards earlier…
if I have 3 cards or so they should have similar (and the ability to
play them)."

Measured first, both halves. **You hold THREE family cards flat from
night 2 to night 8** — `S.run.fcards` is hard-capped at 3 with no
growth curve anywhere; only card TIER rises. Patrons held 0.5 at
nights 1-2 (half of them NONE), 1.3 at nights 3-5, 2.5 at 6-8. And
**25-31% of every card they were dealt was unplayable by them** at
every night: `famUse` gates the rival on `NPC_FAM_READY`, which holds
7 of the 17 actives — the other ten are player-only UI (steady_hand,
transmute wait for a TAP), player-pool rewriters that would detonate
YOUR dice run for the rival (powder_keg, sacrifice), passive-shaped
(fools_gold_f has no `use()` at all), or run-scope economy cards.

Shipped: the hand now mirrors yours — **night 1 → 1, night 2 → 2,
nights 3+ → 3** — and the draw only offers what a patron can actually
use (any passive, or an active in the ready registry). Tavern cards
left the pool entirely (run-scope, inert in a hand — the grudge pool
already excluded them, the main pool didn't). Persona is a bias now
rather than a ceiling: amber/silver/obsidian carry only 2-3 usable
cards, so a 3-card hand used to silently under-deal. And the night<5
"one active" telegraph rule now SWAPS the surplus active for a passive
instead of deleting it — it was quietly costing a card.
**Measured after: 1 / 2 / 3 cards per night, 0% empty hands, 0 dead
cards at every night.** Driven (apv_patron_plays): a real night-6
patron fires double_or_nothing and sleight in a real rival turn,
charge 1→0 both times.

**Deliberately NOT done:** the ten dead actives were not force-added to
`NPC_FAM_READY`. That registry is load-bearing, not merely unfinished —
`CFX.tamper` run for the rival would break the rival's OWN cards and
pay YOU 300 (its target list is hard-coded to `G.oF`). Teaching the
other ten an actor branch is the scoped job in AUDIT_BACKLOG; this
patch stops dealing cards that job hasn't reached yet. ~44% of a
patron's cards are now playable actives, so ~4 in 5 hands hold
something they can fire.

**Still yours:** whether the night<5 one-active telegraph cap should
lift now that hands are full (it holds nights 3-4 to ~1 active + 2
passives), and whether patron DICE should follow the same parity logic
(family dice still start at night 4 per P822).

---

## Card interactions round 3: the roster deletes itself (P846, 2026-08-21)

> **SCOPE CORRECTION (2026-08-21, driven):** the CARDS-table layer is
> UNREACHABLE (see §1c) — `S.run.cards` is never filled by any live
> path. So "Gambler's Eye is live and obtainable" below is WRONG, and
> the sweep's "19 live / 6 retired" labels are wrong: the obtainability
> check I added asked `_buildDraftPool`, which feeds a draft screen
> that never opens. What remains TRUE and live: `_setDieVal` itself,
> and its enrollment of the FAM layer (steady_hand, transmute,
> powder_keg, encore, sacrifice via `_removeDieAt`) plus
> `famQuicksilver` — an enchant, genuinely reachable. The Gambler's Eye
> work (P846-P849) is correct code on a card no player can currently
> hold; it costs nothing to keep and is ready if the layer is revived.

Your second review held on every count. Shipped:
- **`_setDieVal(d,v)`** — write + redraw + R1 void at the MUTATION,
  routed through every player-side out-of-roll face write (17 sites).
  The dispatch id roster is DELETED: it enrolled six retired ids,
  missed the live Gambler's Eye, couldn't cover an enchant, and voided
  on refunded no-ops. Enrollment is by construction now; the new-card
  checklist item is "you already did".
- **Gambler's Eye enrolled** (live, obtainable, the worst hole: a
  whole-pool reroll off the roll path — driven through its real flow:
  activate → hold two dice → ROLL; promise+ghosts void, holds freeze).
- **famQuicksilver enrolled** (the enchant no card list could cover).
- **Still Waters fixed at rollFaceExclude**: it now carries the die
  object to `_rollTable`, so `_famHushed` sees it — both live call
  sites (Gambler's Eye, Grog's Flask) were bypassing the badge.
- **The over-void is gone**: a refunded no-op (flask with nothing to
  reroll) writes nothing, voids nothing — asserted as a PASS condition
  now, not accepted as a cost.
- **The sweep verdict is the claim**: 25 legs, zero tolerance, both
  sides asserted per leg (mutated ⇒ voided; refunded ⇒ promise
  intact), obtainability labeled per id (19 live / 6 retired). 25/25.
- **§1c above is rewritten** — the stale unreachable-layer claim (dead
  since P615, ~230 patches) is retracted, the source comment it had
  colonized is re-driven, and the original wipe finding is back as a
  live ruling ask.
Still open from your review, queued in AUDIT_BACKLOG: the ~18 live
draftable actives have void-coverage now but have never had their
EFFECTS audited to the fam-card standard; rollFace (NPC + hot-dice
path) has the same die-less Still Waters question as rollFaceExclude
did — measured next pass.

**P848 (your P847 verification — the structural answer taken):**
Gambler's Eye is no longer a second roll implementation. The branch
validates the split, freezes the holds, arms the visibly-differs flag
(`G._geExclude`, consumed by the deal's value writer, one exit in
`_clearRollForces`) and FALLS THROUGH to the main roll path — which
rolls exactly the free unfrozen dice, so every seam comes for free.
Driven (apv_ge_edges, 6/6): entry disarm preserved; the roll seam
fires once through the main path with the right rollNum; both holds
survive; all rerolled lanes visibly differ; and the headline — **a GE
reroll into a dead table fires deadRoll and fool's gold rescues**
(charge spent, turn alive; before this the player busted holding the
charge). The bust also resolves at the real settle now, not a 600ms
timer under 2s physics. Deleted with the copy: the inline reroll loop,
the duplicate bust check, onclick restore, turnRollCount++, and both
seams P846/P847 had grafted on. The tell-extraction backlog item
closed as moot. The full 25-leg sweep re-ran green after the rewrite.
One accepted edge, stated in the patch header: a Drill Order cap can
refuse the fall-through roll AFTER the freeze — the player keeps their
holds and banks, which is what the cap means. Also corrected on your
note: fool's gold's structural entry now states the real invariant
("every path into a dead table has already disarmed") instead of
crediting one handleRoll call site with the wrong line number.

**P849 (your P848 notes, both taken):** the Spur-wins-the-ternary
priority is now stated at the site ("do not fix this by reordering"),
and `_geExclude` joined `famTableChanged`'s gate with a comment telling
the next buffer's author to join it too — the one-exit invariant holds
by construction now, not by the current call graph. apv_ge_edges 6/6
after the gate change.

**P847 (your P846 verification, all four items):** Gambler's Eye's
ENTRY now disarms (famTableChanged after the refund guard — driven:
steady's flag+rings die at activation, where they used to sit painted
and inert for the whole GE window) and its reroll fires the roll seam
with the main path's payload (driven: one event, rollNum right —
slow_cook counts GE rerolls now). The post-roll TELL hooks are NOT
copied into the branch — that block wants one extraction with two
callers; backlogged. famFoolsGold and the jade Break row are documented
as structural in the rules doc: fool's gold is order-safe on both
branches, and jade must STAY direct-write — converting it would void
the promise the resumed roll is about to legitimately consume.

## Card interactions REVISED on your review (P845/P845b, 2026-08-21)

All four objections held, and one found a shipped bug:
1. **The 16-name list**: every id now verified three ways (in the
   dispatch switch, handler body read, individually DRIVEN — 22/22
   sweep legs green in apv_card_interactions_sweep.js) and the
   collision table is in the doc: old_bones/the_nudge + 6 others also
   live in NPC_RESCUES (rival seat, no cross-wire), finnicks_palm is a
   THREE-way collision (card + rescue + relic die), seven_dice is one
   id — the CARDS row IS the P834 redesign in place.
2. **Driving seven_dice found it UNREACHABLE in real play**: the P834
   redesign shipped behind timing:'idle' where the pool is always
   empty (measured) — the P834 probe drove the handler directly and
   never ran the gate. Fixed to 'choosing' (P845). Driving it further
   showed it's an ARM (mutates at its die tap), so it left the
   dispatch list and enrolls at the tap with its own flag (P845b) —
   the dispatch hook had been stripping its rings while the hijack
   lived.
3. **Preserve reclassified**: the taxonomy is now FOUR kinds — promise
   (void), arm (disarm), LANE RECORD (maintain — preserve's honest
   home), flag (nothing). Faces void, seats follow.
4. **Palm's two stories cross-referenced**: it has BOTH its 840ms lock
   and the R1 hook, in sequence, and the doc says how they compose.
The doc's coverage section now states exactly what was driven (22
legs) vs. what is structural (NPC-side ordering, the drag refloat).

## Card interactions: the rules are written + the Stargazer break fixed (P844, 2026-08-21)

Your report reproduced exactly: stargazer → sacrifice left all six
ghost numbers floating over five dice, and the next roll landed the
promised faces lane-shifted onto the WRONG dice. Fixed and generalized:
**docs/CARD_INTERACTION_RULES.md** is the written contract — a promise
or arm is about the table as it stood; any dice-mutating effect voids
it (values + visuals through the one exit, with a "THE STARS BLUR" log
so the player knows); flag-only cards touch nothing; a drag reorder
moves the floats instead of voiding. Enforced by `famTableChanged()`
at every mutation moment (fam handlers + `_removeDieAt` + one
classified hook for the 16 dice-mutating actives). Five adjacent holes
from the same census fixed in the pass: transmute's stranded rings +
leaked die ref, steady_hand's missing bank-flow disarm, encore's
unguarded deferred callback, preserve's `_pvDie` lane maintenance.
Probe `apv_card_interactions.js`: 4 legs green (break fixed, base
stargazer unregressed, honeytrap survives a wager, arm sweeps).

**One default you may want to overrule:** a removal/reroll VOIDS a
promise (charge stays spent). The alternative — the promise follows
the surviving dice — is richer but was the measured wrong-dice bug;
say the word if any specific card should follow instead of void.

---

## Corvus In-Arrears: want the economy back? (P843, 2026-08-20)

The feats-rot pass deleted the dead In-Arrears code — ALL of it was
unreachable (the per-roll gold drain sat behind `if(false)`, the HUD
badge element was never created, and the win refund was gated on a
counter nothing incremented). First Strike stays pure information, as
its tell text says today.

But the refund carried your player feedback in its comment: *"Maybe you
win Corvus lost gold through the match when you beat him, makes it
sweeter."* That feature only means something if the drain comes back.
**Question: should Corvus drain gold per roll again (with the
beat-him-get-it-back refund), or does First Strike stay
information-only?** If revive: the exact deleted code is in git history
at P843 (drain in _afterRollImpl, totalRollCost counter, refund at
settle, HUD badge) — it's a rebuild from record, not from scratch.

---

## 1. THE RETUNE BATCH — ruled, ready to build, must land together

Three changes that all move difficulty. Ruled that they ship as **one measured
batch**, not three uncontrolled swings.

### 1a. The ladder is out of spec everywhere. Targets come down.

Every boss against the gear a player would genuinely hold that night, two
independent policies, a fresh loadout drawn per match.

| boss | night | carl | rita |
|---|---|---|---|
| GROG | 1 | 22.5 | 20.0 |
| MABEL | 2 | 32.5 | 32.0 |
| **FINNICK** | 3 | **65.0** | 64.0 |
| CORVUS | 4 | 23.0 | 23.0 |
| BRUTUS | 5 | 36.0 | 33.0 |
| **ALDRIC** | 6 | **11.0** | 12.0 |
| **WHISPER** | 7 | **9.5** | 7.5 |
| **AMBROSE** | 8 | **7.5** | 7.0 |

Target is 45–55%. **Seven below, one above, none inside.**

**Ruled: reductions concentrated and uneven, matching the shape** — nights 6–8
need by far the largest (they sit at a fifth to a third of target), nights 1–2
modest, night 3 none or a slight raise.

**And ruled honestly: targets alone probably cannot close a gap that size at
6–8 without making those matches trivial.** Likely needs targets down *and* some
player-scoring growth *and* §1c, working together rather than one lever doing
everything.

**Confidence bound:** nights 3–5 carry about **±10** of model-assumption
uncertainty — measured by re-running the whole table under the opposite spoils
assumption, not guessed. Nights 6–8 and 1–2 barely move between assumptions, so
their shape is safe to tune against. Do not tune a mid-ladder cell to a point
value.

#### STOP — the table above is not safe to tune against. One question for you.

Trying to build the ruled reduction turned up four dead levers in a row, and the
fifth thing checked explains all four. **The two seats in the sim do not run the
same code.**

- `F.simTurn` — the player — drives the **real game**: `startPTurn`,
  `rollPool`, `afterRollLite`, `handleBank`.
- `F.oppTurn` — the boss — is a **separate implementation inside the harness**,
  with its own roll loop. Its own comment says so: *"the SIM has its own copy of
  the rival's scoring."*

So every win rate in the table is the real player engine measured against a
*model* of the opponent, and the boss's whole advantage is per-turn scoring:

| night | boss | player pts/turn | boss pts/turn | turns each |
|---|---|---|---|---|
| 6 | ALDRIC | 368 | **688** | 10 v 10 |
| 7 | WHISPER | 523 | **1096** | 9.5 v 9.1 |
| 8 | AMBROSE | 594 | **1424** | 9.3 v 8.6 |

The boss does not get more turns — it gets **fewer**. And four candidate causes
are now measured and dead, each with a control:

1. **Targets** — inert at 6–8. Those matches end at the turn cap 92 / 54 / 27%
   of the time, so a finish line most matches never reach cannot matter.
2. **Boss aggression / minBank** — inert, and `agg` is **backwards**: it gates
   *"don't bank yet"*, so lowering it makes the boss bank sooner and keep
   *more* (Aldric 6860 → 7259). Ratio never left 1.8–2.2.
3. **Dice** — not the cause. The design comment claims boss dice sit *"one step
   above the player's typical loadout"*; at nights 7–8 the player is **ahead**
   (boss carries flint and amber). Handing the player Aldric's own dice made
   them slightly *worse*.
4. **Player skill** — not the cause. Every shipped policy banks at a **fixed
   threshold that never scales** (carl 300, bea 500, ned 400, rita 200) while
   late bosses bank at 700–900 — but raising it 300 → 1400 is **flat**, because
   bust rate climbs 0.14 → 0.54 and cancels the gain exactly. Best of the whole
   roster is otto at 14.7%.

#### ANSWERED — the model is not faithful, and it errs toward flattery

Measured, not argued. `tools/probe_oppturn_real.js` drives the **real** engine
at night-6 gear and reads what the rival actually banks per turn. It reuses no
scoring code of its own — a third copy could not settle an argument between the
first two — so it observes `G.oTurns` / `G.oPts`, which the game itself moves.

| rival points per turn, ALDRIC | value |
|---|---|
| what the sim model says | **688** |
| real engine, opening turn only *(no assumptions)* | **843** — n=7 |
| real engine, running match | **1041** — n=45, median 950, busts 7 |

**The model understates the real rival by 23–51%.** So the ladder at nights 6–8
is not softer than the table claimed — it is **harder**. The real ratio at
Aldric is about **2.8×**, not the 1.86× the sim reported, against a player rate
of 368 that *is* trustworthy because the sim runs the real engine for the
player.

**What this settles, and what it does not:**

- The four dead levers stay dead — targets, `agg`/`minBank`, dice and player
  threshold were all measured against a model that, if anything, was too kind.
  Fixing the model makes them *more* inert, not less.
- The direction of §1a survives: nights 6–8 need help. The **magnitude was
  understated**, so tuning to the old table would have under-corrected.
- The absolute win rates in the table are **not** safe to tune to a point
  value. They need re-measuring against the real rival before any target is
  written down.

Caveat kept honest: 4 of 49 turns did not complete within the probe's window
and were dropped rather than counted as busts. If long turns are the ones that
stall, the true figure is **above** 1041, not below.

**RULED (Denis): rebuild the ladder against the real rival before touching anything else — commissioned, in flight.**
That is now a measurement with a working instrument rather than an open
question, so it is hours, not half a day.

One known gap in the model regardless: it has **no hot-dice rule** (`hot`
appears zero times in it), while the player's real engine does. The keep
policies *are* exercised — via `_oppChooseFrom` — so P495 is genuinely measured.

### 1i. RULED — the double-cast closes, and it is a difficulty change

Denis ruled: a brand that can fire twice in one turn via hot dice makes the
card's own promise ("this turn") false as written, so **make it true** — a spent
brand stops counting as a live icon until the next turn. Correctness grounds.

**SHIPPED — P585, flagged as a real difficulty change, outside this batch** — not folded in silently. Denis's reasoning for
letting it go early: the ladder already sits well under target across most of the
game, so closing a double-cast that is currently overperforming is very likely
relief in the right direction rather than a new problem.

**MEASURED AFTER SHIPPING, and the "difficulty change" framing was overstated.**
I called it one on the strength of "a row whose only live face is a spent brand
is now a bust" — which says it *can* happen and nothing about how often. Driven
through FSIM (whose player side is the real engine):

| | rule off | rule on | delta |
|---|---|---|---|
| no brands *(control)* | 67.55% | 67.55% | **0.00pp** |
| one brand | 68.40% | 68.60% | +0.20pp |
| three brands | 71.25% | 71.03% | −0.22pp |

n=4000 per arm, SE ≈ 0.72pp — both deltas inside the noise and pointing opposite
ways. Counting the **event** instead of its effect on the aggregate, wrapped at
the bust gate itself: in **12,000 turns holding three brands the rule never once
changed a bust decision** (0 events), with both controls green — the hook fired
22,475 times and the icon rescue was genuinely exercised 13,918 times.

**So it is a correctness fix with no measurable difficulty cost**, not a balance
change to account for in the retune.

**AND THE POLICY CAVEAT IS NOW TESTED, not just stated.** The two checks above
shared a harness, a policy, a gear and a seed — they observed different things
(an outcome vs a decision) but their agreement said nothing about any of those.
Sweeping the event count across every shipped policy, 12,000 turns each:

| policy | fires/turn | bust rate | rescues seen | cost events |
|---|---|---|---|---|
| bea | 0.200 | 71.3% | 13,918 | **0** |
| carl | 0.047 | 65.6% | 13,153 | **0** |
| rita | 0.057 | 71.6% | 13,719 | **0** |
| ned | 0.212 | 63.6% | 12,899 | **0** |
| greg_naive | 0.221 | 97.1% | 16,616 | **0** |
| greg_informed | 0.221 | 97.1% | 16,616 | **0** |

The greg arms matter most: they roll hardest after firing and bust 97% of the
time, which is the exact shape that would produce the event.

**Counted as FIVE distinct policies, not six** — greg_naive and greg_informed
returned byte-identical numbers in every column, which usually means they
collapsed to the same behaviour. Worth someone checking why; it does not change
this conclusion.

Remaining caveat: one gear (three tithes on bone), and FSIM itself.

**A TRAP FOR THE NEXT READER:** FSIM's `iconsFired` now reads **0** by
construction — it splits with `_splitIcons` *after* the commit that marks the
brand spent, so `_dieIsIcon` correctly says "not a live icon". Brands still fire
(counted at `_iconFire`: 0.2/turn). Do not read that zero as a regression.

### 1e-bis. RETRACTED — those two bosses can fire the card, and the premise was backwards

**This section used to say** `blessed_dice` (Ambrose) and `crown_authority`
(Whisper) were **dead slots**: dealt into the boss's hand, activatable only by
the player, so each boss could draw a card it can never fire. It concluded that
removing the ids would make both bosses **stronger** by freeing a wasted draw.

**Both halves are false, and the conclusion points the wrong way.**

Measured while fixing D3 (P557). Both cards carry
`effect:{type:'once',mechanic:'reroll_all_kept'}`, and the after-roll dispatch
runs straight off `G.oCards` keyed on `effect.mechanic` with **no**
`type:'active'` or player-only gate. Driven 40/40 through the real dispatch:
`usedOnce:{crown_authority:1}`. The `activate...Player` functions are the
*mirror*, not the only path — the cards' own text says so:

> `desc`: "Once per match, **Whisper forces you** to reroll every die you selected"
> `playerDesc`: "Activate while yielding: **the opponent must** reroll…"

So they are dual-use by design, and the boss half works.

**Why this mattered more than a documentation slip:** the section sat inside the
retune conversation with a difficulty recommendation attached. Removing those
ids would make Ambrose and Whisper **weaker**, not stronger — and both are
already flagged as needing help. Acting on it would have pushed the wrong way on
two of the three worst-off nights.

**The same false claim was in the source** (a P509 comment reading "those bosses
can draw a card only the player can activate"); corrected in place by P557. This
doc inherited it. Nothing to action here now — the item is simply withdrawn.

### 1c. `blessed_dice` / `crown_authority` say "reroll", the code wipes

#### CORRECTION (2026-08-21, driven): §1c's CONCLUSION WAS RIGHT. My P846 retraction was wrong.

**Do not build the reroll.** The layer is unreachable — I retracted a
stale REASON and replaced it with an unverified opposite conclusion,
then shipped four patches on top of it.

What is actually true: P615 did revive the *plumbing*
(`const pCards=(params.pCards||[]).filter(Boolean)`, both launchers
feeding from `S.run.cards`) — that part of my P846 note stands. But
**nothing ever fills `S.run.cards`.** All six writers are behind doors
that never open:

| writer | blocked by |
|---|---|
| `_draftSelectCard` / `_draftReplaceSlot` (42437/42454) | `showScreen('draft')` — never called |
| `_rewardSelectCard` (42578) | `showScreen('bossreward')` — never called |
| `_draftPlaceCard` / `_draftUndoActivePick` (40806/40840) | `#endDraftSlots` — read 9×, created 0× |
| `_showLegendDraft` (42694) | `S.renownPerks.legend` — `_getS` wipes the map (11143), nothing sets it |

The only `showScreen` names the file ever passes are `menu`,
`gauntlet`, `match`, `shop`, `gameover`. **Driven** (`apv_cards_layer_reach`):
a real patron win and a real boss win both leave
`S.run.cards=[null,null,null,null]`; `bossreward` and `draft` never
open. Boss rewards pay through the FAMILY layer (`famSpoilsPick`).

So `crown_authority` / `blessed_dice` cannot reach your hand, the wipe
is not a live lie, and building the real reroll would be building into
dead code — exactly what the original §1c warned. **The honest state:
the whole CARDS-table active layer is unreachable, and the question for
you is whether to REVIVE it (wire a draft/reward screen) or DELETE it
(~40 handlers + the reward/draft screens). Recommendation: decide
before anyone spends on it again — I already did, twice.**

<details><summary>The wrong P846 text, kept for the record</summary>

#### THE RETRACTION IS ITSELF RETRACTED (P846, on your review) — the layer is LIVE

The paragraph that stood here said the whole legacy player-active layer
was unreachable because `initMatchScreen` declared `const pCards=[]`.
That was true when written and has been FALSE since **P615**, whose own
comment says "THE PLAYER'S HAND, AT LAST… the hand died on this one
line" — the line now reads `const pCards=(params.pCards||[]).filter(Boolean)`
and both launchers feed it from `S.run.cards`. The stale claim stood for
~230 patches, got copied into a source comment that was justifying a live
design decision (the sacrifice `_frozen` exclusion — re-driven in P846,
same verdict, honest reason), and steered P844's enrollment design. You
caught it.

**So the ORIGINAL §1c finding is back on the table.** The player-side
`crown_authority` / `blessed_dice` arms are in the live dispatch, and
their consume site (the rival-turn block at ~35924) is the WIPER: it
un-keeps the rival's kept dice and zeroes their total while announcing
"KEPT DICE REROLLED!" — **without rerolling a single value**. If a
player can hold either card (they're npc-rarity; the player-side
activators exist on purpose, so the game intends it), that's a lying
announce on a live weapon. **Rule: build the real reroll, or retire the
two player-side arms.** Recommendation: build the reroll — it's the
card text, and the NPC-side implementation already shows the shape.


The block un-keeps the rival's dice, sets `total=0`, and announces *"KEPT DICE
REROLLED!"* without re-rolling a single value. Build the real reroll; do not
reword the card.

#### RECONCILED — there are TWO implementations, and the LIVE one already works

Denis read this section and reasonably concluded the mechanic is still broken
everywhere. It isn't. `reroll_all_kept` has **two** implementations, in opposite
directions, and only the dead one wipes:

| | direction | state |
|---|---|---|
| **26667** | **boss → player.** Fires off `G.oCards` through the after-roll dispatch | **WORKS.** P475 replaced the wipe with a real reroll; P557 fixed the rescoring (the pre/post-split `vals` bug that turned a punishment into a 4×). `dd.val=_rollD(dd)`, re-split, rescore per group. |
| **29875** | **player-armed → rival.** `G._playerRerollKeptArmed`, set by `activateCrownAuthorityPlayer` / `activateBlessedDicePlayer` | **STILL WIPES.** `d.kept=false; total=0;` then announces the reroll. No roller, no `val=`. **Unreachable** — it comes through `activateCard`, and the legacy player-active layer is dead (driven tonight: `canActivateCard` refuses every id, `pCards` and `effectiveCards()` both empty). |

**So the paragraph above is true only of the dead half.** The boss firing it at
you — the direction `docs/archive/CARD_ART_NEEDED.md` describes, and the only one a
player meets — genuinely rerolls and rescores.

**What this means for the art list:** nothing needs a caveat. Its wording for
Crown Authority and Blessed Dice ("forces you to reroll every die you selected")
describes the live path and is accurate today.

**Correction to the original ruling, which assumed the wrong direction.** These
were taken to be boss cards punishing the player, and therefore a softening
lever for nights 7–8. They are not. There is **no NPC firing path at all** — the
only activations are `activateCrownAuthorityPlayer` / `activateBlessedDicePlayer`,
which arm it against the *rival*. So it is a **player weapon**, the wipe is
*stronger* than an honest reroll, and fixing it makes the game slightly
**harder** — which is exactly why it must be batched rather than shipped as
relief.

</details>

---

## 1d. The rival's cards are still wearing the old game's skin

You saw this in a live Grog match and asked whether we have been shipping old
cards. **The card logic is entirely current** — Grog's three (`her_lucky_coin`,
`one_more_round`, `grogs_bump`) are present-day `NPC_CARDS`, and the previous
game's 149 card faces are archived and genuinely unreachable: `_cardArtImg`
returns `''` at all 9 of its call sites, so none of them are drawn.

**What is old is the presentation.** Two card looks ship side by side:

- **player cards** — `famCardArt`, a painted `.webp` face, the pixel-tarot
  direction. This is the current look.
- **rival cards** — `gcard`, an emoji on a flat colour swatch inside a red
  frame with corner brackets. This is the previous game's card chrome with the
  art removed and never reskinned.

Different look, layout and scale, exactly as you described — and it is why one
card read as current and the others as foreign. It is a live art gap, not a
data regression.

**RULED: no card gets a CSS style, every card gets art.** The list is
**`docs/archive/CARD_ART_NEEDED.md` — 41 cards**, and the loader is built, so a PNG
dropped into `assets/cards/` renders on its own with no code change per card.

- **41 rival/boss cards** — every `NPC_CARDS` id reachable through a rung's
  `cardPool`. `pocket_sand` is defined but pooled nowhere, so it is excluded.
- **The 30 family cards are complete** — all 30 already have art.

I first sent this as **132** by including 90 entries from the previous game's
`CARDS` roster. Denis caught it. See §1e — those cards are real and still being
dealt, but that is a bug to remove, not 90 pictures to draw.

The palette work (P505) is a **stopgap that retires itself**: each PNG that
lands strips that card's border, ground, glow and emoji automatically, so the
CSS skin survives only on cards still waiting for a face. Delete it outright
once the list is filled.

---

## 1e. The previous game's card roster is still being dealt

Found while checking the art list, and confirmed by launching real patron
matches rather than by reading the code — `tools/probe_patron_cards.js`.

`_generatePatronInner` builds every patron's hand from the **legacy 133-card
`CARDS` array**, the one the asset registry describes as retired. It is not
retired in practice: `pCardCount = tierIndex>=2 ? 3 : tierIndex>=1 ? 2 : 0`
with `cardChance:1`, so **every patron from night 2 onward always draws 3**.

Seventeen distinct legacy ids came out in one sweep of tiers 2–7 —
`chain_lightning`, `the_hearth`, `honor_guard`, `the_fence`, `slippery_table`,
`even_row`, `the_whetstone`, `anchor`, `last_stand`, `finnicks_trick`,
`the_heir`, `snake_oil`, `brutus_grit`, `whispers_veil`, `tavern_cheer`,
`the_ledger`, `prompt_hand`.

Boss hands are correct — they draw from `NPC_CARDS`.

**Why it matters beyond tidiness:** these are unapproved cards with no art and
no place in the current design, firing real effects at the player on six of
eight nights. They are also inside every difficulty number measured tonight.

**RULED and FIXED — P507.** No patron cards at all, rather than repointing at a
current pool: a fresh patron card layer is unscoped design work, and cutting
the dead roster out matches what was already supposed to be true.

Root cause: **P473** lifted a `return []` stub in `generateOppCards` that had
been keeping every hand empty. That was right for bosses, who draw from the
current `NPC_CARDS`. It switched the patron branch on as a side effect. P507
undoes only that side effect — `pCardCount` 3/2/0 → 0 — and leaves the boss
path alone.

Verified by re-running the probe that found it: all eight tiers now report
`patronCount: 0` and no legacy id in any hand. Nights 1–2 had already been
shipping the no-cards path, so nothing untested was introduced.

**This makes nights 3–8 easier** — patrons lose 3 cards each. It is a
correctness fix, not a balance decision, and it lands inside a ladder whose
numbers are already known to be untrustworthy. Do not read it as tuning.

---

## 1f. CLOSED - false alarm, the win art is live

I reported four finished pieces in `Art/Assets/Win/Standard` that the game
"references nowhere", on the strength of three grep strings returning zero.
Denis ruled: don't take either side's word for it, check what the win screen
actually loads.

Checked by forcing a real win through the game's own `dbgWin` and reading two
independent channels - the network log and the rendered DOM. The win screen
loads `assets/win/bg.webp`, `banner.webp`, `panel.webp` and `hands.webp`.

They are the same art: identical file sizes to the four `_opt.webp` copies
(0.11 / 0.13 / 0.20 / 0.07 MB), optimized 1 Aug 15:24 and deployed 15:38 the
same day, renamed on the way in.

Nothing is orphaned. Nothing needs deleting or re-optimizing.

**Why the greps missed it:** I searched `win_standard`, `Assets/Win` and
`winStandard`. The live path is `assets/win/bg.webp` - lowercase folder, and
the filenames dropped the `win_standard_` prefix. None of the three could have
matched. Seventh time this session a zero from a name search became a claim.

---

## 1g. Dice-lane integrity — see `docs/DICE_LANE_INTEGRITY_PLAN.md`

The full brief now lives in that file: six shipped patches (P510-P515) with
their verification, the two ruled standing lessons, the scoped rival-side
rework, and everything still open including the card-slot parallel and a
newly-flagged list (Vagabond's drag-reorder, `reduce_first_roll`, `swap_die`).

It carries a standing ask: **a systematic sweep** of every consumer of
`matchDice`, `_enchArr`, `numDice` and the lane functions cross-referenced
against every card and enchant — not another list built from recall.

Priority unchanged: behind card art and the playtest.

## 1h. CLOSED - hot dice no longer refunds this turn's penalties

**Ruled:** five. A penalty costs you for its stated duration; rolling a clean
sweep must not be the escape hatch that cancels the opponent's card.

Fixed player-side (P517) as a MINIMUM rather than a decrement - hot dice must
still be able to restore a hand, it just cannot exceed what the player had this
turn. Verified live: Hex armed, loadout 6, turn start 5, after hot dice **5**
(was 6). Without the Hex, 6 to 6, unchanged.

Pocket Sand is covered by the same change. **The rival's hot-dice reset must
match and does not yet** - it is `left=6`, a local inside `runOppTurn`, one of
seven writers of which five are literals, so it belongs to the rival-side
rework in `docs/DICE_LANE_INTEGRITY_PLAN.md` rather than a patch here.

## 2. Early-game signal — needs a person, not more reasoning

Restoring the brief's 24 feats removed every feat that fires in a new player's
first hour. Ruled that nothing goes back into the feat list; the proposal is
that dialogue beats do that job instead. **No argument settles this — it needs a
playtest.**

---

## 3. `assets/` — an art-scope call on your timeline

47 live references into the previous game's tree have no replacement.

| group | count | style-mismatch risk |
|---|---|---|
| Character portraits | 9 | **highest** |
| Match frames | 8 | **highest** |
| Night_Art UI set | 10 | **highest** |
| Environment / menu | 9 | mixed |
| Fonts | 8 | lowest |
| Audio | 3 | lowest |

**If there is only room for a subset, it is the 27 in the high-risk rows.**

---

## 4. Unplayed numbers — flagged, not trusted

Last Call's 800 and most restored feat conditions read real state and render,
but only HIGH ROLLER has fired through a live match.

---

## Not blocking, for your awareness

- **Pages deploy is healthy.** The GitHub outage recorded here is over; six
  deploys went out tonight and each was verified LIVE by grepping a marker on
  `rigamix.github.io`, never by a green build — `_dieLeftSeat`, `_cultArr` and
  `_drillMax` are all present on the served file. **Keep verifying that way**:
  `index.html` is only a redirect stub, so grepping the site root always looks
  empty.
- **Four model assumptions remain untested** — 65% patron win rate, boss beaten
  first try, buys the dearest die in stock, no enchant/tavern gold. None *looks*
  load-bearing, but that is an impression rather than a measurement; the same
  sensitivity method settles any of them if a retune leans on one.

---

## 9. FOUR THINGS THAT WANT YOUR HANDS, NOT MORE MEASURING

All shipped and working. Each is one number or one reading pass, and none blocks
anything else.

**9a. The 23 patron voices.** Part 6b placed the brief's content against the real
pools — placement is verified, correctness is not claimed. The brief locked those
voices partly against backstory lines this build doesn't have (it assumed 6 per
patron; there are 3). `tools/_p627_patron_lines.py` lists every line by patron
and group in one place if you want to read them together.
*My recommendation: read them; don't have me rewrite them blind.*

**9b. The card activation threshold** — `--card-arm-lift`, currently 16cqw
(≈68.8px above the card row). Measured, not played. Raise it if cards fire by
accident, lower it if the drag feels dead. One value in `:root`.

**9c. How often the rival hesitates** — `DLG.prob.OPP_HESITATE_PUSH` and
`.OPP_HESITATE_BANK`, both `.3`. Raise for more, lower for fewer.
*(The old `_HESITATE_LO`/`_HESITATE_HI` band is gone — P632. It claimed to fire
only on close decisions; measured, `agg` is the same value every roll of a match,
so it was really a per-OPPONENT switch: some patrons hesitated on every single
roll, others never. The spacing is `DLG.trigger`'s job now, like every other
beat.)*

**9d. The card activation sound** — `SFX.cardFire()`. The voices are verified as
scheduled and shaped; whether it's satisfying is your ear. Body / bloom / tail
are three tunable blocks in one function.

---

## 10. THE ≤700 KEPT-TRAY OVERLAP — pre-existing, out of your band

On viewports 700px tall and under, the kept-dice tray overlaps the card-drop
target (-8.97px at 690). It predates this work and sits outside the 700–760 band
you play on, which is why it wasn't fixed with the rest.
Fixing it means dropping the activation zone there too, and card clearance is
already only 50px at that size — so it trades one tight number for another.
*My recommendation: leave it until someone reports it on a real short phone.*

---

## 15. THE LEGACY-ART PURGE (P714) — three surfaces now wait on new art

Your rule — nothing from the old `assets/` tree loads — is in, and your
follow-up rulings landed (P715): the **boss splash is removed** (its boss
music cue moved to the launch/resume paths, the tell stays on its badge),
the **pouch is gone entirely** (win-draft button, modal icon, loadout chip
— its panel code sleeps with no entrances), and the **shop door** point is
withdrawn — you have an icon for that already.

One art gap remains from the purge: the **boss peek sheet and end-screen
dialogue portrait** are name-only (they used to show the old-game busts
through the bosses' legacy keys). If those two surfaces should show a face
again, they want boss busts in the new style; if name-only is fine, nothing
to do.

Also kept, named plainly: `assets/cards/`, `win/`, `loss/`, `Audio/`,
`vendor/`, `models/`, Macondo, and `table_commoner.webp` (the 07-27 table
plate — current art in the old folder). Those are current infrastructure;
relocating them out of `assets/` is quiet housekeeping if you want the
folder to die completely. The now-unreferenced legacy FILES are still on
disk/repo — say the word and I git-rm them.

---

## 12. THE ENCHANT-PAGE CRASH — DIAGNOSED + FIX SHIPPED (P842, 2026-08-20)

Your "more layers on screen" report cracked it. The five exception-hunting
probes found nothing because there was nothing to find: **it was never a JS
error — it's GPU pressure**, and your description named the exact state.

**Measured (layer census on the enchant-focus state):** six visible
1080×1920 art layers + one *ghost* (the faded-out tab character — opacity 0
but still composited, the transition holds the layer alive) + the live
full-viewport WebGL dice canvas (it IS running in the shop — 4 rack dice,
rAF at full rate). On top of that, `st-focus`/`st-epick` applied an
**animated `blur(5px) brightness(.62) saturate(.9)` filter to every art
layer separately** — seven+ independent full-screen blur rasters, re-run
through the .35s transition, plus a second blur on the enchant shelf. At
phone dpr 3 that's the overload; desktop GPUs shrug it off, which is why I
couldn't reproduce.

**The fix (P842), look-preserving:**
- The per-layer filters are gone. Two `backdrop-filter` scrims blur the
  *composed* region once: scrimA under the goods shelf (die focus — art
  recedes, shelf sharp, as today), scrimB above it (enchant picker —
  everything beneath recedes in one pass). Same blur/brightness values.
- The faded-out tab character now gets `visibility:hidden` after its .34s
  fade (instant on the way back in) — one character layer composited per
  tab, not two.
- One stated look delta: in the enchant picker the art behind the shelf
  reads ~.42 brightness instead of .62 — slightly darker behind the modal.

Probes green (`tools/apv_shop_scrims.js`): scrims carry the blur, zero
per-layer filters remain, ghost layer count 0. **The one thing I can't
verify from here is the kill itself — that needs your phone.** If the
enchant screen still dies after this build, say so and the next suspect is
the WebGL canvas running under the shop (it can be paused there).

## Bank-seam mirror rulings - RULED AND SHIPPED (P774, 2026-08-19)
1. GAIN_WHEN_AHEAD: bank-inclusive both seats (Denis: evaluated on the
   result of the banking action). Player test now (pPts+total)>oPts.
2. HALVE_FIRST_BANK: the FIRST bank specifically, both seats (the card's
   own text). oppFirstBankDone latch mirrors firstBankDone.
3. CHALLENGE: gut-check confirmed missing-check-not-design (the turn
   gates were already equivalent per the init offset); the player-owned
   arm reads oPts>=threshold, mirroring the rival's. NOTE for the
   flow-shell audit: the rival's challenge pre-arms with an announce,
   the player-owned resolves inline against the judged bank - both
   match their card texts; telegraph asymmetry recorded, not changed.
Also confirmed: block_low_bank now has ZERO implementation sites (the
backlog's 'implemented both seats' is stale - fully undealt AND gone);
periodic_drain mirrors correctly (per-owner turn counters) - the tool's
player-side scope just misses its site.


## Preserve return-turn flake (card audit, 2026-08-20)

3 of 11 headless probe runs ended the preserve RETURN turn paying zero
(one run's banked 100 also vanished during the rival turn). Never
reproduces under instrumentation: numDice trap, turn-exit wraps, and a
pPts write-trap all ran green 8/8 — pPts written exactly twice, both
by handleBank, same G object throughout. **My read: headless
SwiftShader/rAF stall, not a game bug — preserve stays PASS.** Nothing
to answer unless a phone playtest ever shows a vanished bank after a
preserve turn; if it does, that's this.

## The cardHit taxonomy (P814, retort's second trigger — 2026-08-20)

Retort's hit-half was fully dead (spec says "fully automatic on either
trigger"; a driven hex hit paid 0). P814 adds famFire('cardHit',
{actor:<victim>}) at the TAKING sites: NPC hex, NPC confiscation,
pickpocket/reprisal/ill_omen-landing (both owners). **My rule: an
opponent card that takes dice or points is a hit; pure buffs to their
own side are not, and retort's own payment never fires the seam (no
retort-vs-retort chains).** RULED (Denis): extend to every NPC quirk card that takes dice or
points — the rule should be complete, not answer for two cards and
stay silent on the rest. Census + build in flight.

## Boss dialogue is BACK (P818, 2026-08-20) — three content gaps remain

Your "no Grog dialogue" note traced to a two-patch contradiction: the
per-boss bark pools were deliberately deleted (moved to the lore
resolver), but P682's boss BYPASS still routed bosses around the
resolver into the emptied store, and bosses had no seat identity.
P818: bypass deleted, bosses stamp a lore TRAIT (art stays null so the
patron personal arcs stay closed), and the getLine guard no longer
kills LEDGER_LINES — driven: Grog greets with his real record ("2
nights at me table an' we're dead even"), busts get "Ha! Greedy!",
patron side regression-clean, resume restamps.
RULED (Denis): Corvus is ORDERLY, not greedy (shipped, P832); the
`boss:<key>:open` pool mechanism gets built now and **Denis writes the
eight greeting lines as a follow-up** — that's the one open item here;
DLG.triggerCard's call sites get DELETED, not revived (being built).

## BANK TO WIN, stage 1 shipped (P819) — the full oracle is a choice

Fixed and probe-driven: the winning press no longer snaps back (P728
latch restored at the win check), a sealed LAST CALL seat no longer
captions a bank it will refuse, tab-escrowed banks can't claim TO WIN,
slow_cook's pot and the hangover double are projected, and the label
self-heals from updHUD (Loan / tier-3 tamper used to leave it stale).
STILL UNPROJECTED (label under-promises): the ~30-card bank-bonus
stack (×2 cards, underdog, weight...), short_fuse's commit-time double
in the selection preview, and rival deductions (cowards_bell, halve /
steal-low). Closing those needs handleBank's total pipeline extracted
into one dry-runnable oracle — a real refactor of the game's most
central function. RULED (Denis): plan it as its own session, not urgent — the failure
direction is safe (under-promises, never over). The plan lives in
docs/BANK_ORACLE_PLAN.md once written.

## Patron leveling (P822 shipped; four rulings left) — 2026-08-20

Recon verified your brief's three check-items: the card ramp already
keys off the real night (your preferred reading, no build needed); the
die-family bias was genuinely dead (two contradictory tables and no
family material in any patron pool); named patrons have NO stable
persona. P822 ships the die bias: aggro→obsidian, ones→silver,
combo→vagabond/starstone head their bias lists and the tier pools
admit family materials from night 4 (the tier-2 one-up splash gives
night 3 its occasional curveball — measured 5%). Driven: nights 1-2
mundane 0/80, aggro 93% obsidian vs 24% baseline, family dice deal and
roll on a real rival seat.
ALL FOUR RULED (Denis), being built: (1) wire the rival's obsidian
shatter — the material can't mean different things per side; (2) same
tier locks as the player, no raw tier-III for patrons; (3) build the
persona↔name registry — the approved growth dialogue needs a stable
character under it; (4) make the resolver genuinely additive for band
lines, per the brief's explicit intent.

 — ALL SHIPPED (P823-P830, 2026-08-20)

Denis ruled: do all of it now. Done, each item probe-driven:
P825 reprisal/ill_omen/sleight live-states on the cards + slow_cook
simmer and for_keeps stakes chips; P826 fool's-gold burn beat, retort
hits both ways, the DoN flip beat, falling_star's starburst; P827
stargazer GHOST DICE over each free die, honeytrap honey marks + the
die-anchored pull, vanguard's primer revived (it tested the retired
card list) + end-spot hints; P828 encore rerolls starstone-BLUE (the
keg contrast) + cultivate growth floats off the die; P829 transmute's
in-world face picker (window.prompt retired); P830 sleight's
land-pause-reroll beat both directions.

P830 also fixed a real family bug the beat work uncovered: every
rival DEAL-LOOP value rewrite (sleight, their stargazer, their
honeytrap, NPC hot streak) ran in mkDie's 40ms pre-adoption window —
the mesh was born from the stale stamp, so THE FACE SHOWN WAS NOT THE
VALUE SCORED on the 3D path. reDrawDieFace now stamps the true value
first, unconditionally; driven: six rival dice sampled live, every
mesh stamp equals its scored value.

RULED (Denis, same night): the sleight-beats-their-script precedence
stays as shipped — "if Sleight fires, the original roll is gone, full
stop, not gone except for whatever the rival had scripted on top of
it." The old precedence would have weakened the card exactly when
aimed at a rival about to do something clever.

## Skim-vs-LAST-CALL — RULED AND SHIPPED (P839, 2026-08-20)

Denis ruled: the threshold judges the PRE-take amount — "a bank that
cleared the floor on its own terms shouldn't retroactively fail
because of a tax applied after the fact. The skim still gets its cut
regardless." Shipped and driven: the exact construction that voided
(1,000 skimmed to 700 on Grog's table) now pays 700 with the skim
keeping its 300; a genuine sub-floor bank still voids. His eighty
boss greeting lines are wired the same commit (state router: open /
undefeated / firstloss / beaten by the ledger's own w-count) — all
four states answered with his lines under a driven probe. Delete on
read.

## Architecture audit delivered (2026-08-20) — one fold candidate, five rot items

docs/ARCHITECTURE_AUDIT.md is the full table. Headlines needing you:
1. FOLDED same night (P841, Denis's word): three _DLG_COND
   predicates, one pool per boss, the router collapsed to a single
   _dlgPick call - the P839 probe passed VERBATIM after the fold
   (behavior-preserving, proven).
2. FIXED same night (P840, Denis pulled it forward): the two
   side-channel grants are roster rows, evaluateFeats writes the
   stat - driven: 3 feats earned, stat 3, renown honest. (Also
   caught: the _featView whitelist needed the keg flag.)
3. FIXED (P843, 2026-08-20): seven orphan flags deleted (each
   adversarially verified through every access pattern before
   deletion; _featHotDiceCount KEPT — the committed sim instruments
   read it, so it was never an orphan); the resume gap closed — the
   snapshot now carries a featState block (12 live fields, not the
   audit's 4 — including _forKeeps, whose family-card charge was
   carried while the flag it bought was not) restored by one
   presence-guarded loop; the stale _RETIRED_RULES paragraph deleted;
   the dead In-Arrears economy removed in ALL legs (the census found a
   fourth leg the audit missed — an inert HUD writer whose element no
   markup creates). Probes: apv_feats_resume (12/12 fields across the
   localStorage boundary, pre-P843 snapshots resume clean, restored
   progress awards feats on a driven win), apv_feats_stat re-run
   verbatim green, first_strike tell route clean.
Everything else: seven systems confirmed genuinely separate with
stated reasons, three confirmed already-data — no forced merges.
