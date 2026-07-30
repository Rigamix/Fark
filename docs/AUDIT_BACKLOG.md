# Audit backlog — pick up here

Written 2026-07-30 so a fresh session loses nothing. Companion to
`AUDIT_FINDINGS_RAW.md` (all 72 soak findings verbatim, with repro lines).

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
  `AUDIT_FINDINGS_RAW.md`.

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
