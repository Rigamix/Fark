# -*- coding: utf-8 -*-
u"""P861 (BOSS REWARD BRIEF section 3): Mabel's badge becomes THE MENDING -
"the player may not bank until they have rolled at least twice this turn" -
and Zero Hour is parked, not deleted.

WHY THE SWAP. Zero Hour punishes enchanted faces. Enchants cost 150-400g at
the innkeep and Mabel is night 2, where a player holds starting gold plus one
win, so her badge fires against nothing. It is the only badge in the set that
can be a no-op for the whole match by the player simply not having bought
anything yet.

WHY NOT STEEPED, the obvious swap. It works from a bare loadout, so it looks
right, and it is not: every Steeped site is player-side and it PAYS +100 per
extra roll. Worn, it is free points. That would make it the only badge that is
not a constraint - Last Call floors your banks, Drill Order caps your rolls,
Pickpocket takes a die, First Strike charges gold, Reckoning makes you match a
total, Still Waters silences your dice, Kindred amplifies theirs. Each is an
obstacle facing you and a weapon worn. A bonus in both directions is a lure,
not a badge.

THE PARKING IS LOad-BEARING, not politeness. _tellById scans RUNGS and falls
back to PARKED_TELLS, and zero_hour STAYS in _SEAL_POOL - a cursed seat can
still roll it. The moment Mabel stops carrying the record, _tellById('zero_hour')
would return null for every cursed seat that drew it, and tools/apv_tell_remap.js
already asserts exactly that (`sealPoolUnresolvable`). So zero_hour moves INTO
PARKED_TELLS in the same edit that takes it off her rung. This is the same
reason the table exists at all, spelled out in its own comment.

BALANCE CHANGE, SAID OUT LOUD, the way P568 said its own: _rollSealTell picks
uniformly, so adding the_mending moves _SEAL_POOL from nine rules to ten and
every other rule from 1/9 to 1/10 on a cursed seat.

TWO SEATS, ONE RULE. The brief is explicit that a badge working in one
direction only is the Steeped defect, so the gate is enforced on both:
  player  - the BANK button goes dead and handleBank refuses, keyed on
            G.turnRollCount, which is the player's authoritative per-turn count.
  rival   - oppShouldBank returns false below the floor, keyed on G._oRollNum,
            which runOppTurn writes at 35794 before this is consulted.
It is placed ABOVE oppShouldBank's own "(oppTotal+oppBank)>=target -> bank"
line deliberately: for the player the gate is absolute and holds even on a
winning total, so the rival's has to hold there too or the two seats are
playing different rules.

NO SOFT-LOCK, and not by luck. A rule that can demand a roll the table cannot
supply would leave both buttons dead. setBtns already computes whether a roll
is on offer - that is its `r` - so it records it and the gate reads it. One
writer, one reader, no second copy of the rollability expression to drift from
the first.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. Mabel's rung carries The Mending ──────────────────────────────
sub(u"""    /* MABEL \u2014 ZERO HOUR, moved off Grog. Chosen by NAME, not by slot:
       Aldric already carries an enchant-suppression rule (Still Waters) and
       Brutus already carries a turn-length constraint (Drill Order), so
       either would have doubled a theme that boss already owns. Steeped is
       pure passive accumulation with no overlap with enchant tempo.
       THE VOICE MOVES WITH THE RULE. Grog's line was a bar-closing line and
       read wrong in Mabel's mouth; hers is stitchwork, which is also what
       her cards are made of. The mechanic is untouched. */
    /* "enchanted", never "marked". A mark on a die IS an enchant now, and the
       terminology probe asserts no tell says otherwise \u2014 it caught this line
       within a minute of it being written. The word was inherited from Grog's
       original Zero Hour text, which had been corrected for the same reason. */
    tell:{id:'zero_hour',name:'ZERO HOUR',desc:"\u201cTake an enchanted face at my table, dear, and I cut the thread.\u201d",icon:'\u2702\ufe0f'}},""",
    u"""    /* MABEL \u2014 THE MENDING. Zero Hour is parked, not deleted, and the reason
       is night 2: it punishes ENCHANTED faces, enchants cost 150-400g at the
       innkeep, and at night 2 a player holds starting gold plus one win. Her
       badge could fire against nothing at all, for the whole match, purely by
       the player not having shopped yet. That is the one thing a badge may
       not be.
       STEEPED WAS THE OBVIOUS SWAP AND IS WRONG for a different reason: it
       works from a bare loadout, but every one of its sites is player-side
       and it PAYS +100 per extra roll, so worn it is free points. It would be
       the only badge that is not a constraint - Last Call floors your banks,
       Drill Order caps your rolls, Pickpocket takes a die, First Strike
       charges gold, Reckoning makes you match a total, Still Waters silences
       your dice, Kindred amplifies theirs. A bonus in both directions is a
       lure, not a badge. Both rules are parked; neither is deleted.
       THE MENDING IS A CONSTRAINT AND A WEAPON, which is the test the other
       eight pass: against you it removes the safe one-roll bank and makes you
       throw again, which is exactly the pressure night 2 should teach; worn,
       it forces the rival to over-roll into busts.
       THE VOICE IS STILL HERS. She is the mender and the rule is "finish the
       work" - the same stitchwork her cards are made of. */
    tell:{id:'the_mending',name:'THE MENDING',desc:"\u201cNothing leaves my table half-done, dear. Roll twice before you bank.\u201d",icon:'\U0001fa22',minRolls:2}},""",
    '1 Mabel carries The Mending')

# ── 2. zero_hour is parked so the seal pool can still resolve it ─────
sub(u"""var PARKED_TELLS={steeped:{id:'steeped',name:'STEEPED',desc:"\u201cEach extra roll, I'll add 100 to your bank \u2014 bust and it all spills.\u201d",icon:'\U0001f375',perRoll:100}};""",
    u"""var PARKED_TELLS={steeped:{id:'steeped',name:'STEEPED',desc:"\u201cEach extra roll, I'll add 100 to your bank \u2014 bust and it all spills.\u201d",icon:'\U0001f375',perRoll:100},
  /* P861: ZERO HOUR PARKS HERE THE MOMENT IT LEAVES MABEL'S RUNG, and this
     is not tidiness - it is the whole reason this table exists. zero_hour
     STAYS in _SEAL_POOL below, so a cursed seat can still draw it; _tellById
     scans RUNGS first and would have returned null for every one of those
     seats the instant no rung carried the record. tools/apv_tell_remap.js
     asserts precisely this (`sealPoolUnresolvable`), so the two edits are one
     edit. Ready if the game ever wants an anti-enchant boss late, when a
     player actually owns enchants for it to bite. */
  zero_hour:{id:'zero_hour',name:'ZERO HOUR',desc:"\u201cTake an enchanted face at my table, dear, and I cut the thread.\u201d",icon:'\u2702\ufe0f'}};""",
    '2 zero_hour parked')

# ── 3. the seal pool gains the new rule (9 -> 10) ────────────────────
sub(u"""var _SEAL_POOL=['last_call','zero_hour','steeped','pickpocket','first_strike','drill_order','kindred','reckoning','still_waters'];""",
    u"""/* P861: the_mending JOINS, and this is a balance change said out loud the way
   P568 said its own - _rollSealTell picks uniformly, so every other rule moves
   from 1/9 to 1/10 on a cursed seat. zero_hour KEEPS its place: it is parked
   off Mabel's rung, not retired, and PARKED_TELLS above is what keeps
   _tellById able to answer for it here. */
var _SEAL_POOL=['last_call','zero_hour','the_mending','steeped','pickpocket','first_strike','drill_order','kindred','reckoning','still_waters'];""",
    '3 seal pool 9->10')

# ── 4. per-match state (there is none) ───────────────────────────────
sub(u"""    case 'drill_order':/* uses turnRollCount + maxRolls */ break;""",
    u"""    case 'drill_order':/* uses turnRollCount + maxRolls */ break;
    case 'the_mending':/* P861: reads turnRollCount against the record's minRolls, no state */ break;""",
    '4 applyTell case')

# ── 5. the rule's own record, and the gate ───────────────────────────
sub(u"""function _drillCap(){""",
    u"""/* P861: THE FLOOR COMES FROM THE RECORD, never a literal - the same shape
   _drillMax landed on, and for the same reason: retune the record and the
   player, the rival and the badge would otherwise enforce three different
   numbers. Reads whichever slot holds the rule, because a SLEEVED or SEALED
   Mending has no G._tell to read - that direct-read mistake is what left Zero
   Hour dead outside Grog's badge. */
function _mendMin(){
  var m=(typeof G!=='undefined'&&G&&G._tell&&G._tell.id==='the_mending')
        ?G._tell:(_tellById('the_mending')||{});
  return m.minRolls||2;
}
/* Is the player's bank held shut this instant? `short` is the rule; whether it
   may be ENFORCED is a separate question, because a rule that demanded a roll
   the table cannot supply would kill both buttons and hang the turn. setBtns
   already computes whether a roll is on offer - that is its `r` - so it records
   it there and this reads it. One writer, one reader; the alternative was a
   second copy of refreshSelUI's rollability expression, free to drift. */
function _mendGate(){
  var off={active:false,need:0,count:0,short:false,blocked:false};
  if(!G||typeof _ruleActive!=='function'||!_ruleActive('the_mending','p'))return off;
  var need=_mendMin(),count=G.turnRollCount||0,short=count<need;
  return {active:true,need:need,count:count,short:short,
          blocked:short&&(G._canRollNow!==false)};
}
function _drillCap(){""",
    '5 mend record + gate')

# ── 6. setBtns records rollability and enforces the hold ─────────────
sub(u"""  }else{bankBtn.classList.add('disabled');}""",
    u"""  }else{bankBtn.classList.add('disabled');}
  /* P861: THE MENDING holds the bank shut while the turn is one roll old.
     Recorded here rather than derived again elsewhere - `r` IS the answer to
     "is a roll on offer", and the escape hatch depends on it: if no roll is
     available the rule stands down rather than hanging the turn with two dead
     buttons. Runs after the enable above so it wins, exactly as the Drill
     Order lock below re-asserts itself over a fresh setBtns(true,...). */
  G._canRollNow=!!r;
  try{
    var _mg=_mendGate();
    bankBtn.classList.toggle('mend-held',!!_mg.blocked);
    if(_mg.blocked)bankBtn.classList.add('disabled');
  }catch(e){}""",
    '6 setBtns holds the bank')

# ── 7. the backstop, beside Last Call's ──────────────────────────────
sub(u"""    var _lcRule=_tellById('last_call');""",
    u"""    /* P861: THE MENDING refuses the bank outright rather than voiding it -
       Last Call below zeroes a bank that broke its floor, but this rule is
       "not yet", so the turn continues untouched and the player rolls again.
       The button is already dead by here (setBtns); this is the backstop for
       any path that reaches handleBank without going through it. */
    var _mgB=(typeof _mendGate==='function')?_mendGate():{blocked:false};
    if(_mgB.blocked){
      setStatusMsg('THE MENDING \u2014 ROLL AGAIN BEFORE YOU BANK ('+_mgB.count+'/'+_mgB.need+')','red');
      try{_flashTellRule();}catch(e){}
      try{Haptic.bust&&Haptic.bust();}catch(e){}
      return;
    }
    var _lcRule=_tellById('last_call');""",
    '7 handleBank backstop')

# ── 8. the rival obeys the same rule ─────────────────────────────────
sub(u"""function oppShouldBank(rung,oppBank,diceLeft,oppTotal,playerTotal,target){
  if((oppTotal+oppBank)>=target)return true;""",
    u"""function oppShouldBank(rung,oppBank,diceLeft,oppTotal,playerTotal,target){
  /* P861: THE MENDING, worn by the player, binds the rival - and it sits ABOVE
     the winning-total line on purpose. The player's gate is absolute: it holds
     even on a total that would win. If this sat below, the two seats would be
     playing different rules and the badge would be worth less worn than met,
     which is the Steeped defect the brief names.
     diceLeft>0 is the same escape hatch the player side has: a rule may not
     demand a roll the table cannot supply. G._oRollNum is written in
     runOppTurn before this is consulted. */
  if(typeof _ruleActive==='function'&&_ruleActive('the_mending','o')&&
     diceLeft>0&&((typeof G!=='undefined'&&G&&G._oRollNum)||0)<_mendMin())return false;
  if((oppTotal+oppBank)>=target)return true;""",
    '8 rival obeys The Mending')

# ── 9. the badge shows the count, like Drill Order's ─────────────────
sub(u"""  var _drillInlineVal=(t.id==='drill_order')?' <span class="tb-val tb-val-inline" id="drillVal">0/'+_drillMax()+'</span>':'';/* P567 */""",
    u"""  var _drillInlineVal=(t.id==='drill_order')?' <span class="tb-val tb-val-inline" id="drillVal">0/'+_drillMax()+'</span>':'';/* P567 */
  /* P861: the same inline counter Drill Order carries, for the same reason -
     the rule is a number the player has to be able to see coming. Drill Order
     counts UP to a ceiling; this counts up to a floor. */
  var _mendInlineVal=(t.id==='the_mending')?' <span class="tb-val tb-val-inline" id="mendVal">0/'+_mendMin()+'</span>':'';""",
    '9a badge slot')

sub(u"""    '<span class="tb-name">'+_tellNameHtml+_stedInlineVal+_arInlineVal+_drillInlineVal+'</span>'+""",
    u"""    '<span class="tb-name">'+_tellNameHtml+_stedInlineVal+_arInlineVal+_drillInlineVal+_mendInlineVal+'</span>'+""",
    '9b badge slot mounted')

sub(u"""  if(t.id==='reckoning'){
    var r=document.getElementById('reckoningVal');""",
    u"""  if(t.id==='the_mending'){
    var _mv=document.getElementById('mendVal');
    if(_mv){var _mn=_mendMin(),_mc=Math.min(G.turnRollCount||0,_mn);
      _mv.textContent=_mc+'/'+_mn;
      /* clears the moment the floor is met - the badge stops warning about a
         rule that is no longer holding anything shut */
      _mv.classList.toggle('tb-warn',_mc<_mn);}
  }
  if(t.id==='reckoning'){
    var r=document.getElementById('reckoningVal');""",
    '9c badge updates')

# ── 10. the badge's colour, and the held button ──────────────────────
sub(u""".tell-badge.tell-reckoning{color:#e0a848}""",
    u"""/* P861: Mabel's linen-blue, off BOSS_ACCENT.mabel - every other live rule
   carries its own tint and a badge with none reads as unfinished. */
.tell-badge.tell-the_mending{color:#a8c0e0}
.tell-badge.tell-the_mending .tb-name{color:#c0d4f0;text-shadow:0 0 8px rgba(150,185,240,.45)}
/* the bank held shut by a rule, not merely unavailable - the ordinary disabled
   state is a grey nothing, and the player needs to see WHICH kind of no this
   is. Same linen as the badge, so the two read as one rule. */
#btnBank.mend-held{border-color:rgba(168,192,224,.55)!important;box-shadow:0 0 10px rgba(150,185,240,.25) inset}
.tell-badge.tell-reckoning{color:#e0a848}""",
    '10 css')

# ── post-asserts ─────────────────────────────────────────────────────
if "id:'zero_hour',name:'ZERO HOUR'" not in s:
    sys.exit('ZERO HOUR RECORD LOST ENTIRELY (nothing written)')
if s.count("id:'zero_hour'") != 1:
    sys.exit("zero_hour defined %d times, expected 1 (PARKED_TELLS only) (nothing written)"
             % s.count("id:'zero_hour'"))
if "'the_mending'" not in s or 'minRolls:2' not in s:
    sys.exit('THE MENDING RECORD MISSING (nothing written)')
if s.count("'the_mending'") < 6:
    sys.exit('the_mending referenced only %d times - expected rung, pool, applyTell, '
             'gate, badge x2, rival (nothing written)' % s.count("'the_mending'"))
for needed in ['_mendMin', '_mendGate', 'G._canRollNow', 'mend-held', 'mendVal',
               "_ruleActive('the_mending','o')"]:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
