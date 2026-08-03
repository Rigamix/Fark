# OPEN — questions and blockers

The only file you need to read. Everything has my recommendation, so **"yours"
is a valid answer.** Answered items are deleted, not marked — this stays short.

**One decision is needed before Phase 4 builds: §0.**

---

## 0. Six run-scoped cards on a match-scoped bus — what should they be?

**This is now six cards, not five.** The five tavern cards — `double_stakes`,
`the_tab`, `hair_of_the_dog`, `marked_table`, `high_table` — plus **`for_keeps`**,
which reading it showed has exactly the same shape: it is armed in the Room on
`S.run._fkArmed`, burns at seat launch, and its payoff **moves a die between
loadouts at match end**. It is armed outside a match and paid in the run's dice;
the match is only when it is observed.

The effect plan flags the problem and never resolves it: **they act on the RUN,
not the match.** The bus they'd go onto is match-scoped — it fires on rolls,
banks and busts, and it is thrown away when the match ends.

So writing them onto it means either giving them a lifetime the bus can't
express, or quietly changing what they do to fit.

**The other two of the ten are settled, no input needed:** `tar_pit` is
**retired** — the code says so outright, its `_famTarPit`/`_oTarPit` consumers
have no writer and are left for a dead-code sweep — and the remaining three
(`bloom`, `cultivate`, `vanguard_f`) are **migrated**, on the new `commit` hook.

**Three ways this can go:**

- **A run-scoped seam** alongside the match bus. Most correct, most work, and
  nothing else needs it yet.
- **Leave the five hardcoded** and migrate the other five now. Honest, and the
  group stays half-done — which the plan warns is the worst state.
- **Confirm they really are match-scoped** and I've read them wrong, in which
  case they go on the bus with everything else.

*My rec: the middle one, with the six named in code as deliberately off the
bus.* Half a group is bad, but a run-scoped card faking a match lifetime is
worse, and the seam isn't worth building for five cards until something else
wants it.

I need your read on what these six are supposed to do across a run before I
pick — this is a design question about the cards, not a code-shape question.
**Nothing else is waiting on you**, and nothing needs approving: everything
else in Phase 4 either resolved by reading or is built and verified.

---

## 1. The rules screen — two calls, and the premise was wrong

The backlog said the rules screen teaches six things the code doesn't do.
Measured, it's the opposite of that.

**The sheet a player can actually reach is correct.** The book icon on the home
screen opens a scoring sheet making 14 claims. I checked all 14 by *running the
scorer* against the hands they describe — 14 of 14 match, including every
doubling step.

**The six wrong claims are in a screen nobody can open.** A four-tab overlay
(Play / Scoring / Dice / Gauntlet) whose only entry point is a RULES button the
home screen renders over — measured not visible. Same shape as the boss reward
screen. So **nothing player-facing is wrong.**

**1a. What happens to the dead overlay?** Eight tabs of authored copy, at least
six claims now false, one `onclick` away from being live. I've marked it in the
code with each false claim named so nobody revives it blind.
*My rec: delete it.* The master brief already rules against reviving it — *"the
pause menu is the ONLY rules-reference surface … there is no innkeep's book
screen; do not rebuild one."* But it's authored content, so deleting is yours.

**1b. The real gap: the sheet teaches scoring and nothing else.** The brief asks
for a *"scoring & your dice"* sheet. The dice half doesn't exist — nothing
teaches materials, enchants, lanes, or why loadout order matters.

Draft below, **not shipped** — this is the entire teaching layer, so it wants
your voice, not mine.

> **Your dice**
> Six dice, yours to change. Materials lean the odds — silver rolls 1s and 5s
> more often, jade turns wild, obsidian shatters for points.
>
> **Marks** A branded face banks nothing and does something instead. Keep it and
> the mark fires: coin pays gold, shield softens a bust, skull breaks a die.
>
> **Order matters** Dice sit in fixed places at the table. Some cards read the
> ends of the row, and some marks reach across to the seat opposite.

Three sections because three is what fits without scrolling. Say the word and
I'll ship yours instead.

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

**No recommendation attached on purpose.** Raising aggression, lowering late
targets and letting player scoring grow are all consistent with this table, and
the master brief already has an instruction on the order of those
(*"tune TARGETS down before inflating player scoring"*). Which lever is yours.

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

## Everything else you answered is now work, not a question

Tracked in `NEXT_SESSION.md` and being built. Nothing there needs you.
