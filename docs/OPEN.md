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
