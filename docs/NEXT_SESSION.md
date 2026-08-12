# NEXT SESSION — start here

Tree is clean. Worktree, root `fark` and `origin/fark` are all at **28ebaea**.
Everything below is deployed and verified live by grepping a marker on the
served file, never by a green build.

---

## THE PLAYTHROUGH NOTES ARE DONE — 6 fixed, 1 is yours

| # | note | outcome |
|---|---|---|
| 1 | roll button jitters sideways | **P634** — 131px, and it was never the pivot |
| 2 | win screen's bottom UI is slow | **P635** — a hard-coded 3.2s wait, now 2.4s |
| 3 | boss cards mirrored + degradation | **P633** — the row was rotated 180° |
| 4 | what IS First Strike? | **answered — needs your ruling**, `docs/OPEN.md` §11 |
| 5 | dialogue in two places | **P632** — one cause with 6 |
| 6 | dialogue never stops talking | **P632** — same cause |
| 7 | shelf cards ignore the perspective | **P636** — measured off your painting |

Three of the six were regressions from the session before this one. Each is
named as such in its own commit message.

---

## WHAT THE FIXES ACTUALLY WERE — the short version

**P632 (notes 5+6).** P628's hesitation beat called `setStatusMsg` — the "PATRON
IS ROLLING…" channel — which also skipped `DLG.trigger`, where every other beat
gets both its surface and its spacing. And the `agg` band that justified it does
not measure what it claimed: measured over a real match, `agg` was **0.53 on all
seven calls**, because it starts as `rung.agg` and for an ordinary patron nothing
moves it. So the band selected OPPONENTS, not decisions — one patron hesitated on
every single roll, another never (24 calls, 0 lines, in a separate run). Deleted
the helper, the band and the `G._oppAgg` stash; the beat is two ordinary
`_DLG_MOMENT` entries now. **No new pacing system was built. One existed.**

**P633 (note 3).** `#famRowO` carried `rotate(180deg)`, written when the row held
flat `.mcBack` rectangles — its own comment said reversing their order was
"meaningless for identical backs". P591 put painted faces in that row. The
degradation Denis wanted removed had *already stopped painting* for the same
reason: `.mcBack.broken` had nothing left to match. Same edit also restored the
rival's ARMED telegraph, which had been invisible since P591.

**P634 (note 1).** `@keyframes rollBounce` declared `translateX(-50%)` at both 0%
and 100% — the other half of a `left:50%` centring `#btnRoll` stopped using long
ago. 125.859px is exactly half its 251.7px width. **Intermittent** because
`#btnRoll.disabled{transform:none !important}` outranks an animation, so whether
you see it depends on whether something re-disables the button inside those
150ms. That is why two sessions of transform-origin work never touched it.

**P635 (note 2).** One hard-coded `setTimeout`. The reveal's last moving part is
`coinSheen .6s` starting at 1600ms, so everything stops at 2200ms; the patron win
held the lower half until 3200ms while the boss win beside it already used 2400.

**P636 (note 7).** Measured off `shelf_bg.png`: the middle slot's width runs
402.9 → 494.2 (ratio 1.2266) with its centre on the image centre — one ground
plane, vanishing point above the middle slot. `rotateX` from the slot's height
against the card's, `perspective` from the taper. Two measurements, neither
fitted to the other, both exact on the back-check.

---

## THE LESSON THIS SESSION KEEPS EARNING: a clean number is not a finding

Four times, and each cost real time:

1. A whole-match run reported the hesitation firing 24 times and saying nothing.
   True — for that opponent. A second run said 7 for 7. **The contradiction was
   the finding**, not either number.
2. The roll-button repro measured **0px of travel across 151 samples of a real
   bank** and was completely wrong. The positive control — call the same function
   directly — showed 131px. Without that arm the bug would have been closed as
   "not reproducible".
3. The win-screen probe reported the screen still animating six seconds in,
   because `getAnimations()` returns FINISHED animations that hold their end
   state via `forwards`, and the table's ambient loops never stop.
4. A grep for `.mcBack.broken` on the live file came back with one hit after the
   rule was deleted. It was my own comment quoting the rule.

**Every probe here now carries a `control` block, and any zero without one should
be treated as an instrument failure until proven otherwise.**

---

## HARD-WON FACTS — do not re-derive these

* **`agg` is a per-opponent constant, not a per-decision one.** It starts as
  `rung.agg` and only `chaotic`, `adaptive` and the desperate-play branch move it
  — none of which most patron matches reach. Do not build anything on "how close
  was that call" without measuring it first.
* **`DLG.trigger` is the only front door for a dialogue beat.** It carries the
  per-category probability, the `busyUntil + gap` spacing and the `_priority`
  interrupt list. `triggerCard` bypasses both gates by design (the teach moment);
  everything else must not.
* **`.mcBack` is gone.** The rival's cards are `.fcv` through `famCardArt`. Any
  rule still keyed to `.mcBack` matches nothing.
* **`.in-zone` is gone.** `usedCards[cardId]` is the only source of truth for a
  card being spent.
* **The card activation threshold** is `--card-arm-lift` (16cqw), resolved
  through a hidden strut (`#armLiftStrut`) so the CSS engine handles the unit.
  `parseFloat` on the var is WRONG — it drops the unit and fails open.
* **The dice throw has no rise.** `y[0]` IS the peak.
* **`PERSONAS` ≠ the dialogue traits.** Two six-way lowercase taxonomies. Dialogue
  traits are cunning/greedy/orderly/reckless/steady/**strong** — `strong` is what
  other docs call BULLISH.
* **`_dlgSay` tries `patron:<key>` FIRST**, and a patron's stage-0 lines are a
  floor that never empties, so a thread pool placed after it is unreachable for
  anyone with personal lines. This bit twice.
* **The last row of `PATRON_LINES` has no trailing comma.**
* **The FSIM harness calls `oppShouldBank` too** (~40145). Hooks belong on the
  in-match call only.
* **A transform makes a stacking context.** `.loCard.zoom{z-index:60}` means
  nothing outside `#loCardPlane`; that is why P636 lifts the plane, and it is the
  same bug P594 shipped on the leader's flag.
* **First Strike is a sealed-seat tell, not a card or a handicap**, and it only
  fires when the player casts Snare, Trade, Snuff or Fog. See `docs/OPEN.md` §11.

## INSTRUMENT TRAPS THAT COST REAL TIME

* `getAnimations()` returns FINISHED `forwards` animations and infinite ambient
  loops. Filter on `playState === 'running'` AND finite iterations AND scope to
  the subtree you mean.
* `G.phase === 'idle'` never becomes true. Gate on the element you need.
* Timers throttle to ~7fps headless — but that only matters for sampling a
  *curve*. A constant offset (like rollBounce's) lands in any single sample.
* The player's dice are tapped through a hidden `<i class="die-hit">` pad; a
  click on the `.die` itself selects nothing. Drive selection through
  `toggleDie(d)` on `G.pool` instead.
* `FAM_CARDS` is an ARRAY of definitions, not a keyed map.
* `window.G = {}` does NOT rebind a `let`-declared `G` — but a top-level
  `function foo(){}` IS a global-object property and CAN be overridden that way.
* Bash heredocs mangle `\uXXXX`. Patch through a Write-tool `.py` script whose
  anchors assert an exact match count.
* **Always dedupe new dialogue against the WHOLE existing table**, not just
  against itself.

## VERIFICATION STANDARD THIS PROJECT NOW EXPECTS

Every check needs a control that FAILS. Reachability before correctness: three
times in the previous session the code was correct and simply never reached.
`tools/apv_loadout_reaches_table.js` exists specifically because its absence let
`const pCards=[]` survive review.
