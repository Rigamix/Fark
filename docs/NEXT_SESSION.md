# NEXT SESSION — start here

Tree is clean. Worktree, root `fark` and `origin/fark` are all at **b1ac688**.
Everything below is deployed and live.

---

## THE ACTIVE JOB: Denis's playthrough notes (7 items, 0 done)

Given at the very end of last session. Three are almost certainly regressions
from that session's own work — those first.

### 1. Roll button still jitters sideways  — MINE, and my first fix was wrong
P599 pinned each match button's `transform-origin` to its outer edge so the
BANK-TO-WIN size swap wouldn't move their screen margins. P601 undid that (back
to centre origin + a companion `translate`) on the theory that an unconditional
origin was re-pivoting some *other* `transform` animation on those buttons.
**It still jitters, so that theory is disproven.** Do not guess a third
mechanism — get a repro first.
Note: the headless harness throttles timers to ~7fps (measured), far too coarse
to sample a 0.28s transition. Two samplers already failed this way and both
reported "nothing moved". Use `shoot.js --burst N --every MS` instead, which
forces real frames.

### 2 + 5 + 6. The dialogue display and pacing — ONE fix, MINE, diagnosed
**Symptom 5:** NPC lines appear in two places — some in the parchment box, some
as status text like "Patron is rolling".
**Symptom 6:** lines fire back to back with no silences.
**Cause, same for both:** P628's hesitation beat calls
`setStatusMsg(...)` at fark_proto.html:31941. That is the wrong surface —
`DLG.show()` fills the parchment box — and it also bypasses `DLG.trigger`, which
ALREADY has everything item 6 asks for (read it at ~33601):
  * `this.prob[cat]` — a per-category chance, so not every event speaks
  * `now < this.busyUntil + this.gap` — no line lands while another is up
  * a `_priority` whitelist for the few moments allowed to interrupt
  * its own comment: "spaces lines out so they don't read as rapid-fire chatter"
**Fix:** give hesitation its own category and route it through `DLG.trigger`
like every other beat, instead of shortcutting to the end of the pipeline. The
silence Denis wants comes free from a probability below 1.
Do NOT build a new pacing system. One exists.

### 3. Boss cards — mirroring + degradation  — POSSIBLY MINE
Screenshot shows what looks like the player's card drawn on top of the rival's.
P591 changed `famRowO` to render real faces via `famCardArt` — start there.
Also: **remove the degradation/destroyed-outline effect from boss cards** so
they render like regular cards. Denis will do his own treatment later.

### 4. Win screen: bottom UI takes seconds to appear
Denis: "a card dotted line slot isn't heavy to render, or text. So what gives?"
Not investigated. Suspect a timer/animation chain rather than render cost —
measure before assuming.

### 7. Shelf screen: cards ignore the art's perspective
The three card slots are DRAWN in perspective; the cards sit flat. Also: focusing
a card should animate smoothly from its slot into the focus panel the way DICE
already do — same for tapping a patron card on the peek panel.
Adjacent to P609 (`_loCardFocus`), so start there.

### 4b. First Strike — is it a handicap or a card?
Denis entered a handicap match labelled First Strike, with "a super abstract
description", and nothing happened in game. Establish what it actually is before
touching anything.

---

## HARD-WON FACTS — do not re-derive these

* **`.in-zone` is gone.** `usedCards[cardId]` is the only source of truth for a
  card being spent. Nothing may infer used-ness from DOM position again.
* **The card activation threshold** is `--card-arm-lift` (16cqw ≈ 68.8px above
  the row), resolved through a hidden strut (`#armLiftStrut`) so the CSS engine
  handles the unit. `parseFloat` on the var is WRONG — it drops the unit and
  `calc()`/`clamp()` fail open into "armed at rest".
* **The dice throw has no rise.** `y[0]` IS the peak. Anything keyed to "the
  apex" fires at the wrong time. `D3X._airRamp(y)` is the one height ramp; both
  the air darkening and the apex swell read it.
* **`PERSONAS` ≠ the dialogue traits.** Two six-way lowercase taxonomies a few
  hundred lines apart. PERSONAS is ones/triples/straights/aggro/hoard/combo
  (loadouts). Dialogue traits are cunning/greedy/orderly/reckless/steady/**strong**
  — `strong` is what other docs call BULLISH. Writing to the wrong one ships
  lines that parse, deploy and never fire.
* **`_dlgSay` tries `patron:<key>` FIRST**, and a patron's stage-0 lines are a
  floor that never empties — so a thread pool placed after it is unreachable for
  anyone who has personal lines. This bit twice.
* **The last row of `PATRON_LINES` has no trailing comma.** Appending after it
  without one produces two array entries side by side.
* **`agg`** (stashed on `G._oppAgg`) is how close an NPC's bank/push call was.
  Band 0.40–0.65 = coin flip. It is final just after the desperate-play branch.
* **The FSIM harness calls `oppShouldBank` too** (~40145). Hooks belong on the
  in-match call only, or a 12,000-turn sim starts picking dialogue.

## INSTRUMENT TRAPS THAT COST REAL TIME

* `G.phase === 'idle'` never becomes true. Gate on the element you need.
* Timers throttle to ~7fps headless. You cannot sample an animation.
* `snapCardBack` leaves `.dragging` on through its return animation — clear it
  and ASSERT a clean start, or every trial after the first inherits it.
* One arm per page load when arms share a resource. `launchSeat` consumes a seat.
* `window.G = {}` does NOT rebind a `let`-declared `G`. Use a bare assignment.
* Bash heredocs mangle `\uXXXX`; the file mixes literal escapes AND real
  characters (`—`, `·`, `→`). Patch through a Write-tool `.py` script whose
  anchors assert an exact match count.
* **Always dedupe new dialogue against the WHOLE existing table**, not just
  against itself. That gap put a verbatim duplicate into `boss:whisper:loss`,
  and would have put 70 more in if it hadn't been caught.

## VERIFICATION STANDARD THIS PROJECT NOW EXPECTS

Every check needs a control that FAILS. Three times last session the code was
correct and simply never reached — the card gesture, the loadout chain, the
Discrepancy thread. That failure is silent: it parses, it ships, nothing
complains. `tools/apv_loadout_reaches_table.js` exists specifically because its
absence let `const pCards=[]` survive review.
