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

## 3. Ward — THIS SECTION WAS WRONG, and it is the useful kind of wrong

**What it said:** four state variables and expiry in two functions, so Ward's
retirement is a distributed convention, the strongest case for the primitive,
and the worked example.

**What is actually true:** `_ward` is a PREFIX shared by three unrelated
features, and the audit grouped by name.

| variable | what it is | lifetime? |
|---|---|---|
| `_wardArmed` + `_wardBoost` | the Ward **enchant** — armed on your turn against your bust | one turn |
| `_wardCharges` | the `warded` **card**'s charge pool — saved in `saveMatchState`, restored in `initMatchScreen` | none, it persists |
| `_wardBanks` | a counter in `handleBank` paying a bonus every third bank | none, not a lifetime |

And the two expiry sites are **both correct**: `doBust` is *consumed* — the save
paid out — and `startPTurn` is *expired* — a new turn began without a bust. An
armed-for-one-turn state that can be spent needs exactly those two, and merging
them would lose the difference between "it worked" and "it never came up".

**So there is nothing distributed to fix.** Ward's window is coherent; what it
lacked was a sentence saying so, now at the arm site.

**This is the fourth instrument-derived false finding today and the only one
that reached a design doc** — it named a worked example and recommended
restructuring something already correct. Which is precisely the compounding
cost: a missed finding waits to be found, a manufactured one gets built on. It
was caught by reading the sites rather than the summary, the same way as the
other three.

Ward is also **not a lane marker** and must not go on `_lmArm`/`_lmDue`: no
lane, no opponent turn, armed against your own bust.

## 4. What Phase 3 has to cover

1. **A lane-marker lifetime** — `{lane, live, turn}` with the window gate
   enforced rather than optional. Fixes snuff by construction.
2. ~~Ward's armed window~~ — **withdrawn.** Measured properly, it is coherent;
   see §3. The only work it needed was naming, which is done.
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

Each error made the tool report *more* findings than were real, and all three
made the markers look **less coherent than they are**.

**A false positive is not merely worse than a false negative — it is worse in a
way that compounds.** A missed finding sits there waiting to be found later. A
manufactured one *gets acted on*. Any one of these three, landing unchecked in a
design doc, would have shaped Phase 3 around a problem that does not exist — and
the design would then have code embodying it, at which point the cost is a
rewrite rather than a corrected sentence. There is no prompt to go back and
re-check a finding you already believe.

Today's other instrument error ran the same direction: the font probe's first
pass "found" overflow on dice containing no text. Both were caught the same way
— by reading the lines the tool was describing rather than the tool's summary of
them.
