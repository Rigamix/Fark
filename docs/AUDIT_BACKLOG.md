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
2. **Three Grog card arts 404** every match: `assets/Card_ART/grogs_bump.png`,
   `one_more_round.png`, `her_lucky_coin.png`. All three ids are real
   `npcOnly` cards in rung 0's `cardPool`; the files do not exist. Needs the
   art, or a graceful fallback in the card renderer (they draw as blank
   rectangles today). `ugly`, trivial once decided.
3. ~~**CAST stays enabled after casting**~~ — fixed P341. `handleBank` returned
   at `total<=0` without touching the UI, so the button stayed lit reading
   CAST for a selection that no longer existed. BANK now goes dark, ROLL
   carries the turn on, the `+0` tag is cleared, and the empty `{vals:[],pts:0}`
   kept entry is no longer pushed. The effect's own status line stays — that
   is the feedback that the cast happened.
4. **Drill Order**: the badge promises "Hot Dice rolls free" and it is
   unreachable (the ROLL plate is `pointer-events:none` at the cap AND
   `handleRoll` returns at the drill guard). Its status line — the only thing
   explaining why ROLL is dead — runs off both screen edges. When Drill Order
   arrives as the player's SLEEVE on an already-sealed seat the cap is
   enforced with no counter shown at all.
5. **Family cards largely inert.** PRESERVE takes its charge and does nothing.
   The rival's TAR PIT announces itself then gets wiped by `startPTurn` six
   lines later. Nearly every rival family card never fires: the CFX hooks
   return immediately unless `owner==='p'`, and the AI only ever arms
   `tar_pit` / `sleight`. FAIR TRADE III used twice in one turn permanently
   keeps the first borrowed die (one `G._fairTrade` record, overwritten).
   STEADY HAND spends its charge on ARM, not on the reroll, and re-arming
   silently burns another.
6. **No UI offers the resume path.** `S.pendingMatch` is written correctly and
   `resumeMatch()` restores a match perfectly when invoked — nothing calls it
   after a force-close.
7. **`G.isBoss` is never assigned** — the field the match sets is `G._isBoss`,
   so two boss-only behaviours are dead code.
8. **Hot dice +250 goes straight to the banked score**, so busting on the next
   roll cannot take it back. The rules card says a bust loses all turn points.
9. **Rival speech balloon paints over the tell badge** and cuts it in half on
   every seat that has a tell. `ugly`, but the badge is how the rule is read.
10. **`handleRoll` has no `_endMatchFired` guard** and `G.phase` is left at
    `'choosing'` after a match ends, so a queued auto-roll (Double Down's
    ~450ms, the bust-save's ~1.7s) can deal six dice into a finished match.
    Not reachable by finger — the button is `pointer-events:none` and the end
    overlay covers it — but the game schedules those timers itself.

Explicitly out of scope per Denis: end-of-match screens (he is redoing them),
and the first-night 2D dice (never replaced, known).

## Known limits of the audit

- No coverage of rival behaviour over many turns (that agent died).
- Interaction mashing found nothing: ~2,500 taps, zero errors, zero score
  drift, zero stuck buttons. Busts and hot dice held up under everything.
- Some reported "score drift" and a "stale SIT DOWN" were rig artefacts the
  agents themselves identified and discarded. Trust the disclosed caveats in
  `AUDIT_FINDINGS_RAW.md`.

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
