# Next session - start here

## Where things stand (2026-08-21, after the docs cleanup)

Everything through **P845b** is shipped and deployed to Pages
(rigamix.github.io/Fark, `fark` branch). The recent arc, newest first:

- **P844/P845/P845b — card interactions have a written, enforced
  contract**: docs/CARD_INTERACTION_RULES.md. Promise/arm/lane-record/
  flag taxonomy; `famTableChanged()` voids promises and disarms arms at
  every dice-mutation moment (all 22 mutators individually driven —
  tools/apv_card_interactions_sweep.js). Found and fixed on the way:
  seven_dice was UNREACHABLE in real play (idle gate, empty pool) and
  is an arm now, gate at 'choosing'. One default for Denis in OPEN.md:
  mutations VOID promises (vs. follow-the-dice).
- **P843 — feats rot cleared**: seven verified-orphan flags deleted,
  the 12-field resume gap closed (featState carry + presence-guarded
  restore), the dead In-Arrears economy removed in all four legs.
  OPEN.md asks Denis whether the Corvus drain+refund should revive.
- **P842 — the enchant-screen phone crash**: diagnosed as GPU pressure
  (blur filters on seven+ full-screen layers), fixed with backdrop
  scrims + the ghost tab character leaving the compositor. Kill
  confirmed only on Denis's phone — if it still dies, next suspect is
  the WebGL canvas running under the shop (pausable there).
- **P839-P841**: pre-take LAST CALL judgment; Denis's 80 boss greeting
  lines wired through `_DLG_COND` state predicates (the router folded,
  behavior-preserving — the P839 probe passed verbatim); the game-over
  FEATS stat counts real feats.
- **P832-P838**: Denis's full ruling batch (additive dialogue resolver,
  growth + recognition lines, rival obsidian shatter via
  `_oRemoveOppDieAt`, cardHit at all 20 taker docks, Seven Dice
  redesign, vagabond drag fixes, 155 legacy files purged).

## In flight / parked

- **The ladder sweep** (Denis's §1 retune input): instrument is
  tools/ladder_real.js (real engine both seats, ~75-130s/match).
  Four priority cells measured before Denis stopped it:
  ALDRIC carl 0/18, ALDRIC rita 0/16, WHISPER carl 0/20, WHISPER rita
  0/20 — **0 wins in 74 matches**. AMBROSE and FINNICK cells not
  reached. Resume: OPEN.md §1 (tier is 0-indexed: night = tier+1).
- **The bank oracle**: planned only (docs/BANK_ORACLE_PLAN.md), gated
  on its own session by ruling.
- **Waiting on Denis**: OPEN.md carries everything — headline items:
  the promise void-vs-follow default, the Corvus economy revival
  question, §2-§4 playtest items, the P842 phone confirmation.

## The work queue

docs/AUDIT_BACKLOG.md — read the **RE-HOMED (2026-08-21)** section
first: it holds every live item rescued from the archived working
papers, topped by **the settle drag** (Denis reported twice: dice hang
then slide "as if against an invisible wall"; P736's two fixes both
failed and were reverted — the oldest open feel bug).

## Standing traps (all bit recently)

- Patch scripts: Write-tool .py only, never bash heredocs/node -e with
  backticks. Anchors: regions mix line endings per-site — exact match
  first, then the `\r?\n` regex fallback; replacements must preserve
  each site's endings. Parse gate after every patch:
  `node tools/zv_trade_parsegate.js fark_proto.html`.
- Probes: enter through the door the player does — a handler driven
  directly certifies the handler, not the card (seven_dice's gate bug
  hid exactly there). Wait ~3s after launch; roll taps can be eaten
  right after a relaunch (re-tap up to 3×); rival turns need
  `G._ffMult=0.05` pressed on an interval or they eat the next leg's
  window; `launchSeat` silently refuses a played seat
  (`S.run.night.seatsPlayed[0]=false` to re-run seat 0);
  `window._fkDiscardOk=true` before relaunches.
- Execution witnesses on anything a probe claims to test — a green
  that never ran the mechanism is the house's most-repeated trap
  (see memory + CARD_INTERACTION_RULES' coverage section for the
  standard).
- Ports: **8085 is Denis's server, never touch.** Probes: 8087.
  A background sweep owns 8086. Kill strays by PID/commandline filter,
  never `taskkill //IM python.exe` broadly.
- Denis generates art into Art/ mid-session: never `git add -A`,
  explicit paths only. Art/ masters untouched; optimized copies only.
- Deploy: commit in the worktree → from the repo root
  `git merge --ff-only claude/zen-chatterjee-f04c42` →
  `git push origin fark`. Never push main.
