# Effect system — Phase 1, the inventory

Read out of the running game (`tools/effect_inventory.js`), not off a document.
Self-contained; paste it on its own.

**69 items, not ~50.** And the headline is not the count.

---

## 0. The headline: the bus already exists, and it already covers 20 of 29 cards

The plan is written as though a trigger bus has to be designed. One is shipped.
`CFX` — the family-card effect table — dispatches on **seven hooks**, and they
are the vocabulary someone would otherwise spend Phase 3 inventing:

| Hook | What fires it |
|---|---|
| `canUse` / `use` | player activates a card |
| `roll` | a roll resolves |
| `bank` / `bankBonus` | a bank resolves |
| `turnStart` | a turn begins |
| `bust` | a bust resolves |

**20 of the 29 live family cards route through it. The other 9 are hardcoded
at call sites** — `bloom`, `cultivate` and `vanguard_f` live inside
`famCommitBonus`; the five tavern cards and `for_keeps` are wired wherever they
happen to act.

That reframes the migration. It is not "build a bus and move 50 things onto it".
It is **"finish a bus that is 69% done, then decide whether the other four
content types belong on it at all"** — which is a much smaller and much better
understood job, and it changes what Phase 3 is for.

---

## 1. What exists, counted

| Group | Live | Notes |
|---|---|---|
| Enchants | 8 | 7 face-branded + Quicksilver, which has no face |
| Break death rows | 6 | one per family; the 7th (mundane) is the *absence* of a row |
| Family cards | 29 of 30 | Tar Pit is retired |
| Table rules (badges) | 9 | 8 worn + Steeped, parked |
| Relics | 8 | |
| Material family traits | 9 | includes jade2/jade3 tiers and two retired materials |
| **Total** | **69** | |

---

## 2. The misfits — the actual output

A clean table would prove nothing except that the vocabulary was written by
someone who had seen the content. These are the rows that fight it.

### 2a. The three the plan predicted — all three confirmed

- **Jade's Break row.** "Claims/replaces the interrupted roll." Not
  `reroll_grant`; a **re-entrancy rule about a roll already in flight**. The
  code comment is emphatic that the alternate reading would create a second
  Ward. There is no "effect" here — there is a decision about what a
  half-executed operation resolves to.
- **Fair Trade.** A **loan with its own clock**, and tier I ("this roll") vs
  tier II ("the turn") are genuinely different durations, deliberately. Plus a
  death rule: if the borrowed die dies, the *lender's* die is gone until their
  next match. Trigger/condition/effect has no slot for a lease.
- **Honeytrap.** "Your next roll pulls one die into matching." A **constraint on
  generation**, not an effect on a result. It reaches forward into a roll that
  has not happened.

### 2b. Six more, found by decomposing

- **Quicksilver is a permission, not an effect.** No face, no `fire`. It grants
  a *capability* ("once per turn you may reroll this die alone"), and the
  trigger is the player choosing to. Every other enchant answers an event; this
  one creates an option. It is already the odd one out in the code — two
  separate tables, `ENCH_ICONS` and `ENCHANTS` — and that split is a shape
  finding rather than bookkeeping.

- **Silver's weighted face table is not an effect at all.** `[1,5,1,5,2,3,4,6]`
  is the die's **base geometry**. The rework brief exempts it from the
  one-face law explicitly. Any effect system needs a place to say "this die's
  distribution differs", and that place is not the trigger bus.

- **Still Waters operates ON the effect system.** It suppresses a family trait
  for the match. It does not fire on a trigger; it changes **whether other
  things fire**. That is Tier-2 in the proposal's own terms, and it is the one
  rule whose correctness depends on the bus existing first.

- **Kindred is five rules wearing one name, and this is the important one.**
  "Double strength" was defined per-enchant, and each meaning is *structurally
  different*: Tithe pays 2× gold; **Ward saves two-thirds instead of a half**;
  Snare halves **twice on the same shot** rather than watching a longer window;
  Snuff and Fog hold their seat for **two turns rather than two lanes**. Break
  and Trade are excluded because no coherent 2× exists.

  **So Kindred is not a multiplier.** The plan's Phase 3 wants to settle "the
  additive-then-multiplicative rule … the one that silently changes numbers
  later". Measured, **there is nothing to multiply** — the only doubling in the
  game is five bespoke per-effect rules that happen to share a badge. Settling a
  multiplier rule now would be settling a question the content does not ask.

- **Zero Hour triggers on another effect firing.** Keeping any icon face ends
  the turn. Its trigger is not a game event but *another effect resolving*. An
  observer, and it needs the bus to exist before it can be expressed honestly —
  today it is a flag set inside `_iconFire`.

- **Four enchants are markers with a lifetime, not effects with a moment.**
  Snare, Snuff, Fog and Trade each mark a **lane** and resolve on the
  opponent's next turn, then clear. They have a placement, a window and an
  expiry. "Effect" captures the payout and loses the three things that actually
  make them work — and Snare's whole design correction was *shortening the
  window* from "until it fires" to "next turn only", which is a statement about
  lifetime, not about effect.

### 2c. Two whole groups that may not belong on the bus

- **The five tavern cards act on the RUN, not the match.** `the_tab` is a
  **debt with a due date** (settled at last orders). `hair_of_the_dog` fires on
  the **next match**. `double_stakes` and `high_table` change the terms before
  a match starts. A match-scoped trigger bus is the wrong home for all five.
- **`for_keeps` is a stake.** Played at sit-down, resolved at match end, and its
  "effect" is a change to the reward screen. Nothing it does is a game action.

---

## 3. Two simplifications, which are the opposite of misfits

Worth as much as the misfits, and easier to act on:

- **Relics are not a category. They are materials with different numbers.**
  Measured: `grogs_tooth` and `obsidian` both dispatch `shatter_bonus`;
  `mabels_thimble` and `amber` both `triple_bonus`; `corvus_ledger_d` and
  `starstone` both `starstone_bonus`. Six of the eight relics reuse a material's
  mechanic. The seventh, `brutus_shield`, is a die **born carrying an enchant**.
  Only `whispers_fang` and `finnicks_palm` have mechanics of their own.
  **Relics do not need their own vocabulary; they need the material one plus a
  numeric override.**
- **Last Call and The Reckoning are the same rule.** Both void a bank under a
  threshold. The only difference is where the threshold comes from — a fixed
  800 vs the rival's last bank. One condition, two sources.

---

## 4. The dividing line nobody had drawn

Of the nine table rules, **four carry a numeric field and five carry none**:

| Parameterised | Bespoke |
|---|---|
| `last_call` (`minBank`) | `zero_hour` |
| `drill_order` (`maxRolls`) | `first_strike` |
| `pickpocket` (`chance`) | `still_waters` |
| `steeped` (`perRoll`) | `kindred` |
| | `reckoning` |

The four with fields are **data**. The five without are **code**. That split is
not a coincidence and it predicts the migration cost almost exactly: the four
are table rows waiting to happen, and every one of the five is in section 2's
misfit list or acts on the system itself.

---

## 5. What this says about the plan

**Phase 3 should be re-scoped before it is built.**

- *"Decide the multiplier rule now even though nothing multiplies yet."* —
  measured, nothing multiplies **and nothing will**: Kindred is five bespoke
  rules. Deciding an arithmetic rule for it would be inventing a requirement.
- *"Build the trigger bus."* — 69% of it is shipped as `CFX`. The work is
  **finishing and naming** it, not designing it.
- **Phase 4's dependency order is right but its first group is wrong.**
  It says enchants first, "newest, best understood, already share `_iconFire`".
  True — but four of the seven are lifetime-markers and one (Quicksilver) is a
  permission, so enchants are where the vocabulary needs its *hardest* new
  concept. **The 20 cards already on `CFX` are the honest first group**: they
  are the ones the existing vocabulary already fits.

**And one thing the plan does not mention at all:** 9 live cards are hardcoded
at call sites with no `CFX` entry — `bloom`, `cultivate`, `vanguard_f`,
`for_keeps` and all five tavern cards. Those are invisible to any migration that
starts from the effect table, and they are exactly where a half-migration would
leave a hole.

---

## 6. What Phase 1 did NOT settle

- **No decision is made here.** This is the map; the re-plan is the next step,
  and the plan's own instruction was *"start with Phase 1 alone and re-plan
  after it."*
- **The 29 cards were decomposed by shape, not by reading every implementation.**
  A card whose `CFX` hooks look ordinary may still do something structural
  inside them. Slow Cook (four hooks: `roll`, `bankBonus`, `turnStart`, `bust`)
  is the most likely to be under-described above.
- **Opponent-side effects do not exist**, so every "affects the opponent" row
  is one-directional today. The brief defers this deliberately; it will change
  the vocabulary when it lands.
