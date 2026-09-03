# BOSS REWARD BRIEF — the card layer, the badges, the win screen

*Denis's rulings, 2026-08-23. Supersedes the master brief on boss spoils
and on the CARDS-table active layer. Where this brief and any other
disagree on those two subjects, this one wins; everywhere else the master
brief stands.*

**Status: nothing here is built. Do not start until §8's order is read —
three of these changes have save-migration or id-collision hazards and
one of them has to happen before the others or it lands twice.**

---

## 0. Why this exists

The CARDS-table active layer — 28 cards with art, text and working
handlers — has never been reachable in play. `OPEN.md` §1c recorded the
whole layer as dead for ~230 patches on a mechanism that had gone stale,
and two card audits were silently scoped around it. When the reachability
question was finally driven rather than read, the answer was: the layer
works, and nothing hands the cards out.

Denis's ruling is not "wire it back on". It is smaller and better:

> "each boss has a special boss card specific to them and yes you can win
> it off them."

Eight cards, one per boss, won on the win screen. The other twenty are
deleted. This brief is that change plus the three rulings that came out
of examining it.

---

## 1. THE EIGHT — and why the shape was already there

Of the 28 actives, exactly **eight carry an `npc:` tag AND a
`rewardQuote`** — one per boss, with the boss's own line for handing it
over (Grog's: *"Here… take thish. Won it fair an' shquare."*). The
structure Denis described already exists in the data. Nothing about the
shape needs inventing.

**What does need replacing is what is printed on them.** Six of the eight
duplicate something the player can already get:

| Boss | Current card | Already exists as |
|---|---|---|
| Grog | Flask — reroll 2 non-scoring | Steady Hand, but that is 1 die *of your choice* — a real distinction. **KEEP** |
| Mabel | Stitch — bust → bank pts + free reroll | Ward enchant (bust saves half). Stitch is strictly better, at no cost |
| Finnick | Palm — one unselected die → 1 or 5 | Transmute — any die, any face, chosen. Strictly better |
| Corvus | Ledger — next bank ×2 | Double or Nothing — same upside, **no downside at all** |
| Brutus | Fist — force one die → 1 | Transmute again. Already `dep:true` |
| Aldric | Vow — "DOUBLE OR NOTHING" | *literally the Obsidian family card's name and effect* |
| Whisper | Hex — opponent plays a die short | Snuff enchant. Same effect |
| Ambrose | Grace — 2 blanks → 5s | Transmute / Old Bones. Already `dep:true` |

Corvus's is a balance defect independent of the redundancy: it is Double
or Nothing with the risk removed, which makes the real card pointless in
any run that holds it.

---

## 2. THE NEW ASSIGNMENT

Each boss's card now does something no family card and no enchant does,
and each is matched to that boss's own badge rather than to a vibe.

| Boss | Their badge says | Card | Effect | Source |
|---|---|---|---|---|
| **Grog** | *nothing under 800 crosses my bar* | **Grog's Flask** | reroll 2 non-scoring dice | unchanged |
| **Mabel** | *(new — see §3)* | **Mabel's Stitch** | bust, then roll 3 rescue dice once; whatever they score banks, turn ends | `second_wind` |
| **Finnick** | *15% chance I palm one of your dice* | **Finnick's Eye** | keep any dice, scoring or not, reroll the rest | `gamblers_eye` |
| **Corvus** | *every roll costs you 5 gold* | **Corvus's Note** | +1500 points now, −200 a turn for five turns | `loan` |
| **Brutus** | *three rolls a turn, then you're done* | **Brutus's Grip** | hold one die through your rerolls this turn | `frozen_die` |
| **Aldric** | *every die forgets what it was made of* | **Aldric's Whetstone** | one die takes another's material | `alchemists_chisel` |
| **Whisper** | *enchanted dice sing louder at my table* | **Whisper's Wager** | double this turn's points, then reroll every kept die | `double_down` |
| **Ambrose** | *match my last bank, or you score nothing* | **Ambrose's Pyre** | burn one of your own cards for +500 to this bank | `the_pyre` |

Two of these are worth stating out loud because the pairing is the point,
not decoration:

- **Aldric's badge makes every die forget its material; his card is the
  only thing in the game that lets you choose one.** Exact inverse.
- **Corvus charges you gold per roll; his card lends you points at
  interest.** The merchant, twice.

**Delete the other twenty** — including the four currently-`dep:true`
boss cards being replaced (`brutus_fist`, `ambrose_grace`, plus
`alchemist_touch`, `wild_die`, `double_down_die`, `old_bones`,
`sleight_of_hand`, `broken_lantern`). Everything in the discard pile is
either a duplicate of Transmute (face manipulation), a duplicate of
Double or Nothing (`all_in`), or a run-economy card the tavern layer
already covers (`the_tab`).

---

## 3. MABEL'S BADGE — a new rule, and why nothing existing fits

**ZERO HOUR is wrong for night 2.** *"Take an enchanted face at my table,
dear, and I cut the thread"* punishes enchants. Enchants cost 150–400g at
the innkeep; at night 2 a player holds starting gold plus one win. The
badge fires against nothing.

**STEEPED — the obvious swap — is also wrong, for a different reason.**
It is parked and unassigned, and it works from a bare loadout, so it
looks like the answer. It is not:

- Every Steeped site is player-side (`_ruleActive('steeped','p')` at the
  payout and the reset; accrual in the player's roll path). Worn, it pays
  *you* +100 per extra roll with no cost beyond a bust you were already
  risking.
- **That makes it the only badge that is not a constraint.** Last Call
  puts a floor under your banks, Drill Order caps your rolls, Pickpocket
  takes a die, First Strike charges gold, Reckoning makes you match a
  total, Still Waters silences your dice, Kindred amplifies theirs. Each
  is an obstacle facing you and a weapon when worn. Steeped is a bonus in
  both directions — a lure as a boss's, free points as yours.
- It is also half-wired: the accrual reads `G._tell.perRoll`, so a
  **sleeved** Steeped in a patron match has no tell to read and accrues
  nothing, while `_applySleeve` carefully initialises its state. Record
  this; do not fix it as part of this brief.

The file's own note is honest about how it got here: *"Zero Hour took
Mabel's badge, and every other candidate boss already carried a rule of
their own, so SOMETHING was always going to be displaced."* Steeped was
not parked for being bad — it was parked because Zero Hour needed a home.
Swapping them back reverses that trade without solving night 2.

### The new rule

> **MABEL — THE MENDING**
> *"Nothing leaves my table half-done, dear. Roll twice before you bank."*
> The player may not bank until they have rolled at least twice this turn.

Checked against the requirements the other eight meet:

- **Works on a bare loadout.** No dice, cards or enchants needed.
- **Is a constraint, not a bonus.** It removes the safe one-roll bank and
  forces a second throw, which is exactly the pressure night 2 should
  teach.
- **Is a real weapon when worn.** Forces the rival to over-roll into
  busts — which is what makes a won badge worth wearing.
- **Is in her voice.** She is the mender; the rule is "finish the work".

**Both ZERO HOUR and STEEPED go to `PARKED_TELLS`.** Neither is deleted —
they are tested, working rules, and the parked table exists precisely so
"keep the rule, drop the badge" is expressible. Zero Hour is ready if the
game ever wants an anti-enchant boss late; Steeped is ready if a bonus
rule ever fits somewhere.

**Note the pool arithmetic:** `_SEAL_POOL` is what cursed seats draw
from, and it currently holds nine. Adding The Mending makes ten, which
moves every other rule from 1/9 to 1/10 on a cursed seat. That is a
balance change — state it in the patch header the way P568 stated its
own.

---

## 4. THE WIN SCREEN — three choices, not four

Boss spoils currently offers **his die / his badge / his purse**, take one,
final.

**The die is dropped.** Denis: *"No one will pick a relic as a reward if
it's just visual."* This follows his own P834 ruling — relics are
trophies, rank 0 against real dice, never seated. It was a keepsake
competing against two mechanical rewards.

New spoils: **his badge · his card · his purse.** Take one, still final.

- Keep the trophy shelf itself if it costs nothing; just stop offering
  the relic as a pick.
- **Open question to answer while you are in there:** are the relic
  `effect:{}` blocks and the `_RELIC_FAM` family handling inert
  post-P834, or still firing somewhere? They read as leftovers from when
  relics were seatable. Report; do not act without a ruling.

---

## 5. ONE WORD: BADGE

Denis: *"let's ensure it's all one name for Badges. Because it's just too
confusing right now. Bosses have badges, you win them, you can use them,
that's it."*

The mechanism is already single — `_ruleActive(id, side)` holds all three
routes in one function:

```
_sealRule === id   -> both seats      (cursed seat)
_sleeve   === id   -> whoever asks    (the one you wear)
_tell     === id   -> side 'p' only   (the boss's, against you)
```

So this is vocabulary, not surgery. **Three passes, in this order, and do
not merge them.**

**Pass A — player-facing only.** Every string the player reads: the shelf
screen, the badge panel, the match-start splash, dialogue, card and rule
descriptions, tooltips. One word: *badge*. Retire "tell", "sleeve",
"seal" and "relic" from anything on screen. No code identifiers, no save
keys. Ship and verify this alone.

**Pass B — save keys, WITH a migration.** `S.run.tells` (what you have
won) and `S.run.sleeve` (what you are wearing) are **persisted**.
Renaming them without a migration orphans every existing save's won
badges. The `_ruleRename` map already in the loader is the pattern to
follow; the `_p12CardsConverted` latch is what a botched migration looks
like. Only do this pass if the rename actually buys something — internal
key names are invisible to the player.

**Pass C — code identifiers. Probably never.** `G._tell`, `_tellById`,
`_SEAL_POOL`, `PARKED_TELLS`, `.tell-badge` CSS, `--tell-badge-*` vars.
These cost nothing to leave alone and churning them risks more than it
returns. If Pass A and B land cleanly and someone still wants it, it is a
separate decision.

---

## 6. THE ID COLLISION CENSUS — read this before naming anything

**23 ids in this file already exist in two or more tables. Three exist in
three.** Full list, so the renames in §2 do not add a twenty-fourth:

```
finnicks_palm 3   slow_cook 3   the_tab 3
aldrics_vow 2     all_in 2      ambrose_grace 2   brutus_fist 2
coin_flip 2       corvus_ledger 2   falling_star 2   grogs_flask 2
high_roller 2     loan 2        old_bones 2       pickpocket 2
preserve 2        second_wind 2  short_fuse 2      steady_hand 2
the_collector 2   the_nudge 2    twinning_charm 2  wild_die 2
```

Four of the eight cards being reassigned are already collided ids:
`grogs_flask`, `second_wind`, `loan`, `corvus_ledger`. Two of the eight
bosses' **relic dice** collide with their cards — `finnicks_palm` is a
card, a relic die and an NPC-rescue entry, all three.

**The §2 renames are the fix, provided the new ids are checked against
this census before use.** Under the new spoils screen a boss's card and
his die would have been offered side by side — Finnick's would have shown
two picks both called FINNICK'S PALM with the same 🤏 icon.

**Add a startup assertion** that fails loudly on a duplicate id across
CARDS / DICE_TYPES / NPC_CARDS / FEATS / the rescue tables. This class of
bug has now cost this project real time three separate times (a feat and
a card sharing a name; a legacy dead card and a live redesigned card
sharing an id; this). An assertion is cheaper than a fourth census.

---

## 7. WHAT NOT TO DO

- **Do not wire `showScreen('bossreward')`.** That screen stays dead. The
  card is a tile on the existing spoils screen, which already fires
  inline from the end-match win branch. A revived reward screen would be
  a *third* reward beat on the same win, after spoils and the family
  draft.
- **Do not rename the relic dice** to resolve the `finnicks_palm`
  collision. The card is being renamed anyway; the die keeps its name and
  its shelf story.
- **Do not delete Zero Hour or Steeped.** Park them. Both are tested,
  working rules and the parked table exists for exactly this.
- **Do not touch the twenty deleted cards' handlers before the CARDS rows
  are gone.** Delete the rows first, run the parse gate, then sweep the
  orphaned handlers — not the other way round, or a live `case` in
  `activateCard` points at a function that no longer exists.
- **Do not merge Pass A and Pass B of §5.**

---

## 8. ORDER OF OPERATIONS

1. **§6 first — the duplicate-id assertion.** Land it before any rename,
   so every rename that follows is checked by it rather than by a person.
   Expect it to fail on the 23 existing collisions; grandfather those
   explicitly with a named list so new ones still fail.
2. **§3 — Mabel's badge.** Independent of everything else. Write The
   Mending, park Zero Hour and Steeped, state the `_SEAL_POOL` 1/9→1/10
   balance change in the header.
3. **§2 — the eight cards.** Rename and re-point first, then delete the
   twenty rows, then sweep orphaned handlers, then run the parse gate.
4. **§4 — the spoils screen.** Drop the relic tile, add the card tile.
   Do this after §2 or the tile has nothing correct to offer.
5. **§5 Pass A — the vocabulary.** Last, because §2–§4 change several of
   the strings it would otherwise rewrite twice.

---

## 9. VERIFICATION REQUIRED

Driven, not read. Every one of these has a failure mode that a code-read
returns green on:

- **Each of the eight cards, acquired the way a player acquires it** —
  beat the boss, take the card from spoils, then use it in a later match.
  Not `usedCards[id]=1` seeded by hand: that is what hid the layer's
  unreachability for 230 patches. The whole point of this brief is a
  path that did not exist, so the probe has to walk it.
- **Mabel's badge from both directions** — as her rule against the
  player, and worn by the player against a rival. A badge that only works
  in one direction is the Steeped defect.
- **The spoils screen with three tiles** — screenshot it. Tile layout is
  a 3-column grid today; confirm it still reads at 430×900 and that no
  tile is clipped.
- **A save written before this change, loaded after it.** Existing runs
  hold won badges and equipped cards; confirm nothing is orphaned and no
  slot points at a deleted id.
- **The duplicate-id assertion, by deliberately adding a collision** and
  confirming it fails. An assertion nobody has seen fail is not known to
  work.

---

## 10. RECORDED, NOT FIXED

Do not do these here; log them so they are not rediscovered:

- **Steeped's sleeve accrual is half-wired** (reads `G._tell.perRoll`;
  a sleeved Steeped in a patron match accrues nothing). It is parked now,
  so this is dormant — but it is a live example of a badge that works as
  a tell and not as a sleeve, and the other eight should be checked
  against that shape at some point.
- **The relic `effect:{}` blocks and `_RELIC_FAM`** — inert post-P834, or
  still firing? Report before anyone builds on either answer.
- **The 23 grandfathered id collisions.** The assertion stops new ones;
  the existing ones are still there and `finnicks_palm` ×3 is the one
  most likely to bite next.

---

## 11. NPC LOADOUTS — cap at three, and draw with synergy

*Denis, 2026-08-23: "right now bosses can have more than 3 cards which I
think is weird… The cards owned by bosses or patrons should be random,
they should have some sort of synergy with their dice, enchants, badges."*

### 11.1 The cap needs TWO changes, not one

`cardCount` is only half of it. `generateOppCards` also does:

```js
/* Boss matches: match player card count so it feels fair */
if(playerCardCount!==undefined)n=Math.max(n,playerCardCount);
```

The player holds up to four (slot 0 boss + 1–3 regulars), so **every boss
can already draw four regardless of their row.** Editing `cardCount`
alone changes nothing whenever the player carries a full hand — the
symptom would persist and look like the fix failed.

Do both:

1. `cardCount` → **3** on ALDRIC (was 4), WHISPER (was 4), AMBROSE (was
   5). Leave GROG at 2 — the cap is a maximum, not a level, and night 1
   should be light.
2. Clamp the match-the-player lift: `n = Math.min(3, Math.max(n,
   playerCardCount))`, or delete the lift entirely. **Deleting is
   cleaner** — with a hard cap of 3 and player hands of up to 4, the lift
   can only ever raise a boss toward a ceiling it already sits at, so it
   buys nothing and costs a reader's time. If it is kept, the comment
   must stop saying "so it feels fair", because a clamped lift no longer
   does that.

Assert it: no rung can produce more than 3 cards at any player card count
0–4. Drive it, do not read it — the two mechanisms interact and only one
of them is in the data.

### 11.2 The signature guarantee is handing nights 7–8 the match

Named bosses always draw `cardPool[0]`. For three of the eight that slot
holds a flat start-bonus card:

| Boss | Signature | Effect |
|---|---|---|
| GROG | `her_lucky_coin` | start +600 |
| WHISPER | `the_royal_purse` | **start +3500** |
| AMBROSE | `communion_wine` | **start +4500** |

Ambrose's target is 12,500, so his guaranteed signature is **36% of the
match, awarded before a die is rolled**, every time. Whisper's is ~31% of
11,250. Those are the two nights measuring 9.5% and 7.5% against a 45–55%
target, and the ladder has never won a single match at either
(0/20 and 0/20).

They are also exactly the wrong shape for §11.3: a flat number interacts
with nothing — not their dice, not their badge, not their pool.

**RULED (Denis delegated the call, 2026-08-23): REORDER THE POOLS.**
The start-bonus cards are kept and stay drawable; they simply stop being
guaranteed. This is the smallest of the three options, it loses no
content, and it removes a certainty rather than a card.

New `cardPool[0]` for the two bosses concerned:

| Boss | Was | Now | Why |
|---|---|---|---|
| WHISPER | `the_royal_purse` (+3500 flat) | **`royal_seizure`** — takes your best die, once, you play with five | A noble seizing property. Touches the player's LOADOUT, which is exactly the interaction §11.3 asks for, and it is bounded: one die, once, not a percentage of target. |
| AMBROSE | `communion_wine` (+4500 flat) | **`blessed_confiscation`** — takes your best die AND plays it himself, once | The bishop takes your best and turns it to his service. Interacts in both directions, still bounded, and it is the strongest night-8 signature in his own pool. |

Both new signatures are **weaker than what they replace** — a bounded
one-off against a guaranteed 31–36% of target — which matters because
these are the two nights the ladder has never won at (0/20, 0/20).

Rejected, with reasons recorded so this is not re-litigated:

- `the_quiet_decree` (45% of every bank → Whisper) reads like the right
  signature and is **worse than the flat +3500** over a full match — it
  scales with how well the player plays, on the night that needs relief.
- `crown_authority` / `blessed_dice` (force a reroll of your kept dice)
  are bounded and interacting, but they are the dual-use pair and a
  one-off tempo hit is a weaker character statement than a seizure.
- `sundays_rest`, `never_saw_a_robe` (he cannot bust / he is immune to
  your cards) are defensive and **invisible to the player** — a
  signature the player never sees fire is not a signature.

**GUARD — do not delete these two rows in §2's sweep.** `royal_seizure`
and `blessed_confiscation` live in `NPC_CARDS`, not in the CARDS actives
table; what §2 deletes is the CARDS layer. They each also have a
player-side activator dispatched through `NPC_CARDS_MAP`
(`activateRoyalSeizurePlayer`, `activateBlessedConfiscationPlayer`) —
those activators go with the rest of the player-active layer, but **the
NPC_CARDS rows must survive**, or the two new signatures point at
nothing. Same applies to the other seven NPC-derived player actives:
delete the activators, keep the rows.

It is still a **difficulty lever** and still belongs in the §1a measured
batch with the target reductions, the card cap, Short Fuse's scaling and
the removed boss draft.

### 11.3 Synergy — weight the draw, never filter it

The pools are already themed by *character* (Grog: lucky coin, one more
round, a bump; Corvus: interest, fine print, an audit). What is missing is
mechanical coherence with what the NPC actually brings to the table.

**The mechanism: one optional data field, one weighted pick.** Do not
add per-boss branching, and do not filter — filtering makes loadouts
repetitive and turns an empty match-set into a crash.

Add an optional `syn:` array to any NPC card row, naming what it pairs
with — a die material, a badge id, an enchant id:

```js
{id:'hold_the_line', …, syn:['drill_order']}     pairs with his badge
{id:'the_quiet_decree', …, syn:['jade','jade2']} pairs with wild dice
```

At draw time, score each candidate: **base weight 1, +2 for each `syn`
entry the NPC actually has** (their `dice` materials, their badge id,
their enchants if they ever get any). Pick without replacement by weight
instead of shuffling. Untagged cards keep weight 1 and stay drawable, so
the change **degrades to today's behaviour** when no tags exist — tag the
pools incrementally rather than all at once.

Why weighting and not filtering:

- A boss with a small pool and no matching tags still gets a full hand.
- Loadouts stay varied — the same boss does not bring the same three
  cards every night, which is what Denis asked to preserve ("should be
  random").
- Adding a tag can never make a card undrawable, so a typo degrades
  rather than breaks.

Keep the signature guarantee working alongside it: draw the signature
first, then weight-pick the remainder. Patrons (`key === 'patron'`) skip
the signature already; they should get the weighting, since their pools
are persona-biased and the whole point is that a patron's cards suit
their dice.

`S.npcWonCards` cards — ones the NPC won off the player — join the pool
today. They will have no `syn` tags and will therefore sit at base
weight. That is correct: a won card is loot, not part of the character's
kit, and it should be the least likely of the set.

### 11.4 Verification

- **The cap, driven at player card counts 0 through 4**, for all eight
  bosses plus a patron. Reading the data proves nothing here — the
  `Math.max` lift is the half that is not in the data.
- **Weighting distribution**, over enough draws to see it: a tagged card
  matching the boss should appear materially more often than an untagged
  one from the same pool, and **every** pool member should still appear
  at least once. If any card reaches zero across a large sample, the
  weighting has become a filter.
- **An untagged pool** (tag nothing, run the draw) must produce the same
  distribution as today. That is the degrades-cleanly guarantee, and it
  is the leg that lets the pools be tagged one boss at a time.
