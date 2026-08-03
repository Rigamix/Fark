# Phase 4 — the migration groups, measured 2026-08-03

`tools/cfx_coverage.js` (live) and `tools/cfx_bespoke.py` (static) rerun this.

## CORRECTION (same day): group 1 is NOT clean

**The section below was published saying all 20 on-bus cards are clean. That is
wrong and it is retracted.** At least one card is genuinely half-on:

**`short_fuse` sits on `CFX` for `turnStart` and `bust`, and its x2 is
hardcoded in `famCommitBonus`** (line 13493, `famInst('short_fuse')`). Read by
eye, not inferred.

**Why the check missed it.** It classified any line where the id appeared inside
quotes as a log string. `famInst('short_fuse')` is quoted — and it is a lookup,
not a log. **The seventh instrument artifact of the day and the first false
NEGATIVE.** The other six invented work; this one hid it, which is worse here,
because a clean result *ends the investigation* and an invented one gets checked.

It also fits the pattern exactly as described: a number that visibly narrowed
from 18 to 1 to 0 reads as diligence — each correction looking like the process
working — and that earned trust the final answer had not separately earned.

**What is now established, all eye-verified:**

- `short_fuse` is genuinely half-on. Real.
- `_npcFamCard(...)` sites are the **opponent-side** implementation, separate by
  design — `PROTO_NOTES` has NPC usage landing in P5 with `G.oF` empty until
  then. Not drift.
- `pickpocket` in `_SEAL_POOL` is a **name collision**: the sealed-seat table
  rule and the vagabond card share a string and are unrelated. The same trap as
  Ward's shared prefix, one level down.

**What is NOT established: the final count.** After separating those two
categories, nine cards still show sites needing to be read individually. That
work is not done, and no migration has been built on any of it.

## ~~Group 1 is a no-op~~ — RETRACTED, see above

The plan says *"start where partial infrastructure exists, prove the machinery,
then take the hard cases."* Measured, the machinery is already proved:

~~**All 20 on-bus cards are genuinely on the bus.**~~ **RETRACTED.** The claim
rested on treating every quoted id as a log string; `famInst('short_fuse')` is
a lookup. At least `short_fuse` has a second implementation.

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
