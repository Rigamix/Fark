# Under FOG the rival kept the wrong dice

Found while sizing the keep wiring, fixed in P491.

## The bug

FOG hides one seat from the rival's own reckoning by **splicing it out of the
array that gets scored**:

```js
var _fogV=fV.slice(); ... _fogV.splice(_fi,1);
var{total,used,...}=_scoreRollBest(_fogV,...);
```

So `used` came back **one element short**. But every downstream reader indexed
it with a position from the **full** free list:

| site | index source |
|---|---|
| L27815 snare | `used[_snIdx]`, `_snIdx` scanned over `_oFree` |
| the keep loop | `used[i]`, `i` over `G.oppDice.filter(!kept)` |

Every index at or above the fogged seat was off by one.

**Measured** with the real scorer, `free=[1,2,5,1,3,5]`, fog hiding index 2:

| | |
|---|---|
| game kept | `[1,5,3]` |
| correct | `[1,1,5]` |

It held a **3** — a die that scored nothing — and dropped a scoring 1.

## The sim already had this right

`sim_harness.js` carries `/* index shift: used is indexed against the fogged
array */` and compensates. Someone found it there and never carried it into the
game.

Third instance of the two-copies problem in this stretch, and the first in this
direction — P479 and P489 were the game being right and the sim being blind;
here **the sim was correct and the game was not**.

## Why re-expansion, not per-site compensation

Adjusting each read site would have been wrong within a few lines. `used` is
**reassigned five times** downstream — encore, reprisal, `quick_hands`,
`gilded_bones`, `slippery_table` — from arrays built off the **full** free list.
Those are already full-length, so shifting them would have introduced the very
bug being fixed.

Instead the fogged seat is put back into `used` as `false` immediately after
scoring. `used` is then full-length for its whole life and every index — present
and future — is correct with no further thought. `false` is the right value, not
a filler: the rival cannot see that seat, so it never keeps it. The sim says the
same thing in words: *"unseen seat is never kept"*.

## Verification

`tools/apv_fog_index.js` — every roll of 2–6 dice against **every** fog
position, not the one case that found it.

| | |
|---|---|
| cases | **4,746** |
| keep mismatches vs corrected | **0** |
| wrong-length `used` | **0** |
| fogged seat kept | **0** |
| **control — no fog, 923 rolls** | **0 differences** |

The control matters as much as the fix: if a no-fog roll had changed, the patch
would have altered every rival turn rather than only the fogged ones.
