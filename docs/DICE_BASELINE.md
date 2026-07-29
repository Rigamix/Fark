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
