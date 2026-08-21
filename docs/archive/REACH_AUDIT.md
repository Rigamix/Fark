# Which of tonight's fixes changed a match today? 8 of 10 — and not the 8 I'd have guessed

`generateOppCards` begins `return [];`, so `G.oCards` is always empty and any
branch inside a `G.oCards` loop cannot run in this build. `G.pCards` is
populated normally. Most patches touched **both** copies of a mirrored mechanic,
so this is per site, not per patch. Rerun with `tools/reach_audit.py`.

| patch | live sites | dead sites | changes a match today? |
|---|---|---|---|
| P462 turn value / `rivalTurn` seam | — | — | **yes** (not card-gated) |
| P463 `ill_omen` migration | — | — | **yes** (not card-gated) |
| P464 `WILD_LEVEL` | — | — | **yes** (dice, not cards) |
| P465 `BANK_FX` | 4 | 4 | **yes**, half |
| P466 `BANK_TAKE` / `SCORE_DRAIN` | 1 / 1 | 1 / 1 | **yes**, half |
| **P466 `challenge` rival double-charge** | **3** | 0 | **yes — fully live** |
| **P467 `challenge` player under-charge** | 0 | **5** | **no — waits for P5** |
| P468 `BUST_FX` | 5 | 4 | **yes**, half |
| P469 `bust_immune_turns` off-by-one | 0 | 1 | **no — waits for P5** |

## The inversion worth naming

I assumed the boss-side fix was the speculative one and the player-side fix was
the live behaviour change. **It is exactly the other way round.**

- **P466 is live.** `finOpp`'s `challenge` branch sits in a `G.pCards` loop — the
  *player's* card punishing the patron. A boss really could be charged up to
  double, and really is not any more.
- **P467 is dead.** `handleBank`'s branch sits in a `G.oCards` loop — the
  *patron's* card punishing the player. The patron cannot hold it, so the
  under-charge was never reachable.

**Which corrects something I told Denis:** I flagged P467 as "a third difficulty
change, making the player harsher", and put it in `OPEN.md` §6 on that basis. It
changes nothing today. **§6's boss half stands** — P466 is live, so bosses really
did get tougher tonight from a correctness fix.

## What "dead" does and does not mean

**Not wasted.** These are precisely the branches P5 switches on, and they are
correct now rather than needing rediscovery then. The only distinction being
drawn is between *"changed what happens in a match today"* and *"correct and
waiting"* — which my reporting collapsed, describing fixes to unreachable code
as live gameplay bugs.

**And "live" means reachable, not exercised.** A `pCards` branch still needs the
player to hold that card.
