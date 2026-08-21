# The run-scoped domain — its seams, measured 2026-08-03

`tools/runscope_seams.py` reruns the grouping; the positions below were read by
hand afterwards, because the tool's own caveat says enclosing function is only
a **proxy** for the moment.

RULED: build this as a genuine parallel system, the way `_lm*` was built —
from what the content actually needs, verified against real cards. `_lm*` was
named after reading what Snare, Snuff and Fog did, and the reading is what kept
Trade out of it. So this is the reading.

## CORRECTION: one seam, not two — `seatCommit` failed the same test

Writing the patch meant reading the three `seatCommit` lines exactly, and that
disqualified it. **The third time today the read-the-exact-lines step has
changed the answer** (endMatch, then seatCommit).

Its three cards sit at `launchSeat` body lines 23, 26 and 33, and the work
between them is load-bearing:

```js
_rsTake('_dsArmed'); if(_dsPlay) buy = ...*2      // Double Stakes
S.run.gold = (S.run.gold||0) - buy;               // MUST follow the double
_rsTake('_fkArmed'); if(_fkPlay) famBurn(...)     // For Keeps
night.seatsPlayed[...]=true; save();
var oCards = generateOppCards(patron);
if(famOwnTier('high_table')>0) patron.target += 500   // High Table
```

Firing one hook at one point would mean moving High Table's target change above
`save()` and `generateOppCards`, or Double Stakes below the gold deduction.
Either reorders things that depend on each other — the same shape as endMatch's
disqualification and the two-phase turn clear, at 30 lines instead of 570.

`matchArmed` survives: **three consecutive lines, nothing between.**

## The original two-seam reading (superseded above)

`launchSeat` is 63 lines and the six cards cluster into **two tight groups**,
not one:

| body line | % in | card | what it does |
|---|---|---|---|
| 23 | 36% | Double Stakes | `_rsTake('_dsArmed')`, doubles the buy-in |
| 26 | 41% | For Keeps | `_rsTake('_fkArmed')`, burns the card |
| 33 | 52% | High Table | `patron.target += 500` |
| 59 | 93% | For Keeps | `G._forKeeps = true` + log |
| 60 | 95% | Double Stakes | `G._doubleStakes = true` + log |
| 61 | 96% | High Table | `G._highTable = true` + log |

**All three cards appear in both groups**, and the groups do different work:

- **`seatCommit`** (36–52%) — spend the arm and modify the *match setup*:
  buy-in, the burn, the target. `G` does not exist yet.
- **`matchArmed`** (93–96%) — stamp the flag onto `G` and tell the player.
  `G` exists; this is the announcement.

They are separated by ~26 lines of match construction, and the split is not
cosmetic: one runs before the match object and one after. A single seam could
not express both, for the same reason one `endTurnState()` could not express
the two-phase turn clear.

## `endMatch` is NOT a seam — and it is the finding that matters

Four cards touch `endMatch`, which made it the top candidate. Read by hand:

| body line | % in | card |
|---|---|---|
| 39 | 6% | Cursed Table (circle count) |
| 251 | 40% | High Table (pot payout) |
| 513 | 82% | For Keeps (win: take a die) |
| 590 | 95% | For Keeps (loss: they take one) |
| 609 | 98% | Hair of the Dog (arm for next match) |

`endMatch` is **619 lines**. Cursed Table's circle count and Hair of the Dog's
arming are ~570 lines apart. These four share a *function*, not a *moment*.

**Naming `endMatch` as a seam would be the Trade mistake exactly** — grouping
things that share a name rather than a shape, which is what this project has
spent the session finding and removing. The tool ranked it first on card count;
the hand-read is what disqualified it. That is the caveat working as written.

## The vocabulary, as measured

| | cards | status |
|---|---|---|
| `seatCommit` | 3 | **real seam** — spend the arm, modify the setup |
| `matchArmed` | 3 | **real seam** — stamp `G`, announce |
| ~~`endMatch`~~ | 4 | **not a seam** — four unrelated moments in one long function |
| `_tabSettle` / `famTabPay` / `famTabTake` | 1 | The Tab's own, standalone as ruled |
| `_hotdToll` / `handleBank` | 1 | Hair of the Dog, no new code as ruled |

**What carries forward unchanged**, per the ruling: Double Stakes and For Keeps
stay one primitive (`_rs*`, built); The Tab stays standalone; Hair of the Dog
needs no new code. Building the system properly means matching the discipline
that produced those findings, not discarding them to make the count look
unified.


---

## BUILT: `matchArmed` (P452)

`RSX`, keyed by card id like `CFX`, and `_rsFire(seam, ev)`. Three cards
registered; the three hand-written stamps are gone.

**No accumulator and no ordering rule, unlike `famFire`.** Its participants
compose — `short_fuse` multiplies what `bloom` adds — which is why `ev.mul` had
to exist. These three write three different flags on `G` and read none of each
other's, so dispatch is the whole job. Adding an accumulator would be inventing
a requirement, which is what the multiplier decision was dropped for.

**A separate table from `CFX` on purpose:** a run-scoped card on the match bus
would be given a lifetime the match bus cannot express, which is the entire
reason this domain exists.

**Verified, 7 checks:** each card fires alone under its own condition, all
three fire together, nothing fires when nothing is armed, and the registry is
exactly the three — because a card silently missing from `RSX` would leave its
flag unset while every other check still passed.

High Table reads `G.rung._highTable` rather than `ev.plays`: it is not
player-armed, it applies whenever the card is owned.
