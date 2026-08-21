# Audit backlog — pick up here

Written 2026-07-30 so a fresh session loses nothing. Companion to
`archive/AUDIT_FINDINGS_RAW.md` (all 72 soak findings verbatim, with repro lines).

## RE-HOMED 2026-08-21 (docs cleanup — these lived only in now-archived working papers)

Every item below was quoted out of a doc moving to `archive/` because no
live doc tracked it. Sources named so the full context is one hop away.

**Player-facing / highest first:**
- **THE SETTLE DRAG IS STILL OPEN.** Denis reported it twice: dice hang,
  then slide slowly into place "as if against an invisible wall". Measured
  (archive/NOTES_2026-08-15.md): tapes run 1.2–1.9s with 183–650ms of
  crawl. P736 tried two fixes — BOTH FAILED — and was reverted whole. No
  fix shipped since; this is the oldest open player-reported feel bug.
- **~46 KB heap retained per match, never released** (archive/BREAK_ROWS_2026-08-03.md,
  diagnosed: cumulative per page load, not DOM, not batch size). Caps every
  long study and is a slow leak on a phone session. Worth finding.
- **shoot.js has no watchdog** — a vanished browser blocks a run forever
  (one 178-minute hang measured, archive/FINDINGS.md); each hang leaks a
  profile. Same family as the 270GB/orphan-browser incidents.

**Design calls (Denis, when wanted):**
- **Seven fam actives are never played BY bosses**: `_npcArmActives` was
  never taught when a boss should choose transmute / powder_keg /
  sacrifice / steady_hand / fair_trade / tamper / fool's gold — "a
  genuinely larger job nobody has scoped" (archive/P5_NPC_CARDS.md).
- **Opponent-enchant sourcing** (archive/OPP_ENCHANTS_SIZE.md): if rival
  enchants ever exist, where from — patron generation, boss relic dice, or
  only via For Keeps/Trade? Dormant until wanted; the engine currently has
  none by ruling.
- **Seven patrons have no growth/recognition lines by deliberate
  exclusion** (Twill, Fenn, Ferrand, Odo, Ollis, Tam, Peck — not enough
  lore grounding to write without inventing; archive/PATRON_GROWTH_LINES.md).
  Your lines whenever you want them to grow too.
- **Patron leveling "up to 3 late" cap**: shipped as a flat cap for every
  persona; the brief flagged "confirm rather than assume" and it was never
  explicitly confirmed (archive/PATRON_LEVELING_BRIEF.md).
- **CARD_VFX A3b environment darkening** (room dims 1.0→0.82 as
  pPts→target, stepped per bank): never built, never ruled
  (archive/CARD_VFX.md).
- **Hand/goblet gather at throw start**: recorded, deliberately not acted
  (archive/PLAYTHROUGH_PASS_PLAN.md step 5).
- **The enchant-badge rework's §5 open items** (briefs/FARK_ENCHANT_BADGE_REWORK.md
  — the brief is live, its open list just had no pointer here): enchant
  gold prices are placeholders needing a pricing pass; Snuff/Fog power
  vs an ADAPTING rival unmeasured; relic-vs-badge architecture open;
  First Strike's reduced form never explicitly signed off (OPEN.md's P843
  entry covers only the economy half).
- **FARK_MASTER_BRIEF's own stale-content pass** (flagged in its header):
  the line-by-line mark-or-strike sweep (old enchant menu, old Silver
  pricing, Renown perks, dead boss-tell UI, Bookends feat) is owed and
  not done.

**Added 2026-08-21 by P846 (Denis's second interaction review):**
- **The legacy player-active layer's EFFECTS audit** — ~18 live,
  obtainable CARDS-table actives (gamblers_eye, the_pyre,
  mabels_stitch, loan, all_in, corvus_ledger, aldrics_vow,
  whispers_hex, grogs_flask, finnicks_palm, vanishing_act, frozen_die,
  double_down, coin_flip, the_nudge, alchemists_chisel,
  twinning_charm, seven_dice) have never been probe-driven to
  CARD_AUDIT_2's adversarial standard. They were silently out of every
  audit's scope because OPEN.md §1c wrongly called the layer
  unreachable for ~230 patches (dead since P615). Interaction/void
  coverage exists (the P846 sweep); effects coverage does not.
- **rollFace is die-less** — the NPC's only roller and the player's
  hot-dice path call `_rollTable(mat)` with no die object, so Still
  Waters cannot hush those rolls (the same shape P846 fixed in
  `rollFaceExclude`). Whether the badge SHOULD reach those paths is a
  design question; measure, then ask.
- **The §1c wipe finding is re-armed** (see OPEN.md §1c): the
  player-side crown_authority/blessed_dice consume site un-keeps and
  zeroes without rerolling — build the real reroll or retire the arms.
- **The post-roll TELL block wants extraction** (P847): Gambler's Eye's
  reroll now fires `famFire('roll')` but the tell hooks below it in
  `_afterRollImpl` (Steeped's per-roll bonus, Loaded Die, Gambler's
  Thumb, Hot Streak) still run only on the main path — a GE reroll is
  invisible to them. Copying the block into the GE branch would be the
  two-copies bug; extract it into one function with two callers.

**Instrument/code hygiene:**
- **`_oppHas(mech)` helper never shipped** — the 6 inline
  `G.oCards.some(...mechanic===...)` query sites remain
  (archive/MECHANIC_TABLE_SCOPE.md).
- **jade3 reachability never verified** — it is in no tier's diceWeights;
  whether any upgrade path reaches it was flagged and never answered
  (archive/EFFECT_INVENTORY.md).
- **famsweep_steady_stale probe is known-broken** (pre-P519 line refs,
  excluded from the suite) — fix or retire (archive/CARD_AUDIT_2.md...
  which stays live; the probe note had no other home).
- **ill_omen flake signature**: one witness run measured +400/−800
  (irreproducible; write-trap showed one +800 write). Recorded beside the
  preserve flake as the second member of the headless-flake ledger.
- **Sim-spread comparability trap**: a 4-agent and an 8-agent spread are
  not comparable numbers; changing agent count breaks comparability with
  every prior run (archive/SPREAD_AUDIT.md).
- **The sim brief's four-lens program** (FUN spread / POWER delta /
  ELEGANCE checks / Scavenger sweep) was deferred pending resolutions
  that later landed, and never run end-to-end (briefs/FARK_SIM_BRIEF.md).
- **Art filename nits** (archive/ART_TODO.md): two masters are camelCase
  (`card_face_steadyHand.png`, `card_face_FairTrade.png`) where the set is
  snake_case; `fools_gold_f`/`vanguard_f` map to un-suffixed filenames and
  `anchor_f`/`bookends_f` are `_FAM_ALIAS` aliases — any script deriving
  ids from filenames needs these four exceptions.
- **The P505 CSS-palette stopgap's deletion is armed**: OPEN.md §1d said
  it "retires itself once the card-art list is filled" — the list is now
  filled (archive/CARD_ART_NEEDED.md); the deletion itself has not been
  done.
- **Old audit-resolution residuals** (archive/AUDIT_RESOLUTIONS.md):
  whispers_fang's post-fix "worth it?" sim check never ran by name; the
  SFX.shield→ward.fire re-home has no landing record (Ward may still arm
  silently); the Still Waters pre-wide-build sim pass is subsumed by the
  ladder-rebuild-first ruling but never explicitly closed.

## STATUS CORRECTIONS (2026-08-21) — entries below that are now wrong

- `block_low_bank` "implemented on both seats": now has ZERO
  implementation sites (OPEN.md P774 entry — fully undealt AND gone).
- "Area A is in (P383). The other six are not": B–G all shipped (P397–P400).
- "Still to build: Brutus relic Ward / Fair Trade tiers / Still Waters /
  1-or-5 restriction": all done or mooted (P383, P718 retired Fair Trade).
- The two "in flight" workflow-journal sections reference dead session
  journals; their subjects were superseded (Steady Hand P535, Preserve
  P744 + the P844 lane-record taxonomy).
- "PRESERVE built, NOT APPLIED": superseded — preserve is live as a real
  pool die (P744); docs/CARD_INTERACTION_RULES.md files it as a lane
  record.

## Open, low-stakes

- **Tamper's texts say "for the night"; the break is match-scoped.** (found
  2026-08-19, card-text audit) `CFX.tamper` sets `broken` on the `G.oF`
  instance, which is re-dealt per match. No observable difference today —
  bosses are the only family-card holders and are faced once a night — but if
  a second boss match per night ever exists, the wording and the code split.

- **The halo blur's radius is DPR-quantized.** `blurOnto`'s mip count is
  `round(log2(r*dpr))`, so the effective radius is `2^n/dpr` user px: a lab
  `soft:6` is ~8px at dpr2 and ~5.3px at dpr3. The dice happen to round UP at
  dpr3 (softer on phone), cards round DOWN (tighter). P753's "the lab's
  numbers keep their meaning" contract is only approximately true. Fix if a
  look ever needs to match exactly across devices: make the last mip step
  fractional so the final scale is exactly `1/F`.

- **`tar_pit` dead-reader sweep** (noted in code at the NPC_ARMS site): the
  card is retired off FAM_LIVE; the `G._oTarPit`/`G._famTarPit` consumption
  blocks have no writer left.

- **`type:'once'` is decorative on 11 of 14 pooled cards.** Only `challenge`
  and `steal_low_bank` gate on `effect.type`; everywhere else the use-count is
  enforced by `eff.uses||1` or a boolean flag, and `type` is never read.
  Nothing is wrong today - all 14 agree - but `grogs_bump` carries
  `type:'twice'` **and** `uses:2`, so rebalancing it via the obvious field would
  silently do nothing. Either enforce `type` or drop it from the mechanics that
  ignore it. Same latent-drift class as the `||500` defaults. See
  `docs/archive/CARD_AUDIT.md`.

- **`block_low_bank` is implemented on both seats and no card declares it.**
  The mechanic has branches in `handleBank` and `finOpp` — tabulated during the
  mechanic-table work — but nothing in `NPC_CARDS` carries
  `mechanic:'block_low_bank'`. Dead in the opposite direction from most findings:
  built, never dealt. Either a card lost the mechanic or never got one. Not
  urgent; needs a design call, not a fix. See `docs/OPPCARDS_LIFT_SIZE.md`.

## Read this first

**You can see the game.** `tools/shoot.js` drives headless Edge over CDP and
writes PNGs the Read tool displays; `tools/shoot_play.js` plays a real match
from the menu. Do not synthesise game state — it lands on screens that are not
the game being played, which cost most of a day.

```bash
node tools/shoot.js --url http://localhost:8084/fark_proto.html \
    --eval-file tools/shoot_play.js --out shot.png
```

Flags: `--burst N --every MS` (frame strip), `--w --h --dpr`, `--wait MS`.
Reports the WebGL renderer, page throws and every 404. Works against the live
Pages URL identically. The dev server dies occasionally — if everything is
`undefined`, restart it before diagnosing.

The real entry chain, all of it load-bearing: NEW RUN is `#hsBtnBottom`; the
offered dice ignore taps until `die._floatDone`; `#nrTakeBtn` is "TAKE IT";
patron cards are `.ptcard` with **no** onclick attribute; "SIT DOWN" is a bare
`<span>` whose handler lives further up. `G` is a top-level `let` — bare `G`
resolves, `window.G` is undefined.

Why each fix looks the way it does is in the commit messages, not here. This
session ran P316 → P340; `git log --grep=P3` is the audit trail.

## Fixed today

Slot system cut from six interacting mechanisms to one rule (a die's slot is
its slot). Jade's 6 scores as a 6. Boss cards and boss relics (both keyed off
`_bossKey`). Break-onto-Jade no longer hard-locks. Overtime terminates. Card
bar stops eating ROLL. ENCORE cannot be replayed inside its own resolve
window. Feats ceremony deleted, feats still awarded. Kept-die look derived
from the class so it survives a reroll, and depth-sorted so it reads
translucent rather than broken. Score stack clears the drawn dice on both
sides. Selection glow rebuilt from strokes so it needs no engine probe.
Greybox fill removed — boss tables and the match vignette paint again.
Branded dice stop leaking textures. Bosses use the patron table.

## Open, in the order I would take it

1. ~~**Zero Hour does not end the turn**~~ — fixed P341. Both commit paths now
   call one `_zeroHourClose()`: it banks when there is something to bank and
   hands the table over when there is not. Also moved ahead of the hot-dice
   branch, which returned early and let a brand that completed the row skip
   the tell and cut a later roll. Verified by play in
   `tools/shoot_zero_hour.js`. **Design call left for Denis:** a brand that
   completes the row now ends the turn *instead of* awarding hot dice — no
   +250, no fresh six. The alternative is to award the bonus and then end the
   turn; one message and one outcome read cleaner, so that is what it does.
2. ~~**Three Grog card arts 404** every match~~ — fixed P342, and it needed
   neither art nor a fallback. The fallback already worked (the `<img>` removes
   itself on error and the emoji on its colour swatch shows), and the cards
   were not on screen at all: ROOM V2 hid the whole legacy panel with
   `#screen-gauntlet .tier-boss-loadout{display:none !important}` and kept the
   node, and `_renderBossLoadout` kept writing into it — two card previews,
   their tooltips, six `mkDie` calls and a saved pick list per gauntlet render.
   It now leaves if that rule is in force, and resumes if the rule is deleted
   (verified both ways). **Still true:** those three PNGs do not exist, so if
   that panel is ever unhidden the cards read as emoji-on-swatch until Denis
   draws them. Nothing else in the game asks for them.
3. ~~**CAST stays enabled after casting**~~ — fixed P341. `handleBank` returned
   at `total<=0` without touching the UI, so the button stayed lit reading
   CAST for a selection that no longer existed. BANK now goes dark, ROLL
   carries the turn on, the `+0` tag is cleared, and the empty `{vals:[],pts:0}`
   kept entry is no longer pushed. The effect's own status line stays — that
   is the feedback that the cast happened.
4. ~~**Drill Order**~~ — fixed P343 / P343b / P344, all three parts. One
   `_drillCap()` now answers for the guard, the button lock and the bust-save
   (they asked three different questions, which is why a sleeved drill was
   enforced by `handleRoll` while the button still looked live). It knows about
   the free roll: when every remaining die is selected, that press IS the
   hot-dice commit the badge promises, so ROLL unlocks for exactly that press.
   Message shortened to "ROLL LOCKED — BANK IT" (224px in a 430px screen; the
   old one ran off both edges). The sleeve chip carries the count, since a
   sleeved rule gets no badge. Counter display clamps at the cap — the free
   roll does spend a slot (it goes through `afterRoll`, not `handleRoll`, which
   is where the counter actually lives), so the raw number could read 4/3.
5. **Family cards** — diagnosed by an 11-agent workflow, each proposed patch put
   past two independent verifiers. Split five ways:
   - ~~**STEADY HAND**~~ — fixed. 2/2. `use()` now returns false so `famUse`'s
     `if(fx.use(inst)){inst.charges--}` leaves the counter alone; the die tap
     bills instead. Re-arming is free, an abandoned arm costs nothing, and
     `handleRoll` drops the flag and the red outline since the roll rebinds the
     dice the arm belonged to.
   - ~~**FAIR TRADE III**~~ — fixed. 2/2. `canUse` requires `!G._fairTrade`, one
     loan at a time; the record clears each `startPTurn`, so the second charge is
     spendable next turn. **Correction to the original finding:** "permanently"
     overstated it — `use()` writes only `G.matchDice`, which is rebuilt at match
     start, so the damage was match-scoped.
   - ~~**"Rival cards never fire because CFX hooks check `owner==='p'`"**~~ —
     **THE FINDING WAS WRONG.** The rival was never meant to run through CFX: it
     has a parallel hand-written path (`_npcFamCard`, plus inline blocks in
     `_npcArmActives` / `runOppTurn` / `finOpp`). Nothing to fix here.
   - **PRESERVE** — real, an ordering bug in `startPTurn`: the effect lands
     ABOVE the per-turn reset, so `G.kept=[]` deletes the amber die six lines
     after it is written and the charge buys a log line. The fix is a relocation
     (below the reset AND below Stakes Rising, which *assigns* `G.turnPts`).
     **NOT APPLIED — 1/2 verifiers.** The dissent is worth reading: the card says
     "already kept and scored", i.e. a visible DIE, and the patch delivers a
     number in the tray. Denis's call.
   - **RIVAL TAR PIT** — real, 2/2, same ordering bug (the `G.numDice` cut sits
     above the reset that rebuilds it). **NOT APPLIED** on a verifier's explicit
     advice: fixing it makes the *rival's* Tar Pit real while the *player's* stays
     cosmetic — same card text, one-way weapon. Ship both sides together or
     neither. Denis's call.

   Full findings, evidence and patch text: the workflow output at
   `tasks/weys6qm7r.output` (see the in-flight note above for the script path).
6. ~~**No UI offers the resume path**~~ — **the finding was wrong.** There is a
   resume section in Settings, gated on the snapshot, and it works end to end.
   Played and measured: the snapshot is written and persisted to localStorage,
   survives leaving the match, the section shows with a correct label
   ("MATCH IN PROGRESS — PATRON · YOU 100 / 2,800 (TURN 2)"), and the button
   restores pPts, oPts, turn and phase identically. Its placement is deliberate
   — the markup says so: "Resume lives here in Settings (no on-screen banner)."
   Nothing to fix. If it should be easier to find, that is a design change to
   ask for, not a bug.
7. ~~**`G.isBoss` is never assigned**~~ — fixed P345. `'isBoss' in G` measured
   `false`, `'_isBoss' in G` `true`. Both readers were dead: the tell badge
   never got `.bossbind`, so a boss's tell was painted in patron colours
   instead of the red seal the CSS carries for it; and `_bossFirstEnc` stayed
   `undefined`, so the fast-rival speedup applied to a first boss encounter —
   the one turn it exists to leave at full length.
8. ~~**Hot dice +250 goes straight to the banked score**~~ — fixed P346. Both
   hot bonuses (the +250 and Iron Crown's) join `_stakesRisingBonus`, the shared
   turn-bonus pot Flintlock's +200 already uses, and inherit every path written
   for it. Measured: hot dice leaves `pot 250 / turnPts 2750 / pPts 0`, and a
   bust takes all of it. **Tidy-up left over:** that field's name is a lie — it
   is not only Stakes Rising and has not been since Flintlock joined it. A
   rename across ~35 sites is mechanical but would have buried the scoring
   change in this commit.
9. ~~**Rival speech balloon paints over the tell badge**~~ — fixed P348.
   Measured at 430x900: badge 150..280 x 135..184 (z 20), balloon scroll
   76..354 x 163..216 (z 90), overlap 130x21px = 43% of the badge, including the
   half that carries the roll counter. Neither can move without landing on
   something else (55px of clearance to the HUD above, 4px to the dice area
   below), so the badge yields for the few seconds the rival speaks and comes
   straight back — verified opacity 1 → 0 → 1 with its box unchanged.
10. ~~**`handleRoll` has no `_endMatchFired` guard**~~ — fixed P345, one line in
    each of `handleRoll` and `handleBank`. Verified by calling both directly
    after `endMatch(true)` (which is what a leftover timer does): phase, pool
    and the dice row all unchanged. `G.phase` is deliberately left alone —
    `_endMatchFired` is the flag every scheduled callback in the file already
    checks, and inventing a terminal phase value would put every
    `phase==='choosing'` test in the game in play for no gain.

Explicitly out of scope per Denis: end-of-match screens (he is redoing them),
and the first-night 2D dice (never replaced, known).

## Known limits of the audit

- No coverage of rival behaviour over many turns (that agent died).
- Interaction mashing found nothing: ~2,500 taps, zero errors, zero score
  drift, zero stuck buttons. Busts and hot dice held up under everything.
- Some reported "score drift" and a "stale SIT DOWN" were rig artefacts the
  agents themselves identified and discarded. Trust the disclosed caveats in
  `archive/AUDIT_FINDINGS_RAW.md`.

## In flight — play-test + Preserve build

Launched at the end of the 2026-07-30 session, when the orchestrator was nearly
out of context. Results land as a task notification and in the journal; **read
them before starting any of this by hand.**

    run id     wf_9aa2dedc-0e6
    journal    .claude/projects/<project>/<session>/subagents/workflows/wf_9aa2dedc-0e6/journal.jsonl
    script     .claude/projects/<project>/<session>/workflows/scripts/fark-playtest-and-preserve-wf_9aa2dedc-0e6.js

Three things in it: play-tests of STEADY HAND and FAIR TRADE (the two fixes that
went in on review alone), and a build of PRESERVE as a visible die in an isolated
worktree, checked by two adversarial verifiers — one on correctness, one asking
whether a player can *look* at the table and see the preserved die, which is the
whole reason the points version was rejected.

The Preserve build returns a diff rather than landing on this branch — it needs
applying and re-verifying here. If the journal is gone, the script is checked in
and can be re-invoked with `Workflow({scriptPath})`.

## In flight — a diagnosis workflow whose findings were never read

A 11-agent workflow was launched to diagnose backlog item 5 (the five inert
family-card defects) and to scout the Game Over screen. The Game Over half was
overtaken by hand — P350 is built and deployed. The **five card diagnoses were
never read**: the run was still in its Verify phase when the session ran out of
context.

Each defect got one investigator (returning an exact old/new patch pair) and two
adversarial verifiers — one checking correctness and old-string uniqueness, one
checking the patch delivers what the card's own description text promises.

    run id     wf_cc266d46-aa3
    journal    .claude/projects/<project>/<session>/subagents/workflows/wf_cc266d46-aa3/journal.jsonl
    script     .claude/projects/<project>/<session>/workflows/scripts/fark-family-cards-and-gameover-wf_cc266d46-aa3.js

Read the journal for the returned findings. It is session-scoped and will not
survive cleanup, so if it is gone, re-run the script — it is checked in at the
path above and can be re-invoked with `Workflow({scriptPath})`. Treat every
proposed patch as unverified until its `oldString` is confirmed present and
unique with Read, not Grep (Grep renders `/*` as `\*`).

## Decided by the creative director — one still to build

All five design questions in `DESIGN_QUESTIONS.md` were answered. Four are done
and in the build (Zero Hour kept as-is with its reasoning now in the code, Tar
Pit retired, camera flattened instead of shrinking the dice, Game Over placement
anchored to the art). **One remains:**

### PRESERVE must be a visible die, not points

The call was A, and it was not a fresh 50/50 — it was already locked in the match
brief: *"A PRESERVED die SURVIVES turn end: it stays on the table in its casing
through the pile reset and is excluded from the wipe"* and *"players track curses
and Preserve choices by looking at them."* The workflow's proposed patch delivers
a number in the tally, which is exactly the invisible-effect failure mode this
project has repeatedly hunted down — on Amber's own signature card.

What the card promises: *"Trap one scoring die in amber at the end of your turn.
It is still there next turn, already kept and scored."* Tier 3 adds +100 when it
cracks free.

To build:
1. **The die survives the turn reset.** The underlying bug is an ordering one —
   the effect currently lands ABOVE the per-turn reset in `startPTurn`, which
   does `G.turnPts=0;G.kept=[];G.numDice=...` and deletes it. Relocating it must
   also land *below* the Stakes Rising branch, which **assigns** `G.turnPts`
   rather than adding to it.
2. **It is on the table, in its casing.** Not just a kept-tray entry: a die the
   player can look at, visibly held, excluded from the pile wipe.
3. **It cannot be re-rolled or re-selected** — it is already scored. That needs
   its own visual state, distinct from both live and spent dice. The budget for
   this was accepted when the brief line was written.
4. `G.numDice` should drop by one, not be hardcoded to 5 — a hand already cut by
   Confiscate/Seize would otherwise get the amber die for free.

Sibling bug, same cause, worth fixing in the same pass: the rival Tar Pit
consumption block had the identical ordering fault. Tar Pit is now retired so it
no longer matters, but if anything else is ever consumed at the top of
`startPTurn`, check it against that reset.

## From the play-test workflow (wf_9aa2dedc-0e6) — read before touching these cards

The two fixes that had gone in on review alone were PLAYED. **Both charge
economies are correct** — Steady Hand bills exactly one on the tap and nothing on
the arm; Fair Trade allows one loan at a time. But playing them found things
review could not:

**STEADY HAND — two fixed in P363, three left.**
- ~~stale gold ring after a reroll~~ and ~~the arm stranded by other cards~~ are
  fixed. The second is the recurring lesson: `handleRoll` was taught to disarm and
  *four other sites that rebind the free dice were not* — Powder Keg, Encore,
  Fool's Gold and the card-reroll block. One `_steadyDisarm()` now, called by all
  of them.
- **Still open:** the reroll gives no feedback of its own (`famLog` is wiped in
  the same tick by `refreshSelUI`'s `setStatusMsg('','')`), so a reroll landing on
  the same face looks like a dead tap. An already-selected die shows no red target
  ring (`.selected` paint wins). `G._steadyArmed` is never cleared at turn end —
  latent, not live, since `handleRoll` clears it before the new dice bind.

**FAIR TRADE — one `wrong`, not yet fixed.**
- **A shattered borrowed die leaves a stale `G._fairTrade` whose lane now points
  at somebody else's die, and the next turn's restore destroys that die for the
  match.** That is the one to fix first.
- `canUse` approves a trade `use()` then refuses, silently — the card is tapped,
  PLAY pressed, nothing happens, no message. While a loan is outstanding the card
  still reads as live ("uses left: 1").
- Tier I and tier II are mechanically identical: tier I's "for this roll only"
  lasts the whole turn.

**PRESERVE — built, 15/16 routes pass, NOT APPLIED.** The diff is in the workflow
output. 1/2 verifiers, and the dissent is concrete and confirmed: the patch
*creates* a regression — the preserved kept entry re-qualifies for Preserve, so a
charge can be spent on a die already in amber without rolling — and RESUME
refunds the spent charge while keeping the amber die, because `G.pF` is not in the
snapshot. Both need closing before it lands. Its own open design questions are
worth Denis's eye too: should a bust crack the amber, and should the player choose
which die is trapped rather than the card taking the first.

**Missing card art:** `assets/cards/steady_hand.webp` and `fair_trade.webp` 404
and paint as broken-image glyphs; `famCardArt` has no fallback (unlike
`_cardArtImg`, which removes itself on error).

## The revised rework brief — what it answered, what is left

`docs/briefs/FARK_ENCHANT_BADGE_REWORK.md` was updated after the code audit and
now settles three things it previously deferred:

- **Fair Trade, borrowed die destroyed** → REVERSED. The die is permanently
  gone. The old "loan voids" ruling was a live exploit: borrow your own Obsidian,
  Break it for the guaranteed +1000, and Fair Trade erased the loss — section 4's
  whole timing trade for free. **Done in P365.**
- **Brutus's relic** → becomes a die that permanently carries the Ward enchant,
  pre-applied, counted against the one-Ward-per-loadout cap. **Not done.** This
  also deletes the last guaranteed full bust-save, which §1 calls a structural
  break — the audit found §1's claim that it "doesn't exist anywhere" was false.
- **Kindred** → rescoped to the PLAYER's loadout only, because the engine has no
  opponent-side enchants. The code already checks only the player, so this now
  **matches** without work. Its "double strength" for non-numeric effects is
  still open item 1 — do not guess a per-enchant default.
- **First Strike** → redesigned to "first time the PLAYER fires a lane icon,
  reveal the opponent's layout". **Not done**, and the brief itself asks for a
  decision on whether the reduced form is worth keeping at all rather than
  shipping a downgrade nobody signed off on.

Still to build, in the order I would take it:

1. **Brutus's relic → permanent Ward**, and delete the full-save shield path with
   it (die def, `dieShieldsPlayer`/`dieShieldsOpp`, both doBust branches, the
   save snapshot, the CSS/SFX). `_wardOwned` must count the relic so the cap
   holds. Note the shield bloom is already broken: it queries
   `.die-wrap[data-mat="silver"]`, which matches nothing when the holder is
   `brutus_shield`.
2. **Fair Trade tiers** — tier I is one ROLL, tier II the whole turn. Today both
   unwind in `startPTurn`, which is per-turn, so tier I is a free upgrade.
3. **Still Waters vs Obsidian's shatter** — the one case §7 names as validated.
4. **The 1-or-5 face restriction** and the shop's face-picker step. The brief
   reaffirms it; the code ships a different system deliberately and documents
   why. Biggest single divergence, and it closes two other holes on its own — a
   branded face can then never be a 6, which is what breaks Anchor and Jade's
   wild today.

## Still open, found after the audit

- **Painted width is not modelled properly, and a sweep built on the bad model
  lied.** `_physSolve`'s spread pass measures each die's footprint as a unit
  square turned by its yaw. A die paints ~1.25 die-widths in the middle of the
  row and ~1.82 at the ends, where it sits off-axis and its near and far faces
  project apart — so the unit-square model understates footprints by ~80%, and
  P349 scales it by `drawnMid` (1.25) as a first-order correction. What is NOT
  solved: the yaw term and the projection term are not independent. Multiplying
  the end-of-row figure by the yaw term double-counts the spread and predicts a
  93px die where the widest ever measured is 78px. `tools/shoot_throw_sweep.js`
  is built on that bad model and reported "98% of throws overlap" while the
  projected-mesh ground truth over 23 rolls reported zero — **trust the ground
  truth, and fix or delete the sweep before using it again.** A correct model
  needs the projected silhouette as a function of (x, yaw), which only the live
  mesh can give.
- ~~**Six dice near the geometric limit**~~ and ~~**the outermost die paints
  ~3px past the edge**~~ — both closed by P352's camera. The creative director
  chose the lens over die size (floored by the 44px touch minimum and by enchant
  icon legibility). FOV_MATCH 54→34 with RISE_MATCH 20→34: measured on a real
  throw, widest die 59px, gaps 20–25px where they were 6–34, and the row sits
  9px inside both screen edges instead of 1px over.


### Verification debt

- **STEADY HAND and FAIR TRADE were never played.** They went in on the diff plus
  two independent reviewers each and a parse gate — the weakest verification in
  the session, and worth an actual play-test. Everything else was measured in a
  running match.

### Cleanup, none of it urgent

- **Tar Pit's consumption blocks are dead code.** `G._oTarPit` and `G._famTarPit`
  have no writer since the card was retired, so the blocks that read them at the
  top of `startPTurn` and in the rival's turn are unreachable. Left deliberately:
  removing them means edits inside the rival's turn machine for no behavioural
  gain.
- **`_stakesRisingBonus` is a misleading name.** It is the shared turn-bonus pot
  and holds Flintlock's +200 and both hot-dice bonuses too. ~35 sites, purely
  mechanical.
- **`tools/shoot_throw_sweep.js` reports nonsense.** Its width model multiplies
  the end-of-row painted width by the yaw term, double-counting the projection
  spread — it claimed 98% of throws overlap while ground truth said zero. Fix the
  model or delete the tool; do not trust its numbers meanwhile.

### Copy and art, the author's

- The victory headline still reads **"LAST ORDERS RUNG"**, which is wrong under
  either meaning of the phrase now that Last Orders is the night-end beat.
- The victory ending still lands on the greybox placeholder and wants art of its
  own — the creative director ruled it must not share the loss screen.

## Numbers worth not re-deriving

Measured at 430x900, dpr 2, after P334-P337:

    die DOM box     55.9px     slot pitch        72.2px
    drawn at rest   64.0px     drawn at peak     72.4px
    row width      417px       throw line       418px

Slot drift from own slot is 0.26–0.28 die-widths in **every** kept
arrangement (full row, kept left/right/both ends, every-other, ends-only,
middle gap, single die), minGap ≥1.15, zero off-edge, zero frame-cap, zero
reorders. `tools/dice_harness.js` reproduces this headlessly in seconds — pass
`pitch` or it guesses wrong on any subset with a hole in it.

---

## The brief sweep (wf_e505c7ff-bdc) — area A landed, six to go

28 agents, 0 errors, seven disjoint areas each audited, double-verified and
reconciled into applyable patch text. All seven came back `applyable:true`,
67 patches total. **Area A is in (P383). The other six are not.**

Apply them with the staged applier, ONE AT A TIME:

```bash
python <scratch>/apply_area.py B   # stages to fark_proto.html.stage
```

It absorbs the two artefacts that have broken anchors on this project before —
CRLF where the file has LF, and a `\uXXXX` source escape transcribed as the
literal glyph — and refuses anything that still will not match rather than
guessing. Parse-gate the `.stage` file, promote it, verify by playing, commit,
then cut the next area against the new file.

**Why one at a time.** The areas overlap on six functions, so applying them in
sequence double-patches the same regions — the failure that wasted a round on
the match-scoping sweep. Measured overlaps:

| function | claimed by |
|---|---|
| `_enchInit` | A + B + F |
| `saveMatchState` | A + D + F |
| `doBust` | A + C |
| `_breakDie` | C + E |
| `endMatch` | D + E |
| `initMatchScreen` | D + F |

**G is the only area touching none of the others** — it can go next with no
re-cutting. After that, expect misses and re-anchor.

Remaining, with what each carries:

- **B** (7 patches) — the 1-or-5 brand restriction, the shop's random draw
  narrowed to {1,5}, and refund-and-clear for brands already on an illegal face.
- **C** (3) — the seven Break death-trigger rows.
- **D** (9) — the Trade enchant's match-end restore. **Its audit found Trade
  writing through to the RUN** (`S.run.dice[L]=theirs;save();` with a comment
  saying "for the rest of the RUN, not just the match"), which contradicts the
  match-scoped ruling outright. Highest-value of the six.
- **E** (19) — Kindred (Tithe only, per the brief's do-not-guess) and Still
  Waters, including retiring the old card-sealing code still live under the
  `confession` id.
- **F** (10) — legacy-save refunds (Break ~450g, Trade 350g) and missing-die
  visibility in the loadout/peek UI.
- **G** (4) — confirming the cut enchants are gone and routing the universal
  icon rule through one shared helper.

Cross-area findings the agents were told to report rather than patch are in
each area's `crossArea` field in the journal. The D one above is the important
one.
