# OPEN — questions and blockers

The only file you need to read. Everything has my recommendation, so **"yours"
is a valid answer.** Answered items are deleted, not marked — this stays short.

**Nothing is blocking.**

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

## 1c. Two card faces are drawn that no card can use

`Art/Assets/Cards/Silver/card_face_ward.png` and `card_face_insurance.png` — both
also already optimized into `assets/cards/`, so they are one card definition away
from rendering. But:

- **`ward` is an enchant, not a card.** It's in `ENCH_GRID` alongside tithe,
  snare and break. Nothing in the card roster has that id.
- **`insurance` doesn't exist anywhere in the game.**

Silver has 4 cards built (fair trade, reprisal, retort, steady hand) and 6 faces
painted. **Were these two meant to be Silver cards?** If ward was drawn as a card
before it became an enchant, the file is spent work and should be retired so the
next person doesn't try to wire it up. If Silver is meant to be a 6-card family,
that's two cards to design.

*No recommendation — I can't tell which of those happened from the files.*

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

## 1e. The previous game's card roster — is any of it meant to survive?

You flagged old card art on screen. Chasing it down found something bigger than
the art.

**The live game doesn't use it.** A full played match makes **zero** requests to
`assets/Card_ART/` and **zero** calls to the function that loads it. Family cards
render your new art correctly. The old art I screenshotted was on the **draft
screen, which is dead** — its only reference is the `case 'draft'` line inside
`showScreen`; nothing calls `showScreen('draft')`. I opened it by hand.

**But 233 old cards are still defined**, with 147 art files, and five surfaces
still reference them in code (the card bar, the mini-card, end-of-match draft
slots, the pouch slot, the boss loadout). None of the five fired during a full
match — but "didn't fire in the one run I drove" is weaker than "can't fire", and
I can't get to "can't" without knowing your intent.

**Is the old roster retired?** If yes, this is a large, clean deletion — 233
definitions, 147 art files, three dead screens (`draft`, `bossreward`,
`reshuffleDraft`). If some of it is still meant to be live — the NPC/boss cards
are the likely candidate, `her_lucky_coin` and `grogs_bump` are Grog's — then
those need new-style art, because two of them 404 today.

*My rec: tell me which of the 233 (if any) survive, and I'll delete the rest.*
Not doing it unprompted — that's a lot of authored content.

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
