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

**The question: is the opponent model faithful to the real opponent turn?** I
cannot answer it from inside the sim — that is the one thing it cannot check
about itself. It matters either way:

- **If it is faithful**, the ladder really is this hard and the fix has to be
  player-side scoring, not targets — the three levers already ruled would all
  have shipped as no-ops.
- **If it is not**, the whole table is fiction and the retune would have been
  tuned against an artifact.

**My rec: settle it before building any of §1.** Measure the *real* opponent
turn in the live game at night-6 gear and compare its points-per-turn against
the model's 688. One number decides it. Roughly half a day; everything in §1
waits on the answer, and the honest reason to wait is that four consecutive
ruled levers already turned out inert against this instrument.

One known gap in the model regardless: it has **no hot-dice rule** (`hot`
appears zero times in it), while the player's real engine does. The keep
policies *are* exercised — via `_oppChooseFrom` — so P495 is genuinely measured.

### 1b. `challenge` is broken on the PLAYER side too

Law 6 has no stated exception here — a bug, to be closed on correctness grounds.
But it is also a difficulty change, and the ladder is already too hard
everywhere, so it lands **in this batch, measured with the rest**.

### 1c. `blessed_dice` / `crown_authority` say "reroll", the code wipes

The block un-keeps the rival's dice, sets `total=0`, and announces *"KEPT DICE
REROLLED!"* without re-rolling a single value. Build the real reroll; do not
reword the card.

**Correction to the original ruling, which assumed the wrong direction.** These
were taken to be boss cards punishing the player, and therefore a softening
lever for nights 7–8. They are not. There is **no NPC firing path at all** — the
only activations are `activateCrownAuthorityPlayer` / `activateBlessedDicePlayer`,
which arm it against the *rival*. So it is a **player weapon**, the wipe is
*stronger* than an honest reroll, and fixing it makes the game slightly
**harder** — which is exactly why it must be batched rather than shipped as
relief.

---

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

## Not blocking, for your awareness

- **Pages deploy is stuck behind a GitHub outage.** Actions and Pages both still
  at `major_outage`, failing on `Invalid actions OIDC token`. Nothing fixable at
  our end — the newest push did not even queue a run.
  **Last successful deploy: 15:32Z. Four runs since have failed.**
  Everything is safely on `origin/fark`; only the publish step is stuck.
  Measured, not assumed: the live `fark_proto.html` is **2,073,103** bytes
  against **2,076,799** in `origin/fark`, and the marker
  `numDice=Math.max(1,G.numDice-1)` is **absent live** while `_laneOf` and
  `noble:'combo'` are present — so the live build predates P504. The player
  therefore still has the hot-dice lane bug.
  It will go out on the first push after recovery. **Verify with that marker
  grep against `fark_proto.html`, never a green build** — and note `index.html`
  is only a redirect stub, so grepping the site root always looks empty.
- **Four model assumptions remain untested** — 65% patron win rate, boss beaten
  first try, buys the dearest die in stock, no enchant/tavern gold. None *looks*
  load-bearing, but that is an impression rather than a measurement; the same
  sensitivity method settles any of them if a retune leans on one.
