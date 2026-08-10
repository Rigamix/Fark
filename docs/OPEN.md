# OPEN — questions and blockers

The only file you need to read. Everything has my recommendation, so **"yours"
is a valid answer.** Answered items are deleted, not marked — this stays short.

**§1 is now blocked and needs you.** The ladder table it rests on was measured
with the real player engine on one side and a *harness model* on the other —
see §1a. §2–§4 need you or a playtest; §5 is a small cleanup question.

Rebuilt 2026-08-06 — it had reached 960 lines with four `CLOSED` sections still
in it, which defeated the point of the file. Deleted items live in git history.

---

## 1. THE RETUNE BATCH — ruled, ready to build, must land together

Three changes that all move difficulty. Ruled that they ship as **one measured
batch**, not three uncontrolled swings.

### 1a. The ladder is out of spec everywhere. Targets come down.

Every boss against the gear a player would genuinely hold that night, two
independent policies, a fresh loadout drawn per match.

| boss | night | carl | rita |
|---|---|---|---|
| GROG | 1 | 22.5 | 20.0 |
| MABEL | 2 | 32.5 | 32.0 |
| **FINNICK** | 3 | **65.0** | 64.0 |
| CORVUS | 4 | 23.0 | 23.0 |
| BRUTUS | 5 | 36.0 | 33.0 |
| **ALDRIC** | 6 | **11.0** | 12.0 |
| **WHISPER** | 7 | **9.5** | 7.5 |
| **AMBROSE** | 8 | **7.5** | 7.0 |

Target is 45–55%. **Seven below, one above, none inside.**

**Ruled: reductions concentrated and uneven, matching the shape** — nights 6–8
need by far the largest (they sit at a fifth to a third of target), nights 1–2
modest, night 3 none or a slight raise.

**And ruled honestly: targets alone probably cannot close a gap that size at
6–8 without making those matches trivial.** Likely needs targets down *and* some
player-scoring growth *and* §1c, working together rather than one lever doing
everything.

**Confidence bound:** nights 3–5 carry about **±10** of model-assumption
uncertainty — measured by re-running the whole table under the opposite spoils
assumption, not guessed. Nights 6–8 and 1–2 barely move between assumptions, so
their shape is safe to tune against. Do not tune a mid-ladder cell to a point
value.

#### STOP — the table above is not safe to tune against. One question for you.

Trying to build the ruled reduction turned up four dead levers in a row, and the
fifth thing checked explains all four. **The two seats in the sim do not run the
same code.**

- `F.simTurn` — the player — drives the **real game**: `startPTurn`,
  `rollPool`, `afterRollLite`, `handleBank`.
- `F.oppTurn` — the boss — is a **separate implementation inside the harness**,
  with its own roll loop. Its own comment says so: *"the SIM has its own copy of
  the rival's scoring."*

So every win rate in the table is the real player engine measured against a
*model* of the opponent, and the boss's whole advantage is per-turn scoring:

| night | boss | player pts/turn | boss pts/turn | turns each |
|---|---|---|---|---|
| 6 | ALDRIC | 368 | **688** | 10 v 10 |
| 7 | WHISPER | 523 | **1096** | 9.5 v 9.1 |
| 8 | AMBROSE | 594 | **1424** | 9.3 v 8.6 |

The boss does not get more turns — it gets **fewer**. And four candidate causes
are now measured and dead, each with a control:

1. **Targets** — inert at 6–8. Those matches end at the turn cap 92 / 54 / 27%
   of the time, so a finish line most matches never reach cannot matter.
2. **Boss aggression / minBank** — inert, and `agg` is **backwards**: it gates
   *"don't bank yet"*, so lowering it makes the boss bank sooner and keep
   *more* (Aldric 6860 → 7259). Ratio never left 1.8–2.2.
3. **Dice** — not the cause. The design comment claims boss dice sit *"one step
   above the player's typical loadout"*; at nights 7–8 the player is **ahead**
   (boss carries flint and amber). Handing the player Aldric's own dice made
   them slightly *worse*.
4. **Player skill** — not the cause. Every shipped policy banks at a **fixed
   threshold that never scales** (carl 300, bea 500, ned 400, rita 200) while
   late bosses bank at 700–900 — but raising it 300 → 1400 is **flat**, because
   bust rate climbs 0.14 → 0.54 and cancels the gain exactly. Best of the whole
   roster is otto at 14.7%.

#### ANSWERED — the model is not faithful, and it errs toward flattery

Measured, not argued. `tools/probe_oppturn_real.js` drives the **real** engine
at night-6 gear and reads what the rival actually banks per turn. It reuses no
scoring code of its own — a third copy could not settle an argument between the
first two — so it observes `G.oTurns` / `G.oPts`, which the game itself moves.

| rival points per turn, ALDRIC | value |
|---|---|
| what the sim model says | **688** |
| real engine, opening turn only *(no assumptions)* | **843** — n=7 |
| real engine, running match | **1041** — n=45, median 950, busts 7 |

**The model understates the real rival by 23–51%.** So the ladder at nights 6–8
is not softer than the table claimed — it is **harder**. The real ratio at
Aldric is about **2.8×**, not the 1.86× the sim reported, against a player rate
of 368 that *is* trustworthy because the sim runs the real engine for the
player.

**What this settles, and what it does not:**

- The four dead levers stay dead — targets, `agg`/`minBank`, dice and player
  threshold were all measured against a model that, if anything, was too kind.
  Fixing the model makes them *more* inert, not less.
- The direction of §1a survives: nights 6–8 need help. The **magnitude was
  understated**, so tuning to the old table would have under-corrected.
- The absolute win rates in the table are **not** safe to tune to a point
  value. They need re-measuring against the real rival before any target is
  written down.

Caveat kept honest: 4 of 49 turns did not complete within the probe's window
and were dropped rather than counted as busts. If long turns are the ones that
stall, the true figure is **above** 1041, not below.

**My rec: rebuild the ladder table against the real rival before touching §1.**
That is now a measurement with a working instrument rather than an open
question, so it is hours, not half a day.

One known gap in the model regardless: it has **no hot-dice rule** (`hot`
appears zero times in it), while the player's real engine does. The keep
policies *are* exercised — via `_oppChooseFrom` — so P495 is genuinely measured.

### 1i. RULED — the double-cast closes, and it is a difficulty change

Denis ruled: a brand that can fire twice in one turn via hot dice makes the
card's own promise ("this turn") false as written, so **make it true** — a spent
brand stops counting as a live icon until the next turn. Correctness grounds.

**It lands OUTSIDE this batch, deliberately, and must be flagged as a real
difficulty change when it ships** — not folded in silently. Denis's reasoning for
letting it go early: the ladder already sits well under target across most of the
game, so closing a double-cast that is currently overperforming is very likely
relief in the right direction rather than a new problem.

Two knock-ons to carry into any retune measured after it: it removes a real (if
rare) double-cast, and it creates a **new way to lose a turn** — a row whose only
live face is a spent brand is now a bust.

### 1e-bis. RETRACTED — those two bosses can fire the card, and the premise was backwards

**This section used to say** `blessed_dice` (Ambrose) and `crown_authority`
(Whisper) were **dead slots**: dealt into the boss's hand, activatable only by
the player, so each boss could draw a card it can never fire. It concluded that
removing the ids would make both bosses **stronger** by freeing a wasted draw.

**Both halves are false, and the conclusion points the wrong way.**

Measured while fixing D3 (P557). Both cards carry
`effect:{type:'once',mechanic:'reroll_all_kept'}`, and the after-roll dispatch
runs straight off `G.oCards` keyed on `effect.mechanic` with **no**
`type:'active'` or player-only gate. Driven 40/40 through the real dispatch:
`usedOnce:{crown_authority:1}`. The `activate...Player` functions are the
*mirror*, not the only path — the cards' own text says so:

> `desc`: "Once per match, **Whisper forces you** to reroll every die you selected"
> `playerDesc`: "Activate while yielding: **the opponent must** reroll…"

So they are dual-use by design, and the boss half works.

**Why this mattered more than a documentation slip:** the section sat inside the
retune conversation with a difficulty recommendation attached. Removing those
ids would make Ambrose and Whisper **weaker**, not stronger — and both are
already flagged as needing help. Acting on it would have pushed the wrong way on
two of the three worst-off nights.

**The same false claim was in the source** (a P509 comment reading "those bosses
can draw a card only the player can activate"); corrected in place by P557. This
doc inherited it. Nothing to action here now — the item is simply withdrawn.

### 1b. `challenge` is broken on the PLAYER side too

Law 6 has no stated exception here — a bug, to be closed on correctness grounds.
But it is also a difficulty change, and the ladder is already too hard
everywhere, so it lands **in this batch, measured with the rest**.

### 1c. `blessed_dice` / `crown_authority` say "reroll", the code wipes

#### RETRACTED — do not build this. The code is unreachable.

Verified end to end: `initMatchScreen` declares `const pCards=[];` at **31786**
with the comment *"P1 cutover: old cards retired"*, discarding `params.pCards`.
That empty array is the only thing that populates `G.activeCardState.usedCards`
(**31859**). `activateCard` (**30842**) has exactly one caller and opens with a
`canActivateCard` gate requiring `usedCards[cardId] > 0`. `effectiveCards()`
(**24283**) returns `[]` outright.

So **`activateBlessedDicePlayer` and `activateCrownAuthorityPlayer` can never
fire.** Building "a real reroll" here would have been building a feature into
dead code.

The same chain kills the whole legacy player-active layer: Seven Dice,
Gambler's Eye, Vanishing Act, Double Down, Alchemist's Chisel, player-side
Blessed Confiscation and Royal Seizure, Sticky Fingers, Mabel's Stitch and
Second Wind are all unreachable. What is live is the **family engine** (CFX /
`G.pF`), **NPC cards**, and **patron tells** — Pickpocket is a tell, not a card,
which is why it fires.

**This also corrects §5's reasoning.** I called these two "player weapons" and
ruled on that basis. They are not weapons for anyone — dead on both sides.
Dropping the tags was still right (measured inert), but the justification was
wrong.


The block un-keeps the rival's dice, sets `total=0`, and announces *"KEPT DICE
REROLLED!"* without re-rolling a single value. Build the real reroll; do not
reword the card.

#### RECONCILED — there are TWO implementations, and the LIVE one already works

Denis read this section and reasonably concluded the mechanic is still broken
everywhere. It isn't. `reroll_all_kept` has **two** implementations, in opposite
directions, and only the dead one wipes:

| | direction | state |
|---|---|---|
| **26667** | **boss → player.** Fires off `G.oCards` through the after-roll dispatch | **WORKS.** P475 replaced the wipe with a real reroll; P557 fixed the rescoring (the pre/post-split `vals` bug that turned a punishment into a 4×). `dd.val=_rollD(dd)`, re-split, rescore per group. |
| **29875** | **player-armed → rival.** `G._playerRerollKeptArmed`, set by `activateCrownAuthorityPlayer` / `activateBlessedDicePlayer` | **STILL WIPES.** `d.kept=false; total=0;` then announces the reroll. No roller, no `val=`. **Unreachable** — it comes through `activateCard`, and the legacy player-active layer is dead (driven tonight: `canActivateCard` refuses every id, `pCards` and `effectiveCards()` both empty). |

**So the paragraph above is true only of the dead half.** The boss firing it at
you — the direction `docs/CARD_ART_NEEDED.md` describes, and the only one a
player meets — genuinely rerolls and rescores.

**What this means for the art list:** nothing needs a caveat. Its wording for
Crown Authority and Blessed Dice ("forces you to reroll every die you selected")
describes the live path and is accurate today.

**Correction to the original ruling, which assumed the wrong direction.** These
were taken to be boss cards punishing the player, and therefore a softening
lever for nights 7–8. They are not. There is **no NPC firing path at all** — the
only activations are `activateCrownAuthorityPlayer` / `activateBlessedDicePlayer`,
which arm it against the *rival*. So it is a **player weapon**, the wipe is
*stronger* than an honest reroll, and fixing it makes the game slightly
**harder** — which is exactly why it must be batched rather than shipped as
relief.

---

## 1d. The rival's cards are still wearing the old game's skin

You saw this in a live Grog match and asked whether we have been shipping old
cards. **The card logic is entirely current** — Grog's three (`her_lucky_coin`,
`one_more_round`, `grogs_bump`) are present-day `NPC_CARDS`, and the previous
game's 149 card faces are archived and genuinely unreachable: `_cardArtImg`
returns `''` at all 9 of its call sites, so none of them are drawn.

**What is old is the presentation.** Two card looks ship side by side:

- **player cards** — `famCardArt`, a painted `.webp` face, the pixel-tarot
  direction. This is the current look.
- **rival cards** — `gcard`, an emoji on a flat colour swatch inside a red
  frame with corner brackets. This is the previous game's card chrome with the
  art removed and never reskinned.

Different look, layout and scale, exactly as you described — and it is why one
card read as current and the others as foreign. It is a live art gap, not a
data regression.

**RULED: no card gets a CSS style, every card gets art.** The list is
**`docs/CARD_ART_NEEDED.md` — 41 cards**, and the loader is built, so a PNG
dropped into `assets/cards/` renders on its own with no code change per card.

- **41 rival/boss cards** — every `NPC_CARDS` id reachable through a rung's
  `cardPool`. `pocket_sand` is defined but pooled nowhere, so it is excluded.
- **The 30 family cards are complete** — all 30 already have art.

I first sent this as **132** by including 90 entries from the previous game's
`CARDS` roster. Denis caught it. See §1e — those cards are real and still being
dealt, but that is a bug to remove, not 90 pictures to draw.

The palette work (P505) is a **stopgap that retires itself**: each PNG that
lands strips that card's border, ground, glow and emoji automatically, so the
CSS skin survives only on cards still waiting for a face. Delete it outright
once the list is filled.

---

## 1e. The previous game's card roster is still being dealt

Found while checking the art list, and confirmed by launching real patron
matches rather than by reading the code — `tools/probe_patron_cards.js`.

`_generatePatronInner` builds every patron's hand from the **legacy 133-card
`CARDS` array**, the one the asset registry describes as retired. It is not
retired in practice: `pCardCount = tierIndex>=2 ? 3 : tierIndex>=1 ? 2 : 0`
with `cardChance:1`, so **every patron from night 2 onward always draws 3**.

Seventeen distinct legacy ids came out in one sweep of tiers 2–7 —
`chain_lightning`, `the_hearth`, `honor_guard`, `the_fence`, `slippery_table`,
`even_row`, `the_whetstone`, `anchor`, `last_stand`, `finnicks_trick`,
`the_heir`, `snake_oil`, `brutus_grit`, `whispers_veil`, `tavern_cheer`,
`the_ledger`, `prompt_hand`.

Boss hands are correct — they draw from `NPC_CARDS`.

**Why it matters beyond tidiness:** these are unapproved cards with no art and
no place in the current design, firing real effects at the player on six of
eight nights. They are also inside every difficulty number measured tonight.

**RULED and FIXED — P507.** No patron cards at all, rather than repointing at a
current pool: a fresh patron card layer is unscoped design work, and cutting
the dead roster out matches what was already supposed to be true.

Root cause: **P473** lifted a `return []` stub in `generateOppCards` that had
been keeping every hand empty. That was right for bosses, who draw from the
current `NPC_CARDS`. It switched the patron branch on as a side effect. P507
undoes only that side effect — `pCardCount` 3/2/0 → 0 — and leaves the boss
path alone.

Verified by re-running the probe that found it: all eight tiers now report
`patronCount: 0` and no legacy id in any hand. Nights 1–2 had already been
shipping the no-cards path, so nothing untested was introduced.

**This makes nights 3–8 easier** — patrons lose 3 cards each. It is a
correctness fix, not a balance decision, and it lands inside a ladder whose
numbers are already known to be untrustworthy. Do not read it as tuning.

---

## 1f. CLOSED - false alarm, the win art is live

I reported four finished pieces in `Art/Assets/Win/Standard` that the game
"references nowhere", on the strength of three grep strings returning zero.
Denis ruled: don't take either side's word for it, check what the win screen
actually loads.

Checked by forcing a real win through the game's own `dbgWin` and reading two
independent channels - the network log and the rendered DOM. The win screen
loads `assets/win/bg.webp`, `banner.webp`, `panel.webp` and `hands.webp`.

They are the same art: identical file sizes to the four `_opt.webp` copies
(0.11 / 0.13 / 0.20 / 0.07 MB), optimized 1 Aug 15:24 and deployed 15:38 the
same day, renamed on the way in.

Nothing is orphaned. Nothing needs deleting or re-optimizing.

**Why the greps missed it:** I searched `win_standard`, `Assets/Win` and
`winStandard`. The live path is `assets/win/bg.webp` - lowercase folder, and
the filenames dropped the `win_standard_` prefix. None of the three could have
matched. Seventh time this session a zero from a name search became a claim.

---

## 1g. Dice-lane integrity — see `docs/DICE_LANE_INTEGRITY_PLAN.md`

The full brief now lives in that file: six shipped patches (P510-P515) with
their verification, the two ruled standing lessons, the scoped rival-side
rework, and everything still open including the card-slot parallel and a
newly-flagged list (Vagabond's drag-reorder, `reduce_first_roll`, `swap_die`).

It carries a standing ask: **a systematic sweep** of every consumer of
`matchDice`, `_enchArr`, `numDice` and the lane functions cross-referenced
against every card and enchant — not another list built from recall.

Priority unchanged: behind card art and the playtest.

## 1h. CLOSED - hot dice no longer refunds this turn's penalties

**Ruled:** five. A penalty costs you for its stated duration; rolling a clean
sweep must not be the escape hatch that cancels the opponent's card.

Fixed player-side (P517) as a MINIMUM rather than a decrement - hot dice must
still be able to restore a hand, it just cannot exceed what the player had this
turn. Verified live: Hex armed, loadout 6, turn start 5, after hot dice **5**
(was 6). Without the Hex, 6 to 6, unchanged.

Pocket Sand is covered by the same change. **The rival's hot-dice reset must
match and does not yet** - it is `left=6`, a local inside `runOppTurn`, one of
seven writers of which five are literals, so it belongs to the rival-side
rework in `docs/DICE_LANE_INTEGRITY_PLAN.md` rather than a patch here.

## 2. Early-game signal — needs a person, not more reasoning

Restoring the brief's 24 feats removed every feat that fires in a new player's
first hour. Ruled that nothing goes back into the feat list; the proposal is
that dialogue beats do that job instead. **No argument settles this — it needs a
playtest.**

---

## 3. `assets/` — an art-scope call on your timeline

47 live references into the previous game's tree have no replacement.

| group | count | style-mismatch risk |
|---|---|---|
| Character portraits | 9 | **highest** |
| Match frames | 8 | **highest** |
| Night_Art UI set | 10 | **highest** |
| Environment / menu | 9 | mixed |
| Fonts | 8 | lowest |
| Audio | 3 | lowest |

**If there is only room for a subset, it is the 27 in the high-risk rows.**

---

## 4. Unplayed numbers — flagged, not trusted

Last Call's 800 and most restored feat conditions read real state and render,
but only HIGH ROLLER has fired through a live match.

---

## 5. Tags describing a mechanic that does not exist

`blessed_dice` and `crown_authority` are tagged `npcOnly:true` with
`owner:'ambrose'` / `owner:'whisper'`, but **nothing ever makes a boss fire
them** — they exist only as player activations. Either the tags are wrong, or a
boss firing path was intended and never built.

**Not to be resolved by building the path** — that would be a further difficulty
increase on the two worst-off nights. My rec: treat the tags as the bug, drop
them, keep the cards as player spoils. Cheap either way, but it should be a
decision rather than a silent edit.

---

## 6. Vagabond's drag — does a die keep its lane, or does the seat?

**A one-line ruling, and four cards are waiting on it.** Dragging a die to
reorder your row moves the die's *look* but not its *lane*, so lane stops
meaning "the seat you can see". Driven: vagabond dragged seat 2 → seat 6, and
**Trade took the rival's silver — the die facing lane 1 — while the player was
looking at a starstone** in the seat it now sits in. Snuff and Fog read the same
way, and all four cards say *"in the same seat"* in their own text.

Two coherent answers:

- **(a) the seat wins.** The drag permutes material, brand and lane together, so
  seat == lane always and every card takes the die the player is pointing at.
- **(b) the lane wins.** Lanes are an invisible identity, and those four cards
  stop presenting as seat-facing — their text has to change.

**My rec: (a).** It matches what you already ruled for §9 — per-die facts travel
*with the die* — and it is the only one where the card's existing text stays
true. (b) means rewriting four cards to describe an identity the player cannot
see.

Separate and confirmed, same drag: it reorders **committed** dice too, which
moves Finnick's Palm adjacency mid-turn. That one is a bug on either ruling.

---

## 7. Sleight does nothing, and fixing it is a difficulty change

**The card's text:** *"Force your opponent to reroll everything they just rolled.
Once per match."* Tier 2 twice, tier 3 twice plus once per table-rule trigger.

**What it does:** sets `G._famSleight = true` and prints *"SLEIGHT READY — THEIR
NEXT ROLL COMES BACK"*. **Nothing anywhere reads that flag** except the card's
own "have I been used?" guard. Nothing clears it either, so the 2- and 3-charge
tiers are inert too — one use, then the button is dead for the match.

**The rival's Sleight is fully built** and is a working template: armed when
they're 800+ behind, fires on your first roll of a turn, rerolls your free dice,
clears itself. Mirroring it for the player is a small, bounded job.

**So why this is a question and not just a fix:** a working Sleight is a **new
player weapon**, and §1 already ruled that difficulty changes ship as one
measured batch rather than uncontrolled swings. Building it quietly would be a
stealth buff on a ladder whose numbers you've already been told not to trust.
It's the same reasoning that put §1b and §1c in the batch.

**My rec: implement it, but land it inside the §1 retune batch**, tiers 1–2 only
(the tier-3 "once whenever the table rule triggers" clause is a separate
mechanic and can wait). If you'd rather not carry another card into that batch,
the honest alternative is to **retire it** — a card that prints a promise and
does nothing is worse than one that isn't offered.

---

## Not blocking, for your awareness

- **Pages deploy is healthy.** The GitHub outage recorded here is over; six
  deploys went out tonight and each was verified LIVE by grepping a marker on
  `rigamix.github.io`, never by a green build — `_dieLeftSeat`, `_cultArr` and
  `_drillMax` are all present on the served file. **Keep verifying that way**:
  `index.html` is only a redirect stub, so grepping the site root always looks
  empty.
- **Four model assumptions remain untested** — 65% patron win rate, boss beaten
  first try, buys the dearest die in stock, no enchant/tavern gold. None *looks*
  load-bearing, but that is an impression rather than a measurement; the same
  sensitivity method settles any of them if a retune leans on one.
