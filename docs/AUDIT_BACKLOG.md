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
5. **Family cards largely inert.** PRESERVE takes its charge and does nothing.
   The rival's TAR PIT announces itself then gets wiped by `startPTurn` six
   lines later. Nearly every rival family card never fires: the CFX hooks
   return immediately unless `owner==='p'`, and the AI only ever arms
   `tar_pit` / `sleight`. FAIR TRADE III used twice in one turn permanently
   keeps the first borrowed die (one `G._fairTrade` record, overwritten).
   STEADY HAND spends its charge on ARM, not on the reroll, and re-arming
   silently burns another.
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

## Still open, found after the audit

- **The outermost die paints ~3px past the screen edge**, every roll, on a
  430px viewport. Not drift — a layout asymmetry. Perspective makes an
  off-centre die's silhouette wider on its OUTBOARD side than its inboard side,
  so a symmetric `drawn/2` margin understates it by about that much, and the
  slot centre is where the flex layout put it (P347 deliberately stopped moving
  slot centres — moving them is what used to squeeze the ends into their
  neighbours by 23px). Cheapest fix if it matters: trim the row gap by ~1.2px
  (`3.8cqw` → `3.5cqw`), which pulls each end centre in ~3px at a cost of ~1px
  off every inter-die gap. Left alone because it also tightens `SLOT_BASE`,
  which is already only ~3px.

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
