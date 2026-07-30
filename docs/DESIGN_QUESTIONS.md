# Fark — open design decisions

Five questions thrown up by the current bug-fixing pass. Each one is a
player-facing choice rather than an engineering one: in every case the code can
go either way at similar cost, so it needs a call rather than an estimate.

Everything else from the pass has been decided and is already in the build.

---

## 1. When two rules collide: Hot Dice vs. Grog's Zero Hour

**Grog's table rule reads:** *"Take a marked face at my table and your turn is
over."*

**The collision:** the marked die you keep is the last unscored die on the
table — which is normally HOT DICE: a fresh set of six, a bonus, and you keep
rolling. One rule says the turn is over, the other says here's a whole new turn.

| | What the player sees |
|---|---|
| **A. Zero Hour wins** *(current)* | "ZERO HOUR — THE TURN ENDS." No bonus, no fresh six. |
| **B. Hot Dice pays out first** | HOT DICE banner and bonus, then the turn ends. |

**The trade.** A is one message and one outcome, but the player loses a
celebration they genuinely earned. B is more generous, but a HOT DICE banner
followed immediately by the turn ending is very likely to read as a bug.

**Currently A.** Worth changing only if Zero Hour is landing as too punishing.

---

## 2. Preserve: is it a die, or is it points?

**The card reads:** *"Trap one scoring die in amber at the end of your turn. It
is still there next turn, already kept and scored."*

Right now it does nothing at all — it takes its charge and the effect is thrown
away before the turn starts. That's a bug and it will be fixed either way. The
question is what *"still there"* should mean.

| | What the player sees |
|---|---|
| **A. A die** | The amber die is sitting on the table when the turn opens, already scored, and the hand is one die shorter. |
| **B. Points** | The score is already on the tally when the turn opens. No die on the table. |

**The trade.** A matches the card's own words and the whole fantasy of amber —
the card sells an *object*. It costs more: a die that is present but can't be
re-rolled or re-selected needs its own visual state. B is quicker and reads fine
as a number, but then the trapped die is only ever a line of text.

**No default — this one genuinely needs the call.**

---

## 3. Tar Pit: does it exist, and does it cut both ways?

Tar Pit shortens the opponent's hand for a turn. At present **neither** side's
copy does anything — the rival announces it and nothing happens, and the
player's does nothing either.

- **A. Make both work**, identically, as the card reads.
- **B. Cut the card.**

**Explicitly not an option:** fixing only the rival's copy. That would put the
same printed card in both decks while only one side's actually bites — a
one-way weapon the player can read but not use.

**Question:** should Tar Pit stay in the game? If yes, confirming it binds both
sides is enough to proceed.

---

## 4. Six dice in one row — how much crowding is acceptable?

On a phone, six dice at the current size very nearly fill the row. They no
longer overlap, but the margin is thin, and the outermost die can paint a few
pixels past the screen edge.

If you want more air, there are three levers:

- **A. Smaller dice.** They have already come down twice; there is a floor
  before they stop reading as objects.
- **B. A more top-down camera.** A die seen from further above takes up less
  horizontal room, so this buys space *without* shrinking anything — but it
  changes the look of the table.
- **C. Fewer dice on screen, or a different row arrangement.**

**Question:** which of these is on the table, and where is the line on die size?
This decides how much headroom there is before crowding comes back.

---

## 5. Game Over screen

Built on the new art: four flags reading **NIGHTS / MATCHES / PEAK GOLD /
FEATS**, with **NEW RUN** and **MENU** beneath.

Two things to confirm:

- **Placement.** Where the banner and the flag rail sit is a first estimate
  taken off the mockup. It wants an eye on it.
- **The victory ending.** Clearing the final boss still lands on an old
  placeholder screen. It's a different moment from dying and probably wants art
  of its own — is that coming, or should it share this one?
