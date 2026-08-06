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

### Measured since filing: the lever is much stronger than a threshold

Worth knowing before choosing a policy. The control sweep (`KEEP_CONTROL.md`,
every roll of 1–6 dice) established that **the maximal keep is always the full
set of scoring dice, and it is unique** — the scorer rejects any keep holding a
non-scoring die, so every option is an all-scoring subset and every non-maximal
one scores strictly less.

**So choosing is necessarily choosing to score less now for more dice live.**
There is no free variation between equally-good options; a persona either takes
the maximum or trades points for rerolls. `[1,1,1,5]` is the shape of it:

| keep | points | dice left to reroll |
|---|---|---|
| all four | **1050** | 0 |
| the three 1s | 1000 | 1 |
| two 1s + the 5 | 250 | 1 |
| one 1 | 100 | 3 |
| **just the 5** | **50** | **3** |

A "keep the fewest dice that still score" persona takes **50 and rerolls three**
where a maximal one takes **1050 and rerolls none**. That is not a dial, it is a
cliff — which argues for picking the first policy deliberately, since it sets
the template.

### ANSWERED — the six policies are specified. Two things to check before they are built.

Policies received: `hoard` maximal; `aggro` most-dice-live; `straights` hardest
gamble for completion; `triples` combo-aware; `ones` maximal but never empties
the hand; `combo` calculates points plus value-per-live-die.

**1. Hand type is NOT exposed — confirmed, and it is a small addition.**
`_legalKeeps` returns `{sel, pts, icons, left}`. No type. But the derivation
already exists in `famCommitBonus`:

```js
var _isTriple=Object.keys(_counts).some(v=>_counts[v]>=3);
var _run=1,_best=1; ... var _isStraight=_best>=5;
```

So it is a data addition that must **reuse that derivation**, not write a second
one — two derivations of "is this a straight" drifting apart was five of the
findings in this stretch.

**2. The `straights` rationale rests on a premise the code contradicts.**
The spec says *"a partial straight is worth exactly nothing until it's
six-for-six — there's no partial credit"*. Measured:

| | |
|---|---|
| `123456` six-run | **1500** |
| `12345` five-run | **500** |
| `23456` five-run | **750** |
| `2345` four-run | 50 (just the lone 5) |

**Five-for-six pays 500–750**, and `_isStraight` is `_best >= 5`, matching. So
"gamble hardest because there is no partial credit" does not hold — a straights
persona already banks substantially at five dice. **Worth your re-read**: the
policy may still be right, but its stated reason is not.

`combo`'s value-per-live-die is correctly flagged as needing its own measured
pass; that one is not guessable.

---

### The original question, for the record

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

## 11. CLOSED — ruled yes, fixed and measured in P489. Nothing needed from you.

Rival now scores wilds the way the player does, all seven call sites plus the
sim. Control: 923 bone rolls, **0** difference from before. Parity: `23456` went
50 → 750, the player's exact number, and 0 of 462 jade rolls took anything other
than the better pass. Difficulty, three seeds: **+1.68–41.86%** mean bank for a
jade-holding rival, control pinned at **0** on every seed.

One thing worth knowing for the wiring that follows: the scoring gap is closed
(`scoreSelectionBeatsScoreRoll` 3 → 0), but 32 of the original 38 keep
divergences remain and they are **choice, not scoring** — verified on `11226`,
where both seats now score the whole roll at 400 and the better subset at 1000.
So the keep wiring will still show a jade delta, and that is correct: the wiring
*is* the fix for the choice gap. What P489 bought is that the delta is now
attributable to choice alone. Detail in `WILD_PARITY_FIX.md`.

<details><summary>original entry</summary>

### A jade 6 is worth 50 to the rival and 750 to you

Not a design question in itself; the *fix* is a difficulty change, which is why
it is here rather than done.

**The player's scoring path runs a second pass that the rival's does not.**
Player keeps go through `scoreSelection`, which scores the wild both ways and
takes the better — its comment: *"a Jade 6 could only ever be spent as a wild
and never as a 6… a 1-2-3-4-5-6 straight could not complete because its 6 had
been replaced."* The rival calls `scoreRoll` directly and gets one pass.

That fix reached the player and never reached the rival. Measured over all 462
rolls containing a jade 6:

| | |
|---|---|
| rolls where jade vs bone changes the score | **308** |
| best candidate ≠ the rival's maximal keep | **38 points, 7 dice** |
| worst case | **`23456`: rival takes 50, the dice are worth 750** |

`jade`/`jade2` are both wild and both in `dieBias` (`triples:jade`,
`straights:jade/jade2`) → Brutus and Aldric. Live, not theoretical.

**Why it blocks the keep wiring.** The plan was to route all three keep sites
through one chooser, land it **inert**, and make the persona policy a separate
change with its own before/after. `_legalKeeps` scores via `scoreSelection` — so
routing the rival through it *silently fixes this*, and the rival gets sharply
stronger whenever it holds a jade. A difficulty change hidden inside a patch
whose whole purpose was to change nothing, and the next before/after would have
credited it to the persona choice. §6 exists because that already happened once.

**The ask: does the rival get the wild-as-option treatment the player has?**

- **Yes** → fix it first as its own measured change; the wiring is then inert
  against the corrected baseline and everything proceeds as planned.
- **No** → then `_legalKeeps` must score the rival's candidates single-pass to
  match, so the wiring stays genuinely inert. More work, but it preserves "a
  jade behaves differently in a rival's hands" as a deliberate rule.

Either answer unblocks it. Detail and how the blind spot was caught in
`WILD_SEAT_ASYMMETRY.md`.

</details>

---

## 12. Two persona decisions, measured. My recommendations, both ways.

The six are wired and measured. Bone dice, n=3000 turns per arm, same seed,
`oPts` reset per turn. Control: **hoard and combo delta exactly 0**, bust and
roll counts identical - the wiring changes only what it should.

| persona | mean bank | delta | bust | rolls |
|---|---|---|---|---|
| hoard / combo | 548.5 -> 548.5 | **0** | unchanged | unchanged |
| **straights** | 555 -> 543.3 | **-11.7** | 0.259 -> 0.261 | 2.15 -> 2.11 |
| **ones** | 548.5 -> 427.1 | **-121** | 0.241 -> 0.248 | 2.04 -> **1.89** |
| triples | 555 -> 431.7 | -123 | 0.259 -> 0.347 | 2.15 -> 2.36 |
| **aggro** | 549.7 -> 202.9 | **-347** | 0.249 -> **0.491** | 2.1 -> **3.58** |

### 12a. `aggro` - my rec: SHIP AS SPECIFIED, but know where it lands

The rule does exactly what it says and doing exactly what it says is expensive:
reroll volume genuinely rises (2.1 -> 3.58) and the bust rate **doubles to 49%**,
costing 63% of mean bank. That is not a bug - it is what "keep the fewest dice
that still score" means in a game where busting takes the turn.

**Ship it.** A persona that is genuinely weaker for playing recklessly is a real
design choice, and a roster where every personality is equally strong is a
roster where personality does not matter.

**But it lands on Whisper.** `_BOSS_PERSONAS` maps commoner->aggro (Finnick,
night 3) and **noble->aggro (Whisper, night 7)**. A night-7 boss losing ~63% of
its per-turn scoring is a much larger difficulty change than a patron doing so.
If that is unwanted, the cheapest fix is to keep the rule and let Whisper carry a
different persona, rather than to soften the rule for everyone.

### 12b. `ones` - my rec: DROP THE KEEP RULE ENTIRELY

This one is not costly for a stated reason, which is what makes it different
from aggro. "Never go all-in" pays **121 points** and the data shows it buys
nothing back: rolls go **down** (2.04 -> 1.89) and the bust rate barely moves.
It is giving up value to preserve an extra roll it then does not take.

**And `ones` already has a distinct identity that costs nothing.**
`PERSONAS.ones.behavior` is `'safe'`, and `oppShouldBank` reads it:
`if(_pBeh==='safe')agg=Math.max(0.10,agg-0.10)` - it already banks earlier than
everyone else. That is exactly "reliable, low-drama", implemented on the banking
axis where it belongs.

So the keep-side restriction was a second lever for a personality that already
had one, and the second lever only subtracts. **Recommend `ones` takes the
maximal keep** and keeps its identity in `behavior`.

### Also fixed while measuring these

`straights` was a **no-op** - it differed from hoard on 0 of the 13 rolls (in
692) containing a five-run, because on all 13 the maximal keep already contained
the run. No dice set could have fixed that. Sorting run candidates by POINTS
always picked the one that also swept up every other scoring die. Now sorted by
dice LEFT, so it keeps the run and pushes the remainder as intended -
`112345` takes 500 with a die live instead of 600 with none.

Then the first version of that fix traded `123456` - a complete six-run worth
1500 - for 750 and one live die, chasing a completion it had already made. A
complete run is now taken, not gambled. **The aggregate would not have caught
it**: -40 is what one good trade and one terrible one average to. The examples
caught it.

---

## Everything else you answered is now work, not a question

Tracked in `NEXT_SESSION.md` and being built. Nothing there needs you.
