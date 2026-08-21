# Lifting the `generateOppCards` stub — sized. It can lift cleanly.

Ruled: lift it. The body below `return [];` is already written — 22 lines that
build a pool, shuffle, pick `n`, and guarantee a boss's signature card. So the
question was never *how to write it*, but **whether it still references a world
that exists**. Rerun with `tools/oppcards_size.py`.

## Answer: yes, on all four checks

| check | result |
|---|---|
| **Every pooled id resolves** | **41 of 41** present in `NPC_CARDS` (42 defined) |
| **Fields the dead code reads** | `rung.key`, `cardCount`, `cardChance`, `S.npcWonCards` — all present |
| **`start_bonus` cards** (8 of the 41) | handled at three sites — they use `effect.type`, not `mechanic` |
| **`steal_on_bust`** | handled, **by card id** rather than by mechanic |

**Nothing blocks the lift.** Deleting the `return [];` line is the whole change.

## Two things found while checking, neither blocking

**1. `block_low_bank` has branches but no card carries it.** The mechanic is
implemented on both seats — and was tabulated last session — yet **no card in
`NPC_CARDS` declares it**. Dead in the opposite direction from everything else:
implemented, never dealt. Either a card lost the mechanic or it was never given
one.

**2. Three comments misattribute behaviour to `iron_gate_npc`.**

| line | comment says | truth |
|---|---|---|
| 25017 | *"reroll one scoring die (uses:2)"* | not Iron Gate at all |
| 26247 | *"Block opp's low bank (iron_gate_npc)"* | Iron Gate is `steal_on_bust` |
| 26776 | *"Block low bank (iron_gate_npc)"* | and `block_low_bank` has **no** card |

Worth fixing because they point the next reader at the wrong card for a mechanic
no card has — the same shape as `mabels_pinch`/`the_nightshift` last session,
where a plausible name beside the right numbers survived a whole patch.

## And a ninth instance of the session's pattern, in my own sizing

My first pass reported **1 orphan mechanic** — `steal_on_bust` with no dispatch
branch. It has no `mechanic===` branch and works perfectly: it is wired by card
id. **The scan measured dispatch STYLE and I read it as "does the card work".**

The same pass also reported *"8 cards with no mechanic"* — they use
`effect.type:'start_bonus'`, so it was reading the wrong field. And the earlier
loose version said *"16 mechanics, 0 orphans"* where the tight one found 24;
the clean sweep was partly an artifact of matching any `id:` object rather than
the real registry.

Three wrong readings, each caught by tightening one step further. **The final
answer is the reassuring one, but only the fourth measurement earned it.**

## What follows the lift

Once patrons hold cards, the two ungated seams — `commit` and `deadRoll` — are
in the same domain and worth scoping together, since neither matters until a
patron holds a card that can use them.

**And the lift makes bosses meaningfully stronger** — it switches on the three
patron-favouring mirror mechanics plus every `start_bonus` (up to +3500 for
Whisper). That is a third difficulty change on an axis that already has two
this session, per `OPEN.md` §6. It should land with a same-seed before/after.

---

## The step this sizing was missing

Everything above measures what the dead code **references**. It never asked
**what references the stub** — and `apv_legacy_retired` asserted the stub must
hold, with a written rationale, in the suite being run all session. It went red
on the next run.

**Standing step for any future stub / guard / early-return removal:** grep the
name across `tools/` and `docs/` before touching the body. *"What does this
depend on"* and *"what depends on this"* are different questions, and the second
is where deliberate decisions are recorded — guards, asserts, probes, and
comments explaining why something is the way it is.

Ruled after the fact: `NPC_CARDS` and `CARDS` are different rosters, current and
retired; the two delivery mechanisms are not exclusive; and the invariant is
**`nothingOldHeld`**, not `opponentStubHolds`. The stub was one disposable
enforcement of a rule that had a more durable form once named directly.
