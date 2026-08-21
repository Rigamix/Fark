# A jade 6 is worth far less to the rival than to the player

Found while closing a stated limit in `KEEP_CONTROL.md` — the control sweep was
all-bone, and a number computed for bone does not answer the question for jade.

## The asymmetry

| seat | scoring path | wild handling |
|---|---|---|
| **player** | `scoreSelection` (L23996, 24476, 24489, 25201, 25443, 26378…) | runs a second `_noWild` pass and **keeps the better** |
| **rival** | `scoreRoll` directly (L27777, 27831, 27907, 27995, 28103) | single pass — the wild is **always substituted** |

`scoreSelection`'s own comment states the intent:

> *a wild was substituted unconditionally, so a Jade 6 could only ever be spent
> as a wild and never as a 6 — four Jade 6s scored 600 where four Bone 6s score
> 1200, and a 1-2-3-4-5-6 straight could not complete because its 6 had been
> replaced.*

That fix landed on the player's path. **The rival never got it.** Measured over
every roll containing a jade 6:

| | |
|---|---|
| rolls with a jade 6 | 462 |
| rolls where jade vs bone changes the score | **308** |
| rolls where `scoreSelection` beats `scoreRoll` | 3 |
| **best candidate ≠ the rival's maximal keep** | **38 points, 7 dice** |

Worst case measured: **`23456` with a jade 6 — the rival takes 50, the same
dice are worth 750.** That is the straight the comment describes: with
`_noWild` the jade stays a 6 and completes 2-3-4-5-6; without it the 6 is
consumed as a wild and only the lone 5 scores.

`jade` and `jade2` are both wild, and both are in `dieBias` — `triples:jade`,
`straights:jade/jade2` — which maps to Brutus (soldier→triples) and Aldric
(knight→straights). Reachable by design, not a theoretical case.

## Why this stops the wiring patch

The plan was to route all three keep sites through one chooser that returns the
maximal keep, land it **inert**, and let the persona policy be a separate change
with its own before/after. `_legalKeeps` scores via `scoreSelection`.

So routing the rival through it **silently fixes this asymmetry** — and the
rival gets sharply stronger whenever it holds a jade. That is a difficulty
change bundled inside what was supposed to be a no-op. If it had shipped, the
next before/after would have attributed that delta to the persona choice.

`OPEN.md` §6 exists because three difficulty changes landed in one session
without being separable. This would have been a fourth, hidden inside a patch
whose entire stated purpose was changing nothing.

## How the blind spot was caught

Worth recording, because the first two measurements both said "fine".

1. `probe_wild_divergence` — 394 rolls with a jade, **0 divergences**.
2. `probe_wild_instrument` — checked whether the instrument could see, by
   swapping bone→jade and asking whether the score ever changed:
   **0 of 461**. The material never reached the scorer, so result (1) was
   **void, not clean**.
3. Cause, found by reading: `scoreRoll` L17353 is
   `if(!eff||vals[i]!==6)continue;` — **a wild only activates on a die showing
   6.** The sweep built non-decreasing sequences and placed the jade at index 0,
   which is by construction the lowest value, so the jade showed 6 only when
   every die was a 6.
4. `probe_wild_real` — jade placed *on* a 6. Instrument check first:
   308 of 462 rolls change score. Only then were the divergences read.

The generator and the material placement conspired; neither was wrong alone.

## The question for Denis

In `OPEN.md` §11. Briefly: **does the rival get the wild-as-option treatment the
player has?** It is a difficulty change either way — fixing it makes the rival
stronger, leaving it means a jade is a worse die in the rival's hands than in
yours. The wiring work is blocked on the answer only because the two cannot be
measured separately if they land together.
