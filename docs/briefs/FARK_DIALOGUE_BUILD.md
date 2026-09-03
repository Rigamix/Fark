# DIALOGUE BUILD — the levers, and the voices

*2026-08-24. Companion to `FARK_DIALOGUE_AUDIT.md`, which diagnoses.
This one is what to change and what to paste. Written after looking at
all thirty patron portraits, because the art is doing characterisation
the line tables were ignoring.*

---

## PART ONE — FIVE ENGINE CHANGES

All five are small. None touches the resolver, `_dlgPick`, or the row
format — `PATRON_LINES` stays exactly as it is.

### 1. Display duration should follow the line (Denis, by name)

`DLG.show()` currently:

```js
const dur=Math.max(5000,Math.min(9000,text.length*100));
```

The 5000ms floor is the bug. A six-word bark ("Told you.") holds the
screen for the same five seconds as a full sentence, which is most of a
turn. Replace with:

```js
/* P8xx: the floor was 5000, so "Told you." held the screen as long as a
   full line - most of a player turn - and made the channel feel jammed
   (Denis: "make it that the short lines don't get displayed as long as
   the long ones"). Read speed plus a fixed beat to notice it appeared. */
const dur=Math.max(1800,Math.min(7000,900+text.length*55));
```

At 10 chars → 1800ms. At 40 → 3100. At 90 → 5850. At 140+ → 7000.
Roughly halves the channel occupancy of the short barks, which are the
majority, and that alone makes room for everything below.

Pair it with a shorter `gap`: **1400 → 700**. The old gap was sized
against a 5s floor.

### 2. Thread-first ambient picking

`_dlgAmbient` currently tries `reaction:king` first and only falls to
`gossip:town` when the King pool is empty — 48 rows deep. Replace the
chain with a weighted thread pick, the same shape `famOffer` already uses
for card families:

```js
/* THREAD-FIRST, the famOffer pattern: pick the THREAD by weight, then a
   line inside it, so a thread's row count stops deciding how often the
   room talks about it. The old chain tried the King first and reached
   town gossip only once 48 King rows were spent - which in a normal run
   is never. Weights are the dial; adding a fourth thread is a row. */
var DLG_THREADS=[
  {id:'gossip:town',        w:6},
  {id:'reaction:king',      w:2},
  {id:'reaction:discrepancy',w:2,speakers:_DISCREPANCY_SPEAKERS}
];
```

Pick by weight among threads that still have an eligible line; fall back
to any thread that does. `gossip:town` becomes the room's ordinary voice
and the stories become the occasional interruption — which is the
inversion Denis asked for, and it makes a fourth storyline a data row.

**`gossip:town` needs more rows to carry this** — it has 10. Part Three
adds 24.

### 3. Commit `heard` when a line is SEEN, not when it is picked

`_dlgSay`/`_dlgAmbient` set `run._dlgHeard[row.tag]=1` at selection.
`DLG.show()` can then be overwritten mid-display by a priority category,
so a King introduction can be marked heard without ever being read —
after which all 41 follow-up lines speak as though it landed. That is the
"as if I already knew" bug.

Minimal fix, two parts:

- Return the row from `_dlgSay`/`_dlgAmbient`; commit `row.tag` from
  `DLG.hide()` (the line completed) rather than at pick.
- Add story lines to the non-interruptible set so a priority bark cannot
  overwrite one:
  `var _priority=(cat==='MATCH_START'||...) && !this.storyLine;`

### 4. A one-slot deferral queue, and swap the check order

`trigger()` rolls probability **before** checking whether the channel is
free, so a moment can win its roll and be discarded anyway, roll spent,
no retry. Swap them, then keep the loser:

```js
/* spacing FIRST: a probability roll spent on a line that could never
   have shown is a beat lost for no reason */
if(!_priority&&now<this.busyUntil+this.gap){this.defer(cat);return;}
const p=this.prob[cat]||.5;if(Math.random()>p)return;
```

`defer(cat)` holds one category, overwritten only by a higher-`prob` one.
When the channel clears, fire it if still relevant (a `_DLG_MOMENT`
category expires after ~4s; match-state ones do not). This is what turns
"the gates feel unsturdy" into "the opponent always gets the last
interesting thing out".

### 5. The idle tick — the room gets a pulse

Every line in the game today is a reaction. Nothing speaks unless the
player acts, which is why the tavern feels like it is watching rather
than living. Add one timer:

```js
/* P8xx: STORY BEATS BETWEEN MOVES, not hung off events (Denis). Every
   ~14s of quiet, a 35% chance the room says something from the thread
   scheduler. Never during the player's roll animation; never when the
   channel is busy - it takes the same gate as everything else. */
```

Interval ~14s, probability ~0.35, gated on `busyUntil` and on the phase
not being `rolling` or `opp`. Draws from §2's thread scheduler, so it is
also the thing that finally makes `gossip:town` reachable.

### 6. Two new moments

Add to `_DLG_MOMENT`: `OPP_ABOUT_TO_ROLL:'preroll'` and
`PLAYER_IDLE:'waiting'`. The plumbing already handles anything in that
map; both need only a trigger site and rows. `waiting` fires from the
same idle timer as §5 when it is the *player's* turn and they have not
acted for ~20s.

---

## PART TWO — THE CHARACTER BIBLE

Thirty patrons, each an animal with a costume and an expression. The line
tables were written to six trait words; the art was doing far more work
than that. **This is the source of truth for voice.** One line each:
species, look, how they talk.

| id | who they are | voice |
|---|---|---|
| **corbin** | black crow, wide feathered hat, hooded, one suspicious eye | counts everything, says half of it. Clipped, watchful |
| **dunstan** | pale goat, teal cloak, gold brooch, mildly amused | courteous, faintly condescending, never rattled |
| **eira** | owl, purple hood, hard yellow glare | severe, few words, each one lands |
| **fenn** | green snake, hood and strap, tongue out | hisses the sibilants, enjoys your trouble |
| **ferrand** | scruffy hyena, shoulder pad, sneering | laughs first, thinks later. Coarse |
| **golgoth** | plague-doctor mask, green hood, amulets | **does not speak.** Breath, coughs, the beak turning. Never a word |
| **krox** | crocodile, gold chains, all teeth | slow, heavy, certain. Never hurries |
| **mudge** | frog in a cravat, holding a coin, delighted | foppish, money-pleased, giggles |
| **nebb** | old stork, headscarf, beads, tired lids | seen it all, expects the worst, usually right |
| **nell** | hare, red headscarf, sly warm smile | friendly and shrewd at once. Nicknames you |
| **nix** | shark, grinning, rows of teeth | cheerful about violence. Everything is appetite |
| **odo** | otter mid-shout, brown coat | loud, excitable, no volume control |
| **ollis** | owl in round spectacles, scholarly | precise, pedantic, quietly delighted by data |
| **osgood** | bull, horns, nose ring, flat stare | immovable. Short sentences. Says the obvious |
| **peck** | orange lizard, one enormous eye | off-kilter, sees things sideways, non-sequiturs |
| **pell** | goose, green headscarf, prim blouse | tidy, correct, disapproving of mess |
| **poll** | turtle in a straw hat and dungarees, beaming | simple, sunny, farm talk. Genuinely pleased for you |
| **rask** | sphinx cat, eye patch, purple and gold | aristocratic, vain, wounded pride |
| **regis** | rooster with a monocle, ruffled chest | pompous, formal, announces things |
| **remny** | goat, long horns, purple coat, gold, languid | rich and bored. Everything is beneath him, faintly |
| **rilla** | sheep, curly wool, flowers, pendant | kind, motherly, worries about you |
| **roan** | rhino, cloth wrap, one horn, mild | huge and gentle. Apologetic when he wins |
| **sil** | dark wolf, high collar, glowering | grim, threatening, minimal |
| **sparr** | pigeon in a blue hood, medallion, yellow eyes | a messenger. Reports rather than talks |
| **squib** | small green lizard, hood, tongue out, beads | twitchy, sly, talks too fast |
| **tam** | boar in a blue coat and cravat, smug, eyes closed | self-satisfied merchant. Rounds numbers up |
| **thorne** | lynx, tufted ears, earring, cool half-lidded stare | elegant and dangerous. Understates everything |
| **tuck** | mouse in a wide hat, green scarf, huge grin | eager, small, delighted to be here |
| **twill** | mouse in a maid's cap and apron, holding a broom | works here. Dry, unimpressed, has to clean up after |
| **vess** | cat, gold headband, pearl collar, poised | composed, precise, faintly regal |

Two notes for whoever writes more:

- **Species is the cheapest personality lever in the file.** "You'll want
  to keep both hands where I can see them" is a fine line; from a
  crocodile it is a great one. Reach for the animal first.
- **Twill is the only one who works there.** She sees every match, cleans
  up after every bust, and has no stake. That is a distinct and very
  usable voice, and she currently has three lines.

---

## PART THREE — THE ROWS

Paste into `PATRON_LINES`. Format unchanged: `{p,s,c,t}`.

**Six in-match moments** (`_dlgEvent` looks up `patron:<id>:<moment>`
before falling back to `trait:*`):

- `bust` — they bust
- `yourBust` — you bust
- `bank` — they bank big
- `yourBank` — you bank big
- `push` — they hesitated, then rolled on
- `banksafe` — they hesitated, then banked

Two rows per patron for the four that fire most, one each for the two
hesitation moments. Every line is short on purpose — see Part One §1.

### On "told you to stop"

Do not write a `yourBust` line that references advice unless it is gated.
Tag the `push`/`banksafe` rows with `g:'warned'`, give the gloating
`yourBust` lines `c:['said:warned']`, and add a per-match `said` store
beside `_dlgLastG`. Then "Told you" is *correct*, and it becomes one of
the best lines in the game because it only fires when they did.

```js
/* ══ PER-PATRON TABLE VOICES ═══════════════════════════════════════════
   The override path _dlgEvent already checks (patron:<id>:<moment>)
   before the trait fallback. It existed and was used TWICE in the whole
   file, so at the table thirty-one characters spoke with six voices.
   Written to the PORTRAITS, not to the trait word - the art was doing
   characterisation the tables were ignoring. Species first: the same
   sentence from a crocodile and from a sheep are different lines. */

/* CORBIN — crow, counts everything, says half of it */
{p:'patron:corbin:yourBust',s:0,t:"Noted."},
{p:'patron:corbin:yourBust',s:0,t:"That's the third time. I keep count."},
{p:'patron:corbin:bust',s:0,t:"...I'll amend the figure."},
{p:'patron:corbin:yourBank',s:0,t:"Mm. I'll write it down."},
{p:'patron:corbin:bank',s:0,t:"Balanced."},
{p:'patron:corbin:push',s:0,g:'warned',t:"This is unwise. I'll do it anyway."},
{p:'patron:corbin:banksafe',s:0,t:"The books prefer it this way."},

/* DUNSTAN — goat, courteous, faintly condescending */
{p:'patron:dunstan:yourBust',s:0,t:"Oh, bad luck. Truly."},
{p:'patron:dunstan:yourBust',s:0,t:"These things happen. To some more than others."},
{p:'patron:dunstan:bust',s:0,t:"Well. That was undignified."},
{p:'patron:dunstan:yourBank',s:0,t:"Very good. Genuinely."},
{p:'patron:dunstan:bank',s:0,t:"One does try."},
{p:'patron:dunstan:push',s:0,g:'warned',t:"I shouldn't. And yet."},
{p:'patron:dunstan:banksafe',s:0,t:"Enough is a perfectly good amount."},

/* EIRA — owl, severe, few words */
{p:'patron:eira:yourBust',s:0,t:"Predictable."},
{p:'patron:eira:yourBust',s:0,t:"I saw that coming from across the room."},
{p:'patron:eira:bust',s:0,t:"...Hm."},
{p:'patron:eira:yourBank',s:0,t:"Acceptable."},
{p:'patron:eira:bank',s:0,t:"As intended."},
{p:'patron:eira:push',s:0,g:'warned',t:"Watch."},
{p:'patron:eira:banksafe',s:0,t:"I don't gamble. I calculate."},

/* FENN — snake, sibilant, enjoys your trouble */
{p:'patron:fenn:yourBust',s:0,t:"Ssssuch a shame."},
{p:'patron:fenn:yourBust',s:0,t:"All that, and nothing. Delicious."},
{p:'patron:fenn:bust',s:0,t:"Sssso. Even I bite myself sometimes."},
{p:'patron:fenn:yourBank',s:0,t:"Clever little thing."},
{p:'patron:fenn:bank',s:0,t:"Swallowed whole."},
{p:'patron:fenn:push',s:0,g:'warned',t:"One more. Alwaysss one more."},
{p:'patron:fenn:banksafe',s:0,t:"I coil. I wait."},

/* FERRAND — hyena, laughs first, thinks later */
{p:'patron:ferrand:yourBust',s:0,t:"HAH! Oh, that's lovely."},
{p:'patron:ferrand:yourBust',s:0,t:"Ha! Do it again, go on."},
{p:'patron:ferrand:bust',s:0,t:"Ha. HA. ...no, that's not funny."},
{p:'patron:ferrand:yourBank',s:0,t:"Pff. Lucky."},
{p:'patron:ferrand:bank',s:0,t:"HAH! Mine."},
{p:'patron:ferrand:push',s:0,g:'warned',t:"Why not? WHY NOT!"},
{p:'patron:ferrand:banksafe',s:0,t:"...fine. Fine! I'll take it."},

/* GOLGOTH — THE ONE WHO DOES NOT SPEAK.
   Denis: a mask, so breathing and coughs, never words. Every row here
   carries nv:1 (Part One 7) so the bubble renders it WITHOUT the quote
   marks every other line gets - a wheeze inside speech marks reads as
   someone saying the word "wheeze". He is the only patron built this
   way, and that is the point: thirty voices and one silence. */
{p:'patron:golgoth:yourBust',s:0,nv:1,t:"hhhhhhh\u2026"},
{p:'patron:golgoth:yourBust',s:0,nv:1,t:"kh. kh. khhhk."},
{p:'patron:golgoth:yourBust',s:0,nv:1,t:"the beak tilts. slowly."},
{p:'patron:golgoth:bust',s:0,nv:1,t:"\u2026hnnh."},
{p:'patron:golgoth:bust',s:0,nv:1,t:"a long breath out. glass eyes, fixed."},
{p:'patron:golgoth:yourBank',s:0,nv:1,t:"hhh\u2014hk."},
{p:'patron:golgoth:yourBank',s:0,nv:1,t:"one gloved finger taps the table. once."},
{p:'patron:golgoth:bank',s:0,nv:1,t:"khhhhh."},
{p:'patron:golgoth:bank',s:0,nv:1,t:"the mask does not move."},
{p:'patron:golgoth:push',s:0,g:'warned',nv:1,t:"a slow inhale through the beak."},
{p:'patron:golgoth:banksafe',s:0,nv:1,t:"hnn. hnn."},

/* KROX — crocodile, slow, heavy, certain */
{p:'patron:krox:yourBust',s:0,t:"Mm. Thought so."},
{p:'patron:krox:yourBust',s:0,t:"You thrashed. That's when they take you."},
{p:'patron:krox:bust',s:0,t:"...huh."},
{p:'patron:krox:yourBank',s:0,t:"Good. Bigger meal later."},
{p:'patron:krox:bank',s:0,t:"Patience. Then teeth."},
{p:'patron:krox:push',s:0,g:'warned',t:"Not yet. Not yet."},
{p:'patron:krox:banksafe',s:0,t:"I don't chase. I wait at the water."},

/* MUDGE — frog, foppish, money-pleased */
{p:'patron:mudge:yourBust',s:0,t:"Oh! Oh dear. Hee."},
{p:'patron:mudge:yourBust',s:0,t:"All those lovely points. Gone. Gone!"},
{p:'patron:mudge:bust',s:0,t:"My coin! My beautiful coin!"},
{p:'patron:mudge:yourBank',s:0,t:"Hmph. Spend it wisely. Or don't."},
{p:'patron:mudge:bank',s:0,t:"Into the purse. Hee hee."},
{p:'patron:mudge:push',s:0,g:'warned',t:"More! There's always more!"},
{p:'patron:mudge:banksafe',s:0,t:"A bird in the hand is worth counting."},

/* NEBB — old stork, expects the worst */
{p:'patron:nebb:yourBust',s:0,t:"Aye. That's how it goes."},
{p:'patron:nebb:yourBust',s:0,t:"Seen a hundred of those. Seen a hundred more coming."},
{p:'patron:nebb:bust',s:0,t:"Well. I'm old. I've had worse."},
{p:'patron:nebb:yourBank',s:0,t:"Enjoy it while it's yours."},
{p:'patron:nebb:bank',s:0,t:"Small mercies."},
{p:'patron:nebb:push',s:0,g:'warned',t:"Ah, why not. I'm not getting younger."},
{p:'patron:nebb:banksafe',s:0,t:"At my age you take what's offered."},

/* NELL — hare, warm and shrewd, gives you nicknames */
{p:'patron:nell:yourBust',s:0,t:"Ohh, duckling. Come here."},
{p:'patron:nell:yourBust',s:0,t:"That's a hard one, love. Shake it off."},
{p:'patron:nell:bust',s:0,t:"Serves me right, doesn't it."},
{p:'patron:nell:yourBank',s:0,t:"Look at you go, sweetheart."},
{p:'patron:nell:bank',s:0,t:"Don't mind if I do."},
{p:'patron:nell:push',s:0,g:'warned',t:"One more, then I'm good. Promise."},
{p:'patron:nell:banksafe',s:0,t:"Rabbit knows when to stop running."},

/* NIX — shark, cheerful about violence */
{p:'patron:nix:yourBust',s:0,t:"Blood in the water. Love it."},
{p:'patron:nix:yourBust',s:0,t:"Ohh, you went under. Happens."},
{p:'patron:nix:bust',s:0,t:"Bit off more than I could chew."},
{p:'patron:nix:yourBank',s:0,t:"Nice bite. Save some for me."},
{p:'patron:nix:bank',s:0,t:"Chomp."},
{p:'patron:nix:push',s:0,g:'warned',t:"Keep swimming or you sink!"},
{p:'patron:nix:banksafe',s:0,t:"Eat what you caught. Then hunt again."},

/* ODO — otter, loud, no volume control */
{p:'patron:odo:yourBust',s:0,t:"OOF! Right in front of me!"},
{p:'patron:odo:yourBust',s:0,t:"NO! No no no. Oh, that HURT."},
{p:'patron:odo:bust',s:0,t:"AAGH! Why! WHY!"},
{p:'patron:odo:yourBank',s:0,t:"WHOO! Look at that!"},
{p:'patron:odo:bank',s:0,t:"YES! HA! YES!"},
{p:'patron:odo:push',s:0,g:'warned',t:"AGAIN! ONE MORE! AGAIN!"},
{p:'patron:odo:banksafe',s:0,t:"...okay. OKAY. Banking. Banking!"},

/* OLLIS — spectacled owl, pedantic, delighted by data */
{p:'patron:ollis:yourBust',s:0,t:"Statistically overdue, that."},
{p:'patron:ollis:yourBust',s:0,t:"Fascinating. Tragic for you, but fascinating."},
{p:'patron:ollis:bust',s:0,t:"An outlier. It happens."},
{p:'patron:ollis:yourBank',s:0,t:"Within expected variance. Well played regardless."},
{p:'patron:ollis:bank',s:0,t:"Precisely as modelled."},
{p:'patron:ollis:push',s:0,g:'warned',t:"The odds say no. I'm curious anyway."},
{p:'patron:ollis:banksafe',s:0,t:"The correct decision is rarely the fun one."},

/* OSGOOD — bull, immovable, states the obvious */
{p:'patron:osgood:yourBust',s:0,t:"Bust."},
{p:'patron:osgood:yourBust',s:0,t:"You had enough. You kept going."},
{p:'patron:osgood:bust',s:0,t:"Bad roll."},
{p:'patron:osgood:yourBank',s:0,t:"Good number."},
{p:'patron:osgood:bank',s:0,t:"Banked."},
{p:'patron:osgood:push',s:0,g:'warned',t:"Not enough yet."},
{p:'patron:osgood:banksafe',s:0,t:"That'll do."},

/* PECK — one enormous eye, sees things sideways */
{p:'patron:peck:yourBust',s:0,t:"I watched every one of those. All at once."},
{p:'patron:peck:yourBust',s:0,t:"The dice were wrong before they landed."},
{p:'patron:peck:bust',s:0,t:"I saw it coming. Didn't help."},
{p:'patron:peck:yourBank',s:0,t:"Bright. Very bright. Too bright."},
{p:'patron:peck:bank',s:0,t:"Everything lines up if you look properly."},
{p:'patron:peck:push',s:0,g:'warned',t:"The next one's already happened somewhere."},
{p:'patron:peck:banksafe',s:0,t:"Stop. Blink. Stop."},

/* PELL — goose, tidy, disapproving of mess */
{p:'patron:pell:yourBust',s:0,t:"Well, that's a mess."},
{p:'patron:pell:yourBust',s:0,t:"You could have folded that neatly. You didn't."},
{p:'patron:pell:bust',s:0,t:"Untidy. I do apologise."},
{p:'patron:pell:yourBank',s:0,t:"Properly done. Thank you."},
{p:'patron:pell:bank',s:0,t:"Straightened out."},
{p:'patron:pell:push',s:0,g:'warned',t:"It isn't finished yet."},
{p:'patron:pell:banksafe',s:0,t:"Tidy sum. Tidy end."},

/* POLL — turtle in a straw hat, sunny, farm talk */
{p:'patron:poll:yourBust',s:0,t:"Aw, shoot. Bad weather, that."},
{p:'patron:poll:yourBust',s:0,t:"Some seasons the crop just don't come."},
{p:'patron:poll:bust',s:0,t:"Hah! Well, that's the frost got me."},
{p:'patron:poll:yourBank',s:0,t:"Good harvest! Good on you!"},
{p:'patron:poll:bank',s:0,t:"In the barn she goes."},
{p:'patron:poll:push',s:0,g:'warned',t:"One more row afore dark."},
{p:'patron:poll:banksafe',s:0,t:"Don't pick more'n you can carry."},

/* RASK — sphinx cat, vain, wounded pride */
{p:'patron:rask:yourBust',s:0,t:"How very common."},
{p:'patron:rask:yourBust',s:0,t:"I would say I'm sorry. I would be lying."},
{p:'patron:rask:bust',s:0,t:"Do not look at me."},
{p:'patron:rask:yourBank',s:0,t:"Adequate. For you."},
{p:'patron:rask:bank',s:0,t:"Naturally."},
{p:'patron:rask:push',s:0,g:'warned',t:"I have never once settled."},
{p:'patron:rask:banksafe',s:0,t:"I choose to stop. That is not the same as fear."},

/* REGIS — rooster with a monocle, pompous, announces */
{p:'patron:regis:yourBust',s:0,t:"And the challenger FALLS."},
{p:'patron:regis:yourBust',s:0,t:"A calamity! Announced by me!"},
{p:'patron:regis:bust',s:0,t:"I shall not be taking questions."},
{p:'patron:regis:yourBank',s:0,t:"A fine sum! Noted for the record!"},
{p:'patron:regis:bank',s:0,t:"Observe. And weep, possibly."},
{p:'patron:regis:push',s:0,g:'warned',t:"The cockerel does not retreat at dawn!"},
{p:'patron:regis:banksafe',s:0,t:"A strategic withdrawal. Nothing more."},

/* REMNY — goat in gold, rich and bored */
{p:'patron:remny:yourBust',s:0,t:"Mm. Was that meant to happen?"},
{p:'patron:remny:yourBust',s:0,t:"How exhausting for you."},
{p:'patron:remny:bust',s:0,t:"Irrelevant. I have others."},
{p:'patron:remny:yourBank',s:0,t:"Charming. Is that a lot, for you?"},
{p:'patron:remny:bank',s:0,t:"Add it to the rest."},
{p:'patron:remny:push',s:0,g:'warned',t:"I'm not bored yet."},
{p:'patron:remny:banksafe',s:0,t:"I've made my point. That's the expensive part."},

/* RILLA — sheep, kind, worries about you */
{p:'patron:rilla:yourBust',s:0,t:"Oh, love. Oh no."},
{p:'patron:rilla:yourBust',s:0,t:"Sit a moment. Have something warm."},
{p:'patron:rilla:bust',s:0,t:"Oh, silly me."},
{p:'patron:rilla:yourBank',s:0,t:"There now! I knew you had it."},
{p:'patron:rilla:bank',s:0,t:"That's lovely, thank you."},
{p:'patron:rilla:push',s:0,g:'warned',t:"Just a little more. Then I'll stop."},
{p:'patron:rilla:banksafe',s:0,t:"That's plenty for anyone."},

/* ROAN — rhino, huge and gentle, apologises for winning */
{p:'patron:roan:yourBust',s:0,t:"Ah. Sorry. Truly."},
{p:'patron:roan:yourBust',s:0,t:"That's rotten. I hate seeing that."},
{p:'patron:roan:bust',s:0,t:"That's fair. That's fair."},
{p:'patron:roan:yourBank',s:0,t:"Good. Good, you deserve it."},
{p:'patron:roan:bank',s:0,t:"Sorry. Didn't mean it to be that big."},
{p:'patron:roan:push',s:0,g:'warned',t:"Once more. Sorry."},
{p:'patron:roan:banksafe',s:0,t:"I'd rather not take too much."},

/* SIL — dark wolf, grim, minimal */
{p:'patron:sil:yourBust',s:0,t:"Good."},
{p:'patron:sil:yourBust',s:0,t:"You're bleeding. I can smell it."},
{p:'patron:sil:bust',s:0,t:"..."},
{p:'patron:sil:yourBank',s:0,t:"Don't get comfortable."},
{p:'patron:sil:bank',s:0,t:"Taken."},
{p:'patron:sil:push',s:0,g:'warned',t:"Not finished."},
{p:'patron:sil:banksafe',s:0,t:"The pack eats. Then the pack moves."},

/* SPARR — pigeon messenger, reports rather than talks */
{p:'patron:sparr:yourBust',s:0,t:"I'll carry word of that one."},
{p:'patron:sparr:yourBust',s:0,t:"Bust, at the corner table. That's the message."},
{p:'patron:sparr:bust',s:0,t:"Don't put that in the letter."},
{p:'patron:sparr:yourBank',s:0,t:"Noted. Word travels."},
{p:'patron:sparr:bank',s:0,t:"Delivered."},
{p:'patron:sparr:push',s:0,g:'warned',t:"One more stop on the route."},
{p:'patron:sparr:banksafe',s:0,t:"Message sent. I'm away."},

/* SQUIB — small lizard, twitchy, talks too fast */
{p:'patron:squib:yourBust',s:0,t:"OhhHH that's bad that's bad that's really bad."},
{p:'patron:squib:yourBust',s:0,t:"Gone! All of it! Just — gone!"},
{p:'patron:squib:bust',s:0,t:"Nope nope nope nope."},
{p:'patron:squib:yourBank',s:0,t:"That's — okay that's a lot, that's fine, that's fine."},
{p:'patron:squib:bank',s:0,t:"Mine mine mine mine mine."},
{p:'patron:squib:push',s:0,g:'warned',t:"Again! Quick! Before I think!"},
{p:'patron:squib:banksafe',s:0,t:"Stopping. Stopped. Done. Stopped."},

/* TAM — boar merchant, smug, rounds up */
{p:'patron:tam:yourBust',s:0,t:"A total loss. My condolences."},
{p:'patron:tam:yourBust',s:0,t:"Bad investment, that. I'd have advised against."},
{p:'patron:tam:bust',s:0,t:"A write-off. Happens in business."},
{p:'patron:tam:yourBank',s:0,t:"A respectable return. Respectable."},
{p:'patron:tam:bank',s:0,t:"Call it a round number. In my favour."},
{p:'patron:tam:push',s:0,g:'warned',t:"The margin is still thin."},
{p:'patron:tam:banksafe',s:0,t:"Profit taken. Never apologise for that."},

/* THORNE — lynx, elegant, understates everything */
{p:'patron:thorne:yourBust',s:0,t:"Unfortunate."},
{p:'patron:thorne:yourBust',s:0,t:"You were doing so well. Right up until."},
{p:'patron:thorne:bust',s:0,t:"Careless of me."},
{p:'patron:thorne:yourBank',s:0,t:"Neatly done."},
{p:'patron:thorne:bank',s:0,t:"A small thing."},
{p:'patron:thorne:push',s:0,g:'warned',t:"I think one more."},
{p:'patron:thorne:banksafe',s:0,t:"I know precisely what I'm worth."},

/* TUCK — mouse, eager, delighted to be here */
{p:'patron:tuck:yourBust',s:0,t:"Oh no! Oh, I'm sorry!"},
{p:'patron:tuck:yourBust',s:0,t:"That's awful. Are you alright?"},
{p:'patron:tuck:bust',s:0,t:"Whoops! That's me done, then!"},
{p:'patron:tuck:yourBank',s:0,t:"Wow! That's brilliant!"},
{p:'patron:tuck:bank',s:0,t:"I got some! I actually got some!"},
{p:'patron:tuck:push',s:0,g:'warned',t:"Just one more! Just one!"},
{p:'patron:tuck:banksafe',s:0,t:"That's loads, that is. That's loads."},

/* TWILL — mouse in an apron, works here, has to clean up */
{p:'patron:twill:yourBust',s:0,t:"Mm. I'll get the mop."},
{p:'patron:twill:yourBust',s:0,t:"You're the fourth tonight. I'm keeping a tally."},
{p:'patron:twill:bust',s:0,t:"Right. Back to work, then."},
{p:'patron:twill:yourBank',s:0,t:"Good for you. Mind the table."},
{p:'patron:twill:bank',s:0,t:"That's my week's wages, that."},
{p:'patron:twill:push',s:0,g:'warned',t:"I'm on shift in an hour. One more."},
{p:'patron:twill:banksafe',s:0,t:"I've swept up after enough of those."},

/* VESS — cat, composed, faintly regal */
{p:'patron:vess:yourBust',s:0,t:"Oh, my dear."},
{p:'patron:vess:yourBust',s:0,t:"Composure. It's the only thing that travels well."},
{p:'patron:vess:bust',s:0,t:"How very tiresome."},
{p:'patron:vess:yourBank',s:0,t:"Elegant. I approve."},
{p:'patron:vess:bank',s:0,t:"Just so."},
{p:'patron:vess:push',s:0,g:'warned',t:"I am not finished being interesting."},
{p:'patron:vess:banksafe',s:0,t:"One should always leave before the end."},
```

### The gated "told you" lines

These fire **only** when that patron actually warned you. Add after the
`said` store exists:

```js
{p:'patron:osgood:yourBust',s:0,c:['said:warned'],t:"I said. Not enough yet."},
{p:'patron:nell:yourBust',s:0,c:['said:warned'],t:"I did say, love."},
{p:'patron:eira:yourBust',s:0,c:['said:warned'],t:"I told you to watch."},
{p:'patron:ollis:yourBust',s:0,c:['said:warned'],t:"I gave you the odds. You had them."},
{p:'patron:twill:yourBust',s:0,c:['said:warned'],t:"Told you. Mop's already out."},
{p:'patron:krox:yourBust',s:0,c:['said:warned'],t:"I said wait. You thrashed."},
```

### `gossip:town` — 24 rows, so the room has something to say

The thread scheduler makes town the ordinary voice; ten rows will not
carry it.

```js
{p:'gossip:town',s:0,t:"Innkeep's watering the ale again. Everyone knows. Nobody says."},
{p:'gossip:town',s:0,t:"Cooper's boy has run off with a juggler. Third one this year."},
{p:'gossip:town',s:0,t:"Rain coming. My knee's never wrong."},
{p:'gossip:town',s:0,t:"There's a cat sleeps in the flour barrel. Innkeep pretends not to know."},
{p:'gossip:town',s:0,t:"Bridge tolls went up again. Someone's getting fat on it."},
{p:'gossip:town',s:0,t:"They found a boot in the well. Just the one."},
{p:'gossip:town',s:0,t:"Miller's wife hasn't spoken to him since the feast. Nobody knows why."},
{p:'gossip:town',s:0,t:"Candles are dear this season. Burn 'em slow."},
{p:'gossip:town',s:0,t:"Somebody's been leaving bread out for the crows. Odd habit."},
{p:'gossip:town',s:0,t:"Fiddler's back. Worse than last year, if you can believe it."},
{p:'gossip:town',s:0,t:"Whole street smelled of smoke Tuesday. Nobody'll say whose."},
{p:'gossip:town',s:0,t:"The old mill's got new shutters. New owner, they reckon."},
{p:'gossip:town',s:0,t:"Two carts came through at night. Covered. Didn't stop."},
{p:'gossip:town',s:0,t:"Blacksmith's taken an apprentice. Poor lad looks terrified."},
{p:'gossip:town',s:0,t:"Somebody's dog had nine pups. Nine! In this economy."},
{p:'gossip:town',s:0,t:"That corner table's been empty a fortnight. Nobody'll sit there."},
{p:'gossip:town',s:0,t:"Ale's up a penny. It's always up a penny."},
{p:'gossip:town',s:0,t:"Heard singing from the churchyard. Wrong hour for it."},
{p:'gossip:town',s:0,t:"Fishmonger's had a good week. You can tell by the hat."},
{p:'gossip:town',s:0,t:"They're saying the winter'll be soft. They said that last year."},
{p:'gossip:town',s:0,t:"Someone left a good coat on a hook. Three days now. Untouched."},
{p:'gossip:town',s:0,t:"Roof's leaking over the far bench. Sit elsewhere."},
{p:'gossip:town',s:0,t:"Baker's started closing early. Won't say why."},
{p:'gossip:town',s:0,t:"There's a new face in every third night lately. Busy season."},
```

Note three of these (the covered carts, the empty corner table, the
churchyard singing) are deliberately open — they cost nothing now and are
the seed of a third storyline if one is ever wanted.

---

## PART FOUR — VERIFICATION

- **Repetition, driven.** Twenty busts against one patron; count distinct
  lines. Today the ceiling is 3; after this it should be 4–5 per patron
  including the gated one.
- **Thread share.** Over a simulated run, `gossip:town` should be the
  most-heard thread and no thread should exceed ~35%. Assert on share,
  not on "appears at least once" — that cannot fail.
- **The tag must not set on an unseen line.** Trigger a King intro,
  overwrite it with a priority bark, assert `king_intro` is still unset.
- **Display duration.** Assert a 10-char line holds under 2s and a
  120-char line holds over 5s. The old floor made them equal.
- **Every id resolves.** All thirty ids above must exist in
  `PT_ART_POOL`. `peck` currently has no personal pool at all — these are
  his first lines.

---

## PART FIVE — THE TWO NEW MOMENTS, FILLED

Part One §6 adds `preroll` (they are about to throw) and `waiting` (you
have gone quiet). Both were on Denis's list of missing beats and both had
zero rows. These are the highest-value additions in this document,
because they are the only two moments where an opponent speaks
*unprompted by a result* — which is most of what makes a table feel
inhabited.

`waiting` is also the one moment that is **about the player** rather than
about the dice, so it is where personality reads loudest. Nobody nags the
same way.

```js
/* ── preroll: about to throw ── */
{p:'patron:corbin:preroll',s:0,t:"Let's see what the ledger says."},
{p:'patron:dunstan:preroll',s:0,t:"Shall we?"},
{p:'patron:eira:preroll',s:0,t:"Watch closely."},
{p:'patron:fenn:preroll',s:0,t:"Ssssomething good. I can feel it."},
{p:'patron:ferrand:preroll',s:0,t:"Ohhh here we go, here we GO —"},
{p:'patron:krox:preroll',s:0,t:"Mm."},
{p:'patron:mudge:preroll',s:0,t:"Ooh! Ooh ooh ooh."},
{p:'patron:nebb:preroll',s:0,t:"Let's get it over with."},
{p:'patron:nell:preroll',s:0,t:"Come on then, my lovelies."},
{p:'patron:nix:preroll',s:0,t:"Hungry."},
{p:'patron:odo:preroll',s:0,t:"HERE WE GO!"},
{p:'patron:ollis:preroll',s:0,t:"Six dice. Forty-six thousand outcomes. One throw."},
{p:'patron:osgood:preroll',s:0,t:"Rolling."},
{p:'patron:peck:preroll',s:0,t:"I already know. But go on."},
{p:'patron:pell:preroll',s:0,t:"Straighten up. Here it comes."},
{p:'patron:poll:preroll',s:0,t:"Right then! Let's see what grows."},
{p:'patron:rask:preroll',s:0,t:"Do try to keep up."},
{p:'patron:regis:preroll',s:0,t:"BEHOLD."},
{p:'patron:remny:preroll',s:0,t:"If we must."},
{p:'patron:rilla:preroll',s:0,t:"Fingers crossed, love."},
{p:'patron:roan:preroll',s:0,t:"Here goes. Sorry in advance."},
{p:'patron:sil:preroll',s:0,t:"Now."},
{p:'patron:sparr:preroll',s:0,t:"Sending it."},
{p:'patron:squib:preroll',s:0,t:"okayokayokay — "},
{p:'patron:tam:preroll',s:0,t:"Speculative. But sound."},
{p:'patron:thorne:preroll',s:0,t:"Let's find out."},
{p:'patron:tuck:preroll',s:0,t:"Ooh, my turn! My turn!"},
{p:'patron:twill:preroll',s:0,t:"Right. Quick one, I'm on shift."},
{p:'patron:vess:preroll',s:0,t:"Watch the wrist."},
{p:'patron:golgoth:preroll',s:0,nv:1,t:"breathing. just breathing."},
{p:'patron:golgoth:preroll',s:0,nv:1,t:"khk—"},

/* ── waiting: the player has gone quiet. The one moment that is about
      YOU rather than the dice, so it is where character reads loudest. */
{p:'patron:corbin:waiting',s:0,t:"I have all night. I am literally paid to wait."},
{p:'patron:corbin:waiting',s:0,t:"Take your time. I'm counting it."},
{p:'patron:dunstan:waiting',s:0,t:"No rush whatsoever. None at all."},
{p:'patron:dunstan:waiting',s:0,t:"Thinking? Good. Someone should."},
{p:'patron:eira:waiting',s:0,t:"Decide."},
{p:'patron:eira:waiting',s:0,t:"Owls are patient. I am not an owl about this."},
{p:'patron:fenn:waiting',s:0,t:"Ssssstill there?"},
{p:'patron:fenn:waiting',s:0,t:"I could wait in the sssun all day. Could you?"},
{p:'patron:ferrand:waiting',s:0,t:"Oi! Dice! Now!"},
{p:'patron:ferrand:waiting',s:0,t:"You gone to sleep? HA!"},
{p:'patron:krox:waiting',s:0,t:"I can hold my breath a very long time."},
{p:'patron:krox:waiting',s:0,t:"Take as long as you like. Truly."},
{p:'patron:mudge:waiting',s:0,t:"Any day! Any day now!"},
{p:'patron:mudge:waiting',s:0,t:"My coin's getting cold."},
{p:'patron:nebb:waiting',s:0,t:"I might die at this table. Genuinely."},
{p:'patron:nebb:waiting',s:0,t:"Whenever you're ready. I've got years. Some."},
{p:'patron:nell:waiting',s:0,t:"Still with me, duckling?"},
{p:'patron:nell:waiting',s:0,t:"Take a breath, love. Then throw."},
{p:'patron:nix:waiting',s:0,t:"Circling."},
{p:'patron:nix:waiting',s:0,t:"You know sharks can't stop moving? I'm getting restless."},
{p:'patron:odo:waiting',s:0,t:"ROLL! ROLL THEM!"},
{p:'patron:odo:waiting',s:0,t:"I'VE GONE ALL TENSE!"},
{p:'patron:ollis:waiting',s:0,t:"Deliberation is correct. This much of it is not."},
{p:'patron:ollis:waiting',s:0,t:"The odds haven't changed since you started staring."},
{p:'patron:osgood:waiting',s:0,t:"Your turn."},
{p:'patron:osgood:waiting',s:0,t:"Dice. There."},
{p:'patron:peck:waiting',s:0,t:"I can see what you're going to do. It's taking ages."},
{p:'patron:peck:waiting',s:0,t:"Blink. You haven't in a while. Neither have I."},
{p:'patron:pell:waiting',s:0,t:"We do have a table to run."},
{p:'patron:pell:waiting',s:0,t:"Dawdling is a kind of untidiness."},
{p:'patron:poll:waiting',s:0,t:"No hurry! Sun's still up. Somewhere."},
{p:'patron:poll:waiting',s:0,t:"Take yer time. Crops don't rush neither."},
{p:'patron:rask:waiting',s:0,t:"How long does one need?"},
{p:'patron:rask:waiting',s:0,t:"I have been groomed, fed and bored. In that order."},
{p:'patron:regis:waiting',s:0,t:"THE CHALLENGER DELIBERATES. Still."},
{p:'patron:regis:waiting',s:0,t:"I crow at dawn. Shall I demonstrate?"},
{p:'patron:remny:waiting',s:0,t:"Mm. Is this part of your strategy?"},
{p:'patron:remny:waiting',s:0,t:"I could buy the tavern in the time you've taken."},
{p:'patron:rilla:waiting',s:0,t:"You alright there, love?"},
{p:'patron:rilla:waiting',s:0,t:"No rush. Shall I get you something?"},
{p:'patron:roan:waiting',s:0,t:"Take your time. I mean it."},
{p:'patron:roan:waiting',s:0,t:"Sorry — am I putting you off? I'll look away."},
{p:'patron:sil:waiting',s:0,t:"Throw."},
{p:'patron:sil:waiting',s:0,t:"I don't like waiting."},
{p:'patron:sparr:waiting',s:0,t:"I've three more stops tonight."},
{p:'patron:sparr:waiting',s:0,t:"Message for you: hurry up."},
{p:'patron:squib:waiting',s:0,t:"is it me? did I do something? roll!"},
{p:'patron:squib:waiting',s:0,t:"waiting waiting waiting waiting —"},
{p:'patron:tam:waiting',s:0,t:"Time is the one cost nobody itemises."},
{p:'patron:tam:waiting',s:0,t:"I'd charge interest, but I'm a gentleman."},
{p:'patron:thorne:waiting',s:0,t:"Whenever you're ready."},
{p:'patron:thorne:waiting',s:0,t:"I've been told I'm very good at waiting. It isn't a compliment."},
{p:'patron:tuck:waiting',s:0,t:"Oh — sorry, was it me? Is it my go?"},
{p:'patron:tuck:waiting',s:0,t:"I'll just... wait here. Happily!"},
{p:'patron:twill:waiting',s:0,t:"I could've swept the whole room by now."},
{p:'patron:twill:waiting',s:0,t:"Some of us finish at midnight."},
{p:'patron:vess:waiting',s:0,t:"Poise is one thing. This is another."},
{p:'patron:vess:waiting',s:0,t:"Do let me know when you've decided."},
{p:'patron:golgoth:waiting',s:0,nv:1,t:"the mask turns to you. waits."},
{p:'patron:golgoth:waiting',s:0,nv:1,t:"hhhhhhhhhh."},
```

---

## PART ONE, §7 — NON-VERBAL LINES (`nv:1`)

Golgoth needs one small engine addition. `DLG.show()` wraps every line in
curly quotes unconditionally:

```js
const full='“'+text+'”';
```

A wheeze inside speech marks reads as someone *saying the word* "wheeze".
Add the flag:

```js
/* P8xx: nv rows are not speech - Golgoth wears a plague mask and never
   says a word (Denis). Rendered without quote marks and in italic, so
   breath and business read as what they are. The flag is on the ROW, so
   any patron can take a wordless beat without a second code path. */
const full=row.nv?text:('“'+text+'”');
if(row.nv)textEl.classList.add('dlg-nv'); else textEl.classList.remove('dlg-nv');
```

```css
.dlg-nv{font-style:italic;opacity:.82;letter-spacing:.3px}
```

`_dlgEvent` returns `r.t` today; it needs to return the row (or `{t,nv}`)
so the flag survives to `show()`. That is the same change §3 already
needs for committing `heard` on display, so do them together.

**Golgoth is the only patron built this way and that is the point** —
thirty voices and one silence. Resist giving anyone else `nv` rows except
as a rare beat (Sil's "..." is the one other candidate).
