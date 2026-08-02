# -*- coding: utf-8 -*-
"""P425 - the feat roster migration.

Restores the brief's section-8 roster (24 authored, 23 live + 1 parked) over
the 32 that had drifted into the code, and adds the additive telemetry the
restored conditions read. Every hook here is a counter or a flag; none of them
changes a score, a roll or a branch that already existed.

Run:  python tools/p425_feat_roster.py
Then: node tools/zv_trade_parsegate.js
"""
import io, sys, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')

with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

def sub_once(hay, old, new, what):
    n = hay.count(old)
    assert n == 1, 'anchor %s matched %d times (want 1)' % (what, n)
    return hay.replace(old, new)


# ══ 1. TELEMETRY ═══════════════════════════════════════════════════════
# Eight additive channels. Each sits beside state the game already keeps, so
# a reader can see the feat's evidence next to the event that produced it.

# 1a. Bloom fires, and a straight that used a jade wild. Both are decided at
#     commit time; the jade one is only CLAIMED at the bank, because "bank a
#     straight" is a claim about a turn that survived to be banked.
s = sub_once(s,
  "  if((inst=famInst('bloom'))&&(_isTriple||_isStraight)&&_jadeDice.length){\n"
  "    var P=famDef('bloom').p[inst.tier-1];pts+=P;_famPop('+'+P+' BLOOM');\n"
  "  }\n",
  "  if((inst=famInst('bloom'))&&(_isTriple||_isStraight)&&_jadeDice.length){\n"
  "    var P=famDef('bloom').p[inst.tier-1];pts+=P;_famPop('+'+P+' BLOOM');\n"
  "    G._featBloom=(G._featBloom||0)+1;/* FULL BLOOM */\n"
  "  }\n"
  "  /* GREEN THUMB - a straight a jade wild completed. Pending until banked:\n"
  "     the feat is about a straight that PAID, and a bust takes it back. */\n"
  "  if(_isStraight&&_jadeDice.length)G._featJadePend=true;\n",
  'bloom commit hook')

# 1b. The obsidian break pays +1000 into the turn. POWDER MONKEY is about
#     BANKING it, so the flag is pending here and settles at the bank.
s = sub_once(s,
  "  obsidian:{msg:'OBSIDIAN SHATTERS — +1000',fire:function(){\n"
  "    G.turnPts=(G.turnPts||0)+1000;",
  "  obsidian:{msg:'OBSIDIAN SHATTERS — +1000',fire:function(){\n"
  "    G._featShatterPend=true;/* POWDER MONKEY - claimed only if banked */\n"
  "    G.turnPts=(G.turnPts||0)+1000;",
  'obsidian break trigger')

# 1c. Falling Star's extra turn, counted rather than flagged. The card's own
#     state is a boolean it consumes each turn, so it cannot answer "twice".
s = sub_once(s,
  "    if(ev.amt>=ev.P&&!G._fExtraTurn){G._fExtraTurn=true;famLog('FALLING STAR — ANOTHER TURN COMES');}}",
  "    if(ev.amt>=ev.P&&!G._fExtraTurn){G._fExtraTurn=true;\n"
  "      G._featStarChain=(G._featStarChain||0)+1;/* WISH GRANTED */\n"
  "      famLog('FALLING STAR — ANOTHER TURN COMES');}}",
  'falling star bank hook')

# 1d. A called omen that landed.
s = sub_once(s,
  "      if(pts<=0){var take=Math.min(_ioP[0],G.oPts);G.oPts-=take;G.pPts+=take;\n"
  "        famLog('THE OMEN LANDS — YOU TAKE '+take);}",
  "      if(pts<=0){var take=Math.min(_ioP[0],G.oPts);G.oPts-=take;G.pPts+=take;\n"
  "        G._featOmenTrue=true;/* OMENS TRUE */\n"
  "        famLog('THE OMEN LANDS — YOU TAKE '+take);}",
  'ill omen resolution')

# 1e. The amber break eating a bust - STICKY FINGERS, rewritten onto the live
#     amber mechanic because Tar Pit (the brief's condition) is retired.
s = sub_once(s,
  "    G._bustImmuneTurn=false;\n"
  "    try{setStatusMsg('AMBER HOLDS",
  "    G._bustImmuneTurn=false;\n"
  "    G._featAmberAte=(G._featAmberAte||0)+1;/* STICKY FINGERS */\n"
  "    try{setStatusMsg('AMBER HOLDS",
  'amber bust-immunity spend')

# 1f. A ward that paid out - TWICE SAVED.
s = sub_once(s,
  "  if(G._wardArmed){\n"
  "    G._wardArmed=false;",
  "  if(G._wardArmed){\n"
  "    G._wardArmed=false;\n"
  "    G._featWardSaves=(G._featWardSaves||0)+1;/* TWICE SAVED */",
  'ward save branch')

# 1g. The bank settles every turn-scoped claim, and records the turn's length.
s = sub_once(s,
  "  /* Tempting Fate feat: banked a turn in which the player committed a\n"
  "     triple of 1s AND chose to roll again afterward. */\n"
  "  if(G._rolledAfterTriple1)G._featTemptingFate=true;\n",
  "  /* Tempting Fate feat: banked a turn in which the player committed a\n"
  "     triple of 1s AND chose to roll again afterward. */\n"
  "  if(G._rolledAfterTriple1)G._featTemptingFate=true;\n"
  "  /* THE BANK IS WHERE A TURN'S CLAIMS SETTLE. Green Thumb and Powder\n"
  "     Monkey are both stated as \"bank a ...\", so their pending flags are\n"
  "     promoted here and dropped in doBust - a turn that busts proves\n"
  "     neither. Slow Boiled wants the LONGEST turn, which is why it is a max\n"
  "     and not the winning turn's count (that is _featWinBankRolls). */\n"
  "  if(G._featJadePend)G._featJade=true;\n"
  "  if(G._featShatterPend)G._featShatterBanked=true;\n"
  "  G._featJadePend=false;G._featShatterPend=false;\n"
  "  if((G.turnRollCount||0)>(G._featMaxRolls||0))G._featMaxRolls=G.turnRollCount||0;\n",
  'bank feat settle')

# 1h. The bust drops what the bank would have promoted, and still counts the
#     turn's length: a six-roll turn is a six-roll turn either way.
s = sub_once(s,
  "  /* Feat tracking: count player busts for \"Untouchable\" feat */\n"
  "  G._featBusts=(G._featBusts||0)+1;\n",
  "  /* Feat tracking: count player busts for \"Untouchable\" feat */\n"
  "  G._featBusts=(G._featBusts||0)+1;\n"
  "  /* The pending claims die with the turn; the ROLL COUNT does not - Slow\n"
  "     Boiled is about how long you sat there, not about whether it paid. */\n"
  "  if((G.turnRollCount||0)>(G._featMaxRolls||0))G._featMaxRolls=G.turnRollCount||0;\n"
  "  G._featJadePend=false;G._featShatterPend=false;\n",
  'bust feat settle')

# 1i. The deepest hole the player climbed out of, tracked where the existing
#     comeback flag is tracked.
s = sub_once(s,
  "  if(G.target&&(G.oPts-G.pPts)>=G.target*0.5)G._featTrailedDeep=true;\n",
  "  if(G.target&&(G.oPts-G.pPts)>=G.target*0.5)G._featTrailedDeep=true;\n"
  "  /* THE LONG ROAD wants an absolute gap, not a fraction of target: the\n"
  "     brief says 2,000 behind and a tier-7 target would make 50% mean 8,500. */\n"
  "  var _dfc=(G.oPts||0)-(G.pPts||0);\n"
  "  if(_dfc>(G._featMaxDeficit||0))G._featMaxDeficit=_dfc;\n",
  'deficit tracking')

# 1j. Which night ended on LAST ORDERS. Stamped with the tier so it expires
#     by itself when the run advances - no cleanup path to forget.
s = sub_once(s,
  "  S.run.points=0;S.run._chalkMeta=[];S.run.night=null;S.run._lastOrders=true;\n",
  "  S.run.points=0;S.run._chalkMeta=[];S.run.night=null;S.run._lastOrders=true;\n"
  "  /* SECOND WIND reads this. Stamped with the TIER rather than set to true\n"
  "     so it expires on its own when the run advances: there is no \"clear the\n"
  "     flag\" path that a future edit can forget to call. */\n"
  "  S.run._loNight=S.run.tier;\n",
  'last orders night stamp')


# ══ 2. THE ROSTER ══════════════════════════════════════════════════════
START = "/* ── Feats (renown sources — once per run each) ──"
END = "/* ── Renown Perks (curated, threshold-based unlocks — never spent) ──"
i0, i1 = s.find(START), s.find(END)
assert i0 > 0 and i1 > i0, 'roster block not found (%d,%d)' % (i0, i1)

ROSTER = u"""/* ── FEATS — the brief's §8 roster, one per painting ────────────────
   RESTORED FROM DRIFT. The code had grown to 32 feats against 24 authored
   paintings and FEAT_ART could map only 12 — six of those to the wrong
   condition, the clearest being Death&Taxes, which is Ambrose's painting,
   awarded for beating Corvus. The 24 was the authored scope; the 32 was
   accretion nobody decided on. Restoring the list makes the art mapping
   total BY CONSTRUCTION rather than by twelve hand-written guesses.

   THREE CONDITIONS NAMED MECHANICS THAT NO LONGER EXIST and are rewritten
   rather than cut, because what each rewarded still exists:
     NO CLAIM held Insurance   → Ward does that job now.
     STICKY FINGERS used Tar Pit → amber's break-trigger eats a bust instead.
     BOOKKEEPER needed Bookends → collapsed into Vanguard, no analogue left.
   Bookkeeper is therefore PARKED, and its painting is the single orphan.

   BADGES DO NOT EXIST IN THIS BUILD — tells replaced them. FIRST BLOOD, HIS
   OWN MEDICINE and THE COLLECTOR are stated against tells accordingly.

   Cut with this: the six per-boss beat_<boss> feats, and the twenty other
   drifted rows. That is real content loss and it is named on purpose — if
   per-boss recognition matters it wants its own category with its own art
   ask, not a reason to keep a roster nobody authored. */
const FEAT_ART={
  /* FAMILY STUNTS — two per family */
  green_thumb:'GreenThumb',        full_bloom:'FullBloom',
  slow_boiled:'SlowBoiled',        sticky_fingers:'StickyFingers',
  twice_saved:'TwiceSaved',        no_claim:'NoClaim',
  powder_monkey:'PowderMonkey',    three_torches:'ThreeTorches',
  wish_granted:'WishGranted',      omens_true:'OmensTrue',
  for_keeps_feat:'ForKeeps',
  /* vagabond's second stunt is BOOKKEEPER, parked — see the note above */
  /* TABLE STORIES */
  first_blood:'FirstBlood',        his_own_medicine:'HisOwnMedecine',
  clean_night:'CleanNight',        long_road:'LongRoad',
  death_and_taxes:'Death&Taxes',   last_man_sitting:'LastManSitting',
  high_roller:'HighRoller',        teetotaller:'Teetotaller',
  second_wind:'SecondWind',        bare_hands:'Barehands',
  the_collector:'TheCollector',    own_the_night:'OwnTheNight'};
/* HisOwnMedecine is spelled that way ON DISK. The filename is the contract
   here, not the English — renaming it is Denis's call, not a typo fix. */
const FEATS=[
  /* ── JADE ── */
  {id:'green_thumb',     label:'Green Thumb',      desc:'Bank a straight completed by a jade wild', renown:10,
    check:function(G){return !!G._featJade;}},
  {id:'full_bloom',      label:'Full Bloom',       desc:'Bloom fires three times in one match', renown:10,
    check:function(G){return (G._featBloom||0)>=3;}},
  /* ── AMBER ── */
  {id:'slow_boiled',     label:'Slow Boiled',      desc:'A single turn of six or more rolls', renown:10,
    check:function(G){return (G._featMaxRolls||0)>=6;}},
  {id:'sticky_fingers',  label:'Sticky Fingers',   desc:'Win a match in which the amber held and ate a bust', renown:10,
    /* THE BRIEF SAYS TAR PIT, WHICH IS RETIRED. Rewritten onto amber's live
       identity — the tar that holds — rather than deleted. Exact wording is
       Denis's, flagged in the phase report. */
    check:function(G){return (G._featAmberAte||0)>=1;}},
  /* ── SILVER ── */
  {id:'twice_saved',     label:'Twice Saved',      desc:'Two ward saves in one match, then win', renown:15,
    check:function(G){return (G._featWardSaves||0)>=2;}},
  {id:'no_claim',        label:'No Claim',         desc:'Win carrying a ward without ever busting', renown:15,
    /* THE BRIEF SAYS INSURANCE, WHICH IS RETIRED. Ward inherited the job, so
       the condition follows it. Reads the OWNED loadout, not the live table:
       a die broken mid-match should not deny a claim about the build. */
    check:function(G){
      if((G._featBusts||0)!==0)return false;
      try{return !!(typeof _wardOwned==='function'&&_wardOwned(-1));}catch(e){return false;}
    }},
  /* ── OBSIDIAN ── */
  {id:'powder_monkey',   label:'Powder Monkey',    desc:"Bank a shatter's +1000", renown:10,
    check:function(G){return !!G._featShatterBanked;}},
  {id:'three_torches',   label:'Three Torches',    desc:'Win a night fielding three obsidian dice', renown:15,
    check:function(G){
      if(!G._isBoss)return false;
      var md=(typeof S!=='undefined'&&S&&S.run&&Array.isArray(S.run.dice))?S.run.dice:[];
      return md.filter(function(m){return m==='obsidian'||m==='grogs_tooth';}).length>=3;
    }},
  /* ── STARSTONE ── */
  {id:'wish_granted',    label:'Wish Granted',     desc:'Chain two Falling Star extra turns', renown:15,
    check:function(G){return (G._featStarChain||0)>=2;}},
  {id:'omens_true',      label:'Omens True',       desc:'Win the pot on a correct Ill Omen call', renown:10,
    check:function(G){return !!G._featOmenTrue;}},
  /* ── VAGABOND ── (BOOKKEEPER parked — Bookends is retired) */
  {id:'for_keeps_feat',  label:'For Keeps',        desc:'Win a match played for dice', renown:15,
    check:function(G){return !!G._forKeeps;}},
  /* ── TABLE STORIES ── */
  {id:'first_blood',     label:'First Blood',      desc:'Take your first boss', renown:10,
    /* BADGES BECAME TELLS, but "your first boss" survives the rename intact.
       The old check awarded for the first MATCH of a run, boss or not — which
       is why FirstBlood hung on the wall after beating a drunk at a table. */
    check:function(G){
      if(!G._isBoss)return false;
      return (typeof S!=='undefined'&&S&&S.run&&Array.isArray(S.run.bossesBeaten))
        ?S.run.bossesBeaten.length===0:false;
    }},
  {id:'his_own_medicine',label:'His Own Medicine', desc:'Beat a boss with a rule you took off a boss', renown:20,
    check:function(G){return !!(G._isBoss&&G._sleeve);}},
  {id:'clean_night',     label:'Clean Night',      desc:'Clear a night without losing a seat', renown:15,
    /* Read at the BOSS win, which is what clears a night. The seat this match
       occupies is not marked until the settle path runs, so this asks only
       whether any EARLIER seat was lost — and the current one is a win. */
    check:function(G){
      if(!G._isBoss)return false;
      var n=(typeof S!=='undefined'&&S&&S.run)?S.run.night:null;
      if(!n||!Array.isArray(n.results))return false;
      return n.results.indexOf('lost')<0;
    }},
  {id:'long_road',       label:'The Long Road',    desc:'Win from 2,000 or more behind', renown:15,
    check:function(G){return (G._featMaxDeficit||0)>=2000;}},
  {id:'death_and_taxes', label:'Death and Taxes',  desc:'Beat Ambrose', renown:20,
    check:function(G){return !!(G&&G.rung&&G.rung.key==='bishop');}},
  {id:'last_man_sitting',label:'Last Man Sitting', desc:'Win a sudden-death turn', renown:15,
    check:function(G){return G._handicap==='sudden_death';}},
  {id:'high_roller',     label:'High Roller',      desc:'A single bank of 2,500 or more', renown:10,
    check:function(G){return (G._featMaxBank||0)>=2500;}},
  {id:'teetotaller',     label:'Teetotaller',      desc:'Win without ever banking under 500', renown:10,
    /* The brief's number is 500. A live grant in _famFeats used 800 under the
       id never_small and had no painting, so nobody could see it either way. */
    check:function(G){return (G._famBankCount||0)>=1&&(G._famMinBank||0)>=500;}},
  {id:'second_wind',     label:'Second Wind',      desc:'Win the night after LAST ORDERS took a heart', renown:15,
    check:function(G){
      if(!G._isBoss)return false;
      return (typeof S!=='undefined'&&S&&S.run&&S.run._loNight===S.run.tier);
    }},
  {id:'bare_hands',      label:'Bare Hands',       desc:'Beat a boss with all-bone dice', renown:20,
    check:function(G){
      if(!G._isBoss)return false;
      /* THE OWNED LOADOUT, NOT THE LIVE TABLE. G.matchDice is whatever
         survived the fight, so a Break or a Trade could award this for dice
         the player never built with, or deny it for a build that qualified. */
      var md=(typeof S!=='undefined'&&S&&S.run&&Array.isArray(S.run.dice))?S.run.dice
        :((G&&Array.isArray(G.matchDice))?G.matchDice:null);
      if(!md||!md.length)return false;
      return md.every(function(m){var d=(typeof getDie==='function')?getDie(m):null;return !d||!d.effect;});
    }},
  {id:'the_collector',   label:'The Collector',    desc:'Hold four rules at once', renown:15,
    check:function(G){return (typeof S!=='undefined'&&S&&S.run&&Array.isArray(S.run.tells))
      ?S.run.tells.length>=4:false;}},
  {id:'own_the_night',   label:'Own the Night',    desc:'Win the run', renown:25,
    check:function(G){
      if(!G._isBoss)return false;
      return (typeof S!=='undefined'&&S&&S.run&&typeof TIERS!=='undefined'
              &&(S.run.tier||0)>=TIERS.length-1);
    }},
];

"""
s = s[:i0] + ROSTER + s[i1:]


# ══ 3. THE SECOND ROSTER ═══════════════════════════════════════════════
# _famFeats grants five ids straight into S.featsDone, none of which has ever
# had a painting - so all five were invisible. Two of them are now real feats
# with art (never_small -> Teetotaller, ember_night -> ThreeTorches) and would
# otherwise pay renown twice for one act. The other three stay for now and are
# flagged in the phase report; deleting drift is a separate decision.
s = sub_once(s,
  "  if((G._famMinBank||0)>=800&&(G._famBankCount||0)>=2)grant('never_small','NEVER A BANK UNDER EIGHT HUNDRED',20);\n",
  "  /* never_small RETIRED HERE: it is TEETOTALLER now, in FEATS, with the\n"
  "     brief's 500 and a painting. Keeping both paid renown twice for one act\n"
  "     and only one of them could ever be seen. */\n",
  'never_small grant')
s = sub_once(s,
  "  if(G._isBoss&&(S.run.dice||[]).filter(function(m){return m==='obsidian'||m==='grogs_tooth';}).length>=3)\n"
  "    grant('ember_night','A NIGHT WON ON THREE EMBERS',25);\n",
  "  /* ember_night RETIRED HERE: it is THREE TORCHES now, in FEATS, with a\n"
  "     painting. Same condition, same act, one grant. */\n",
  'ember_night grant')

# The debug feats seeder names three ids that no longer exist.
s = sub_once(s,
  "    ['first_blood','no_busts','comeback'].forEach(function(id){",
  "    ['first_blood','clean_night','long_road'].forEach(function(id){",
  'debug feat seeder')

assert s != orig, 'nothing changed'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)

# Post-conditions, measured on the written text.
for gone in ['beat_corvus', 'beat_ambrose', 'crushing_win', 'lightning_round',
             'never_small', 'ember_night']:
    assert ("'" + gone + "'") not in s.split('const FEATS=[')[1].split('\n];')[0], \
        'retired id %s survives in FEATS' % gone
art = s.split('const FEAT_ART={')[1].split('};')[0]
assert art.count(':') == 23, 'FEAT_ART has %d entries, want 23' % art.count(':')
print('P425 applied. FEAT_ART entries: %d' % art.count(':'))
