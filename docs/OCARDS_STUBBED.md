# `generateOppCards` returns `[]` — the patron's card layer is off

Found while asking why wiring the sim's card effects changed nothing. Three
identical five-seed runs in a row was the tell.

## The fact

```js
function generateOppCards(rung,playerCardCount){
  return [];/* P1 cutover: NPC family cards land in P5 */
  ...                       // ~30 lines of dead code below
}
```

**Verified in a live match**, not inferred: `G.oCards.length === 0`,
`G.oF.length === 1`. The *family*-card layer (CFX, `G.oF`) works. The
**`oCards` layer is switched off** pending P5 — which is the very work this
session has been building toward.

## What that means for tonight's mechanic-table work

Every one of the nine mirror mechanics exists **twice**: an `oCards` copy and a
`pCards` copy. So for each:

| copy | reachable today |
|---|---|
| `G.pCards` — the player's cards | **yes**, once the player holds cards |
| `G.oCards` — the patron's cards | **no** — the list is always empty |

And three mechanics are `oCards`-only, so fully unreachable in this build:
**`swap_die`, `steal_die`, `block_activations`.**

**This does not make the fixes wrong.** `BANK_FX`, `BANK_TAKE`, `SCORE_DRAIN`,
`BUST_FX`, the `challenge` double-charge and the `ill_omen` mirror are all
correct, and they are what P5 will switch on. **It does mean I described some of
them as live gameplay bugs without checking they could execute** — the
reachability question I have a standing rule about, skipped on the very finding I
called the session's best result.

**Which specific fix landed on a live copy versus a dead one is not yet audited
per fix.** That is the honest next step, and it is a real one: the `challenge`
double-charge was fixed on `finOpp`'s branch, which the enclosing-list
measurement puts on `pCards` — plausibly live — while its `handleBank`
counterpart may be the dead `oCards` copy. **Plausibly is not measured.**

## And it clears the sim

`OPEN.md` §5b said the sim couldn't be trusted because it ran no patron card
effects. It ran none **because there are none to run** — in the sim *and* in the
game. On this axis the harness was faithful all along.

That is the fourth correction to that finding, each narrowing it:

1. "patron punishes but cannot help itself" — wrong, both seats' cards are involved
2. "understates patron strength" — wrong direction, six of nine favour the player
3. "the branches need untangling" — wrong unit, statements not lines
4. **"the sim omits card effects the game has"** — the game does not have them either

**P470/P471/P472 remain correct and are now prerequisites for P5** rather than
fixes to a live gap. P472 in particular — calling `generateOppCards` instead of
reading a `rung.cards` field that no rung has — is a real latent bug fixed, it
just cannot change a number until the stub above it is lifted.
