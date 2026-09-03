# THE VOICE PASS — medieval register, and Fark as an oath

*2026-08-24. Supersedes the line tables in `FARK_DIALOGUE_BUILD.md`
Parts Three and Five. That document's engine changes (Part One) and
character bible (Part Two) stand unchanged — this replaces only the
words. Denis: "more medieval… slang… people saying Fark! as an
expletive… it overall feels quite formal for a lot of the characters
which are commoners."*

---

## 1. THE RULES OF THE REGISTER

### FARK is the oath

The game is named after it, so it is the tavern's own curse and nobody
needs it explained. Forms, all usable:

| form | use |
|---|---|
| **Fark!** | the bare exclamation |
| **Fark me** | dismay at your own fortune |
| **farkin'** | the intensifier — *farkin' dice* |
| **farked** | ruined — *well, that's you farked* |
| **fark all** | nothing at all |
| **gone to Fark** | lost entirely |
| **what in Fark** | disbelief |

**Who swears matters more than how often.** The gutter voices use it
freely; the middling ones once or twice; the high ones **never** — and
that restraint is what gives it force when Rask finally does. One oath
from a character who has never sworn is worth twenty from Odo.

### Three registers, not one

The old lines read like a costume drama. These are tavern regulars.

**GUTTER** — odo, squib, tuck, twill, poll, nell, ferrand, mudge, nix,
sparr, peck. Dropped g's, `aye`, `nowt`, `owt`, `summat`, `reckon`,
`afore`, `'tis`, `naught`. Contractions everywhere. Swears freely.

**MIDDLING** — corbin, nebb, osgood, roan, sil, rilla, krox, fenn, pell,
tam, thorne. Plain speech, period vocabulary, few flourishes. The odd
oath, and it lands because it is rare.

**HIGH** — regis, rask, remny, vess, dunstan, eira, ollis, golgoth.
Archaic-formal: `thee`, `thy`, `ye`, `mark me`, `I'll wager`, `come
now`. **Never** modern-formal — "statistically overdue" and "within
expected variance" are the wrong century. Ollis is learned, not modern:
he counts in *scores* and swears by *the saints*, not by data.

### What to strike on sight

`acceptable` · `adequate` · `respectable` · `statistically` ·
`variance` · `investment` · `strategic` · `composure` · `precisely` ·
`correct decision` · `expected`. Every one of them is 19th-century
office English wearing a doublet.

---

## 2. THE MEMORY THE WORDS ASSUME

*Read this before typing any of §3. Two of the things the tables below
take for granted are not true of the live build, and one of them is a
field collision I put there myself.*

### 2.1 `say:` — NOT `g:`, which is already taken

An earlier draft of this pass tagged the push lines `g:'warned'`. That is
wrong and would have failed silently. `g` is the anti-repeat group key:

```js
var lastG=_dlgLastG[pool];          /* 19833 */
if(pick&&pick.g)_dlgLastG[pool]=pick.g;   /* 19839 */
```

`_dlgLastG` is keyed **by pool**, so `g:'warned'` on `patron:krox:push`
writes `_dlgLastG['patron:krox:push']` and is invisible to a line reading
from `patron:krox:yourBust`. The gate would never open, nothing would
error, and the seven best lines in the pass would be dead rows.

The field is `say:`, and it needs its own store:

```js
/* WHAT WAS ACTUALLY SAID THIS MATCH. Module state beside _dlgLastG and
   cleared by the same reset, because it answers the same question -
   "did this happen in this match" - for two callers:
     keys that are line TEXT      -> the soft anti-repeat (2.2)
     keys that are 'said:<tag>'   -> what a later line may refer back to
   One map, not two: a second store for the second use is the defect
   this file keeps finding. _dlgHeard is the per-RUN, save()-backed set
   for story tags and is untouched by any of this. */
var _dlgSaid={};
function _dlgResetGroups(){_dlgLastG={};_dlgSaid={};}
```

`_dlgResetGroups()` is already called at match start (40266) and is the
only caller, so the per-match lifetime comes free.

The condition, beside `heard` in `_DLG_COND`:

```js
said:function(a){return !!_dlgSaid['said:'+a];}
```

**Order matters.** `_dlgCondOk` does `if(!fn||!fn(bits[1]))return false;` —
an unknown condition name fails the row *silently*. Ship `_DLG_COND.said`
in the same commit as the first `c:['said:warned']` row, or every gated
line is permanently unpickable and nothing complains.

One property worth knowing rather than rediscovering: `_dlgPick` ranks
most-conditions-first, so a gated `yourBust` line with one condition
outranks the ungated ones beside it whenever the gate is open. That is
the behaviour you want — when they really did warn you, "told you" should
win — and it is why these rows need no extra weighting.

### 2.2 The de-dup these tables assume does not exist yet

§5 of this document used to claim the per-run de-dup would stop a patron
repeating. It would not. Both doors pass **`null`** where the skip map
goes:

```js
if(art)r=_dlgPick('patron:'+String(art).toLowerCase()+':'+moment,0,null);  /* _dlgEvent */
if(!row)row=_dlgPick('patron:'+key,stage,null);                            /* _dlgSay  */
```

`run._dlgHeard` is passed only to `reaction:discrepancy` and
`reaction:king`. Every patron line in the game — greeting, reaction,
outcome — is drawn from the full pool every time. Ten rows and a fair
coin repeat inside a night; that is most of why the barks feel canned,
and no amount of writing fixes it.

The fix is at the call site, in two lines, and it must be **soft**:

```js
/* prefer something not yet said this match, but never return NO line:
   a de-dup that can empty the pool turns a repeat into silence, which
   is worse - the rule _dlgPick already applies to the group exclusion. */
var r=_dlgPick(pool,0,_dlgSaid)||_dlgPick(pool,0,null);
if(r){_dlgSaid[r.t]=1;if(r.say)_dlgSaid['said:'+r.say]=1;}
```

Do **not** move this guard inside `_dlgPick`. The story pools want the
hard drop — a King beat firing twice is worse than not firing — and
`_dlgPick` is shared.

### 2.3 Peck has no lines. At all.

`PT_ART_POOL` (19735) holds 30 names and any of them can take a seat.
Counting rows per name across all 1003:

| | |
|---|---|
| 28 of 30 | 13–19 rows each |
| Golgoth | 6 |
| **Peck** | **0** |

The string `peck` does not occur anywhere in the file. `_dlgEvent`
lowercases the art name to build its key, so a seated Peck asks for
`patron:peck:<moment>`, gets nothing, and falls through to `trait:*`
forever. He is the one patron in the game with no voice, and it reads as
a bug rather than a personality. §3 gives him ten rows like everyone
else; that is the fix, but Code should know the hole was already there
and is not something this pass introduced.

---

## 3. THE LINES

Replaces the block in `FARK_DIALOGUE_BUILD.md` Part Three. Same format,
same ids, same moments.

```js
/* ══ PER-PATRON TABLE VOICES ═══════════════════════════════════════════
   Written to the PORTRAITS and to the register ladder in
   FARK_DIALOGUE_VOICE.md §1. These are tavern regulars, not courtiers:
   the gutter voices drop their g's and swear by Fark, the middling ones
   speak plain, and only the high ones reach for `thee`. Nobody says
   "acceptable". */

/* CORBIN — crow, counts everything, says half of it. MIDDLING */
{p:'patron:corbin:yourBust',s:0,t:"Marked."},
{p:'patron:corbin:yourBust',s:0,t:"Third time tonight. I keep the tally."},
{p:'patron:corbin:bust',s:0,t:"...I'll amend the figure."},
{p:'patron:corbin:yourBank',s:0,t:"Mm. Down it goes."},
{p:'patron:corbin:bank',s:0,t:"Squared."},
{p:'patron:corbin:push',s:0,say:'warned',t:"This is ill-advised. I'll do it regardless."},
{p:'patron:corbin:banksafe',s:0,t:"The book likes it better this way."},
{p:'patron:corbin:preroll',s:0,t:"Let's see what the reckoning says."},
{p:'patron:corbin:waiting',s:0,t:"Take all night. I'm counting the hour too."},
{p:'patron:corbin:waiting',s:0,t:"I've naught but time and a long memory."},

/* DUNSTAN — goat, courteous, faintly condescending. HIGH */
{p:'patron:dunstan:yourBust',s:0,t:"Oh, hard luck. Truly."},
{p:'patron:dunstan:yourBust',s:0,t:"These things befall us. Some of us oftener."},
{p:'patron:dunstan:bust',s:0,t:"Well. That wanted dignity."},
{p:'patron:dunstan:yourBank',s:0,t:"Handsomely done. I mean it kindly."},
{p:'patron:dunstan:bank',s:0,t:"One does try."},
{p:'patron:dunstan:push',s:0,say:'warned',t:"I oughtn't. And yet here we are."},
{p:'patron:dunstan:banksafe',s:0,t:"Enough is a perfectly good sum."},
{p:'patron:dunstan:preroll',s:0,t:"Shall we, then?"},
{p:'patron:dunstan:waiting',s:0,t:"No haste. None whatsoever."},
{p:'patron:dunstan:waiting',s:0,t:"Thinking, are we? Good. Someone ought."},

/* EIRA — owl, severe, few words. HIGH */
{p:'patron:eira:yourBust',s:0,t:"As I thought."},
{p:'patron:eira:yourBust',s:0,t:"I saw that from across the room."},
{p:'patron:eira:bust',s:0,t:"...Hm."},
{p:'patron:eira:yourBank',s:0,t:"That will do."},
{p:'patron:eira:bank',s:0,t:"As intended."},
{p:'patron:eira:push',s:0,say:'warned',t:"Watch."},
{p:'patron:eira:banksafe',s:0,t:"I do not gamble. I reckon."},
{p:'patron:eira:preroll',s:0,t:"Eyes open."},
{p:'patron:eira:waiting',s:0,t:"Decide."},
{p:'patron:eira:waiting',s:0,t:"Owls are patient. I am not, about this."},

/* FENN — snake, sibilant, enjoys your trouble. MIDDLING */
{p:'patron:fenn:yourBust',s:0,t:"Ssssuch a pity."},
{p:'patron:fenn:yourBust',s:0,t:"All that, and fark all to show."},
{p:'patron:fenn:bust',s:0,t:"Sssso. Even I bite myself now and again."},
{p:'patron:fenn:yourBank',s:0,t:"Clever little thing."},
{p:'patron:fenn:bank',s:0,t:"Swallowed whole."},
{p:'patron:fenn:push',s:0,say:'warned',t:"One more. Alwaysss one more."},
{p:'patron:fenn:banksafe',s:0,t:"I coil. I bide."},
{p:'patron:fenn:preroll',s:0,t:"Ssssomething good. I feel it in the belly."},
{p:'patron:fenn:waiting',s:0,t:"Ssstill there?"},
{p:'patron:fenn:waiting',s:0,t:"I could lie in the sssun till spring. Could you?"},

/* FERRAND — hyena, laughs first, thinks later. GUTTER */
{p:'patron:ferrand:yourBust',s:0,t:"HAH! Oh, that's lovely, that is."},
{p:'patron:ferrand:yourBust',s:0,t:"Farked! Ha! Do it again!"},
{p:'patron:ferrand:bust',s:0,t:"Ha. HA. ...nah, that's not funny."},
{p:'patron:ferrand:yourBank',s:0,t:"Pff. Jammy."},
{p:'patron:ferrand:bank',s:0,t:"HAH! Mine, that."},
{p:'patron:ferrand:push',s:0,say:'warned',t:"Why not? WHY NOT!"},
{p:'patron:ferrand:banksafe',s:0,t:"...aye, fine. Fine! I'll take it."},
{p:'patron:ferrand:preroll',s:0,t:"Ohhh here we go, here we FARKIN' go —"},
{p:'patron:ferrand:waiting',s:0,t:"Oi! Dice! Now!"},
{p:'patron:ferrand:waiting',s:0,t:"You gone to sleep? HA!"},

/* GOLGOTH — THE ONE WHO DOES NOT SPEAK. nv:1 on every row. */
{p:'patron:golgoth:yourBust',s:0,nv:1,t:"hhhhhhh…"},
{p:'patron:golgoth:yourBust',s:0,nv:1,t:"kh. kh. khhhk."},
{p:'patron:golgoth:yourBust',s:0,nv:1,t:"the beak tilts. slowly."},
{p:'patron:golgoth:bust',s:0,nv:1,t:"…hnnh."},
{p:'patron:golgoth:bust',s:0,nv:1,t:"a long breath out. glass eyes, fixed."},
{p:'patron:golgoth:yourBank',s:0,nv:1,t:"hhh—hk."},
{p:'patron:golgoth:yourBank',s:0,nv:1,t:"one gloved finger taps the board. once."},
{p:'patron:golgoth:bank',s:0,nv:1,t:"khhhhh."},
{p:'patron:golgoth:bank',s:0,nv:1,t:"the mask does not move."},
{p:'patron:golgoth:push',s:0,say:'warned',nv:1,t:"a slow drag of breath through the beak."},
{p:'patron:golgoth:banksafe',s:0,nv:1,t:"hnn. hnn."},
{p:'patron:golgoth:preroll',s:0,nv:1,t:"breathing. only breathing."},
{p:'patron:golgoth:preroll',s:0,nv:1,t:"khk—"},
{p:'patron:golgoth:waiting',s:0,nv:1,t:"the mask turns to you. waits."},
{p:'patron:golgoth:waiting',s:0,nv:1,t:"hhhhhhhhhh."},

/* KROX — crocodile, slow, heavy, certain. MIDDLING */
{p:'patron:krox:yourBust',s:0,t:"Mm. Thought as much."},
{p:'patron:krox:yourBust',s:0,t:"You thrashed. That's when they take you."},
{p:'patron:krox:bust',s:0,t:"...huh."},
{p:'patron:krox:yourBank',s:0,t:"Good. Bigger meal later."},
{p:'patron:krox:bank',s:0,t:"Bide. Then teeth."},
{p:'patron:krox:push',s:0,say:'warned',t:"Not yet. Not yet."},
{p:'patron:krox:banksafe',s:0,t:"I don't chase. I wait at the water."},
{p:'patron:krox:preroll',s:0,t:"Mm."},
{p:'patron:krox:waiting',s:0,t:"I can hold my breath a good long while."},
{p:'patron:krox:waiting',s:0,t:"Take as long as you like. I mean that."},

/* MUDGE — frog, foppish, money-pleased. GUTTER (but affects better) */
{p:'patron:mudge:yourBust',s:0,t:"Oh! Oh dear. Hee."},
{p:'patron:mudge:yourBust',s:0,t:"All them lovely points. Gone! Gone to Fark!"},
{p:'patron:mudge:bust',s:0,t:"My coin! My beautiful farkin' coin!"},
{p:'patron:mudge:yourBank',s:0,t:"Hmph. Spend it wisely. Or don't, see if I care."},
{p:'patron:mudge:bank',s:0,t:"Into the purse. Hee hee."},
{p:'patron:mudge:push',s:0,say:'warned',t:"More! There's always more!"},
{p:'patron:mudge:banksafe',s:0,t:"A coin in hand's worth countin'."},
{p:'patron:mudge:preroll',s:0,t:"Ooh! Ooh ooh ooh."},
{p:'patron:mudge:waiting',s:0,t:"Any day! Any day now!"},
{p:'patron:mudge:waiting',s:0,t:"Me coin's gone cold waitin'."},

/* NEBB — old stork, expects the worst. MIDDLING */
{p:'patron:nebb:yourBust',s:0,t:"Aye. That's how it goes."},
{p:'patron:nebb:yourBust',s:0,t:"Seen a hundred o' those. Hundred more comin'."},
{p:'patron:nebb:bust',s:0,t:"Well. I'm old. I've had worse."},
{p:'patron:nebb:yourBank',s:0,t:"Enjoy it while it's yours."},
{p:'patron:nebb:bank',s:0,t:"Small mercies."},
{p:'patron:nebb:push',s:0,say:'warned',t:"Ah, why not. I'll not get younger."},
{p:'patron:nebb:banksafe',s:0,t:"At my age you take what's put in front of you."},
{p:'patron:nebb:preroll',s:0,t:"Let's have it over with."},
{p:'patron:nebb:waiting',s:0,t:"I might die at this table. I'm not jestin'."},
{p:'patron:nebb:waiting',s:0,t:"Whenever you're ready. I've years yet. Some."},

/* NELL — hare, warm and shrewd, gives you names. GUTTER */
{p:'patron:nell:yourBust',s:0,t:"Ohh, duckling. Come here."},
{p:'patron:nell:yourBust',s:0,t:"That's a hard one, love. Shake it off."},
{p:'patron:nell:bust',s:0,t:"Serves me right, don't it."},
{p:'patron:nell:yourBank',s:0,t:"Look at you go, my lamb."},
{p:'patron:nell:bank',s:0,t:"Don't mind if I do."},
{p:'patron:nell:push',s:0,say:'warned',t:"One more, then I'm done. Promise."},
{p:'patron:nell:banksafe',s:0,t:"Hare knows when to quit runnin'."},
{p:'patron:nell:preroll',s:0,t:"Come on then, my lovelies."},
{p:'patron:nell:waiting',s:0,t:"Still with me, duckling?"},
{p:'patron:nell:waiting',s:0,t:"Take a breath, love. Then throw."},

/* NIX — shark, cheerful about violence. GUTTER */
{p:'patron:nix:yourBust',s:0,t:"Blood in the water. Lovely."},
{p:'patron:nix:yourBust',s:0,t:"Ohh, down you went. Happens."},
{p:'patron:nix:bust',s:0,t:"Bit off more'n I could chew."},
{p:'patron:nix:yourBank',s:0,t:"Nice bite. Leave us some."},
{p:'patron:nix:bank',s:0,t:"Chomp."},
{p:'patron:nix:push',s:0,say:'warned',t:"Keep swimmin' or you sink!"},
{p:'patron:nix:banksafe',s:0,t:"Eat what you caught. Then hunt again."},
{p:'patron:nix:preroll',s:0,t:"Hungry."},
{p:'patron:nix:waiting',s:0,t:"Circlin'."},
{p:'patron:nix:waiting',s:0,t:"We can't stop movin', my lot. I'm gettin' twitchy."},

/* ODO — otter, loud, no volume control. GUTTER */
{p:'patron:odo:yourBust',s:0,t:"OOF! Right in front o' me!"},
{p:'patron:odo:yourBust',s:0,t:"NO! No no no. FARK! That HURT!"},
{p:'patron:odo:bust',s:0,t:"AAGH! Why! WHY!"},
{p:'patron:odo:yourBank',s:0,t:"WHOO! Look at that!"},
{p:'patron:odo:bank',s:0,t:"YES! HA! YES!"},
{p:'patron:odo:push',s:0,say:'warned',t:"AGAIN! ONE MORE! AGAIN!"},
{p:'patron:odo:banksafe',s:0,t:"...right. RIGHT. Bankin'. Bankin'!"},
{p:'patron:odo:preroll',s:0,t:"HERE WE GO!"},
{p:'patron:odo:waiting',s:0,t:"ROLL! ROLL 'EM!"},
{p:'patron:odo:waiting',s:0,t:"I'VE GONE ALL TENSE!"},

/* OLLIS — spectacled owl. LEARNED, not modern. Counts in scores. */
{p:'patron:ollis:yourBust',s:0,t:"Long overdue, that."},
{p:'patron:ollis:yourBust',s:0,t:"A wretched showing. Instructive, though."},
{p:'patron:ollis:bust',s:0,t:"An oddity. It happens to the best of us."},
{p:'patron:ollis:yourBank',s:0,t:"Handsome. Better than the odds allowed."},
{p:'patron:ollis:bank',s:0,t:"Just as I had it reckoned."},
{p:'patron:ollis:push',s:0,say:'warned',t:"The odds say nay. I am curious regardless."},
{p:'patron:ollis:banksafe',s:0,t:"The right course is seldom the merry one."},
{p:'patron:ollis:preroll',s:0,t:"Six dice. More outcomes than there are souls in this town."},
{p:'patron:ollis:waiting',s:0,t:"Deliberation is proper. This much of it is not."},
{p:'patron:ollis:waiting',s:0,t:"The odds have not shifted since you began staring."},

/* OSGOOD — bull, immovable, says the obvious. MIDDLING */
{p:'patron:osgood:yourBust',s:0,t:"Bust."},
{p:'patron:osgood:yourBust',s:0,t:"You had enough. You went on."},
{p:'patron:osgood:bust',s:0,t:"Bad throw."},
{p:'patron:osgood:yourBank',s:0,t:"Good number."},
{p:'patron:osgood:bank',s:0,t:"Banked."},
{p:'patron:osgood:push',s:0,say:'warned',t:"Not enough yet."},
{p:'patron:osgood:banksafe',s:0,t:"That'll serve."},
{p:'patron:osgood:preroll',s:0,t:"Throwin'."},
{p:'patron:osgood:waiting',s:0,t:"Your throw."},
{p:'patron:osgood:waiting',s:0,t:"Dice. There."},

/* PECK — one enormous eye, sees sideways. GUTTER */
{p:'patron:peck:yourBust',s:0,t:"I watched every one o' them. All at once."},
{p:'patron:peck:yourBust',s:0,t:"Them dice was wrong afore they landed."},
{p:'patron:peck:bust',s:0,t:"I saw it comin'. Didn't help none."},
{p:'patron:peck:yourBank',s:0,t:"Bright. Very bright. Too bright."},
{p:'patron:peck:bank',s:0,t:"It all lines up, you look at it proper."},
{p:'patron:peck:push',s:0,say:'warned',t:"Next one's already happened. Somewhere."},
{p:'patron:peck:banksafe',s:0,t:"Stop. Blink. Stop."},
{p:'patron:peck:preroll',s:0,t:"I know already. Go on, though."},
{p:'patron:peck:waiting',s:0,t:"I can see what you'll do. Takin' you an age."},
{p:'patron:peck:waiting',s:0,t:"Blink. You've not, in a while. Nor me."},

/* PELL — goose, tidy, disapproving of mess. MIDDLING */
{p:'patron:pell:yourBust',s:0,t:"Well, that's a mess."},
{p:'patron:pell:yourBust',s:0,t:"You could have folded that neat. You did not."},
{p:'patron:pell:bust',s:0,t:"Untidy. My apologies."},
{p:'patron:pell:yourBank',s:0,t:"Properly done. Thank you."},
{p:'patron:pell:bank',s:0,t:"Straightened."},
{p:'patron:pell:push',s:0,say:'warned',t:"It isn't finished yet."},
{p:'patron:pell:banksafe',s:0,t:"A tidy sum. A tidy end."},
{p:'patron:pell:preroll',s:0,t:"Sit up. Here it comes."},
{p:'patron:pell:waiting',s:0,t:"We've a table to run, you know."},
{p:'patron:pell:waiting',s:0,t:"Dawdlin' is its own sort of untidiness."},

/* POLL — turtle in a straw hat, sunny, farm talk. GUTTER */
{p:'patron:poll:yourBust',s:0,t:"Aw, Fark. Bad weather, that."},
{p:'patron:poll:yourBust',s:0,t:"Some seasons the crop just don't come."},
{p:'patron:poll:bust',s:0,t:"Hah! Well, that's the frost got me."},
{p:'patron:poll:yourBank',s:0,t:"Good harvest! Good on yer!"},
{p:'patron:poll:bank',s:0,t:"In the barn she goes."},
{p:'patron:poll:push',s:0,say:'warned',t:"One more row afore dark."},
{p:'patron:poll:banksafe',s:0,t:"Don't pick more'n you can carry."},
{p:'patron:poll:preroll',s:0,t:"Right then! Let's see what grows."},
{p:'patron:poll:waiting',s:0,t:"No hurry! Sun's still up. Somewhere."},
{p:'patron:poll:waiting',s:0,t:"Take yer time. Crops don't rush neither."},

/* RASK — sphinx cat, vain, wounded pride. HIGH — and the one oath */
{p:'patron:rask:yourBust',s:0,t:"How very common."},
{p:'patron:rask:yourBust',s:0,t:"I would say I am sorry. I would be lying."},
{p:'patron:rask:bust',s:0,t:"...Fark."},
{p:'patron:rask:yourBank',s:0,t:"Passable. For thee."},
{p:'patron:rask:bank',s:0,t:"Naturally."},
{p:'patron:rask:push',s:0,say:'warned',t:"I have never once settled."},
{p:'patron:rask:banksafe',s:0,t:"I choose to stop. That is not fear."},
{p:'patron:rask:preroll',s:0,t:"Do try to keep pace."},
{p:'patron:rask:waiting',s:0,t:"How long does one need?"},
{p:'patron:rask:waiting',s:0,t:"I have been groomed, fed and bored. In that order."},

/* REGIS — rooster with a monocle, pompous, announces. HIGH */
{p:'patron:regis:yourBust',s:0,t:"And the challenger FALLS."},
{p:'patron:regis:yourBust',s:0,t:"A calamity! Proclaimed by me!"},
{p:'patron:regis:bust',s:0,t:"I shall not be taking questions."},
{p:'patron:regis:yourBank',s:0,t:"A fine sum! Set it down!"},
{p:'patron:regis:bank',s:0,t:"Behold. And weep, belike."},
{p:'patron:regis:push',s:0,say:'warned',t:"The cockerel does not retreat at dawn!"},
{p:'patron:regis:banksafe',s:0,t:"A withdrawal of strategy. Nothing more."},
{p:'patron:regis:preroll',s:0,t:"BEHOLD."},
{p:'patron:regis:waiting',s:0,t:"THE CHALLENGER DELIBERATES. Still."},
{p:'patron:regis:waiting',s:0,t:"I crow at dawn. Shall I demonstrate?"},

/* REMNY — goat in gold, rich and bored. HIGH */
{p:'patron:remny:yourBust',s:0,t:"Mm. Was that meant to happen?"},
{p:'patron:remny:yourBust',s:0,t:"How wearying for thee."},
{p:'patron:remny:bust',s:0,t:"No matter. I have others."},
{p:'patron:remny:yourBank',s:0,t:"Charming. Is that a great deal, to you?"},
{p:'patron:remny:bank',s:0,t:"Put it with the rest."},
{p:'patron:remny:push',s:0,say:'warned',t:"I am not yet bored."},
{p:'patron:remny:banksafe',s:0,t:"I've made my point. That is the costly part."},
{p:'patron:remny:preroll',s:0,t:"If we must."},
{p:'patron:remny:waiting',s:0,t:"Mm. Is this part of thy scheme?"},
{p:'patron:remny:waiting',s:0,t:"I could buy this house in the time you've taken."},

/* RILLA — sheep, kind, worries about you. GUTTER-soft */
{p:'patron:rilla:yourBust',s:0,t:"Oh, love. Oh no."},
{p:'patron:rilla:yourBust',s:0,t:"Sit a minute. Have summat warm."},
{p:'patron:rilla:bust',s:0,t:"Oh, silly me."},
{p:'patron:rilla:yourBank',s:0,t:"There now! I knew you had it in you."},
{p:'patron:rilla:bank',s:0,t:"That's lovely, thank you kindly."},
{p:'patron:rilla:push',s:0,say:'warned',t:"Just a bit more. Then I'll stop."},
{p:'patron:rilla:banksafe',s:0,t:"That's plenty for anyone."},
{p:'patron:rilla:preroll',s:0,t:"Fingers crossed, love."},
{p:'patron:rilla:waiting',s:0,t:"You alright there, pet?"},
{p:'patron:rilla:waiting',s:0,t:"No rush. Shall I fetch you summat?"},

/* ROAN — rhino, huge and gentle, apologises for winning. MIDDLING */
{p:'patron:roan:yourBust',s:0,t:"Ah. Sorry. Truly, I am."},
{p:'patron:roan:yourBust',s:0,t:"That's rotten. I hate seein' that."},
{p:'patron:roan:bust',s:0,t:"That's fair. That's fair."},
{p:'patron:roan:yourBank',s:0,t:"Good. Good, you've earned it."},
{p:'patron:roan:bank',s:0,t:"Sorry. Didn't mean it to be so big."},
{p:'patron:roan:push',s:0,say:'warned',t:"Once more. Sorry."},
{p:'patron:roan:banksafe',s:0,t:"I'd rather not take too much off you."},
{p:'patron:roan:preroll',s:0,t:"Here goes. Sorry in advance."},
{p:'patron:roan:waiting',s:0,t:"Take your time. I mean it."},
{p:'patron:roan:waiting',s:0,t:"Sorry — am I puttin' you off? I'll look away."},

/* SIL — dark wolf, grim, minimal. MIDDLING */
{p:'patron:sil:yourBust',s:0,t:"Good."},
{p:'patron:sil:yourBust',s:0,t:"You're bleedin'. I can smell it."},
{p:'patron:sil:bust',s:0,nv:1,t:"..."},
{p:'patron:sil:yourBank',s:0,t:"Don't get comfortable."},
{p:'patron:sil:bank',s:0,t:"Taken."},
{p:'patron:sil:push',s:0,say:'warned',t:"Not finished."},
{p:'patron:sil:banksafe',s:0,t:"The pack eats. Then the pack moves."},
{p:'patron:sil:preroll',s:0,t:"Now."},
{p:'patron:sil:waiting',s:0,t:"Throw."},
{p:'patron:sil:waiting',s:0,t:"I don't care for waitin'."},

/* SPARR — pigeon messenger, reports rather than talks. GUTTER */
{p:'patron:sparr:yourBust',s:0,t:"I'll carry word o' that one."},
{p:'patron:sparr:yourBust',s:0,t:"Bust, corner table. That's the message."},
{p:'patron:sparr:bust',s:0,t:"Don't you put that in the letter."},
{p:'patron:sparr:yourBank',s:0,t:"Noted. Word travels."},
{p:'patron:sparr:bank',s:0,t:"Delivered."},
{p:'patron:sparr:push',s:0,say:'warned',t:"One more stop on the round."},
{p:'patron:sparr:banksafe',s:0,t:"Message sent. I'm away."},
{p:'patron:sparr:preroll',s:0,t:"Sendin' it."},
{p:'patron:sparr:waiting',s:0,t:"I've three more calls tonight."},
{p:'patron:sparr:waiting',s:0,t:"Message for you: get on with it."},

/* SQUIB — small lizard, twitchy, too fast. GUTTER */
{p:'patron:squib:yourBust',s:0,t:"ohhHH that's bad that's bad that's proper bad."},
{p:'patron:squib:yourBust',s:0,t:"Gone! All of it! Just — farkin' gone!"},
{p:'patron:squib:bust',s:0,t:"no no no no no."},
{p:'patron:squib:yourBank',s:0,t:"that's — right that's a lot, that's fine, that's fine."},
{p:'patron:squib:bank',s:0,t:"mine mine mine mine mine."},
{p:'patron:squib:push',s:0,say:'warned',t:"again! quick! afore I think!"},
{p:'patron:squib:banksafe',s:0,t:"stoppin'. stopped. done. stopped."},
{p:'patron:squib:preroll',s:0,t:"right right right — "},
{p:'patron:squib:waiting',s:0,t:"is it me? did I do summat? throw!"},
{p:'patron:squib:waiting',s:0,t:"waitin' waitin' waitin' —"},

/* TAM — boar merchant, smug, rounds up. MIDDLING */
{p:'patron:tam:yourBust',s:0,t:"A total loss. My condolences."},
{p:'patron:tam:yourBust',s:0,t:"Poor trade, that. I'd have counselled against."},
{p:'patron:tam:bust',s:0,t:"A write-off. It happens in trade."},
{p:'patron:tam:yourBank',s:0,t:"A tidy return. Tidy."},
{p:'patron:tam:bank',s:0,t:"Call it a round sum. My way."},
{p:'patron:tam:push',s:0,say:'warned',t:"The margin's thin yet."},
{p:'patron:tam:banksafe',s:0,t:"Profit taken. Never apologise for that."},
{p:'patron:tam:preroll',s:0,t:"A speculation. But a sound one."},
{p:'patron:tam:waiting',s:0,t:"Time's the one cost nobody puts in the book."},
{p:'patron:tam:waiting',s:0,t:"I'd charge you interest, but I'm a gentleman."},

/* THORNE — lynx, elegant, understates. MIDDLING-high */
{p:'patron:thorne:yourBust',s:0,t:"Unfortunate."},
{p:'patron:thorne:yourBust',s:0,t:"You did so well. Right up until."},
{p:'patron:thorne:bust',s:0,t:"Careless of me."},
{p:'patron:thorne:yourBank',s:0,t:"Neatly done."},
{p:'patron:thorne:bank',s:0,t:"A small thing."},
{p:'patron:thorne:push',s:0,say:'warned',t:"One more, I think."},
{p:'patron:thorne:banksafe',s:0,t:"I know what I'm worth to the penny."},
{p:'patron:thorne:preroll',s:0,t:"Let's find out."},
{p:'patron:thorne:waiting',s:0,t:"Whenever you're ready."},
{p:'patron:thorne:waiting',s:0,t:"I'm told I wait well. It isn't meant kindly."},

/* TUCK — mouse, eager, delighted to be here. GUTTER */
{p:'patron:tuck:yourBust',s:0,t:"Oh no! Oh, I'm sorry!"},
{p:'patron:tuck:yourBust',s:0,t:"That's awful, that. You alright?"},
{p:'patron:tuck:bust',s:0,t:"Whoops! That's me done, then!"},
{p:'patron:tuck:yourBank',s:0,t:"Cor! That's brilliant, that is!"},
{p:'patron:tuck:bank',s:0,t:"I got some! I actually got some!"},
{p:'patron:tuck:push',s:0,say:'warned',t:"Just one more! Just the one!"},
{p:'patron:tuck:banksafe',s:0,t:"That's loads, that is. That's loads."},
{p:'patron:tuck:preroll',s:0,t:"Ooh, my go! My go!"},
{p:'patron:tuck:waiting',s:0,t:"Oh — sorry, is it me? Is it my go?"},
{p:'patron:tuck:waiting',s:0,t:"I'll just... wait here. Happily!"},

/* TWILL — mouse in an apron, works here, has to clean up. GUTTER */
{p:'patron:twill:yourBust',s:0,t:"Mm. I'll fetch the mop."},
{p:'patron:twill:yourBust',s:0,t:"Fourth one tonight. I'm keepin' count."},
{p:'patron:twill:bust',s:0,t:"Right. Back to work, then."},
{p:'patron:twill:yourBank',s:0,t:"Good for you. Mind the table."},
{p:'patron:twill:bank',s:0,t:"That's me week's wages, that."},
{p:'patron:twill:push',s:0,say:'warned',t:"I'm on at the hour. One more."},
{p:'patron:twill:banksafe',s:0,t:"I've swept up after enough o' them."},
{p:'patron:twill:preroll',s:0,t:"Right. Quick one, I'm on shift."},
{p:'patron:twill:waiting',s:0,t:"I could've swept the whole room by now."},
{p:'patron:twill:waiting',s:0,t:"Some of us finish at midnight, you know."},

/* VESS — cat, composed, faintly regal. HIGH */
{p:'patron:vess:yourBust',s:0,t:"Oh, my dear."},
{p:'patron:vess:yourBust',s:0,t:"Bearing. It's the only thing that travels."},
{p:'patron:vess:bust',s:0,t:"How very tiresome."},
{p:'patron:vess:yourBank',s:0,t:"Elegant. I approve."},
{p:'patron:vess:bank',s:0,t:"Just so."},
{p:'patron:vess:push',s:0,say:'warned',t:"I am not done being interesting."},
{p:'patron:vess:banksafe',s:0,t:"One ought always leave before the end."},
{p:'patron:vess:preroll',s:0,t:"Watch the wrist."},
{p:'patron:vess:waiting',s:0,t:"Poise is one thing. This is another."},
{p:'patron:vess:waiting',s:0,t:"Do let me know when thou'st decided."},
```

### The gated "told you" lines, in register

*These require §2.1 — the `say:` store and `_DLG_COND.said` — in the same
commit. Seven patrons only, and deliberately: the joke is that some of
them remember and most don't.*

```js
{p:'patron:osgood:yourBust',s:0,c:['said:warned'],t:"I said. Not enough yet."},
{p:'patron:nell:yourBust',s:0,c:['said:warned'],t:"I did say, love."},
{p:'patron:eira:yourBust',s:0,c:['said:warned'],t:"I bid thee watch."},
{p:'patron:ollis:yourBust',s:0,c:['said:warned'],t:"I gave you the odds. You had 'em."},
{p:'patron:twill:yourBust',s:0,c:['said:warned'],t:"Told you. Mop's already out."},
{p:'patron:krox:yourBust',s:0,c:['said:warned'],t:"I said bide. You thrashed."},
{p:'patron:ferrand:yourBust',s:0,c:['said:warned'],t:"I FARKIN' TOLD YOU! HAH!"},
```

---

## 4. TOWN GOSSIP, IN THE SAME MOUTH

Replaces the `gossip:town` block. These are overheard, so they carry the
room's register rather than any one patron's.

```js
{p:'gossip:town',s:0,t:"Innkeep's waterin' the ale again. Everyone knows. Nobody says."},
{p:'gossip:town',s:0,t:"Cooper's lad's run off with a juggler. Third one this year."},
{p:'gossip:town',s:0,t:"Rain comin'. Me knee's never wrong."},
{p:'gossip:town',s:0,t:"There's a cat sleeps in the flour barrel. Innkeep pretends he don't know."},
{p:'gossip:town',s:0,t:"Bridge toll's up again. Someone's gettin' fat on it."},
{p:'gossip:town',s:0,t:"They found a boot in the well. Just the one."},
{p:'gossip:town',s:0,t:"Miller's wife's not spoke to him since the feast. Nobody knows why."},
{p:'gossip:town',s:0,t:"Candles are dear this season. Burn 'em slow."},
{p:'gossip:town',s:0,t:"Somebody's been leavin' bread out for the crows. Odd habit."},
{p:'gossip:town',s:0,t:"Fiddler's back. Worse than last year, if you can credit it."},
{p:'gossip:town',s:0,t:"Whole street stank o' smoke Tuesday. Nobody'll say whose."},
{p:'gossip:town',s:0,t:"Old mill's got new shutters. New owner, they reckon."},
{p:'gossip:town',s:0,t:"Two carts come through in the night. Covered. Didn't stop."},
{p:'gossip:town',s:0,t:"Smith's taken an 'prentice. Poor lad looks terrified."},
{p:'gossip:town',s:0,t:"Somebody's dog had nine pups. Nine! In this year!"},
{p:'gossip:town',s:0,t:"That corner table's been empty a fortnight. Nobody'll sit there."},
{p:'gossip:town',s:0,t:"Ale's up a penny. It's always up a farkin' penny."},
{p:'gossip:town',s:0,t:"Heard singin' from the churchyard. Wrong hour for it."},
{p:'gossip:town',s:0,t:"Fishmonger's had a good week. You can tell by the hat."},
{p:'gossip:town',s:0,t:"They say the winter'll be soft. They said that last year."},
{p:'gossip:town',s:0,t:"Someone left a good coat on a hook. Three days. Untouched."},
{p:'gossip:town',s:0,t:"Roof's leakin' over the far bench. Sit elsewhere."},
{p:'gossip:town',s:0,t:"Baker's started shuttin' early. Won't say why."},
{p:'gossip:town',s:0,t:"New face in here every third night lately. Busy season."},
{p:'gossip:town',s:0,t:"Fark me, it's cold. Shut the door behind you."},
{p:'gossip:town',s:0,t:"Tanner's boy come back from the coast. Won't speak of it."},
```

---

## 5. WHAT THIS CHANGED, AND THE CHECK

The register ladder is doing the work, not the vocabulary. Three tests
worth running by eye before this ships:

- **Read Rask's `bust` line.** It is the single word "...Fark." He is the
  only HIGH voice who swears and he does it once, at his worst moment.
  If that does not land harder than any of Odo's, the ladder is not
  working and the oath is being spent too freely elsewhere.
- **Read the `waiting` block straight through.** Thirty characters
  reacting to the same neutral event is the cleanest test of whether the
  voices are distinct.
- **Grep the struck-word list** (§1) against the final tables. Any
  survivor is a line that is still wearing the wrong century.

And one that has to be measured rather than read, because it is the ask
Denis actually made ("low chance of getting the same dialogue line again
and again") and the words alone do not deliver it:

- **Twenty busts against one patron, count distinct lines.** Before §2.2
  the ceiling is the pool size and the floor is a fair coin — two
  `yourBust` rows means the second bust repeats half the time. After
  §2.2 the first N busts must return N distinct lines, then wrap. Assert
  the distinct count, not that a line appeared.

The register ladder is the writing; §2.2 is what stops the writing being
wasted. Ship them together or the pass will read as no better than what
it replaced.
