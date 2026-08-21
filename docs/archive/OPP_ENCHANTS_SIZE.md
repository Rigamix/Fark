# Opponent enchants — sized, and a live bug found on the way

Ruled: the pricing gate is gone, so opponent-side enchants are unblocked. Sizing
first. `tools/npc_selection_size.py` and the measurements below.

## The plumbing is small. The DATA is a design question.

| | |
|---|---|
| `scoreRoll` already accepts `dieEnchs` | 8 references |
| the player's `_enchArr` | 47 references |
| **an opponent enchant array** | **0** |
| rival `scoreRoll` calls passing `dieEnchs` | **0 of 6** — all pass 5 args |

So the engine applies per-die enchants already; there is simply no opponent
array and the six rival call sites drop the parameter. **That part is an array
and six arguments.**

**What is NOT decided is where an opponent's enchant would come from.** The brief
makes enchants an innkeep service the *player* buys. Nothing grants one to a
patron. The candidates — patron generation, boss relic dice, or arriving only
via For Keeps and Trade — are a design choice, and building the plumbing without
it would be inventing the feature rather than enabling it.

## A hypothesis that turned out wrong, recorded so it is not re-tried

I expected Trade to be silently dropping the enchant when a die crosses to the
opponent. **It does not.** `myEn` is read, stored in `_tradeSwaps` for restore,
and `G._enchArr[L]=null` clears the player's — with a comment stating the intent:
*"The brand leaves with the die — that is what makes Trade self-consuming."*
Deliberate, and handled.

## But Trade handles it because someone thought about it. Three paths did not.

**Only one place in the file splices `_enchArr` alongside `G.matchDice`** —
L18782, Break's die removal. Three others remove a die and leave the enchant
array untouched:

| site | reached by | effect |
|---|---|---|
| L24255 | **`royal_seizure`** (Whisper) | `steal_die` / `take_best` |
| L24262 | **`blessed_confiscation`** (Ambrose) | `steal_die` / `take_and_use` |
| L13979 | Sacrifice | obsidian shatter |

`_enchArr` is indexed by lane. Splicing `matchDice` shifts every lane above the
removed one, so **every enchant above that lane now applies to a different die**.
Silent: no error, no message, the brand simply moves to a neighbour.

Both `steal_die` cards are pooled and live. This is not a design question — an
enchant applying to the wrong die is wrong under any reading.

**Not fixed here.** The `steal_die` sites record the enchant in `G._diceOut` for
restore at match end, so the fix has to splice the live array *without* breaking
that restore — and that restore path has not been read yet. Reading it is the
next step, not a guess.
