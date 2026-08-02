# OPEN — questions and blockers

The only file you need to read. Everything has my recommendation, so **"yours"
is a valid answer to any of them.** Answered items leave; they don't pile up
here.

---

## BLOCKING — nothing proceeds without this

**1. The effect re-plan.** Phase 1 measured the content and it re-scopes two
phases you already approved. I've written the recommendation into
`EFFECT_SYSTEM_PLAN.md` as banners and not acted on it.

- Phase 3 should drop the multiplier rule and settle **effect lifetime**
  instead. Kindred is the only doubling in the game and it isn't a multiplier —
  "double" means something different for each of five enchants. Nothing
  multiplies, and nothing will.
- Phase 4 should start with the **20 cards already on the `CFX` bus**, not the
  enchants. Four of the seven enchants are lane-markers with a lifetime and one
  is a permission — they're the hardest group, not the easiest.
- Add a group the plan never lists: **9 cards hardcoded at call sites** with no
  bus entry. A migration that enumerates the effect table can't see them.

*My rec: take all three. Then Phase 2 (shared conditions) is the next build.*

---

## DESIGN — yours to call, I won't guess

**2. Where the early-game signal comes from.** Restoring the 24 feats removed
every feat that fired in a new player's first hour. Ruled: nothing goes back
into the feat list. Unresolved: whether dialogue beats (greeting tiers, first
backstory unlocks) actually scratch that itch, or whether circles/gold need to.
*Needs a playtest reaction, not more reasoning.*

**3. Preserve is built and never applied.** Finish it or cut it.

**4. Difficulty is flat from tier 3 to tier 7.** Real, measured, no fix chosen.

**5. Corvus's economy tax has no home** after the In Arrears → First Strike
swap. *My rec: leave it; First Strike carries both halves now.*

**6. First Strike's reduced version** — keep the information-only form, or
retire it? *My rec: keep. Information effects don't need balancing.*

**7. `assets/` has no owner.** 47 live dependencies with no replacement in the
current tree — every font, all audio, nine character portraits, eight match
frames, the Night_Art UI set. Whether those get redrawn is an art decision.

**8. Two stale asset paths** — `Environment_ART/gameover.png` (its only twin is
a `.psd`) and `Menu_Art/Settings.png` (twin exists in the current tree).
Swapping them is a look change. *My rec: swap Settings, leave gameover.*

**9. Bookkeeper's painting is unused.** Ruled: leave it. Flagged only so it
isn't rediscovered as a bug.

---

## RATIFY — shipped on my judgement, overturn if wrong

**10. Corvus's Ledger now pays +300 a bank.** It never paid before; nothing read
its mechanic string. This repairs an always-false promise rather than adding
power.

**11. Hot dice can pay the same Starstone die twice** in one turn. Matches every
other per-commit bonus. The only case where the corrected rule pays *more* than
the broken one.

**12. "Scored" means the non-icon half**, not the engine's `used` array.

**13. Sticky Fingers** now reads Vagabond's break-row steal. *You ruled the
family; the wording is mine.*

---

## CHEAP — I'd just do these, say no if you disagree

14. **Turn audio on by default.** It's force-muted behind a one-time flag, so
    every feel assessment so far has been of a silent game.
15. **Land the victory headline** — still reads "LAST ORDERS RUNG"; the correct
    one was ruled long ago. Build catching up, not a question.
16. **Audit the rules screen.** The only teaching surface, and it teaches six
    things the code doesn't do — including *"losing to a patron costs nothing"*
    (it costs a seat) and gold figures 3–4× wrong.
17. **A message queue for `famLog`.** One line, one message, inside the match
    screen — so two effects firing together means one is never announced, and
    anything firing in the shop is announced into a hidden div.
18. **Harness passes on the five unvalidated Break rows** (Amber, Starstone,
    Silver, Jade, Vagabond). Only Obsidian's has numbers.
19. **Re-run the sim.** Every figure in the archived results predates the sweep
    removal, the Trade harness fix and the 2026-08-02 rulings.

---

## YOURS, NOT MINE — art calls

20. **Your prop template crosses the brief's exclusion zone.** §2 bans props
    from x 15–85%; eight of your twelve cross it. The dice band is clear and it
    reads well. I didn't move your art. Want me to?
21. **The app-wide backdrop stretches** — `body::before` uses
    `background-size:100% 100%`, scaling both axes independently. Same fault the
    match rule below it records fixing for itself. It frames *every* screen, so
    I left it. Change it?

---

## UNPLAYED NUMBERS — not questions, just untrusted

Last Call's 800, and most of the restored feat conditions. They read real state
and render, but only HIGH ROLLER has fired through a live match. Wants a
playtest before anyone tunes against them.
