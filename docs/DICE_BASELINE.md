# Dice throw — the numbers before the rework

Measured with `tools/dice_harness.js`, which calls `D3X._physSolve` directly:
no canvas, no rAF, no match in progress. 200 throws per scenario, 1000 total.
Re-run it after any change to the throw and compare.

```
load the page, then:
  D3X.boot(function(){})                      // brings in THREE
  <script src="assets/vendor/cannon.min.js">  // and CANNON
  <script src="tools/dice_harness.js">
  dice.baseline()
```

## Six dice, an opening roll

| metric | value | what it means |
|---|---|---|
| throws with a die REORDERED | **103 / 200** | over half of all throws have at least one die handed a *different* die's landing position, because the last pass re-sorts by loadout order |
| dice reordered, total | **246** | |
| slide, median | **1.10 die-widths** | how far the tidy passes move a die from where the sim actually stopped it — this is the "magnetic" look |
| slide, p95 / max | 1.82 / 2.38 | |
| closest approach, worst | 0.56 | below 1.0 they are visibly overlapping |
| throws that never settled | 2 (700-frame cap) | |

## The other scenarios

| scenario | reordered throws | slide p50 | worst gap | never settled |
|---|---|---|---|---|
| three dice | 25 / 200 | 0.41 | 1.06 | 1 |
| one die | 0 / 200 | 0.16 | — | 0 |
| two kept dice on the table | 79 / 200 | 0.70 | 0.00 | **7** |
| narrow screen (limitX 2.0) | 102 / 200 | 1.04 | 0.00 | 1 |

Kept dice are the worst case by a distance: p95 of 599 solver frames, seven
throws hitting the cap, and dice ending up at zero separation.

## Where the slide comes from

`_physSolve` does not move the dice after they land — it blends the correction
*into the tape*, from 35% of the way through to the end:

```
row[k].x += (want[k] - fin[k].x) * w2
```

So the slide is animated: the die is watched travelling from where it landed to
where the tidy decided it belongs. `dbg.landed` and `dbg.want` on the returned
solve are those two numbers, which is what the harness measures.

Four mechanisms contribute, in order of how much they move a die:

1. **reassign by loadout order** (17028-17035) — takes the sorted landing
   positions and hands them out by slot order, so a die that crossed a
   neighbour is teleported back. This is the one that produces the 246.
2. **the relax pass** (16946-16975) — 80 iterations of pushing neighbours apart.
3. **re-centre and rigid slide** (16979-17013).
4. **the lane spring** (16813-16815) — pulls each die toward its slot for the
   whole flight, and its gain *rises* from 1.0 to 2.2 as the die slows, so the
   pull is strongest exactly when it is being watched.

---

# After the slot rework (P302-P303)

Same harness, the slot geometry the live game actually uses (pitch 1.599,
limitX 4.25). 1500 throws across five scenarios.

| scenario | slide p50 | reordered | off edge | worst gap | max drift | never settled |
|---|---|---|---|---|---|---|
| six dice | **0.00** | **0 / 300** | 0 | 1.07 | 0.34 | 0 |
| five, one kept | 0.00 | 0 / 300 | 0 | 1.09 | 0.44 | 0 |
| four, two kept | 0.00 | 0 / 300 | 0 | 1.11 | 0.34 | 0 |
| two, four kept | 0.00 | 0 / 300 | 0 | 1.15 | 0.34 | 0 |
| one, five kept | 0.00 | 0 / 300 | 0 | — | 0.40 | 0 |

Against the before: median slide 1.10 -> 0.00, reordered throws 103/200 -> 0,
worst gap 0.56 -> 1.07, and the two throws that never settled are gone. The
solve is also about 4x faster (15.7ms -> 3.3ms) because nothing runs 80 relax
passes any more.

`drift` is now capped by the slot radius itself, which is the point: a die can
sit up to 0.34 die-widths from its slot centre and no further.

## What replaced the four tidy passes

One circle per slot, applied as a hard clamp after each solver step, engaging
only below `slotEngageY` so a die still flies free at the top of its arc.
Radius is `slotRK` (0.213) of the measured slot pitch, so it follows the row
rather than assuming it. Two dice at facing borders end up 1.599-0.68 = 0.92
apart, just inside touching, so contact is possible and rare and the collision
solver deals with it.

A slot holding a kept die is not free: each thrown die takes the nearest empty
circle. Clamping into an occupied one is unwinnable and took 116 of 200 throws
to the frame cap before this was added.

## Still open

- The launch itself (static frames, the from-the-table look, darkening while
  high) is untouched - that is the delays in `handleRoll`/`_d3InitHost` and the
  spawn velocities, not the solver.
- `tightScreen` in the harness asks for slots at +-4.0 on a screen that allows
  +-2.6. It reports every throw off-edge, correctly, because the SLOTS are off
  screen. It no longer hangs or stacks. This cannot happen in the game, where
  slots are measured off the DOM row and so are always on screen.
