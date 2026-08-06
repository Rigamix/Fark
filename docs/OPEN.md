# OPEN — questions and blockers

The only file you need to read. Everything has my recommendation, so **"yours"
is a valid answer.** Answered items are deleted, not marked — this stays short.

**One decision: §0.**

---

## 0. What does a rival-turn card mean when a BOSS holds it?

Four of eight opponent seams now raise (`turnStart`, `roll`, `bust`,
`bankBonus`, plus `bank` which already did). Sized per seam in
`docs/REWORK_MEASURED_2026-08-03.md`. What is left splits three ways, and only
one of them is a question for you.

**`commit` — needs its own scoping pass, not a decision.** Ten genuinely
different sites: the rival re-scores under fog, encore and reprisal variants.
Guessing at how to unify them would repeat the `seatCommit` mistake at a new
site. I can do that pass; it just is not a gate flip.

**`deadRoll` — needs new opponent behaviour.** The rival's turn never asks "did
this roll score nothing". Nothing to wire until the NPC can have that concept.

**`rivalTurn` — this one needs your answer, and it is genuinely ambiguous.**

The card is declared on your turn and pays on the rival's. **Held by a boss,
"the rival" is you** — so its moment is `endPTurn`, not `runOppTurn`, and its
meaning inverts with the holder.

`ill_omen` is the live example: *"declare they will bust this turn. Right: take
800 from them. Wrong: they gain 400."*

- **Mirror it** — the boss declares you will bust, and takes from you if you do.
  Symmetric, and it makes the boss's turn a thing you play *around*.
- **Boss-side only on its own turn** — the boss predicts its own outcome. Reads
  oddly: a prediction about yourself is a bet with no read.
- **Never give bosses this shape at all** — some cards are player-only by
  nature, and this may be one.

*My rec: mirror it.* The card's tension is "can I read the other player", and
that works in both directions. But "the rival" flipping meaning by holder is a
rules question, and picking whichever interpretation compiles is exactly what
this should not be.


---

## 1d. The sim re-run — deltas are in, and they are large

`docs/SIM_RERUN_2026-08-03.md`. Not acted on, per your ruling. The three that
matter:

**Win rate on an un-upgraded build collapsed ~4x.** Tiers 3–7 were
`30.8 / 33.0 / 36.4 / 33.9 / 32.3`; they are now `8.1 / 8.0 / 8.9 / 11.1 / 8.2`.

**Cap endings start much earlier** — 55.4% at tier 3, not the 0.3% reported.

**And the mechanism is now visible:** median turns pins to the cap from tier 3
and never moves, while player bank plateaus (1,971 → 1,933 across five tiers)
and opponent bank keeps climbing (5,727 → 6,436). The ladder scales; a held-still
player does not.

Also: **agent spread narrows as tiers rise** (60.9 → 23.6), so how well you play
matters *less* the higher you climb — the strongest support yet for "longer, not
harder".

**Aggression was ruled and shipped** (`8f04cc1`, +0.06 across all eight tiers,
capped at .95). Result **inconclusive** — see `docs/AGGRESSION_2026-08-03.md`.

**And the table above needs a caveat it did not have.** Every figure in it is
**one seed**. Measured since: `spread` carries ±3–6 of seed-to-seed noise per
tier and ~10 on the t0→t7 trend. The narrowing claim survives — a ~30-point
fall clears that comfortably — but the specific numbers were never a range.
Win rates and bank figures in the same table come from the same single run and
deserve the same caution.

**What is still yours:** whether to spend 5–6 seeds per side confirming the
aggression bump, and whether to pull either of the other two levers (lower late
targets, let player scoring grow). The brief's ordering instruction still
stands — *"tune TARGETS down before inflating player scoring"*.

---

## 1e. The old roster — answered by the file, and it was already ruled once

You were right that "unused on every path I drove" isn't "unreachable on every
path that exists." It's checkable, and the answer is **retired, deliberately,
and the same call you just made was made once already.**

`PROTO_NOTES.md`, P1b: *"~330 old effect sites now inert; physical deletion
deferred (dead code, no behavior)."*

**It's held dead by three one-line stubs** — a `return []` on the first line of
`effectiveCards`, `initMatchScreen`'s `pCards`, and `generateOppCards`. The
twenty lines below each stub still read the old pools and still work.

**Not legacy-by-omission.** Zero definitions added, removed or edited since the
family engine landed; `FAM_CARDS` moved 12 times over the same span.

**One correction to my own number:** it's **133** cards, not 233. I'd counted
`{id:` matches across the whole file, which swept in boss tells and NPC entries.

**Tagged, not deleted**, per your call — and the tag is enforced:
`apv_legacy_retired.js` *calls* all three stubs (a commented-out `return []`
still greps as a `return []`) and fails if any starts dealing again.

**The one thing that genuinely isn't deletable:** NPC cards come back in P5 as
*family* cards, so the authored boss pools are the design record of what each
boss's cards mean. `tamper` is already blocked on the same phase.

**Archived too**, on your call: 157 files now at `assets/_archive/Card_ART/`,
moved with `git mv` so it reverses in one command. Nothing open here.

---

## 2. Early-game signal — waiting on a playtest, not on reasoning

Restoring the brief's 24 feats removed every feat that fired in a new player's
first hour. Ruled: nothing goes back into the feat list. The proposal is that
dialogue beats already do that job — greeting tiers, first backstory unlocks.

**Needs someone to play it.** No further argument settles it.

---

## 3. `assets/` — an art-scope call, with the risk sorted

47 live references into the previous game's tree have no replacement. Your
framing, recorded so it isn't re-derived as an undifferentiated 47:

| Group | Count | Style-mismatch risk |
|---|---|---|
| Fonts | 8 | **Lowest** — no "previous game" visual signature |
| Audio | 3 | **Lowest** |
| Character portraits | 9 | **Highest** — a player looks straight at these |
| Match frames | 8 | **Highest** |
| Night_Art UI set | 10 | **Highest** |
| Environment / menu | 9 | mixed |

**If there's only room for a subset, it's the 27 in the high-risk rows.**

---

## 4. Unplayed numbers — flagged, not trusted

Last Call's 800, and most of the restored feat conditions. They read real state
and render, but only HIGH ROLLER has fired through a live match.

---

## 5. The `ill_omen` mirror needs a value that doesn't exist yet

You ruled: mirror it, trigger and payoff flipping together. **The moment is
there; the payload isn't**, and that is a design call, not a build detail.

A boss-held `ill_omen` has to pay when the *player's* turn resolves. That is
`endPTurn` - which zeroes `G.turnPts` on its first working line, has an earlier
bust path that clears it sooner still, and **records nothing about whether the
turn ended in a bank or a bust**. Six call sites, both endings.

So the seam needs one new thing: **what the player's turn was worth, and how it
ended**, available at the moment it ends. Same missing value `commit` needs.

**The question is only whether a bust counts as a turn worth zero, or as no
turn at all.** They give different cards. Once that's settled it's one scoping
pass covering both seams.

---

## 7. `challenge` has the same bug on the PLAYER side — and fixing it is a third difficulty change

P466 fixed the rival being over-charged. Measuring the other side to tabulate it
found the mirror image: **the player can be under-charged to nothing.**

The bank is added to `G.pPts` *after* the challenge branch runs, so the player's
`Math.max(0, G.pPts - penalty)` clamps against the **pool alone** and ignores the
bank about to arrive.

| pool / bank / penalty | player loses | rival loses |
|---|---|---|
| 1000 / 200 / 500 | 500 | 500 |
| 100 / 1000 / 500 | **100** | 500 |
| 0 / 1000 / 500 | **0** | 500 |

**With an empty pool the challenge does nothing at all**, while printing
`LOST 500`. Same shape as the boss bug — the message vouches for the error —
pointing the other way. And it bites hardest early in a match, which is exactly
when a low pool plus a big bank is normal.

**Why this is not shipped already.** The boss fix was unambiguous: the code took
*more* than it announced. Here it takes *less*, which could be read as
deliberate mercy. And fixing it makes **the player** harsher — a third
difficulty change in one session, on top of the two in §6, which is precisely
the accumulation you just asked not to let blur.

**The ruling:** does the penalty apply against pool + bank, like the rival's, or
is the player's leniency intended?

- **Apply against both** — mirrors the rival, matches the announced number, and
  the card starts working when the pool is empty. Player gets harsher.
- **Leave it** — then the message should stop claiming a number it will not take.

**This blocks the `challenge` table row**, and only that. The row cannot express
"the same rule from two seats" while the two seats genuinely clamp against
different things — that difference *is* the question.

---

## 5b. CLOSED — but read why, because it is not a clean bill of health

The stated reason was: the sim runs no patron card effects, so its difficulty
numbers cannot be trusted. **That reason is disproven.** `generateOppCards`
begins `return [];` — a P1-cutover stub — so `G.oCards` is empty **in the game
too**. The sim ran no patron card effects because there are none to run.

**The precise closure: the sim was faithful on this specific axis because
nothing exists on either side for it to be unfaithful to.** That is not the same
sentence as "the sim was fine".

**Still real, and untouched by this:**

- `F.oppTurn` reimplements the turn loop rather than calling it. P470–P472 moved
  the *card effects* to shared code, which is a prerequisite for P5, not a fix
  to a live gap.
- `spread` is `max − min` over four agents. Sound for "these are equal" and for
  a landslide; **unsound for a mid-sized delta**, which is the regime the
  aggression pass used it in. See `SPREAD_AUDIT.md`.
- Four agents, and a 4-agent spread is not comparable with an 8-agent one.

**So: no longer a stop on the grounds given. Not a warrant to trust a
mid-sized difficulty delta from it either.**

---

## 8. `blessed_dice` / `crown_authority` say "reroll", the code wipes

Found by reading, in the card audit's last pass. Two top-tier cards (Ambrose,
Whisper) whose every text field promises a **reroll**:

> "forces you to **reroll** every die you selected — scoring or not"

The whole implementation is `G.kept=[]; G.turnPts=0;` plus the **bust** sound,
the **bust** haptic and the bust shake, with the message "KEPT DICE WIPED!".
**No reroll happens.**

A reroll returns new values and a chance to keep scoring. A wipe takes the dice
*and* the accumulated turn score — mid-turn on 800 kept points, the difference
between a gamble and a guaranteed loss.

**The unusual part:** the code, the sound and the in-game message all agree with
each other. The card's own description is the outlier — and it is the one thing
a player reads before deciding whether to fear the card.

**The ruling:** does the text change to "wipes your kept dice and turn points",
or does the implementation start actually rerolling? Both are defensible and
they are very different cards. Detail in `CARD_AUDIT.md` pass 6.

**Not blocking anything.**

---

## 9. CLOSED — fixed in P480. Nothing needed from you.

Ruled "fix now, before opponent enchants". Done: all four `matchDice` removals
now splice `_enchArr`, following Break's existing pattern. Kept below for the
record because the second symptom is worth remembering — one missing splice also
made resuming a match discard the whole `_diceOut` record, so the "dice out"
seats vanished from the loadout. One bug, two faces, neither announcing itself.

<details><summary>original entry</summary>

### Enchants land on the wrong die after a seizure — live, two pooled cards

`_enchArr` is indexed by lane. **Exactly one place** splices it alongside
`G.matchDice` (Break, L18782). Three others remove a die and leave it alone:

- **`royal_seizure`** (Whisper) — `steal_die` / take_best
- **`blessed_confiscation`** (Ambrose) — `steal_die` / take_and_use
- Sacrifice — obsidian shatter

Splicing `matchDice` shifts every lane above the removed one, so after any of
these **every enchant above that lane applies to a different die**. No error, no
message; the brand moves to a neighbour.

**Not a design question** — this is wrong under any reading. The only reason it
is filed rather than fixed is that the two `steal_die` sites record the enchant
in `G._diceOut` for restore at match end, so the fix must splice the live array
without breaking that restore, and **that restore path has not been read yet.**

**The ask is only: fix now, or after the opponent-enchant work?** Either is fine;
it is live either way. Detail in `OPP_ENCHANTS_SIZE.md`.

</details>

---

## 10. What should a persona's KEEP look like? — the one real question here

The plumbing to make the NPC choose its dice is sized and ready
(`NPC_KEEP_WIRING_SIZE.md`). What it needs is a policy, and picking one by
default would set the template every other persona then gets built against —
so it is worth your read rather than my guess.

### First, what is actually in the file — because it is not what the proposal assumed

A spread was suggested of **greedy / reckless / steady / orderly / cunning**.
**None of those five exist in the code.** What exists is two different axes:

| axis | values | what it steers today |
|---|---|---|
| `PERSONAS` key (6) | `ones` `triples` `straights` `aggro` `hoard` `combo` | which **cards** it draws (`tags`), which **die materials** it gets (`dieBias`) |
| `behavior` (3) | `safe` `chase` `normal` | **when it banks** — and only that |

`behavior` is read **exactly once**, at L27295, and its entire effect is nudging
`agg`, the banking eagerness. **Nothing in the persona system touches which dice
get kept.** The comment above `PERSONAS` says `behavior` "drives the Phase-3 turn
AI", which reads broader than it is.

So keep-choice is genuinely empty ground. There is no existing behaviour to stay
consistent with — which is freeing, but it also means whatever goes in first
*is* the convention.

### The part of the proposal that was already right

*"Orderly could mean 'always the same category of hand' — straights over triples
— rather than a score threshold at all."* **That is already the shape of the data.**
`straights` is `tags:['STRAIGHTS','COMBO']`; `triples` is `tags:['TRIPLES','COMBO']`.
The instinct that one persona wants a *category* rather than a *threshold* matches
the axis the file already has.

Which sharpens the question considerably.

### The question

**Does keep-choice hang off the risk axis, the category axis, or both?**

- **Risk only (`behavior`)** — `safe` keeps more and banks the buffer, `chase`
  keeps the fewest scoring dice to maximise live rerolls, `normal` takes maximal.
  Three temperaments, immediately legible, reuses a field that already exists.
  But all six personas collapse onto three keep styles.
- **Category only (`tags`)** — `straights` holds a 1 and a 5 hoping to complete a
  run; `triples` breaks up a straight to chase a third of a kind. Six distinct,
  recognisable habits, and it makes `tags` mean something at the table rather
  than only in the draw pile. Costlier: needs a notion of "hand I am building
  toward", which does not exist yet.
- **Both** — category picks *among* candidates of similar value, risk decides
  *how much* to keep. Richest, and the two axes are already independent in the
  data. Most work, and hardest to attribute when a difficulty delta shows up.

### The two I would not guess at

**`aggro` and `hoard`** are the awkward ones, the way `cunning` was in the
proposal. `hoard` reads as a *banking* stance, not a keeping one — it may simply
have no keep opinion, which is a fine answer but worth saying out loud rather
than inventing one. And **`cunning`'s "vary specifically to be unpredictable" has
no home in the current data at all** — it is a different kind of logic, not a
point on either axis, and would need its own shape. Nothing in `PERSONAS`
currently expresses "be inconsistent on purpose".

**Nothing is blocked on this that I can measure my way past.** The wiring, the
seat fix, and the harness change are all decided and ready; only the policy is
waiting.

---

## Everything else you answered is now work, not a question

Tracked in `NEXT_SESSION.md` and being built. Nothing there needs you.
