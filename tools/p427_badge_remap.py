# -*- coding: utf-8 -*-
"""P427 - the badge remap, and the id that was carrying the wrong rule.

Denis's rulings:
  Zero Hour goes to MABEL, by name (the position framing is dropped).
  Grog keeps LAST CALL, retuned to 800 - the same number Teetotaller uses.
  Steeped is PARKED, not deleted.
  Boss counters are PER-RUN.

What the code actually looked like, which is not what the brief describes:
  - `last_call` the TELL ID was already carrying ZERO HOUR on Grog. The brief's
    Grog remap shipped by RECYCLING the id rather than minting a new one.
  - Last Call's own mechanic - void a bank under the threshold - was still
    there, in an `if(false)` block, at 500.
  - `_RETIRED_RULES={last_call:1}` therefore switched OFF the rule that id now
    carried, everywhere except Grog's own badge: `_iconFire` reads
    `G._tell.id` directly and bypasses `_ruleActive`. So ZERO HOUR WAS DEAD
    THROUGH A SLEEVE AND THROUGH A SEALED SEAT - and it is claimable as boss
    spoils, so a player could win it and have it do nothing. The code comment
    at _RETIRED_RULES names this trap and says it is not fixed. It is now:
    giving the two rules honest ids removes the reason the guard existed.
  - `_tellById` SCANS RUNGS, so a rule only exists while a boss carries it.
    Parking Steeped by removing it from Mabel would have made the seal pool
    look it up and get null - so parking needs somewhere to park.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

def sub_once(hay, old, new, what):
    n = hay.count(old)
    assert n == 1, 'anchor %s matched %d times (want 1)' % (what, n)
    return hay.replace(old, new)

# ── 1. GROG gets Last Call back, under its own id and at 800 ──────────
# Located by a stable prefix rather than the whole literal: these desc strings
# carry curly quotes and an em dash, and matching them exactly is the kind of
# brittleness that sends a patch through a heredoc and mangles it.
i0 = s.find(u"    tell:{id:'last_call',name:'ZERO HOUR'")
assert i0 > 0, 'grog tell not found'
i1 = s.find(u"}},", i0)
assert i1 > i0, 'grog tell end not found'
s = (s[:i0]
     + u"    /* GROG — LAST CALL, restored under its OWN id and retuned to 800.\n"
       u"       It never actually went away: the mechanic sat in an `if(false)` block\n"
       u"       at 500 while the ID was recycled to carry ZERO HOUR, which is how the\n"
       u"       retired-rules guard ended up switching off the live rule wearing the\n"
       u"       dead one's name. 800 is not a fresh number - it is the same bar\n"
       u"       TEETOTALLER uses for \"never a bank under X\", so the game states one\n"
       u"       threshold rather than two arbitrary ones. 500 read weak because most\n"
       u"       ordinary turns clear it without trying. */\n"
       u"    tell:{id:'last_call',name:'LAST CALL',"
       u"desc:\"“Nothing under eight hundred crosses my bar. "
       u"Drink deep or get out.”\",icon:'\U0001F37B',minBank:800"
     # NO CLOSING BRACE HERE. i1 points at the "}}," that closes the tell
     # object AND the rung object, so the tail supplies both. Writing one
     # here is what made the first run of this patch emit "}}}," - caught by
     # the parse gate, which had been reading a stale scratch file until an
     # hour before this patch and would have waved it through.
     + s[i1:])

# ── 2. MABEL gets Zero Hour, in HER voice ────────────────────────────
j0 = s.find(u"    tell:{id:'steeped',name:'STEEPED'")
assert j0 > 0, 'mabel tell not found'
j1 = s.find(u"}},", j0)
assert j1 > j0, 'mabel tell end not found'
STEEPED_SRC = s[j0:j1 + 1]  # keep the object literal for the parked table
s = (s[:j0]
     + u"    /* MABEL — ZERO HOUR, moved off Grog. Chosen by NAME, not by slot:\n"
       u"       Aldric already carries an enchant-suppression rule (Still Waters) and\n"
       u"       Brutus already carries a turn-length constraint (Drill Order), so\n"
       u"       either would have doubled a theme that boss already owns. Steeped is\n"
       u"       pure passive accumulation with no overlap with enchant tempo.\n"
       u"       THE VOICE MOVES WITH THE RULE. Grog's line was a bar-closing line and\n"
       u"       read wrong in Mabel's mouth; hers is stitchwork, which is also what\n"
       u"       her cards are made of. The mechanic is untouched. */\n"
       u"    tell:{id:'zero_hour',name:'ZERO HOUR',"
       u"desc:\"“Touch a marked die at my table, dear, and I cut the thread.”\","
       u"icon:'✂️'"
     # same as Grog above: j1 is the "}}," that closes both objects.
     + s[j1:])

# ── 3. Somewhere to park a rule that has no badge ────────────────────
s = sub_once(s,
  u"function _tellById(id){\n"
  u"  for(var i=0;i<RUNGS.length;i++)if(RUNGS[i].tell&&RUNGS[i].tell.id===id)return RUNGS[i].tell;\n"
  u"  return null;\n"
  u"}",
  u"/* PARKED RULES — real, working table rules that no boss currently wears.\n"
  u"   Steeped is the first: Zero Hour took Mabel's badge, and every other\n"
  u"   candidate boss already carried a rule of their own, so SOMETHING was\n"
  u"   always going to be displaced whichever name got picked. Deleting tested,\n"
  u"   shipped work once displacement is unavoidable is the worse trade.\n"
  u"   THIS TABLE HAS TO EXIST because _tellById scans RUNGS - a rule only\n"
  u"   existed while a boss carried it, so \"keep the rule, drop the badge\" was\n"
  u"   not expressible at all: the seal pool would have looked Steeped up and\n"
  u"   got null. Cursed seats already draw from the full rule pool, so Steeped\n"
  u"   keeps exactly the role it always had, minus one name attached to it.\n"
  u"   If a future reshuffle needs an eighth rule, it is sitting here intact. */\n"
  u"var PARKED_TELLS={steeped:" + STEEPED_SRC.replace(u"    tell:{id:'steeped'", u"{id:'steeped'") + u"};\n"
  u"function _tellById(id){\n"
  u"  for(var i=0;i<RUNGS.length;i++)if(RUNGS[i].tell&&RUNGS[i].tell.id===id)return RUNGS[i].tell;\n"
  u"  return PARKED_TELLS[id]||null;\n"
  u"}",
  'tellById + parked table')

# ── 4. The guard that was switching Zero Hour off ────────────────────
s = sub_once(s,
  u"var _RETIRED_RULES={last_call:1};",
  u"/* EMPTY, AND THAT IS THE FIX. last_call sat here because the id carried\n"
  u"   ZERO HOUR while the table still called the id retired - so a sleeved or\n"
  u"   sealed Zero Hour did nothing, on a rule the player can WIN as boss\n"
  u"   spoils. The two rules have their own ids now (last_call / zero_hour) and\n"
  u"   both are live, so there is nothing left to guard against. Kept as an\n"
  u"   empty table rather than deleted: the mechanism is still the right one\n"
  u"   the next time a rule is retired ahead of its replacement. */\n"
  u"var _RETIRED_RULES={};",
  'retired rules')

# ── 5. The seal pool learns the new id ───────────────────────────────
s = sub_once(s,
  u"var _SEAL_POOL=['last_call','steeped','pickpocket','in_arrears','drill_order','counterfeit','reckoning'];",
  u"/* zero_hour joins; last_call and steeped both stay - one is a live badge\n"
  u"   rule again, the other is parked but still perfectly playable as a cursed\n"
  u"   seat, which is the whole point of parking it rather than deleting it. */\n"
  u"var _SEAL_POOL=['last_call','zero_hour','steeped','pickpocket','in_arrears','drill_order','counterfeit','reckoning'];",
  'seal pool')

# ── 6. Zero Hour fires through _ruleActive, not off G._tell ──────────
s = sub_once(s,
  u"  /* Grog's Zero Hour: keeping any icon face ends the acting side's turn */\n"
  u"  try{if(G&&G._tell&&G._tell.id==='last_call')G._zeroHourEnds=true;}catch(e){}",
  u"  /* ZERO HOUR: keeping any icon face ends the acting side's turn. Reads\n"
  u"     _ruleActive, not G._tell - the direct read is exactly why the rule\n"
  u"     worked as a badge and was dead through a sleeve and a sealed seat. */\n"
  u"  try{if(_ruleActive('zero_hour','p'))G._zeroHourEnds=true;}catch(e){}",
  'icon fire zero hour')

# ── 7. Per-match state init knows the new id ─────────────────────────
s = sub_once(s,
  u"    case 'last_call':/* threshold-only, no per-match state */ break;\n",
  u"    case 'last_call':/* threshold-only, no per-match state */ break;\n"
  u"    case 'zero_hour':/* fires off the icon path, no per-match state */ break;\n",
  'apply tell switch')

# ── 8. Turn the bank-void back on, at 800 ────────────────────────────
i2 = s.find(u"    /* Last Call (Grog): bank below threshold scores 0 */")
assert i2 > 0, 'last call bank block not found'
i3 = s.find(u"      _flashTellRule();\n    }\n", i2)
assert i3 > i2, 'last call block end not found'
s = (s[:i2]
     + u"    /* LAST CALL (Grog): a bank under the threshold is refused outright.\n"
       u"       Back on after sitting in an `if(false)` since Zero Hour took the id.\n"
       u"       THE THRESHOLD COMES FROM THE RULE, not from G._tell, because a\n"
       u"       sleeved or sealed Last Call has no G._tell to read - the same\n"
       u"       direct-read mistake that left Zero Hour dead outside Grog's badge.\n"
       u"       total>0 guards it: a scoreless turn is a bust, not a refusal, and\n"
       u"       handleBank already returns before here on total<=0. */\n"
       u"    var _lcRule=_tellById('last_call');\n"
       u"    var _lcT=(_lcRule&&_lcRule.minBank)||800;\n"
       u"    if(_ruleActive('last_call','p')&&total>0&&total<_lcT){\n"
       u"      total=0;bonusMsg=' LAST CALL — BANK <'+_lcT;\n"
       u"      setStatusMsg('LAST CALL — NOTHING UNDER '+_lcT,'red');\n"
       u"      /* Distinct harsh sound - reusing SFX.bust felt like a normal bust;\n"
       u"         this is a house-rule rejection and deserves its own tone. */\n"
       u"      try{(SFX.lastCallFail||SFX.bust).call(SFX);}catch(e){}\n"
       u"      try{Haptic.bust&&Haptic.bust();}catch(e){}\n"
       u"      _flashTellRule();\n    }\n"
     + s[i3 + len(u"      _flashTellRule();\n    }\n"):])

# ── 9. Boss counters are per-run ─────────────────────────────────────
s = sub_once(s,
  u"  S.run=_freshRun();",
  u"  S.run=_freshRun();\n"
  u"  /* BOSS COUNTERS ARE PER-RUN. npcState carries each rival's streak (which\n"
  u"     feeds their aggression) and their carryover (which hands the player a\n"
  u"     head start), and it lived on S - so it persisted across runs. A fixed\n"
  u"     cross-run read becomes a memorised answer after the first encounter,\n"
  u"     which is the opposite of the \"adapt your plan\" intent. Fresh each run. */\n"
  u"  S.npcState={};",
  'npcState per-run')

assert s != orig, 'nothing changed'
assert u"if(false){" not in s.split(u'LAST CALL (Grog)')[1][:900], 'if(false) survived'
for want in [u"id:'zero_hour'", u"PARKED_TELLS", u"minBank:800",
             u"_ruleActive('zero_hour','p')", u"var _RETIRED_RULES={};"]:
    assert want in s, 'missing: %s' % want
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P427 applied.')
