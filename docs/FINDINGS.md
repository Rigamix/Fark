# Fark — findings

Written 7 Aug 2026. Everything below was measured against the running game,
not inferred from reading code. Where something is uncertain it says so.

---

## 1. The difficulty numbers were measured against a fake opponent

The simulator runs the **real game** for the player — it calls the game's own
turn, roll, score and bank functions. For the rival it runs **a separate
implementation written inside the harness**, with its own roll loop.

So every boss win rate produced this session compared the real player engine
against a *model* of the opponent. The harness even says so in its own comment:
"the SIM has its own copy of the rival's scoring."

Scale of the difference, measured by stripping comments and counting
decision-carrying code:

| | real rival turn | harness model |
|---|---|---|
| code after comments | 53,502 chars | 3,207 chars |
| decision identifiers | 131 | 5 |

The real turn's decision code outnumbers its presentation code 131 to 72, so
this is not an animation wrapper — the model is missing most of the rival's
actual decision-making.

**This is the single most important finding of the session.**

---

## 2. What that invalidates

Every difficulty conclusion drawn this session rests on it: the ladder table,
the boss target sweep, the aggression and minBank sweeps, the dice comparison,
the persona work.

Four separate levers were tested and each came back inert or backwards:

- **Boss targets** — inert at nights 6–8. Those matches end at the turn cap 92%
  / 54% / 27% of the time, so a finish line most matches never reach cannot
  matter.
- **Boss aggression** — inert, and backwards. The setting gates "don't bank
  yet", so lowering it makes the boss bank sooner and keep *more*.
- **Boss dice** — not the cause. At nights 7–8 the player is already at parity
  or ahead; the boss carries the two cheapest materials in the game.
- **Player banking threshold** — flat. Raising it from 300 to 1400 changes
  nothing, because bust rate climbs from 0.14 to 0.54 per turn and cancels the
  gain exactly.

Four dead levers in a row was the signal that the cause was not among the
variables being tested.

**One of those four survives the instrument problem.** The player threshold was
measured entirely on the real engine, so "a player cannot buy points-per-turn by
pushing harder" still holds and still constrains any retune. Its win-rate column
does not.

---

## 3. The previous game's card roster is still being dealt — now fixed

Found by launching real matches, because the code comment and the code itself
flatly disagreed and neither deserved to win by assertion.

- The asset registry describes the old 133-card roster as retired.
- The patron generator builds every patron hand out of it, always, from night 2
  onward.

One sweep of nights 3–8 dealt **17 distinct retired cards**: chain lightning,
the hearth, honor guard, the fence, slippery table, even row, the whetstone,
anchor, last stand, finnick's trick, the heir, snake oil, brutus grit,
whisper's veil, tavern cheer, the ledger, prompt hand.

Boss hands were always correct — they draw from the current rival roster.

**Root cause:** an earlier fix lifted a stub that had been keeping every
opponent hand empty. That was right for bosses. It switched the patron branch
on as a side effect, and that branch feeds from the retired roster.

**Fixed and verified:** patrons now draw nothing. All eight nights re-measured
at zero cards, no retired card in any hand, boss draws untouched.

**This makes nights 3–8 easier.** It is a correctness fix, not a balance
decision, and it landed inside a ladder whose numbers are already unreliable.

---

## 4. Card art: 41 cards needed, not 132

The full list is in `docs/CARD_ART_NEEDED.md`, grouped by boss in night order
with each card's effect.

- **41 rival and boss cards need art** — every card reachable through a boss's
  pool.
- **The 30 family cards are complete.**
- **The retired roster is excluded** — those cards are a bug to remove, not 90
  pictures to draw.

A loader was built so this is a drop-in job: a PNG named after the card id,
placed in the cards folder, renders on its own with no code change. When a real
face loads it removes the emoji, the coloured background, the border and the
glow, so the artwork carries its own frame exactly as the family cards do.

The temporary CSS card styling retires itself one card at a time as art
arrives, and should be deleted outright once the list is filled.

**Art optimization is complete everywhere** — cards 32/32, game over 6/6, last
orders 2/2, win 4/4. Nothing is waiting.

---

## 5. What we now know about the model, measured not guessed

Three attempts to find the flaw by reading code were all wrong, because two
independently written implementations share no vocabulary — the real game and
the model express identical hot-dice logic with **zero words in common**. A
search for a name can only tell you whether that name appears.

So both sides were instrumented and their output compared directly.

### The bust table, corrected — RETRACTION

An earlier version of this section reported "the model busts 1.6–6.7× more at
seven of eight nights" off samples of 22–48 turns. **That did not survive.**
With Wilson 95% intervals the model rate sits INSIDE the real interval at five
of eight nights, and CORVUS and WHISPER each rested on a single bust event.

The error was mine and specific: in the same breath as retracting a different
claim as small-sample noise, I called bust rate "a per-turn Bernoulli statistic,
far more stable than mean points". At n≈20–50 with p≈0.1 you expect 2–5 events.
That is not stable.

Three nights were then re-measured deeply, ~200–300 real turns each:

| night | real | 95% interval | model | verdict | small-sample said |
|---|---|---|---|---|---|
| 4 CORVUS | 0.037 (296t) | [0.021, 0.065] | 0.140 | **outside, 3.8×** | 6.7× |
| 5 BRUTUS | 0.160 (300t) | [0.123, 0.206] | 0.300 | **outside, 1.9×** | 2.9× |
| 7 WHISPER | 0.085 (188t) | [0.053, 0.134] | 0.220 | **outside, 2.6×** | 4.8× |

**The divergence is real at these three, and every one had its magnitude
overstated by the small sample — three for three, same direction.** That
consistency is itself evidence the deep samples behave like real data.

The other five nights (GROG, MABEL, FINNICK, ALDRIC, AMBROSE) are
**unestablished**: the model sits inside the real interval and no deep sample
was taken. FINNICK is the firmest of them at 58/149 = 0.389 vs 0.390 and serves
as the control throughout.

**Do not quote a per-night bust gap for any night other than 4, 5 and 7.**

Outstanding hole: 7–15% of attempted turns were dropped as stalls across every
run, and what they were is unmeasured. Both plausible mechanisms widen the gaps
rather than narrow them, but that is reasoning, not measurement.

### Located: post-choice dice release

Three shared-function comparisons, each with Finnick live as a control because
its bust rates already match:

- **Banking decision — ruled out.** Both sides call the same `oppShouldBank` at
  the same rate, in the same states, and get the same answers, at the diverging
  night *and* the control.
- **Keep chooser — ruled out.** `_oppChooseFrom` returns the same dice counts on
  both sides at both tiers.
- **Post-choice handling — CONFIRMED.** Interpretation registered before the
  run: a gap between what the chooser picks and what is actually committed.

| | chosen | committed | ratio |
|---|---|---|---|
| CORVUS model | 1890 | 1890 | 1.000 |
| CORVUS real | 134 | 130 | **0.97** |
| FINNICK model | 1357 | 1357 | 1.000 |
| FINNICK real | 125 | 125 | **1.000** |

The model is exactly 1.000 everywhere — structurally it cannot differ, since
`used` derives straight from the chooser's selection — and that was measured
rather than assumed. The real side releases dice after choosing at Corvus and
not at Finnick, which is the null the hypothesis predicted for the control.

This is the real game's release-singles subsystem (`_canRelease` /
`_minUsefulReroll`), which hands low-value 1s and 5s back to keep dice in play.
The model has no equivalent.

### Identified: it is release-singles, confirmed at a larger sample

Predictions registered before the run, all three held:

| | CORVUS | FINNICK (control) |
|---|---|---|
| turns | 64 | 85 |
| dice chosen | 313 | 322 |
| dice released | **11** | **0** |
| unknown (self-check) | 0 | 0 |
| released faces | **5s 91%, 1s 9%** | none |
| released 2/3/4/6 | **zero** | none |

- Releases are **exclusively 5s and 1s**, and 5s go first — matching the
  source's own "sacrifice cheapest first" sort of `_optionalSingles`.
- **No 2/3/4/6 released at all**, which is the release path protecting the
  components of triples and straights.
- The control released **exactly zero across 322 chosen dice** — not small,
  zero.
- `unknown` is 0 on both sides, so no die was misclassified.

**Magnitude: dominant, probably not sole.** Corvus releases 0.17 dice per turn
against a bust-rate gap of 0.12 per turn (real 0.02, model 0.14). Each release
would have to prevent about 0.7 busts to close the gap alone. A release taken at
one die remaining swaps roughly 67% bust odds for 10-20%, so ~0.5 busts
prevented per release is the realistic figure — covering perhaps 70% of the gap.

So release-singles is the main mechanism and is very unlikely to be the whole
of it. Porting it should move Corvus most of the way and leave a residue; if it
closes the gap *exactly*, that is a reason to look harder, not to celebrate.

---

## 6. What is NOT known, and should not be quoted

**Per-night rival scoring is not stable enough to tune against.** Two runs of
the same instrument on the real engine:

| night | run A | run B | spread |
|---|---|---|---|
| 1 GROG | 558 | 671 | 20% |
| 2 MABEL | 935 | 1100 | 18% |
| 3 FINNICK | 224 | 257 | 15% |
| 4 CORVUS | 735 | 1072 | **46%** |
| 5 BRUTUS | 916 | 1047 | 14% |
| 6 ALDRIC | 852 | 966 | 13% |
| 7 WHISPER | 2350 | 1440 | **63%** |
| 8 AMBROSE | 1843 | 1785 | 3% |

An earlier claim that the model "overstates at three nights and understates at
five" **did not survive the second run** — two of those three nights flipped
direction. That shape was sampling noise at 7–30 turns per night. Only Finnick
is consistently overstated.

An earlier claim that the model "understates by 23–51%" was also wrong as a
general statement — it was one night, one sample.

Also unmeasured: rolls-per-turn on the real side failed to collect, so that
comparison is missing rather than zero.

---

## 7. Second, independent reason the ladder is easier than reported

The gear model works out which dice a player holds at each boss from an assumed
**65% patron win rate** — an assumption from the brief, never measured. Patrons
just lost 3 cards each on nights 3–8, so the true rate rises: more wins, more
gold, better dice at every boss.

Direction is clear, size is not. Measuring it means running patron matches
through the same unfaithful model, which would produce a confident number
needing so many caveats it would be useless.

Two independent paths now point the same way: **the game is easier than the
numbers said.**

---

## 8. Where this leaves the retune

**Blocked, and it should stay blocked.** The three ruled changes — targets
down, the challenge fix, the real reroll — would have been tuned against an
artifact, and two of them were already measured inert against a rival now known
to be too weak.

Order of work:

1. Fix the rival model. The bust-rate gap is the concrete lead.
2. Rebuild the ladder table against it, with enough turns per night that the
   numbers hold still between runs.
3. Then retune, and settle the 65% patron assumption at the same time.

**Deploy note:** everything is safe on the deploy branch, but Actions and Pages
have been in a major outage. The live site predates the hot-dice lane fix.
Verify recovery by checking a known marker inside the game file — the site root
is only a redirect stub, so checking it always looks empty whether the deploy
worked or not.
