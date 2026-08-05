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

## 5b. The sim's opponent turn — RULED: build it, sized

**Confirmed as real work and now sized** (`SIM_OPPTURN_SIZE.md`): it is a
shared-function extraction, not a rewrite. All nine card branches separate
cleanly at statement level; the turn *loop* stays reimplemented because it
genuinely is an animation chain. Only the effects move, into an
`_oppBankEffects` both `finOpp` and `F.oppTurn` call.

**Still a stop until that lands:** no difficulty number from this sim should move
a design decision, because the patron cannot currently benefit from its own
cards.

**Three things to settle during the build, not before:** whether `FSIM.quiet()`
already suppresses `triggerCard`/`spawnPop`; where in `finOpp`'s order the
extracted call belongs (it must match in both, or the sim measures a different
game again); and a same-seed before/after, since patron strength will rise and
that must stay attributable.

---

## Everything else you answered is now work, not a question

Tracked in `NEXT_SESSION.md` and being built. Nothing there needs you.
