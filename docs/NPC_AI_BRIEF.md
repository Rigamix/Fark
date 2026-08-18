# NPC Play Brief — audit, research, and the rework plan

*2026-08-18. Commissioned after three sightings: a cardless NPC ignoring a
straight to keep a single 1; an NPC banking a 1 while a 1 and 5 sat
bankable; an NPC ignoring a straight and banking a lone 5.*

---

## 1. The audit — all three sightings are real, and they share one root

### What the code does today (the live match, not the sim)

Every NPC roll runs this sequence (`fark_proto.html`, the `step()` loop
around 34300–35030):

1. `_scoreRollBest` scores the roll maximally → `total`, `used[]`.
2. `_oppChooseFrom` → `_legalKeeps` enumerates **every legal subset**
   (powerset through the real scorer — straights included, this part is
   sound) → `_npcChooseKeep` picks one **by persona style rule**.
3. A separate "strategic release" block may then un-keep "optional
   singles" for reroll volume.
4. `oppShouldBank` decides bank-or-roll **after the keep is final**.

### Sighting 1 — kept a single 1 off a straight *(persona: aggro)*

`_npcChooseKeep`'s aggro rule (~16560):

```js
pick=c.sort(function(a,b){return (b.left-a.left)||(b.pts-a.pts);})[0];
```

Maximum dice left = **always the minimal scoring keep**. Candidates for a
straight roll include the full straight (1500) and a bare 1 (100); aggro
picks the bare 1 because `left=5` beats `left=0`. No term anywhere asks
what the discarded 1400 was worth. Finnick is fixed-aggro, and generated
patrons roll personas — so cardless patrons show this constantly.

### Sighting 2 — banked a 1, left a 1 and 5 on the table

Structural: the keep is chosen for *style* first, and `oppShouldBank`
runs **after** with no power to revise it. When the style keep is minimal
and the bank verdict is "stop", the NPC banks the minimal keep and the
rest of the scoring dice evaporate. Keep and bank are one decision being
made as two, in the wrong order.

### Sighting 3 — ignored a straight, banked a lone 5

Two paths produce it:
- the aggro/minimal keep followed by a bank verdict (as above), and
- the **release block** (~34790): it frees kept 1s/5s whose face-count
  is < 3. Its own comment says *"not part of a triple/straight"* — but
  the code only checks triples. A kept straight's 1 and 5 each count
  once, so the block happily rips them out of the straight **and refunds
  a flat 100/50 against dice that scored as part of 1500** — breaking
  the hand and drifting `oppBank` at once.

### Adjacent findings

- The release block is a **second chooser fighting the first**: persona
  picks a keep, then this block re-litigates it with its own randomness.
  Two deciders, no shared value model.
- `oppShouldBank` is actually rich (personas, gap context, huge-bank
  locks at 1500/2000/3000, desperation caps) — but it can only bless or
  push *whatever keep it was handed*.
- The only EV instrument in the file, `_npcEvTable` (measured per-loadout
  bust/gain per dice count), is consulted by **one persona out of six**
  (combo). Everyone else follows a blind rule.

**Verdict: the candidate generator and the scorer are sound. The choice
layer is style-with-no-value-floor, split across two uncoordinated
deciders, with the bank verdict bolted on afterwards.**

---

## 2. The research — what the established knowledge says

### Farkle EV theory (the solved-game literature)

- Optimal play evaluates each candidate keep as
  **EV(keep) = pts + P(no-farkle | left) × E(gain | left)** against
  **bank = pts**, using bust/gain tables per dice-remaining. Busche &
  Neller solved the full game this way; McKenna's tables give the
  practical shape: with 3 dice, rolling is right at 250 banked
  (EV 293) and wrong at 500; farkle odds run ~2.3% at 6 dice,
  ~15.7% at 4, ~27.8% at 3.
- **Minimal keeps are legitimately optimal in places** — "1 2 2 2 5 4:
  keep the 1, roll five" beats holding the triple 2s. So aggro's
  *instinct* is real Farkle strategy; what's missing is the EV
  comparison that separates that case from discarding a straight.
- Practical banking heuristics: bank when turn points ≥ ~2× the next
  roll's EV; near-always bank at 1000+; end-game overrides everything —
  when the opponent can win next turn, "maximize points" becomes
  "maximize P(win)", i.e. push past normal thresholds.

### Believable-NPC doctrine (game AI practice)

- **Mistakes must be in-character, not random.** Players forgive "Brutus
  would do that" and resent noise. A persona should *bias* a sound
  value function, never replace it.
- **Plausible threat, learnable pattern**: the NPC should be readable
  enough to strategize against — fixed personalities with visible
  tendencies are a feature, invisible coin-flips are not.
- **Bounded imperfection**: shipped AIs are deliberately capped versions
  of a competent core (the "never suicidal" floor), not independent
  rule piles that can each go insane in its own way.

Sources:
[Busche & Neller, *Optimal Play of the Farkle Dice Game*](https://www.mattbusche.org/downloads/farkle/optimal-play-farkle.pdf) ·
[McKenna, *Optimal Strategy for Farkle Dice*](http://www.ryanhmckenna.com/2018/07/optimal-strategy-for-farkle-dice.html) ·
[Perrotta, *Solving Farkle*](https://mikeperrotta.medium.com/solving-farkle-c5f96130e230) ·
[GDKeys, *AI: Keys to Believable Enemies*](https://gdkeys.com/ai-keys-to-believable-enemies/) ·
[Ubisoft, *The Art of Feigning Intelligence*](https://www.ubisoftsingapore.com/post/the-art-of-feigning-intelligence-ai-and-video-game-npcs)

---

## 3. The design — one competent core, personas as flavour on top

### One joint decision, not three

Replace {persona keep → release block → bank verdict} with **one
evaluation over the same candidate list `_legalKeeps` already builds**:

```
for each candidate keep k:
    ROLL value  = k.pts + (1 − bust[k.left]) × gain[k.left]   ← _npcEvTable
    BANK value  = k.pts                       (only when bank is legal/sane)
score both options for every candidate, apply persona WEIGHTS, pick the
argmax (keep, action) PAIR.
```

- Banking automatically implies the max-pts keep — sighting 2 becomes
  impossible *by construction*, not by patch.
- The release block **is deleted**: "keep fewer, reroll more" is exactly
  what the ROLL branch already prices. One decider.
- `oppShouldBank`'s good context (score gap, huge-bank locks, last-licks
  desperation, handicaps) survives as **modifiers on the BANK/ROLL
  values**, not as a second gate.

### Personas become weights and tie-breaks on a sound core

| persona | today | becomes |
|---|---|---|
| aggro | always-minimal keep | ROLL value × ~1.15, EV-slack tolerance (may take a keep within ~10% of best EV with more dice live) |
| ones/safe | banks early via agg | BANK value × ~1.1, slack toward fewer-risk keeps |
| triples | rule + splitsGroup guard | bonus weight on keeps holding pairs/triples (chasing), guard kept |
| straights | rule (runs first) | bonus weight on keeps preserving/extending runs |
| hoard | maximal keep | slack ≈ 0 (plays the book) |
| combo | already EV | the core itself, weights ≈ 1 |

Style shows in *which good option* they take — never in taking a bad one.

### The never-suicidal guardrails (hard, persona-proof)

1. **Never discard a made hand**: no keep may be chosen whose EV trails
   the best candidate's by more than the persona slack (slack capped
   ~10–15%). Discarding a straight fails this by a mile, always.
2. `splitsGroup` stays (never break a made set) — extend it to runs of 5+.
3. Huge-bank locks stay (1500/2000/3000 tiers).
4. **Endgame override**: if `oppTotal + bank ≥ target`, bank. If the
   player is on match point, the required-points calculation overrides
   persona (push exactly as far as needed, no further).
5. Bust math must balance: any un-keep re-scores through the real scorer
   — no flat refunds, ever (that's the sighting-3 drift).

### Verification exists already

`?sim=1` (`playMatch`, policies, TIERS) is the instrument: run old vs
new chooser per persona over thousands of matches. Acceptance: mean
points-per-turn up for every persona; zero occurrences of "chosen keep
EV < best−15%"; personas still measurably distinct (keep-size and
bank-turn distributions stay separated).

---

## 4. The parity architecture — one pipeline, an `actor` parameter

Denis's rule: *"Me playing a card and them playing the same card should
be the same code bit with just the actor being different."* Where the
code stands against that today:

### Already shared (the pattern to extend — it works)

| action | shared mechanism |
|---|---|
| commit bonus | `famCommitBonus(sel,total,actor)` — one seam, both seats |
| passive card hooks | `famFire(hook,ev)` routes to `G.pF` **and** `G.oF` by owner; effects test `_fxMine(ev)` |
| bust visual | `D3X.bustBeat(side)` |
| keep legality | `_legalKeeps(free, actor, …)` |
| dice throw/settle/dim | one D3X path, seat-agnostic |

### Divergent (the debt)

| action | player | NPC | gap |
|---|---|---|---|
| **active card use** | `famUse(i)` → `CFX[id].use(inst)` + FKFX + charges | `npcHasActive`/`npcUseActive` + `getNpcCard(id).effect.mechanic` + inline handlers scattered through `step()` (second_wind, double_down, bust saves…) | **two whole card systems** |
| bank resolution | `handleBank` | `finOpp` | twin dispatch tables (known; mirror_diff audited them once) |
| turn driver | player input → `handleRoll`/`handleBank` | `step()` monolith | NPC "hands" are inlined, not actions |

### The target shape

```
ACTIONS (actor-parameterized, one implementation each):
  act.roll(actor)  act.keep(actor, selection)  act.bank(actor)
  act.playCard(actor, instRef)      ← famUse generalized: CFX effects
                                       read ev.owner, never G.pF directly
POLICY (the only place 'p' and 'o' differ):
  player policy = the UI (taps, drags)
  NPC policy    = the EV core + persona weights (§3)
```

- **`famUse(actor, i)`**: resolve the instance list by owner
  (`G.pF`/`G.oF`), run the *same* `CFX` effect, play the *same* FKFX on
  the rival's card element, decrement the same charges. The CFX
  handlers that reach for player globals get the actor from the event —
  the pattern `_fxMine`/`ev.owner` already established for passives.
- **NPC legacy actives migrate onto CFX rails** card by card (the
  `getNpcCard` mechanics table becomes data for the same engine), so
  "should Brutus play Preserve?" is one policy lever
  (`policy.wantCard(inst) → act.playCard('o', inst)`) and the *effect*
  is byte-identical to the player's, upside down.
- This is the standard **command/action layer** every card engine
  converges on: effects are actor-agnostic commands; AI and input are
  two producers of the same commands. Not invented here — adopted.

---

## 5. Phasing (each lands alone, sim-gated)

1. **Stop the bleeding** — guardrail the current chooser: EV-slack floor
   over `_legalKeeps` (kills sighting 1/3 keeps), delete the release
   block (kills the straight-breaking and the refund drift), bank
   implies max-pts keep (kills sighting 2). Small diff, sim-verified.
2. **The joint decision** — fold `oppShouldBank`'s context into the
   candidate evaluation; personas become weights (§3). Sim A/B per
   persona.
3. **The action layer** — `famUse(actor,…)`, `act.bank` unifying
   `handleBank`/`finOpp` behind one dispatch, NPC legacy actives onto
   CFX rails one card at a time.
4. **Card policy levers** — per-card `wantCard` heuristics for the NPC
   (only after 3, so each lever is one function, not a subsystem).

---

## 6. Status

**Phase 1 SHIPPED (P760)** - verified against the live decision layer:
- EV floor (NPC_MAX_GIVE=500) over `_legalKeeps` in `_oppChooseFrom`:
  all six personas now keep a rolled straight (give-up 0); aggro still
  keeps 1 die vs hoard's 2 on a singles roll (identity intact).
- Bank plan: the bank question is asked FIRST against the max-pts keep;
  verdict stashed with its base and reused at the bank site when nothing
  changed the numbers. Probe: near target, aggro's pick was the max keep.
- Release block deleted (the straight-breaker with the flat-refund
  drift).
- Full-route smoke: five runOppTurn turns - 4 banks (2050/400/1650/850),
  1 bust, no page errors.

**Finding for the record:** the `?sim=1` harness never runs the persona
chooser - `simTurn` always keeps the maximal scoring set - so the sim
was structurally blind to every bug in this brief. Phase 2's acceptance
runs must either drive the live `_oppChooseFrom` (as the P760 probe
does) or first teach `simTurn` to call it.

**Next: phase 2** (fold oppShouldBank's context into the candidate
evaluation; personas as weights), then the action layer (§4/§5).

---

## 7. The pipe - migration inventory (P761/P762)

Denis's ruling: **ALL of it - cards, enchants, special dice - through the
same pipe.** `NPC_FAM_READY` in the code is the registry and the honest
tracker: a card is offered to the rival only when its effect is truly
actor-symmetric.

### Through the pipe now
| thing | how |
|---|---|
| `famUse(i, actor)` | one entry point; owner resolves the list, same CFX effect, same charges, FKFX on the owner's own card element |
| **preserve** | full loop: their kept scorer captured {val, mat, ench, lane} -> real die redealt in its lane, amber shell + settle crack, priced credit. The fake (`G._oPreserve=100`) is dead |
| **slow_cook** | one accumulator, either seat (rival's roll seam now carries its roll count) |
| **pickpocket** | whoever banks lifts from the other purse |
| **double_or_nothing** | armed via famUse('o') when trailing 1000+; the same flip resolves at their bank, pool by owner |
| **enchants** | their deal carries ench per seat (rung.dieEnch), every scoring call on their path passes it (fog/encore/rescue/QH/GB/slippery incl.) |
| **materials** | already flowed (starstone, tint sheets); unchanged |
| bankBonus seam | FIXED: the rival's seam consumed no delta (fired after the add, return discarded) - every rival bankBonus card was silently void |

### Still bespoke or inert - the remaining sweep, in order
0. ~~retort / reprisal / short_fuse / encore~~ MIGRATED (P765) - bust and
   bank passives symmetric (numerically verified both directions); the
   rival's bust seam carries `lost` now; encore rerolls THEIR free dice
   through famUse('o') at their dead roll, the turn code keeping its
   local rescore. stargazer's bespoke dodge remains pending Q2.
1. ~~honeytrap~~ MIGRATED (P764) - the bespoke was a DIFFERENT effect
   (random modal pull, no pair); they play the player's card now: pair
   from _tablePairs('o') arms it at the push decision, their deal pulls
   the die, mirror of the player's consumption. `encore` / `stargazer`
   still bespoke in the roll loop.
2. ~~sleight / stargazer / ill_omen / falling_star~~ RULED AND BUILT
   (P766): sleight resurrected BOTH ways (player half built, card
   un-retired, rival arm through the pipe); stargazer is the faithful
   peek both seats - the AI reads its next roll and banks a foreseen
   dead roll in the open, the bust-dodge deleted; ill_omen is one hook
   on the rivalTurn seams, exactly the player's numbers upside down
   (minting included - the bespoke's capped-only was drift); falling
   star grants THEM the extra turn - RETUNE FLAG per Denis: measure the
   difficulty once live.
3. The rival-only legacy roster (Q5 ruled): migrate rival-only FIRST
   onto CFX rails (cheap path), revisit two-seat when there is a
   concrete reason - Denis leans parity-first but wants to see what
   second_wind / double_down / the bust saves actually do before paying
   for two-seat builds.
3. ~~bloom / cultivate / vanguard_f~~ MIGRATED (P764) - ev.mine, growth
   store per seat (G._oCultArr), feats stay the player's ledger.
   Verified numerically symmetric: 600/750 both seats.
4. `retort`, `short_fuse`, `fools_gold_f`, `falling_star` - need the bust
   and deadRoll seams raised in the rival turn (they exist only on the
   player's), then the same ungate recipe.
5. The npc legacy actives (`getNpcCard` mechanics: second_wind,
   double_down, bust saves...) - migrate onto CFX rails card by card,
   deleting each inline handler in the same move.

---

## 8. The legacy roster migration - the map (batch staged 2026-08-18)

Measured: **42 NPC_CARDS** (9 actives, 11 passives, the rest
boss-special), **21 `npcHasActive` lever sites**, **19
`effect.mechanic` branches** inlined through runOppTurn/finOpp - plus
`npcCardState` (usedOnce / npcActiveUses) which is **saved**, so any
state move is a resume-risk change and gets its own verification.

Denis's Q5 ruling: rival-only first, the cheap path; two-seat builds
only with a concrete reason. These cards have no player twin, so 'one
pipe' here means ONE DISPATCH, not actor symmetry: a mechanics->handler
table (the CFX shape, same event vocabulary: turnStart / roll / keep /
bank / bust / rescue) replacing the inline blocks one cluster at a time,
with `npcCardState` kept as-is (no save-format change in this pass).

Batch order (each cluster lands alone, bespoke deleted with it,
smoke + resume check after every one):
1. **Bust rescues** - 1a DONE (P767): the eight dead-roll rescue cards
   (old_bones, ambrose_grace, wild_die, brutus_fist, finnicks_palm,
   grogs_flask, coin_flip, the_nudge) are one table (NPC_RESCUES), one
   consumer, ladder quirk preserved and flagged (an entered-but-useless
   card stops the chain - ruling wanted on fall-through). Driven with a
   scripted roller: rescue fires once, quirk busts, control clean.
   1b DONE (P768): NPC_BUST_SAVES - survive/immune (one walker, CARD
   order preserved), bank-half, stitch, second wind; outcomes keep their
   exact plumbing (survive resumes, bank rides the finOpp timer,
   _oppBustOut stays the one exit). Driven with scripted dead rolls:
   survive fired and continued; bank-half banked exactly floor(bank/2)
   =375 against stitch's full 750 on identical scripts; second wind
   spent its charge cleanly. Instrument note: the first probe's 'one
   scorer' seed contained a 2-3-4-5-6 straight - the bank was 750, not
   50, and the expected numbers were wrong, not the mechanics.
   NEXT: cluster 2, the turn-start arms.
2. **Turn-start arms** DONE (P769): NPC_ARMS - the_tab, loan,
   seven_dice, all_in at turn start; twinning_charm, aldrics_vow at the
   roll moment; one walker per moment, ctx carrying `left`. Driven live:
   loan +1500 with its same-turn -200 tick, the_tab armed at 80% target,
   twinning fired mid-roll. FOUND DORMANT: seven_dice has dealt 6 since
   P521's seat cap - preserved, ruling in OPEN.md. (whispers_hex arms
   through the generic yielding path, not these blocks; double_down
   moved in P762.)
3. **Bank riders** DONE (P770): the mechanic-driven riders were already
   tabled by P470 (_oppFxOwnA/B + BANK_FX, extracted for the sim);
   corvus_ledger's inline active joined NPC_ARMS at a 'bank' moment.
   FOUND AND DELETED on the way: the rescore-and-repick tail existed
   FIVE times (encore, rescue, quick hands, grog's bump, slippery
   table) - _oppRescore() is the one copy now, hoisted in step().
4. **Roll/keep modifiers** DONE (P771): quick_hands and grogs_bump -
   twin blocks - are one _playerKnock (face + name as data). The
   remaining player-armed disruptions (hot_streak, crown_authority/
   blessed_dice, pocket_sand, snake_oil...) are genuinely DISTINCT
   one-offs: no shared body to extract, documented as such rather than
   tabled for the table's sake.

**CLUSTERS 1-4 COMPLETE (P767-P771).** Full regression battery green
2026-08-19: actor pipe, phase-1 decisions, the four rulings, rescues,
arms, knocks, five-turn smoke, card + dice glow. One scripted-roller
probe flaked once and passed on rerun against the identical build -
instrument variance, recorded. Remaining arcs: cluster 5 (two-seat
re-audit, awaits Denis's play knowledge), phase 2 (personas as weights
on the EV core, sim-tuned), and the deep seam unification
(handleBank/finOpp, the two deal loops).
5. Re-audit for two-seat candidates once the table exists - Denis
   revisits with concrete card knowledge (Q5's second half).

Falling Star (rival half) is LIVE and flagged: Denis plays nights before
the retune batch touches its numbers.

---

## 9. Phase 2 - the calibration baseline (P772/P773, 2026-08-19)

The sim runs the LIVE chooser now (_npcDecide, the G-free core; the sim
was silently degrading to maximal-keep through a swallowed throw - see
the instrument note). _runPersonaSim({turns:800}) per persona, bone
gear, agg .6 / minBank 300 / diceStop 2, mid-match score context:

| persona | banked/turn | bust | rolls | kept/pick | EV given up |
|---|---|---|---|---|---|
| ones | 501 | .193 | 1.80 | 2.25 | 16 |
| triples | 500 | .274 | 2.01 | 2.33 | 23 |
| straights | 491 | .259 | 2.04 | 2.34 | 18 |
| aggro | 530 | .196 | 2.15 | **1.41** | **30** |
| hoard | 529 | .184 | **1.76** | 2.31 | 15 |
| combo | 513 | .211 | 2.07 | 1.80 | **0** |

Readings:
- **Identity is visible in numbers**: aggro keeps 1.41 dice and rolls
  deepest; hoard keeps most and stops earliest; combo gives up exactly 0
  EV by construction (internal validity check - it IS the argmax).
- **The floor works**: mean give-up runs 0-30 against the 500 cap; the
  chasers (triples/straights) pay ~.26-.27 bust rate for their chase and
  land ~30-40 under the top earners - in-character, bounded.
- **The spread is tight** (491-530, ~8%): personas are flavour, not
  traps. Nobody is suicidal; nobody is strictly dominant.

**Calibration verdict: the multiplicative weights sketched in section 3
are NOT needed at these numbers.** The style rules over EV-floored
candidates already deliver distinct, bounded, competitive personas. The
weights stay in the toolbox for the retune batch if Denis's nights (or
the Falling Star data) say a persona needs moving - tune what the
numbers say, not what the plan predicted.

**Instrument note (the catch of the day):** before the fix, the sim's
_npcDecide returned null on 65 of 65 calls - an unused, unguarded `var
row=(G.oppDice...)` threw on the match-less sim page and the defensive
try/catch ate it. The personas still showed DIFFERENT numbers (through
oppShouldBank's behaviour term alone), so the output looked plausible -
a convergence artifact that would have validated a broken sim. The
onPick tap's picks:0 was the only tell. Measured taps are now a
standing assertion of the harness: picks>0 per persona or the run is
void.

