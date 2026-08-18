# P5's other half — the opponent already holds cards, and none of them work

`tools/opp_cards_fire.py` reruns this.

## Two stale beliefs, both corrected by reading

**`PROTO_NOTES` says NPC usage lands in P5 with "G.oF stays []".** It doesn't.
`_famInitOpp(rung)` is implemented and deals a boss **1–3 family cards** from
its own family (`BOSS_FAM`), scaling with the night: one card, two from night
4, three from night 7. `G.oF` is populated at match init, line ~22640.

**So the opponent HAS cards.** The question was never whether to give it any.

## Every passive effect the opponent holds is inert

`famFire` iterates `['p','o']`, so an opponent card's hooks are visited. What
happens then turns on one helper:

```js
function _fxMine(ev){return !!(ev&&ev.mine&&ev.owner==='p');}
```

A hook gated on `_fxMine` returns immediately for an opponent-owned card.
Measured across all 44 hooks in `CFX`, restricted to the **passive** ones —
the hooks `famFire` fires for both sides, as opposed to `canUse`/`use`, which
only run when the player taps:

| | count | |
|---|---|---|
| **player-only** | **15** | `bloom.commit`, `cultivate.commit`, `double_or_nothing.bank`, `falling_star.bank`, `fools_gold_f.bust`, `fools_gold_f.deadRoll`, `ill_omen.rivalTurn`, `pickpocket.bank`, `reprisal.bank`, `retort.bust`, `short_fuse.bust`, `short_fuse.commit`, `slow_cook.bankBonus`, `slow_cook.roll`, `vanguard_f.commit` |
| owner-aware | 3 | `short_fuse.turnStart`, `slow_cook.bust`, `slow_cook.turnStart` — all state **resets**, not effects |
| ungated | 0 | |

**15 of 15 real effects are player-only.** A boss is dealt cards, the player is
shown them, and not one of them does anything.

## This is a design question, not a wiring job

Making a hook owner-aware is not `_fxMine(ev)` → `ev.mine`. Each needs a
decision about what the opponent's version *means*:

- **`pickpocket.bank`** lifts points from the rival on bank. Opponent-side that
  is the boss lifting from the player — symmetric, and probably fine.
- **`ill_omen.rivalTurn`** is declared on your turn and pays on the rival's. For
  an opponent-held copy, "the rival's turn" is the **player's** turn. The seam
  exists; which side it fires on is a rule.
- **`double_or_nothing.bank`** already has an NPC implementation elsewhere, in
  the `_npcFamCard` block — so making the CFX hook owner-aware would give the
  boss the effect **twice**.
- **`fools_gold_f.deadRoll`** claims the roll and cancels a bust. An opponent
  claiming its own dead roll changes NPC turn pacing, which the sim is tuned
  against.

That last pair is the reason this is not a sweep: `_npcFamCard` is a **second,
already-live opponent implementation** for `slow_cook`, `retort`,
`double_or_nothing` and `pickpocket`. Any card migrated onto the bus for the
opponent has to be removed from there in the same move, or it fires twice.

**Needs a ruling before building.** In `OPEN.md`.


---

# CORRECTION — "none of them work" was wrong, twice over

Published above: *"the boss holds cards and none of them work"*, resting on
"four cards already have a second opponent implementation". **Both numbers were
wrong, and the headline with them.**

## `_npcFamCard` covers TEN cards, not four

`stargazer, slow_cook, sleight, retort, preserve, pickpocket, ill_omen,
honeytrap, encore, double_or_nothing`. It reads `G.oF` — the opponent's own
family cards — so those ten **do** have opponent behaviour. It lives in a
hand-written NPC path rather than in `CFX`, which is exactly the split P5 exists
to close, but **"not on the bus" is not "does nothing"** and I conflated them.

Where "four" came from: an earlier pass (`cfx_bespoke`) surfaced the
`_npcFamCard` sites that appeared among nine unexplained hits. That was a subset
produced by a *different question*, and I carried its count into a claim about
the whole population without re-deriving it — the same shape as reading
`missing[:6]` as the data.

## The real gap is 13 cards, and it splits by kind

Of the cards a boss can actually be dealt (live, in a boss family), these have
no NPC path and no opponent-firing hook:

| kind | cards | what they need |
|---|---|---|
| **passive** (6) | `bloom`, `cultivate`, `reprisal`, `falling_star`, `vanguard_f`, `fools_gold_f`\* | just to **fire** — the hook exists and is gated player-only |
| **active** (7) | `transmute`, `powder_keg`, `sacrifice`, `steady_hand`, `fair_trade`, `tamper`, `for_keeps` | an **AI decision to use them** — an NPC never taps a card |

\* `fools_gold_f` is `kind:'active'` but its effect is on `deadRoll`/`bust`,
which fire automatically — so it behaves like a passive here.

**That distinction is the actionable one and I did not have it before.** Six
cards need a gate changed. Seven need `_npcArmActives` taught when a boss should
*choose* to play them — a genuinely larger job, and one nobody has scoped.

## What stands from the original finding

The bus split is real: the opponent's working cards work through a parallel
hand-written path, not through `CFX`, and migrating any of the ten means
removing it from `_npcFamCard` in the same move or it fires twice. That part
was right. The size and the headline were not.


---

# SECOND CORRECTION — the six-passive ship is not viable, and why

Authorised: ship the six passive cards as gate changes (`_fxMine` -> fires for
the owner). **Writing it disqualified it**, which is the third time today that
step has changed the answer.

## Seven of the eight seams are never raised for the opponent

Every `famFire` call site, with its actor:

| seam | actor |
|---|---|
| `bank` | **`'o'`** (28552) and `'p'` (26791) |
| `bankBonus`, `bust`, `commit`, `deadRoll`, `rivalTurn`, `roll`, `turnStart` | `'p'` only |

`famFire` iterates **both** rosters regardless of actor, and sets
`ev.mine = (ev.actor === owner)`. So an opponent card's `turnStart` hook *is*
visited — on the **player's** turn start, with `mine=false`. Ungating it would
not make it fire at the right moment; it would make it fire at the **wrong**
one.

**So four of the six are no-ops and two are the wrong shape:**

- `bloom.commit`, `cultivate.commit`, `vanguard_f.commit` — `commit` is raised
  only from `famCommitBonus`, which is the player's scoring path. Ungating
  changes nothing.
- `fools_gold_f.bust` / `.deadRoll` — same, `'p'` only.
- `reprisal.bank`, `falling_star.bank` — these two DO sit on the one seam the
  opponent raises. Ungating them would fire something, and what it should do
  when a boss banks is a design question, not a gate flip.

## The real gap is seam coverage, not gating

The opponent turn machinery raises **one** of eight CFX seams. That is why
`_npcFamCard` exists at all: with no seams, the only way to give a boss card
behaviour was to hand-write it in `runOppTurn`, which is exactly what someone
did for ten cards.

**So "make the opponent's cards work" is not a card-by-card migration. It is
raising the other seven seams from the opponent's turn at the moments that
correspond** — an opponent `turnStart`, `roll`, `bust`, `commit`. That is
infrastructure, and it is the thing `_npcArmActives` and boss personality would
both hang off once it exists.

**Not built. Not shipped.** The authorisation was for gate changes, and gate
changes turn out not to be the thing.


---

# Two things worth keeping, independent of the seam question

## The live game is MORE levers-ready than the sim that measures it

Asked whether NPC decision-making is tunable or hardcoded per-agent. Measured,
it is layered:

| layer | shape |
|---|---|
| loadout & targets | **levers** — `patronStats{targetMin/Max, aggMin/Max, dicePool, minBank, diceStop}`, per tier |
| persona | **levers** — six of them, each `{tags, dieBias, behavior}` |
| turn AI | **one lever, three settings** — `behavior` is read once (line ~27028) and moves one number: `safe` −0.10 agg, `chase` +0.10, +0.12 more if a pair is showing |
| card play | **no levers** — `_npcArmActives` is hardcoded `if` chains |

**And the sim roster is the more hardcoded of the two.** `F.POLICIES.carl =
mkPolicy({name, thresh, keep:function(f,c){…}})` — each agent's personality is a
**hand-written `keep` function**, not parameters. The live game's personas carry
more structure than the agents measuring them.

**Worth remembering the next time the sim roster is touched:** it is not a
neutral measuring stick against a less-structured game. On this axis it is the
less-structured of the two systems, and a sim agent cannot currently express a
persona the live game already can.

## The ordering, which holds whatever the size turns out to be

**Seam coverage is upstream of both boss card-play and persona levers.**
Neither can be built on top of one seam. `_npcArmActives` gaining an AI, or
`behavior` widening past three values into real card-play personality, both
need the opponent's turn to raise the moments those decisions attach to.

No size attached, deliberately: this area has had two wrong size estimates from
me today, so a third carries no more weight than the first two. The **shape** is
what is established — the ordering above does not depend on the number.


---

# DIRECTION (ruled) and the first two seams (P459)

**Give bosses the same seven turn hooks the player has**, so they act through
the same structure — not full player complexity, just the same levers a player
pulls, set differently per boss.

**Build the seams first, confirmed working generically, before any personality
attaches to them.** Designing both at once means writing boss-specific
behaviour into the seam code, which is the bespoke-per-card trap this project
has been removing everywhere else. Once seams exist, differentiation is **data
on each boss's existing persona record** — `patronStats`, `dieBias`, and
whatever card-play dials get added — **not new logic per boss**.

## Built: `turnStart` and `roll`

The two POINT seams, at the single site each where the opponent's counters
advance:

| seam | site | raised |
|---|---|---|
| `turnStart` | `G.oppTurnCount=(G.oppTurnCount||0)+1;` | immediately after |
| `roll` | `_oppHoldKept();oppRollNum++;` | immediately after |

**After the increment, both times** — a hook asking "which turn is this" must
see the turn it is about. Firing before would hand every opponent hook the
previous index, which is the off-by-one that made Snuff's window meaningless
until Phase 3 gave it a gate.

**Neither call carries anything boss-specific.** They raise the moment and
nothing else, per the direction.

**And no card was ungated.** Every CFX hook still tests `_fxMine` and still
returns early for an opponent. Verified: on a real rival turn both seams raise,
the player's own seams are untouched, and **zero cards changed behaviour**.
That last check is the one that matters — the correct outcome here *is* no
effect, so the probe counts seam raises by wrapping `famFire` rather than by
watching for consequences.

**Remaining five, unchanged:** `commit`, `bust`, `bankBonus` are SPREAD (7, 7
and 12 sites across 425, 229 and 885 lines) and need the "which moment is the
seam" decision; `deadRoll` has no counterpart at all; `rivalTurn` means the
player's turn when a boss holds the card.

---

## 2026-08-18: THE RULING LANDED (P761/P762)

Denis: "they should be able to use ALL of the same things I can use."
famUse(i, actor) + NPC_FAM_READY are the pipe and the tracker; preserve,
slow_cook, pickpocket and double_or_nothing are through it with their
bespoke copies deleted (the double-fire this doc warned about). The
rival bankBonus seam also consumed no delta - fixed. Remaining sweep
order: docs/NPC_AI_BRIEF.md section 7.

