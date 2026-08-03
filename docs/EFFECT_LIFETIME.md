# Effect lifetime — measured, 2026-08-03

Phase 3 groundwork. `tools/effect_lifetime.py` reruns all of it.

Phase 3 settles effect lifetime. The re-plan names five things that have one:
Ward's armed window, and *"four enchants (Snare, Snuff, Fog, Trade) are lane
markers with a placement, a window and an expiry rather than effects with a
moment."*

**Measured, that grouping is wrong in one place and there are three shapes, not
two.** Trade is not a lane marker.

| | placement | window read in | expiry | shape |
|---|---|---|---|---|
| **snare** | 1 | `step` ×5 | `step` | lane marker |
| **snuff** | 1 | `runOppTurn` ×7 | `runOppTurn` | lane marker |
| **fog** | 1 | `step` ×8 | `step` | lane marker |
| **trade** | 2 | `_tradeRestore` ×3, `saveMatchState` ×2, `_tradeSnap` ×2 | `_tradeRestore` | **transaction log** |
| **ward** | 4 | `_consumeWard` ×3, `doBust` ×2, `handleBank` ×2, … | `doBust` ×2, `startPTurn` | **charge counter** |

## 1. The three real lane markers share an idiom — and one doesn't honour it

All three are armed identically:

```js
G._snare = {lane:c.lane, live:true, turn:(G.oppTurnCount||0)+1, …};
G._snuff = {lane:c.lane, live:true, turn:(G.oppTurnCount||0)+1, …};
G._fog   = {lane:c.lane, live:true, turn:(G.oppTurnCount||0)+1, …};
```

`turn` **is** the window: the specific opponent turn this is armed for. Two of
the three gate on it. One does not.

| | reads `.turn` | sets `.turn` | gate |
|---|---|---|---|
| snare | 1 | 1 | `live && turn===oppTurnCount` |
| fog | 1 | 2 | `live && turn===oppTurnCount` |
| **snuff** | **0** | **2** | `live` only |

**Snuff writes a window field it never reads.** It sets `turn` at placement and
again on the Kindred re-arm, and no line anywhere compares it to anything.

**This is not a demonstrable live bug, and it matters anyway.** `oppTurnCount`
increments at 26944, *before* the snuff check at 26956, and placement always
arms for `+1` — so in the normal path `live` alone lands on the same turn the
gate would have selected. The divergence is in what happens when that path is
not normal: if an opponent turn is ever entered without `oppTurnCount` matching
the armed value — a resumed save, a placement made during the opponent's own
turn — snare and fog decline to fire and snuff fires anyway.

So: **one idiom, three implementations, two of which are guarded.** That is
precisely the pattern the effect-system plan exists to remove — *"no shared
definition of a check, so two places drifted"* — and Phase 3's lifetime
primitive is the thing that makes it unrepresentable rather than merely fixed.

*Deliberately not fixed here.* Making snuff honour `turn` is a one-line change
and it is a **behaviour** change, on the enchant whose Kindred form holds a seat
for two turns. It belongs in Phase 3 with the primitive, not as a drive-by.

## 2. Trade is not a lane marker

`G._tradeSwaps` is an **array of swap records**, and `_tradeRestore` unwinds it
newest-first *"so two swaps in one lane unwind in the order they were made"*.
There is no `live`, no `turn`, no window. It has a placement and an undo, and it
lasts until something restores it.

It also snapshots into `S.pendingMatch` (`_tradeSnap`), which none of the lane
markers do — its lifetime crosses a save.

**A lifetime primitive designed from the three lane markers and applied to Trade
would impose a window on something whose whole design is that it has none.**
This is the `_fxFreeDice()` lesson from Phase 2, one layer up: four things that
share a name are not four instances of one thing.

## 3. Ward's lifetime is a convention spread across three functions

Four state variables (`_wardArmed`, `_wardCharges`, `_wardBanks`, `_wardBoost`)
and **expiry in two different functions** — `doBust` twice, `startPTurn` once.

Every other marker here retires in exactly one place. Ward's "when does it end"
is currently distributed, which is the definition the re-plan asks Phase 3 to
name. It is the strongest case for the primitive and should be the worked
example.

## 4. What Phase 3 has to cover

1. **A lane-marker lifetime** — `{lane, live, turn}` with the window gate
   enforced rather than optional. Fixes snuff by construction.
2. **Ward's armed window**, currently spread across three functions.
3. **Trade excluded, explicitly and in writing**, or the next reader re-derives
   it from the plan's own sentence and forces a window onto it.

## Instrument note

`tools/effect_lifetime.py` needed **three corrections**, each caught by reading
the lines it was describing:

1. It reported "NO EXPIRY SITE" for all three lane markers. It recognised only
   `G._fog = null`; these markers retire by flipping a field (`G._fog.live =
   false`).
2. `.turn` without a word boundary also matched `.turns` — a different field
   (the Kindred two-turn counter).
3. `(?!\s*=)` for "not an assignment" also rejected `===`, so **comparisons were
   counted as writes** and all three markers looked like they never read their
   own window field.

Each error made the tool report *more* findings than were real. An instrument
whose failure mode is manufacturing findings is more dangerous than one that
misses them — the false alarms are the interesting-looking part, and there is no
prompt to go and check them. Both today's other instrument errors were the same
direction: the font probe "found" overflow on dice containing no text.
