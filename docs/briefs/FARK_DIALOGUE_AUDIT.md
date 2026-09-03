# DIALOGUE AUDIT — what works, what doesn't, and what to build

*2026-08-24. Audit of the live build. Every number here is counted from
the file, not estimated.*

---

## 0. The verdict first

**The architecture is sound and should be built on, not replaced.** One
resolver fed by data rows, conditions expressed as queries against state
the game already keeps, a per-run de-dup, a stage floor so a thin patron
is still complete. `PATRON_LINES` holds **1003 rows**. Adding a patron or
a line is a row, never a code path — which is the thing that usually goes
wrong with dialogue systems and hasn't here.

Every symptom Denis reports is real, and all four trace to **two root
causes** rather than to the writing or the structure:

1. **`_dlgAmbient` picks the King first, unconditionally.** It is a hard
   priority chain, not a weighting — so the King is not one thread among
   several, he is the first branch and everything else is his fallback.
2. **The gate drops lines silently, and the story advances at PICK time
   rather than at SEEN time.** A line can be selected, marked as heard,
   displayed, and overwritten before it can be read — after which every
   later line assumes the player knows something they never saw.

---

## 1. THE KING PROBLEM — it is a priority chain, not a volume problem

### The counts

| Pool | Rows | What it is |
|---|---|---|
| `reaction:king` | **48** | the royal-visit thread |
| `reaction:discrepancy` | 26 | Corvus's ledgers — the *second* storyline |
| `gossip:town` | 10 | ordinary tavern talk |

The King is the **largest single pool in the entire file** — larger than
any boss's win pool, larger than every patron's personal pool. World-talk
is 48 King against 10 town, an 83/17 split before a line is ever drawn.

### The mechanism

`_dlgAmbient` is the only door the room's talk comes through:

```js
var row=_dlgPick('reaction:king',0,run._dlgHeard);
if(!row)row=_dlgPick('gossip:town',0,null);
```

King first, always. `gossip:town` is reached **only when the King pool is
exhausted** — and with per-run de-dup that takes 48 draws. In a normal
run the player will never hear a town line at all.

`_dlgSay` (a named patron speaking) has the same shape one layer down:
discrepancy → personal → King → town. And the King branch there is
**effectively unreachable**, for the reason the file already documents at
P629 about the discrepancy branch: a personal stage-0 line is a floor
that never empties, so `patron:<id>` never returns null. So the King
reaches the player almost entirely through `_dlgAmbient`, where he has
no competition.

### The fix — a pattern this file already contains

`famOffer` solves this exact problem for card drafts and says so in its
own comment:

> *"FAMILY-FIRST: pick the family by the weighting, THEN a card inside it
> — family sizes never skew draft rates"*

Do the same for threads. **Pick the thread first, weighted; then pick a
line inside it.** A thread's row count then stops deciding how often the
player hears it, which is the entire bug.

```
THREADS = [ {id:'town',        w:5},
            {id:'king',        w:2, gate:<see §2>},
            {id:'discrepancy', w:2, speakers:_DISCREPANCY_SPEAKERS},
            ...room for more ]
```

Weights are Denis's dial, and the point of the change is that they exist
at all. Town gossip as the *default* voice of the room, with the story
threads as the occasional interruption, is the inversion he is asking
for. It also makes a third and fourth storyline a data row rather than a
rewrite — which is what "one of several storylines" requires structurally.

**Do not delete King lines to fix this.** 48 rows of written material is
an asset; the defect is that the picker cannot help but spend them.

---

## 2. THE CAUSALITY PROBLEM — `heard` is written when a line is PICKED

### It is not the condition system, which is correct

41 of the 48 King rows carry a `heard:king_intro` condition. The 7 that
can fire cold are all `tag:'king_intro'` — the introductions. So "a
reaction with nothing to react to" is impossible **by construction**, and
the `_DLG_COND.heard` helper was built for exactly this. Credit where
due: this was designed right.

### The actual break

`_dlgSay` and `_dlgAmbient` mark the tag at **selection**:

```js
if(row.tag)run._dlgHeard[row.tag]=1;
try{save();}catch(e){}
return row.t;
```

The caller then hands the text to `DLG.show()`, which sets a display
window and a hide timer — and **a priority category can overwrite a line
mid-display**:

```js
var _priority=(cat==='MATCH_START'||cat==='REMATCH_START'
              ||cat==='PLAYER_SIX_KIND'||cat==='OPP_WINS');
if(!_priority&&now<this.busyUntil+this.gap)return;
```

Priority cats skip the spacing check entirely and call `show()`, which
replaces the text and resets the timer. So:

> King intro is picked → `king_intro` marked heard → shown → a MATCH_START
> or OPP_WINS bark overwrites it 200ms later → the player never read a
> word of it → every one of the 41 follow-up lines is now eligible and
> speaks as though the introduction landed.

**That is the "as if I already knew" bug, and it is a timing bug wearing
a writing bug's clothes.**

### The fix

Mark the tag when the line has actually held the screen, not when it is
chosen. Concretely: `_dlgSay`/`_dlgAmbient` return the row rather than
just the text; `DLG.show()` commits the tag after the display window
completes without being interrupted. A line that gets overwritten stays
unheard and will be offered again.

Cheaper interim, if the full change is too invasive: make story-thread
lines **non-interruptible** — add them to the `_priority` exclusion so
nothing can overwrite one — and commit the tag on hide rather than on
pick. Two lines of change, closes the common case.

---

## 3. THE GATES — three silent drops in the wrong order

`trigger()` runs three checks and every one returns silently:

```js
const p=this.prob[cat]||.5; if(Math.random()>p)return;   // 1 probability
if(!_priority&&now<this.busyUntil+this.gap)return;       // 2 spacing
const line=this.getLine(cat); if(!line)return;           // 3 content
```

Three problems, in order of how much they cost:

**The probability roll happens before the spacing check.** A moment can
win its coin flip and then be thrown away because a previous line is
still on screen. The roll is consumed, the moment never retries, and the
result is that the *interesting* beats — which cluster together, because
interesting things happen in bursts — are exactly the ones most likely to
be eaten. Reversing the order (spacing first, probability second) costs
nothing and stops spending rolls on lines that were never going to show.

**Airtime is enormous relative to a turn.** `dur = max(5000, min(9000,
len*100))` plus `gap` 1400 means every line occupies **6.4 to 10.4
seconds** of exclusive channel. A brisk player turn is shorter than one
line. So most moments in a fast match are structurally unable to speak,
and which ones get through is decided by arrival time rather than by
interest.

**There is no queue and no deferral.** A dropped line is gone. Nothing
records that the opponent had something to say and couldn't.

**Recommended shape:** a one-slot queue with priority. A dropped moment
writes itself into the slot (overwriting a less interesting pending
moment); when the channel clears, the slot fires if it is still relevant.
That single change converts "the gates feel unsturdy" into "the opponent
always gets the last interesting thing out", and it is the difference
between a system that drops beats and one that defers them.

---

## 4. VARIETY — the census, and it is thinner than 1003 rows suggests

Of the 1003 rows, **only ~120 are things an opponent says at the table
during play.** The rest are greetings, win/loss outcomes and story.

### In-match reactions

`_dlgEvent(moment)` picks `patron:<art>:<moment>` first, then falls back
to `trait:<trait>:<moment>`.

| Moment | trait rows each | ×6 traits |
|---|---|---|
| `bust` (they bust) | 3 | 18 |
| `yourBust` (you bust) | 3 | 18 |
| `bank` (they bank big) | 3 | 18 |
| `yourBank` (you bank big) | 3 | 18 |
| `push` (they hesitate, then push) | 3 | 18 |
| `banksafe` (they hesitate, then bank) | 3 | 18 |
| `grudge` | 2 | 12 |

**When you bust, the opponent chooses from three lines.** That is the
whole of it, and it is why the same barks come round.

### Per-patron personality at the table is essentially zero

The bespoke override `patron:<id>:<moment>` exists and works. It is used
**twice in the entire file** — `patron:sil:bust` and `patron:regis:bank`
— across 23 patrons and 8 bosses. So at the table, almost every patron is
their trait and nothing else. Six voices doing the work of thirty-one.

This is the single biggest lever on Denis's stated goal ("instill as much
personality into each patron and boss as possible"), and it needs **no new
code at all** — the override path is already there and already tested.

### Moments that do not exist

Denis named four and all four are genuinely absent from `_DLG_MOMENT`:

| Wanted | Status |
|---|---|
| when they are **about to play** | no moment exists |
| when they **are playing** (their roll lands) | no moment exists |
| when the player **takes too long** | no moment exists, no idle timer |
| **story beats between moves, at random** | none — every line is event-driven |

That last one is the structural one. **Every line in the game today is a
reaction to something.** There is no heartbeat. The room only speaks when
the player acts, which is why the tavern feels like it is watching rather
than living. An idle tick — every N seconds of quiet, low probability,
drawing from the thread scheduler in §1 — is what turns the pools of
world-talk from unreachable into the thing that gives the place a pulse.

---

## 5. THE "TOLD YOU TO STOP" BUG

`trait:*:yourBust` lines can reference advice that was never given,
because in-match reactions have **no memory of what was said**. The
machinery exists — `_dlgHeard` plus `heard:` conditions — but it is wired
only to the story pools, never to the trait pools.

Two ways, and they compose:

- **Write the tables so no line claims a history it cannot have.** A
  `yourBust` line may gloat, warn, or commiserate; it may not refer to a
  warning unless one exists.
- **Then earn the good version back with a condition.** Give
  `push`/`banksafe` lines a tag, and let a `yourBust` line require it.
  `{c:['said:warned_you']}` makes "told you to stop" *correct* — and it
  becomes one of the best lines in the game precisely because it only
  fires when they did.

That needs a per-match equivalent of `_dlgHeard` for trait lines.
`_dlgLastG` already exists as per-match module state and is the right
place; it needs to record tags, not just groups.

---

## 6. WHAT TO BUILD, IN ORDER

1. **The thread scheduler** (§1). Weighted thread pick before line pick,
   `famOffer`'s family-first pattern. Unblocks everything else and is the
   one Denis asked for by name.
2. **Commit `heard` on display, not on pick** (§2). Small, and it stops
   the story silently outrunning the player.
3. **The one-slot deferral queue, and swap the check order** (§3).
   Turns dropped beats into delayed beats.
4. **The idle tick** (§4). A heartbeat for the room, feeding from 1.
5. **Two new moments** — *about to play* and *player is taking too long*
   (§4). New `_DLG_MOMENT` entries; the plumbing already handles them.
6. **Then write.** Expand `trait:*` from 3 to ~8 per moment, and — the
   big one — fill in `patron:<id>:<moment>` overrides. The path is built
   and used twice; every row added there is a patron becoming a person.

Steps 1–5 are engineering and small. Step 6 is the actual work, and it is
pure data — which is the point of the architecture and the reason it is
worth keeping.

---

## 7. VERIFICATION

- **Thread distribution over a simulated run.** Town should be the most
  frequent voice; no thread should be able to monopolise. Assert on the
  *share*, not on "every thread appears at least once" — with weights and
  a long run, appearance-at-least-once cannot fail and proves nothing.
- **A story tag must never be set for a line the player did not see.**
  Drive it: trigger a King intro, overwrite it with a priority bark,
  assert `king_intro` is still unset.
- **Drop rate at the gate.** Count moments that wanted to speak against
  lines actually shown, in a real match. Today that number is unknown;
  after step 3 it should be near zero for interesting categories.
- **Bust-line repetition.** Twenty busts against one patron, count
  distinct lines. Today the ceiling is 3.
