# What I need answered

Everything here is answerable in a word or two. Each has my recommendation, so
"yours" is a valid reply to any of them and I'll take it.

Ordered by whether it's blocking me, not by size.

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
