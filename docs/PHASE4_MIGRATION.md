# Phase 4 — the migration groups, measured 2026-08-03

`tools/cfx_coverage.js` (live) and `tools/cfx_bespoke.py` (static) rerun this.

## Group 1 is a no-op, and that is the useful result

The plan says *"start where partial infrastructure exists, prove the machinery,
then take the hard cases."* Measured, the machinery is already proved:

**All 20 on-bus cards are genuinely on the bus.** Every mention of their ids
outside their own `CFX` entry is the card's `FAM_CARDS` definition, the
`FAM_LIVE` table, or a log string. **Not one has a second implementation.**

That was worth checking rather than assuming, because "has a CFX entry" and
"CFX is where its behaviour lives" are different claims, and a card that is both
on the bus and bespoke elsewhere is the worst case available — the entry makes
it look migrated, so the next change goes into `CFX` while the bespoke half
carries on doing the old thing.

**There is also no drift in the other direction:** zero `CFX` entries that match
no card.

## Group 2 is TEN cards, not nine

The plan lists nine: `bloom`, `cultivate`, `vanguard_f`, `for_keeps`, and the
five tavern cards.

| id | family | kind | live |
|---|---|---|---|
| cultivate | jade | passive | yes |
| bloom | jade | passive | yes |
| vanguard_f | vagabond | passive | yes |
| for_keeps | vagabond | active | yes |
| double_stakes | tavern | active | yes |
| the_tab | tavern | active | yes |
| hair_of_the_dog | tavern | passive | yes |
| marked_table | tavern | passive | yes |
| high_table | tavern | passive | yes |
| **tar_pit** | **amber** | **active** | **no** |

**`tar_pit` is the tenth** and the plan's list cannot see it, because the list
is of *live* cards and `tar_pit` is off `FAM_LIVE`.

This is the group-2 rationale recurring one level down. Group 2 exists because
*"a migration that enumerates the effect table structurally cannot see them"* —
and a list of group 2 that enumerates live cards cannot see `tar_pit`. The card
whose enumeration you trust is always the one that gets left behind. It needs a
`CFX` entry when it goes live, or an explicit note that it is retired.

## Hook usage, for whoever designs the next hook

| hook | consumers |
|---|---|
| canUse | 13 |
| use | 13 |
| bank | 4 |
| bust | 4 |
| turnStart | 2 |
| roll | 1 |
| bankBonus | 1 |

`roll` and `bankBonus` have **one consumer each, and it is the same card**
(`slow_cook`). A seven-hook bus where two hooks serve one card is worth knowing
before an eighth is added.

## Open question before group 2 is built

The plan flags it and it is still unanswered: **the five tavern cards may not
belong on a match-scoped bus at all — they act on the RUN.** Five of the ten are
tavern cards, so this decides half the group. It is in `OPEN.md`.

## Instrument note — six artifacts before the number was real

`cfx_bespoke.py` first reported **18 of 20 cards half-on**. The true answer is
zero. Every one of the six was caught by reading flagged lines rather than the
summary:

1. `\bpreserve\b` matches inside `preserve-3d` — a hyphen is a word boundary, so
   Preserve "had 15 bespoke sites", all of them CSS transforms.
2. Prose in `/* */` comments counted as code: one comment naming "POWDER KEG,
   ENCORE and STEADY HAND" scored three implementations.
3. The `FSIM` harness re-implements scoring **on purpose**, so it can run
   thousands of matches headless. Counting it as drift would have condemned the
   thing that measures drift.
4. `FAM_LIVE.tamper=1` — the live table is written two ways, and only the
   object-literal form was recognised.

The last one is the instructive one: it left **one** survivor out of an original
eighteen, which is exactly when a wrong finding is most believable — it looks
like a careful audit that narrowed to a single real problem.
