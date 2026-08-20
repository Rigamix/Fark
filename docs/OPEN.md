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

**SHIPPED — P585, flagged as a real difficulty change, outside this batch** — not folded in silently. Denis's reasoning for
letting it go early: the ladder already sits well under target across most of the
game, so closing a double-cast that is currently overperforming is very likely
relief in the right direction rather than a new problem.

**MEASURED AFTER SHIPPING, and the "difficulty change" framing was overstated.**
I called it one on the strength of "a row whose only live face is a spent brand
is now a bust" — which says it *can* happen and nothing about how often. Driven
through FSIM (whose player side is the real engine):

| | rule off | rule on | delta |
|---|---|---|---|
| no brands *(control)* | 67.55% | 67.55% | **0.00pp** |
| one brand | 68.40% | 68.60% | +0.20pp |
| three brands | 71.25% | 71.03% | −0.22pp |

n=4000 per arm, SE ≈ 0.72pp — both deltas inside the noise and pointing opposite
ways. Counting the **event** instead of its effect on the aggregate, wrapped at
the bust gate itself: in **12,000 turns holding three brands the rule never once
changed a bust decision** (0 events), with both controls green — the hook fired
22,475 times and the icon rescue was genuinely exercised 13,918 times.

**So it is a correctness fix with no measurable difficulty cost**, not a balance
change to account for in the retune.

**AND THE POLICY CAVEAT IS NOW TESTED, not just stated.** The two checks above
shared a harness, a policy, a gear and a seed — they observed different things
(an outcome vs a decision) but their agreement said nothing about any of those.
Sweeping the event count across every shipped policy, 12,000 turns each:

| policy | fires/turn | bust rate | rescues seen | cost events |
|---|---|---|---|---|
| bea | 0.200 | 71.3% | 13,918 | **0** |
| carl | 0.047 | 65.6% | 13,153 | **0** |
| rita | 0.057 | 71.6% | 13,719 | **0** |
| ned | 0.212 | 63.6% | 12,899 | **0** |
| greg_naive | 0.221 | 97.1% | 16,616 | **0** |
| greg_informed | 0.221 | 97.1% | 16,616 | **0** |

The greg arms matter most: they roll hardest after firing and bust 97% of the
time, which is the exact shape that would produce the event.

**Counted as FIVE distinct policies, not six** — greg_naive and greg_informed
returned byte-identical numbers in every column, which usually means they
collapsed to the same behaviour. Worth someone checking why; it does not change
this conclusion.

Remaining caveat: one gear (three tithes on bone), and FSIM itself.

**A TRAP FOR THE NEXT READER:** FSIM's `iconsFired` now reads **0** by
construction — it splits with `_splitIcons` *after* the commit that marks the
brand spent, so `_dieIsIcon` correctly says "not a live icon". Brands still fire
(counted at `_iconFire`: 0.2/turn). Do not read that zero as a regression.

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

## 8. Last Orders: the labels are boxed in by the art. Above, or below?

You said the icons and text sit too high in the panel. **The sign itself is
fixed** (P573 hangs it as low as the painted ceiling allows — the ropes and beam
are part of the panel image, so the whole thing moves together and its dark top
has to stay on the background's dark ceiling; 8.7% is where a seam opens).

**Inside the panel I've run out of room, and it's the art, not the CSS.** The
moon and mug are *painted into* `LastOrders_panel.png` at 56.7%–72% of its
height. The hearts and the night number are already centred on them (measured:
hearts 57.6%–70.6%, number 63.9%, painted icons ~64.3%). There is no slack —
lowering them would pull them off the row they belong to.

That leaves the labels, and one real choice:

- **(a) Keep them above the icons**, as you asked. They fit in an 18-unit strip
  of clear parchment, which caps them at **11.5px**. That is a ceiling from the
  artwork, not a tuning choice.
- **(b) Move them into the writing band below the icons** — 5× taller, ruled
  lines already painted there. Labels roughly **double** the size, and it fills
  the empty lower two-thirds you're seeing. But it isn't "above".
- **(c) Repaint the panel** with more clearance above the icons, and keep (a).

**My rec: (b)**, on the grounds that the writing band is clearly what the art was
drawn to hold and it solves the empty-space problem in the same move. But you
asked for "above", so I'm not reversing that on my own.

**Also worth confirming:** the lower two-thirds is empty now because the night
number and NEW ROSTER moved up out of it. That matches your mockup — but it is a
change to what used to live there, so say if it was an accepted trade rather than
a side effect.

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

---

## 9. FOUR THINGS THAT WANT YOUR HANDS, NOT MORE MEASURING

All shipped and working. Each is one number or one reading pass, and none blocks
anything else.

**9a. The 23 patron voices.** Part 6b placed the brief's content against the real
pools — placement is verified, correctness is not claimed. The brief locked those
voices partly against backstory lines this build doesn't have (it assumed 6 per
patron; there are 3). `tools/_p627_patron_lines.py` lists every line by patron
and group in one place if you want to read them together.
*My recommendation: read them; don't have me rewrite them blind.*

**9b. The card activation threshold** — `--card-arm-lift`, currently 16cqw
(≈68.8px above the card row). Measured, not played. Raise it if cards fire by
accident, lower it if the drag feels dead. One value in `:root`.

**9c. How often the rival hesitates** — `DLG.prob.OPP_HESITATE_PUSH` and
`.OPP_HESITATE_BANK`, both `.3`. Raise for more, lower for fewer.
*(The old `_HESITATE_LO`/`_HESITATE_HI` band is gone — P632. It claimed to fire
only on close decisions; measured, `agg` is the same value every roll of a match,
so it was really a per-OPPONENT switch: some patrons hesitated on every single
roll, others never. The spacing is `DLG.trigger`'s job now, like every other
beat.)*

**9d. The card activation sound** — `SFX.cardFire()`. The voices are verified as
scheduled and shaped; whether it's satisfying is your ear. Body / bloom / tail
are three tunable blocks in one function.

---

## 11. FIRST STRIKE — it is a sealed-seat rule, and most players can never trigger it

You asked: *"Is First Strike still an handicap match? Or a card now? What is it?
I went into a handicap match that said First Strike, with a super abstract
description, and in game nothing happened."*

**What it is.** A sealed-seat **tell** — one of the nine in `_SEAL_POOL`, Corvus's
own. Not a card, and not a legacy handicap (those were deleted; the sealed seat
replaced them). It took the `first_strike` id from the retired In Arrears rule,
which is why the id turns up in gold-drain code that has nothing to do with it.

**Why nothing happened, and it is not a bug.** The reveal fires from exactly one
place: `_firstStrike(side)`, called by the *fire* handler of four enchant brands —
**Snare, Trade, Snuff and Fog**. If you are not carrying one of those and do not
cast it that match, the rule has no trigger at all. They cost 250–350g, so on an
early night the seal is guaranteed to do nothing. When it does fire it opens both
six-seat dice layouts side by side for the rest of the match.

**And the description says none of that.** It reads *"Reach across the table and I
read both sides of the book."* — flavour with no mechanical statement, which is
the "super abstract" you hit.

**Three ways out, and this one is yours:**

- **(a) Say what it does.** Rewrite the desc to name the trigger — *"Cast a brand
  at their row and both hands open."* Cheapest, keeps the design, and the rule
  stops looking broken. **My rec.**
- **(b) Widen the trigger** so it fires on something every player has — first
  bank, first hot dice, first card. Makes it always land, but it stops being
  Corvus's counting-house identity and becomes a generic reveal.
- **(c) Take it out of `_SEAL_POOL`** and keep it for Corvus's own boss match,
  where the player is likelier to be geared for it.

I have not touched it — (b) and (c) are design changes and (a) is your words.

---

## 10. THE ≤700 KEPT-TRAY OVERLAP — pre-existing, out of your band

On viewports 700px tall and under, the kept-dice tray overlaps the card-drop
target (-8.97px at 690). It predates this work and sits outside the 700–760 band
you play on, which is why it wasn't fixed with the rest.
Fixing it means dropping the activation zone there too, and card clearance is
already only 50px at that size — so it trades one tight number for another.
*My recommendation: leave it until someone reports it on a real short phone.*

---

## 13. RELIC SPOILS — the last thing still feeding the dead reserve

Fair Trade is retired and For Keeps seats its prize directly (P718, your
ruling a). One inflow still lands in the invisible reserve: taking a
BOSS RELIC as spoils. Nothing can ever surface it now.

- **(a) Same treatment as For Keeps** — the relic asks which seat it takes,
  immediately, on the win screen. One reuse of the P718 picker.
- **(b) Relics are trophies, not dice** — they go to `S.trophies` (the
  run-won screen already shows those) and stop pretending to be playable.
  **My rec** — relics rank 0 as dice, so seating one is strictly worse
  than any real die; their value is the shelf story.

## 15. THE LEGACY-ART PURGE (P714) — three surfaces now wait on new art

Your rule — nothing from the old `assets/` tree loads — is in, and your
follow-up rulings landed (P715): the **boss splash is removed** (its boss
music cue moved to the launch/resume paths, the tell stays on its badge),
the **pouch is gone entirely** (win-draft button, modal icon, loadout chip
— its panel code sleeps with no entrances), and the **shop door** point is
withdrawn — you have an icon for that already.

One art gap remains from the purge: the **boss peek sheet and end-screen
dialogue portrait** are name-only (they used to show the old-game busts
through the bosses' legacy keys). If those two surfaces should show a face
again, they want boss busts in the new style; if name-only is fine, nothing
to do.

Also kept, named plainly: `assets/cards/`, `win/`, `loss/`, `Audio/`,
`vendor/`, `models/`, Macondo, and `table_commoner.webp` (the 07-27 table
plate — current art in the old folder). Those are current infrastructure;
relocating them out of `assets/` is quiet housekeeping if you want the
folder to die completely. The now-unreferenced legacy FILES are still on
disk/repo — say the word and I git-rm them.

---

## 12. THE ENCHANT-PAGE CRASH — cannot reproduce, need one thing from you

Five probes drove the full route (fresh run → shop → ENCHANTS tab → every
plaque → every die, all 8 enchants, fully-branded rack into a boss match,
12 tab flips, shop re-entries, quicksilver, the legacy sheet path) on BOTH
the current build and the pre-session build, headless AND in a real Chrome
tab, with error listeners armed. **Zero exceptions anywhere.**

The one input that couldn't be replayed is **your actual save** — a mid-run
save with fields a fresh run never produces is the remaining suspect.

**What I need, either one:**
- the red error text from the browser console when it crashes (F12 → Console), or
- your save: F12 → Console → `localStorage.getItem('fark_save')` → copy → paste to me.

With either in hand the stack names the line in minutes.

## NPC AI rework (see docs/NPC_AI_BRIEF.md) - 2026-08-18
- The brief proposes personas become WEIGHTS on one EV core (slack capped
  ~10-15%), replacing the pure style rules. aggro keeps its identity
  (minimal keeps, more rerolls) but only among sanity-checked options.
  OK to proceed on phase 1 (guardrails + delete the release block +
  bank-implies-max-keep)?
- Phase 3 migrates NPC legacy actives (second_wind, double_down, bust
  saves...) onto the family-card CFX rails one at a time. That will
  touch boss fights - want it gated behind a specific night for testing?

## The five parity rulings (asked in chat 2026-08-18)
1. SLEIGHT: (a) build the player half too (un-retire), (b) retire both
   ways, or (c) rival-only but through the one pipe?
2. STARGAZER: replace the rival's bespoke bust-dodge with the faithful
   card - they PEEK their next roll and the AI banks if it sees a bust?
3. ILL OMEN mirrored: they declare; you bust next turn -> you pay the
   tier reward; you score -> you gain the consolation. Confirm?
4. FALLING STAR for the rival = extra-turn support in their turn
   machine (they can double-turn like you). Build it?
5. Rival-only roster (second_wind, double_down, bust saves): should the
   player ever be able to draft/win these? If yes they need two-seat
   effects from the start.

## SEVEN DICE is a dormant no-op (found by P769's probe, 2026-08-19)
The card sets left=7 but P521's seat-join caps every deal at the 6 free
seats - it has dealt 6 dice since the seat model landed, silently. The
refactor preserved the behaviour (a refactor is not the place to invent
a 7th seat). Ruling wanted: give the table a 7th lane for this card, or
retire/redesign it (e.g. '+1 die' becomes 'reroll one die free')?

## Bank-seam mirror rulings - RULED AND SHIPPED (P774, 2026-08-19)
1. GAIN_WHEN_AHEAD: bank-inclusive both seats (Denis: evaluated on the
   result of the banking action). Player test now (pPts+total)>oPts.
2. HALVE_FIRST_BANK: the FIRST bank specifically, both seats (the card's
   own text). oppFirstBankDone latch mirrors firstBankDone.
3. CHALLENGE: gut-check confirmed missing-check-not-design (the turn
   gates were already equivalent per the init offset); the player-owned
   arm reads oPts>=threshold, mirroring the rival's. NOTE for the
   flow-shell audit: the rival's challenge pre-arms with an announce,
   the player-owned resolves inline against the judged bank - both
   match their card texts; telegraph asymmetry recorded, not changed.
Also confirmed: block_low_bank now has ZERO implementation sites (the
backlog's 'implemented both seats' is stale - fully undealt AND gone);
periodic_drain mirrors correctly (per-owner turn counters) - the tool's
player-side scope just misses its site.


## Preserve return-turn flake (card audit, 2026-08-20)

3 of 11 headless probe runs ended the preserve RETURN turn paying zero
(one run's banked 100 also vanished during the rival turn). Never
reproduces under instrumentation: numDice trap, turn-exit wraps, and a
pPts write-trap all ran green 8/8 — pPts written exactly twice, both
by handleBank, same G object throughout. **My read: headless
SwiftShader/rAF stall, not a game bug — preserve stays PASS.** Nothing
to answer unless a phone playtest ever shows a vanished bank after a
preserve turn; if it does, that's this.

## The cardHit taxonomy (P814, retort's second trigger — 2026-08-20)

Retort's hit-half was fully dead (spec says "fully automatic on either
trigger"; a driven hex hit paid 0). P814 adds famFire('cardHit',
{actor:<victim>}) at the TAKING sites: NPC hex, NPC confiscation,
pickpocket/reprisal/ill_omen-landing (both owners). **My rule: an
opponent card that takes dice or points is a hit; pure buffs to their
own side are not, and retort's own payment never fires the seam (no
retort-vs-retort chains).** Two things you may want to rule
differently: (1) NPC quirk cards beyond hex/confiscate (bumps,
pinches, etc.) don't fire it yet — census them if you want retort to
answer everything; (2) Ward's spec names the same event, so the seam
is ready for it if Ward ever comes back.

## Sacrifice / Double or Nothing — RULED AND SHIPPED (P816, 2026-08-20)

Denis ruled: sacrifice moves to the TURN total ("there should be real
risk in taking it"); double_or_nothing keeps its pre-bank arm and the
TEXT changes instead. Shipped as P816: the +800 rides G._turnBonusPot
(banks with the turn, burns on a bust - probe-verified both ways:
bank collected 900, bust paid zero and zeroed the pot), and both
cards' text + FAM_SHORT now say what actually happens. Delete this
section on read.

## Boss dialogue is BACK (P818, 2026-08-20) — three content gaps remain

Your "no Grog dialogue" note traced to a two-patch contradiction: the
per-boss bark pools were deliberately deleted (moved to the lore
resolver), but P682's boss BYPASS still routed bosses around the
resolver into the emptied store, and bosses had no seat identity.
P818: bypass deleted, bosses stamp a lore TRAIT (art stays null so the
patron personal arcs stay closed), and the getLine guard no longer
kills LEDGER_LINES — driven: Grog greets with his real record ("2
nights at me table an' we're dead even"), busts get "Ha! Greedy!",
patron side regression-clean, resume restamps.
Three things only you can fill:
1. **BOSS_TRAIT map** — my defaults: grog reckless, mabel steady,
   finnick cunning, corvus greedy, brutus strong, aldric orderly,
   whisper cunning, ambrose orderly. Remap any of these with a word.
2. **First-ever meeting** has no boss MATCH_START line (the ledger
   greeting needs history; PATRON_LINES has only boss:win/loss pools).
   A `boss:<key>:open` pool per boss would close it — needs your lines.
3. **DLG.triggerCard is dead game-wide** (its card-bark pools were
   deleted with OPP_DIALOGUE; ~24 call sites fire into nothing, patron
   matches included). Revive wants content or a ruling to delete the
   call sites.

## BANK TO WIN, stage 1 shipped (P819) — the full oracle is a choice

Fixed and probe-driven: the winning press no longer snaps back (P728
latch restored at the win check), a sealed LAST CALL seat no longer
captions a bank it will refuse, tab-escrowed banks can't claim TO WIN,
slow_cook's pot and the hangover double are projected, and the label
self-heals from updHUD (Loan / tier-3 tamper used to leave it stale).
STILL UNPROJECTED (label under-promises): the ~30-card bank-bonus
stack (×2 cards, underdog, weight...), short_fuse's commit-time double
in the selection preview, and rival deductions (cowards_bell, halve /
steal-low). Closing those needs handleBank's total pipeline extracted
into one dry-runnable oracle — a real refactor of the game's most
central function. **My read: stage 1 covers what you reported; do the
oracle as its own careful session if you want the caption exact to
the point.** Say the word and I'll plan it.

## Boss-win draft (P820) — two small design notes

Shipped per your note: the family draft now follows the spoils pick on
the boss win screen (same offer, same skip/claim flow; SKIP pays 75%
of the boss purse). Two choices you may want different:
1. **Ambrose (night 8)** keeps his renown-card final screen, no draft
   — felt right for the last night. Say so if he should draft too.
2. The draft rolls at the NEW night's odds (tier has already advanced
   when the end screen builds) — a boss draft is one night "ahead" of
   a patron draft the same evening. Deliberate reading: the reward is
   for the night you just entered.
