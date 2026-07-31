# The two rival-dice items, specified — start here

Both confirmed by Denis after the P370-373 dice work landed. Both are on the
RIVAL's side only. Neither is started.

---

## 1. The rival's kept dice change angle on a reroll

**Denis: "Yes I saw the kept die angle change on NPC side."**

Ruled out already, by measurement — do not re-measure these:

* The PLAYER's kept dice are rock steady. `tools/shoot_kept_angle.js` keeps a
  die, rerolls, and compares: quaternion delta `0.0000` before/during/after,
  `translate` byte-identical, CSS `rotate:none`. Whatever this is, it is not
  shared with the player's path.
* `_keptLook` is not the cause. It only walks materials — `transparent`,
  `opacity` — and touches no transform.

Where to look, in order:

1. **`_oppHoldKept` (fark_proto.html ~22597) keeps the DOM element but nothing
   re-establishes the die's POSE.** The player's kept die holds its angle
   because its `d.roll` still points at the solve that landed it, and
   `_physPose` clamps to that solve's last frame forever. Check whether a kept
   RIVAL die still has `d.roll` after `_oppHoldKept` runs — `shoot_kept_angle.js`
   already reports `hasRoll`, so point it at `#oppDiceRow` across a multi-roll
   rival turn. If `d.roll` is gone or was never set, the die falls back to its
   home orientation and that IS the jump.
2. **The `D3.draw(d.el._d3)` calls all over the rival's scoring path** (25115,
   25122, 25188, 25200, 25212, 25218). These redraw the die and are called on
   dice that are already kept. The player's path does not do this to a kept die.
3. Only if both come back clean: `_measureHomes()` re-running on the rival's row
   between rolls, which P370 made meaningful for the first time (before it, kept
   rival dice were re-flowing anyway so a pose change was invisible under a
   bigger one).

Reuse `tools/shoot_kept_angle.js` — it already drives the entry chain and
diffs quaternions; it needs its target row swapped and the loop extended
across a rival turn.

---

## 2. The rival scores before its dice have settled

**Denis: "just ensure dice are settled and static before the selection happens
and it's the selection that gets the score numbers to be displayed."**

So the required order is exactly:

    dice land and go STATIC  ->  selection appears  ->  score numbers appear

and the score is a consequence OF the selection, not a separate step that
happens to run near it. Same causality the player has.

**Why it is wrong today.** The rival's roll loop builds its dice and then runs
`scoreRoll` -> marks dice `kept` + `oppkeep` (25115) -> `_renderOppTags(total)`
(25321) all inside the SAME synchronous block that created them. Nothing waits
for the throw to play back. The player's path is only correct by accident: a
human physically taps after the dice stop, so the ordering is enforced by the
interaction rather than by code. That is why only the rival shows it.

**The settle signal already exists** and is what every harness in `tools/` uses:

    !(D3X.dice || []).some(d => d.roll)

A die's `roll` is cleared when its tape finishes. Gate on that, not on a
timeout — a fixed delay will drift against the physics and this project has
already been bitten by timing constants that assumed a settle duration.

**The beat between settle and selection** is Denis's ~400-500ms deliberate
pause (AUDIT_RESOLUTIONS.md item 3), explicitly wanting a feel-check on device
rather than trusting the number from a text description. Route it through
`_oppDelay()` like every other rival pacing value so the existing speed-up
paths keep working.

**Do not** simply wrap the existing block in a `setTimeout`. `_oppBustOut` and
the disruption-card branches (Quick Hands, Grog's Bump) return early from
inside that block, and several later branches re-run scoring after mutating
dice. The settle gate has to sit ahead of the whole score-and-select section
without changing which branch wins.

**Verify by playing it**, not by reading the diff: sample `#oppDiceRow` during
a rival turn and assert no `.oppTag` / `#oppTotal` text exists at any moment
when any rival die still has `d.roll`. `tools/shoot_npc_lanes.js` already
samples that row on a timer and is the closest starting point.
