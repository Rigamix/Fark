# What I need answered

Everything here is answerable in a word or two. Each has my recommendation, so
"yours" is a valid reply to any of them and I'll take it.

Ordered by whether it's blocking me, not by size.

---

## 0. FOR THE TEAM — Grog's badge, and opponent-side enchants

*This one is written to be circulated. It is self-contained; you can paste this
section on its own.*

### The situation

Grog is the **first boss** — rung 0, target 3,700, buy-in 10. His badge rule is
**ZERO HOUR**: while worn, keeping any enchanted die's icon face immediately ends
that side's turn. It replaced Last Call, which tested as the weakest tell in the
roster.

### Two problems, found in code, not in theory

**1. The rule can only ever point one way.** `_iconFire` is called from exactly
two places and both pass the player side. `_zeroHourClose` is called from
`handleRoll` and `handleBank` — both player paths. There is no opponent enchant
array anywhere; `G._enchArr` is the player's. So a badge whose governing law is
*"a SYMMETRIC house rule for the whole match: binds both sides"* is in practice a
one-way self-tax.

This is the **fourth** casualty of the same missing system. The enchant brief's
open item 8 already lists three clauses made unreachable by "no opponent-side
enchants exist in the engine" — Kindred (rescoped), First Strike (redesigned),
and enchanted patron dice (deferred). Zero Hour has the same defect and was not
on that list.

**2. It arrives before the system it points at.** Grog is night one. The player
is on a starter die and has bought nothing. Grog's own loadout is
`bone, bone, bone, iron, iron, iron` — all mundane. **Neither side has an enchant
at that point, and neither side can.** So even after opponent-side enchants are
built, Zero Hour remains a no-op at Grog's tier specifically.

Those two are independent. Fixing the first does not fix the second.

### Already decided

**Opponent-side enchants get built.** Denis: *"opponents SHOULD have enchants
anyway."* That closes problem 1 for the whole badge system and lets Kindred and
First Strike recover their original, richer designs. It is a feature — NPCs
owning brands, an AI keep-policy for icon faces — not a patch.

### THE QUESTION FOR THE TEAM

**What rule should Grog carry, given he is the first fight in the run?**

The first boss is the game's teaching fight. Whatever he carries is the first
house rule a player ever meets, and it has to bite with plain dice — which is
exactly what Zero Hour cannot do.

**Option A — Grog gets a rule that works on mundane dice; Zero Hour moves to a
late boss.** *(recommended)*
A badge's physical identity belongs to its boss and only the rule ID moves — the
brief already establishes this, and says no new badge art is needed. Zero Hour
lands somewhere the player actually owns brands. This also composes with two
problems we already have: Corvus's First Strike is flagged in the brief as "a
downgrade nobody signed off on", and Corvus's In Arrears was the only gold-tax in
the roster and now has no home. So it is one three-way reshuffle instead of three
separate fixes.
*Open sub-question if we take A: what does Grog carry?* The original Last Call
(banks under 500 don't count) worked and taught the right lesson — it just tested
weak. A retuned Last Call is the low-risk answer.

**Option B — Give Zero Hour a floor so it can never be a no-op.**
It also ends the turn on the Nth roll, brands or not. Works at every tier and
sharpens as the player brands up. Risk: it is close to Brutus's Drill Order
(three rolls a turn), so two of eight badges would be roll-limiters.

**Option C — Leave Zero Hour on Grog and accept it is inert until late.**
Only defensible if we expect players to re-fight Grog wearing it, or to face him
late. Worth stating out loud so it is a choice rather than an oversight.

**Option D — Escalate the tier.** Give bosses brands as part of the
opponent-enchant work, including Grog. Rejected as written: a night-1 boss with
an enchanted die contradicts the progression curve everything else follows.

### What I need back

1. Which option for Grog — A, B, C or D.
2. If A: what rule does Grog get, and which boss inherits Zero Hour?
3. Is opponent-side enchant support scheduled now, or after the pricing pass? It
   gates Kindred and First Strike recovering their real designs.

---

## 0-B. ROUND TWO — from the answers and the expanded lore brief

### Q1. Please send the current `FARK_ENCHANT_BADGE_REWORK.md` — BLOCKING

The answers doc says Corvus's two problems (First Strike's downgrade, In
Arrears' orphaned gold-tax) *"were already resolved together in the prior round
— one badge, both halves of his identity restored."*

**The copy I hold does not contain that resolution.** It still reads *"Flag this
plainly: this is weaker and less interesting than the original race concept —
worth a real decision"* and *"Removing it means no badge taxes gold anymore. If
missed in playtest, needs a new home — not solved by this rework."*

So I am working from a version behind yours. Without the current one I will
either re-open something you consider closed or implement against stale text.
This is the only genuinely blocking item here.

### Q2. Zero Hour lands on Whisper — so where does Kindred go?

The ruling is position-based: *"whichever boss holds the LAST slot before
Ambrose."* Measured against the shipped ladder:

| slot | boss | tell today |
|---|---|---|
| 0 | GROG | ZERO HOUR |
| 1 | MABEL | STEEPED |
| 2 | FINNICK | PICKPOCKET |
| 3 | CORVUS | FIRST STRIKE |
| 4 | BRUTUS | DRILL ORDER |
| 5 | ALDRIC | STILL WATERS |
| **6** | **WHISPER** | **KINDRED** |
| 7 | AMBROSE | THE RECKONING |

Last-before-Ambrose is **Whisper**, who already carries Kindred. So this is not
a two-way swap, it is three-cornered — Grog and Whisper trade, and **Kindred is
displaced with nowhere to go.**

Worth noting Kindred is a poor fit for Grog's slot for exactly the reason Zero
Hour was: it rewards a player with 2+ enchanted dice, which a night-one player
does not have. Moving it to slot 0 recreates the problem we just solved.

- **Kindred takes Grog's vacated slot anyway** — no; same no-op failure.
- **Kindred swaps with Aldric's Still Waters (slot 5)** and Grog gets Last Call
  back — Kindred stays late, Still Waters moves one slot later. *Recommended if
  the intent was "Zero Hour goes late", since it keeps all three enchant-facing
  badges in the late half.*
- **Kindred retires** and Whisper's Counterfeit returns — it was never
  validated, so this loses little, but it is a fourth rule change.
- Or name the boss you want rather than the slot, and I will take it.

### Q3. Retuned Last Call — what are the numbers?

The ruling restores Grog's Last Call *"with corrected numbers"* because it
*"only tested weak on magnitude, not on the idea itself."* It is currently dead
code in the file (an `if(false)` block from when Zero Hour replaced it), so
reviving it is cheap — but the retune is a design number I should not invent.

Original: banks under 500 score zero. Options:
- **Raise the floor** (e.g. 800), so it bites more often against Grog's target
  of 3,700.
- **Scale the floor with the target**, so it stays meaningful if targets move.
  *Recommended* — it is the version that survives the target-curve work in C3.
- Keep 500 and accept it as a gentle first lesson.

### Q4. Boss win/loss counters — per-run or across runs?

The lore doc asks for *"two independent stage counters per boss (times lost to
them, times beaten them)"*. Every other counter in this system is per-run and
resets, and the doc's own patron-progression section explicitly **rejects**
cross-run memory as contradicting that.

But within a single run you fight a given boss once, twice if you lose and
retry — so per-run these are almost always 0 or 1, and the stage-1 lines
(*"Back again? Some folk never learn the shape of a losing streak."*) would
almost never fire.

- **Cross-run**, persisted like feats. The lines read as written, but it is the
  first cross-run state in the dialogue system. *Recommended — the stage-1 copy
  is plainly written for a returning player.*
- **Per-run**, consistent with everything else; accept that stage-1 lines are
  rare and only appear on a boss retry.

### Q5. Does the `greeting` pool apply to generic patrons too?

The new rule: greeting is *"mandatory and exclusive on a patron's first-ever
encounter in a run"*, with personal content only from the second encounter.

Named patrons have a stage counter, so "first encounter" is well-defined. Most
seats are **generic** algorithmic patrons with no identity that persists — for
them every encounter is a first encounter, so they would never say anything but
a greeting.

- **Named patrons only**; generics keep the ambient pools. *Recommended.*
- **Everyone**, and generics simply never progress past greeting.

### Q6. Sequencing — the lore build against the eight playtest bugs

The lore work is now a substantial build: a new `greeting` pool, the density
ramp, the draw-rate cut, 72 trait-reaction lines, 158 win/loss lines with new
boss counters, and a placement move to in-match pauses. The table holds 371 rows
today; this roughly doubles it.

Alongside it sit your eight playtest notes — several of which are "nothing
happens when I do X" bugs (cards, NPC cards, the missing relic).

- **Bugs first, lore second.** *Recommended* — dialogue on top of a game where
  Honeytrap may not fire is decorating a broken room.
- **Lore first**, since it is specced and ready to write.
- **Interleave** — the cheap lore items (draw rate, greeting pool) alongside the
  bug work, the big content pass after.

### A correction, not a question

The lore doc says the seed six *"remain unseatable until they have portraits"*
and that scaling past 24 is *"the same kind of blocked."* **That is stale.** You
sent those portraits and they went in — `PT_ART_POOL` holds **30** names, all
seatable. Ferrand included, which the doc specifically wanted, since his
conditional Grog-beaten line is the system's own worked example. No art blocker
remains on the named cast.

---

## A. Ratify (or overturn) three calls I already shipped

These are live in the build right now. I made them because the work couldn't
proceed without a decision and none of them was ruled — but they're yours to
reverse, and reversing costs minutes.

### A1. Corvus's Ledger now pays +300 a bank. Keep it?

Gating Starstone by mechanic string rather than `mat==='starstone'` meant the
relic started paying. **It has never paid** — nothing in the file read that
mechanic, so the code comment claiming "the +300 rides the starstone_bonus
mechanic in scoring" was false, and its printed "Every bank +300" has never been
true in any build.

So this repairs a promise the master brief still makes (§6, relics). But it's an
unmeasured buff to a boss relic, landed inside a balance pass that was
*removing* power.

- **Keep it live** *(recommended)* — it's a documented promise, and it now obeys
  the same kept-and-scored gate as Starstone, so it isn't the old free money.
- **Scope it back to Starstone** — one clause. The Ledger stays broken until the
  pricing pass.

### A2. Hot dice can pay the same Starstone die twice. Intended?

Your ruling says "part of the KEPT AND SCORED selection that bank" — it doesn't
say once per die. If a Starstone is kept and scored, hot dice clears the table,
and it's kept and scored again in the same turn, the bank pays 1000 for one die.

- **Per participation** *(recommended, and what's shipped)* — matches how Amber's
  triple bonus and every per-commit card bonus already pay. This is the **only**
  case where the new rule pays more than the old one; everywhere else it's a
  strict nerf.
- **Once per die per bank** — costs a `lane` stamp on the kept row and a
  cross-row pass. Doable, but it's a rule you'd have to teach.

### A3. "Scored" means the non-icon half, not the engine's `used` array

Narrow case: with a consume-extras card live (Bookends, Twin Fury, Sevens Gift,
Lucky Seven, The Ladder, Ascending) the scoring engine relaxes its
all-dice-must-be-used check, so a genuinely unused leftover Starstone can ride
along in the keep and get paid.

- **Leave it** *(recommended)* — rare, and the exact fix means changing
  `scoreSelection` to return which dice it actually used, which touches the
  scoring core in a balance pass.
- **Fix it properly** — I'd want to do it on its own, not bundled.

---

## B. Your brief asks for these and doesn't answer them

### B1. First Strike — keep the reduced version, or retire it?

Your words: *"this is weaker and less interesting than the original race concept
— worth a real decision on whether it's still worth keeping in this reduced form
or should retire back toward something else, rather than quietly shipping a
downgrade nobody signed off on."*

The original was a race the opponent structurally cannot enter, so it collapsed
into a freebie. What's left is: first lane-targeting icon you fire reveals the
opponent's six-lane layout.

- **Keep the reveal** — honest, cheap, and information effects don't need
  balancing.
- **Retire it and give Corvus something else** *(recommended)* — see B2; the two
  are the same hole.
- **Wait for opponent-side enchants** — then the original race works. That's a
  real feature, not a patch.

### B2. Corvus's economy tax has no home

In Arrears was the only gold-drain in the eight badges. Nothing taxes gold now,
and your brief flags it as "not solved by this rework". Combined with B1, Corvus
currently has no distinctive rule at all.

- **Fold the tax back into First Strike** *(recommended)* — one badge, one
  identity: it costs gold and buys information.
- **Leave it** and accept no badge touches gold.

### B3. Do I run harness passes on the five unvalidated Break rows?

Open item 4: only Obsidian's row has numbers. Amber (now corrected), Starstone,
Silver, Jade and Vagabond are unvalidated proposals. Vagabond's especially — you
noted it's "a bigger effect than the old vague wording implied, deliberately".

- **Yes, run them** *(recommended)* — it's a contained harness job.
- **Not yet** — wait until the pricing pass so it's one measurement pass.

---

## C. The bigger open ones

### C1. Preserve is built and never applied. Do we finish it?

Fifteen of sixteen routes pass. The whole file contains **one** occurrence of
`_preserved` — the guard. `G._famPreserve` is `{val, pts, crack}`: no die, no
lane. So a card whose entire promise is *a die you can look at, sitting in amber*
is currently a points bonus, and the rule that a preserved die can't be Broken
guards a state that cannot exist.

Finishing it costs the amber casing art plus a pick-a-die targeting step (your
ruling: the player chooses, not an auto-pick).

- **Finish it** *(recommended)* — it's the most-specced unbuilt thing in the game.
- **Cut the promise back** to what it does — a points effect — and reword the card.

### C2. Refund the brand when its die is replaced?

Buying a die silently deletes that slot's brand, no refund, no warning. So the
correct purchase order is dice-then-brands, which is exactly the order that
guarantees you never reach brands: a dedicated shopper reaches **2.0 of 6**.

- **Refund it** *(recommended)* — fixes the ordering trap on its own, independent
  of any pricing decision.
- **Wait for the pricing pass.**

### C3. Difficulty is flat from tier 3 to tier 7

Night-1 win rate at tiers 3–7: 30.8 / 33.0 / 36.4 / 33.9 / 32.3. Late nights
aren't harder, they're **longer** — cap-decided endings go 0.3% → 85.5% because
targets climb 5,000 → 9,500 while opponent bank barely moves. Your own master
brief says "Tune TARGETS down before inflating player scoring."

- **Raise NPC aggression with tier** *(recommended)* — both sides climb, the race
  comes back.
- **Lower late targets** — what the brief literally instructs.
- **Accept cap endings** and give the cap a real presentation.

### C4. Should I re-run the sim?

Every number in `SIM_RESULTS_2026-07-31.md` predates: the zero-point sweep
removal (worth +80.5 points on its own), the Trade harness fix, and today's five
rulings. **Directions are still safe; magnitudes are not.** Nothing should be
tuned against those numbers as they stand.

- **Re-run now** *(recommended)* — otherwise the next balance decision is made on
  a dead baseline.
- **Wait** until Preserve / pricing land, and do one pass.

---

## D. Cheap, and I'd just do them — say no if you disagree

1. **Turn audio on by default.** It's force-muted on first touch behind a
   one-time flag. Every feel assessment so far — mine included — has been of a
   silent game.
2. **Land the victory headline.** Still reads "LAST ORDERS RUNG"; the correct one
   was already ruled. This is the build catching up, not a question.
3. **Audit the rules screen.** It's the only teaching surface and it teaches six
   things the code doesn't do — including *"Losing to a patron costs nothing"*
   (it costs a seat) and patron gold figures that are 3–4× wrong.
4. **A message queue for `famLog`.** The whole game speaks through one line that
   holds one message and lives inside the match screen — so two effects firing
   together means one was never announced, and anything firing in the shop or
   loadout is announced into a hidden div.
5. **Retire the BOOKKEEPER feat** (or restore Bookends). It awards for "Bookends
   pays three times in one match" and Bookends was collapsed into Vanguard, so a
   player can see it and never reach it.

---

## E. Two things that are yours, not mine

1. **Your prop template crosses the brief's exclusion zone.** §2 bans props from
   the central band x 15–85%; eight of your twelve have bounding boxes that cross
   it. The dice band is clear and the composition reads well — and the brief
   describes a *procedural* anchor scatter while the shipped system deliberately
   lets hand-made templates win. I didn't move your art. Want me to?
2. **The app-wide backdrop still stretches.** `body::before` uses
   `background-size:100% 100%`, scaling both axes independently — the exact fault
   the match rule one block below records fixing for itself. I left it because
   that rule frames *every* screen, and reframing every screen isn't what
   "update for matches" asked for. Change it?

---

## Not questions — just so you know they're done

Amber is a one-shot. Starstone gates on kept-and-scored. A borrowed die is an
illegal Break target. Still Waters hushes by family. Kindred's doubling is
documented per enchant. All measured, all deployed.

Plus one bug your rulings made *more* reachable, found and closed: banking with a
Break armed and nothing left to break counted the keep twice — **16,000 banked
instead of 8,000.**
