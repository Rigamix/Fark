# -*- coding: utf-8 -*-
"""P843: the feats-rot pass (architecture audit items 2-5, Denis's
"normal fix flow when you want them").

A. SEVEN orphan _feat* flags deleted - each adversarially verified
   (dotted, bracket/string, dynamic-key, wholesale-G, save-shape, and
   tools/ patterns all empty): _featBanks, _featActivesUsed,
   _featFullStraight, _featTemptingFate (+ its whole feeder chain
   _turnTriple1Scored/_rolledAfterTriple1), _featWinBankRolls,
   _featTwoTriplets, _featTrailedDeep. _featHotDiceCount STAYS: the
   committed sim instruments read it (tools/sim_harness.js:540,
   sim_l3_elegance*.js) - not an orphan after all.

B. The resume gap: saveMatchState's explicit literal carried NO feat
   accumulator, so a mid-match reload zeroed progress toward every
   threshold feat (12 live fields, not the audit's 4) - including
   _forKeeps, where the family card's spent charge WAS carried in
   famState.pF while the flag it bought was not (carrying the cost,
   not the effect). Fix: a featState sub-object in the snapshot + one
   presence-guarded keyed loop at the famState restore site.

C. The stale _RETIRED_RULES paragraph (13176) still reported last_call
   as trapped; the empty-table comment below it is the current truth.
   Paragraph deleted.

D. The dead In-Arrears economy, ALL legs (the census found a fourth
   leg the audit missed - the inert arrearsVal HUD writer at 13377,
   whose element no markup creates): if(false) drain, arrearsVal HUD
   block, win refund + boss fold + "(g recovered)" suffix, the three
   totalRollCost zero-inits, and the orphaned fadeInRefund CSS. The
   revive shape stays in git history at this commit; the design
   question (want the drain+refund back?) goes to docs/OPEN.md.
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


# ── A. the orphan deletions ──────────────────────────────────────────

sub("""    /* Reasonable feat-tracking defaults so SOME feats can fire */
    if(typeof G._featBanks==='undefined')G._featBanks=2;
    if(typeof G._featBusts==='undefined')G._featBusts=0;""",
    """    /* Reasonable feat-tracking defaults so SOME feats can fire */
    if(typeof G._featBusts==='undefined')G._featBusts=0;""",
    'A1 dbg guard _featBanks')

sub("""      _featBanks:2,_featBusts:0,_featMaxBank:1200,
      _featActivesUsed:false,_featFullStraight:false,_featHotDiceCount:0,""",
    """      _featBusts:0,_featMaxBank:1200,_featHotDiceCount:0,""",
    'A2 dbg literal')

sub("""    _featBanks:0,_featBusts:0,_featMaxBank:0,_featActivesUsed:false,_featFullStraight:false,_featHotDiceCount:0,
    _featTemptingFate:false,_featWinBankRolls:0,_turnTriple1Scored:false,_rolledAfterTriple1:false,""",
    """    _featBusts:0,_featMaxBank:0,_featHotDiceCount:0,""",
    'A3 match-init literal')

sub("""    /* Feat tracking \u2014 full straight rolled (regardless of who's scoring) */
    if(typeof G!=='undefined'&&G&&cards===G.pCards)G._featFullStraight=true;
""",
    "", 'A4 full-straight write')

sub("""      _tripFaces.forEach(function(_tf){_triplesFired.push(_tf);});
      if(typeof G!=='undefined'&&G&&cards===G.pCards)G._featTwoTriplets=true;""",
    """      _tripFaces.forEach(function(_tf){_triplesFired.push(_tf);});""",
    'A5 two-triplets write')

sub("""  /* Comeback feat tracking \u2014 flag the moment opponent is up by 50% target.
     If the player still wins after that, the Comeback feat awards renown. */
  if(G.target&&(G.oPts-G.pPts)>=G.target*0.5)G._featTrailedDeep=true;
""",
    "", 'A6 trailed-deep write')

sub("""  /* Tempting Fate feat: per-turn flags reset each turn (the achievement
     flag G._featTemptingFate persists for the match once earned). */
  G._turnTriple1Scored=false;G._rolledAfterTriple1=false;
""",
    "", 'A7 feeder reset')

sub("""  /* Tempting Fate feat: the player is choosing to roll AGAIN after
     committing a triple of 1s this turn \u2014 the gamble the feat rewards. */
  if(G._turnTriple1Scored)G._rolledAfterTriple1=true;
""",
    "", 'A8 feeder arm')

sub("""  /* Tempting Fate feat: triple of 1s committed this turn */
  var _tfOnes=0;selDice.forEach(function(d){if(d.val===1)_tfOnes++;});if(_tfOnes>=3)G._turnTriple1Scored=true;
""",
    "", 'A9 feeder score')

sub("""  /* Feat tracking */
  G._featBanks=(G._featBanks||0)+1;
  if(total>(G._featMaxBank||0))G._featMaxBank=total;
  /* Brinksman feat: remember how many rolls this banked turn took. The
     winning bank is the last one before endMatch, so this holds the
     winning turn's roll count at match end. */
  G._featWinBankRolls=G.turnRollCount||0;
  /* Tempting Fate feat: banked a turn in which the player committed a
     triple of 1s AND chose to roll again afterward. */
  if(G._rolledAfterTriple1)G._featTemptingFate=true;""",
    """  /* Feat tracking */
  if(total>(G._featMaxBank||0))G._featMaxBank=total;""",
    'A10 bank-path writes')

sub("""     neither. Slow Boiled wants the LONGEST turn, which is why it is a max
     and not the winning turn's count (that is _featWinBankRolls). */""",
    """     neither. Slow Boiled wants the LONGEST turn, which is why it is a max
     and not just the winning turn's count. */""",
    'A10b comment naming the deleted flag')

sub("""   in a state where it has no effect. (Doesn't touch the Pure Bones feat
   flag \u2014 borderline cases stay strict.) */""",
    """   in a state where it has no effect. */""",
    'A11 Pure Bones comment (refund helper)')

sub("""  markActiveCardUsed(cardId);
  /* Feat tracking: any active-card use disqualifies "Pure Bones" */
  if(G)G._featActivesUsed=true;""",
    """  markActiveCardUsed(cardId);""",
    'A12 actives-used write')

# ── B. the resume gap ────────────────────────────────────────────────

sub("""  famBankCount:(G._famBankCount===undefined)?null:G._famBankCount,
  famMinBank:(G._famMinBank===undefined)?null:G._famMinBank
}
  };""",
    """  famBankCount:(G._famBankCount===undefined)?null:G._famBankCount,
  famMinBank:(G._famMinBank===undefined)?null:G._famMinBank
},
/* P843: the feat accumulators. Every live threshold check reads one of
   these, and NONE was carried - a mid-match reload zeroed progress
   toward Slow Boiled, Full Bloom, Twice Saved, High Roller, Green
   Thumb, Sticky Fingers, Powder Monkey, Wish Granted, Omens True and
   The Long Road, and let No Claim forget pre-save busts (the one flip
   in the player's favour). _forKeeps was the worst case: the family
   card's spent charge WAS carried in famState.pF while the flag it
   bought was not. Raw values with a null absent-marker (same
   presence-not-truthiness care as famState above); restored by one
   keyed loop at the famState restore site, so a field added here
   restores itself. */
featState:{
  _featMaxRolls:(G._featMaxRolls===undefined)?null:G._featMaxRolls,
  _featBloom:(G._featBloom===undefined)?null:G._featBloom,
  _featWardSaves:(G._featWardSaves===undefined)?null:G._featWardSaves,
  _featMaxBank:(G._featMaxBank===undefined)?null:G._featMaxBank,
  _featJade:(G._featJade===undefined)?null:G._featJade,
  _featSticky:(G._featSticky===undefined)?null:G._featSticky,
  _featBusts:(G._featBusts===undefined)?null:G._featBusts,
  _featShatterBanked:(G._featShatterBanked===undefined)?null:G._featShatterBanked,
  _featStarChain:(G._featStarChain===undefined)?null:G._featStarChain,
  _featOmenTrue:(G._featOmenTrue===undefined)?null:G._featOmenTrue,
  _featMaxDeficit:(G._featMaxDeficit===undefined)?null:G._featMaxDeficit,
  _forKeeps:(G._forKeeps===undefined)?null:G._forKeeps
}
  };""",
    'B1 featState in the snapshot')

sub("""  if(_rdFam.famMinBank!==undefined&&_rdFam.famMinBank!==null)G._famMinBank=_rdFam.famMinBank;
}
var _rdTs=params._resumeData._tradeSwaps;""",
    """  if(_rdFam.famMinBank!==undefined&&_rdFam.famMinBank!==null)G._famMinBank=_rdFam.famMinBank;
}
/* P843: the feat accumulators come home. Same care as the famState
   block above - assign on PRESENCE, not truthiness: these are numbers
   legitimately 0 and booleans legitimately false. Null marks a field
   absent at save time (or a pre-P843 snapshot) and is skipped, keeping
   the fresh-match zero. */
var _rdFt=params._resumeData.featState;
if(_rdFt)for(var _ftK in _rdFt)
  if(_rdFt[_ftK]!==null&&_rdFt[_ftK]!==undefined)G[_ftK]=_rdFt[_ftK];
var _rdTs=params._resumeData._tradeSwaps;""",
    'B2 featState restore loop')

# ── C. the stale _RETIRED_RULES paragraph ────────────────────────────

sub("""   whose replacement does not exist yet.
   last_call is exactly that trap, still armed and NOT fixed here: Grog's
   badge carries ZERO HOUR under this id now, _iconFire reads G._tell.id for
   it directly rather than _ruleActive, and 'last_call' is in _SEAL_POOL - so
   a sealed seat can roll a rule this very table calls retired. Reported to
   whoever owns Zero Hour; the fix is the same shape as the two removals
   below. */""",
    """   whose replacement does not exist yet. */""",
    'C stale last_call paragraph')

# ── D. the dead In-Arrears economy, all legs ─────────────────────────

sub("""    /* In Arrears (Corvus): \u2212Xg per roll, gold can go negative.
       Also ticks the inline HUD value next to the Tell title. */
    /* First Strike is pure information - no gold drain. NOTE: In Arrears was
       the only economy tell in the roster, so no badge taxes gold any more. */
    if(false&&S&&S.run){
      if(!G._tellState)G._tellState={totalRollCost:0};
      var _iaCost=G._tell.perRoll||15;
      S.run.gold=(S.run.gold||0)-_iaCost;
      G._tellState.totalRollCost=(G._tellState.totalRollCost||0)+_iaCost;
      var _gel=document.getElementById('goldAmt');
      if(_gel){_gel.textContent=S.run.gold;_gel.classList.toggle('gold-debt',S.run.gold<0);
        _gel.classList.remove('gold-tick-down');void _gel.offsetWidth;_gel.classList.add('gold-tick-down');}
      _updateTellHUD();
      /* save() persists S to localStorage. Was `saveState()` which doesn't
         exist \u2014 threw a ReferenceError that crashed afterRoll mid-flight,
         leaving phase stuck on \"rolling\" with no way for the player to
         act. Reproduces on Corvus matches (his Tell is first_strike). */
      try{save();}catch(e){}
    }
""",
    """    /* First Strike is pure information - no gold drain. The In Arrears
       per-roll economy that lived here is deleted (P843) - it was dead
       behind if(false); the revive shape is in git history at P843. */
""",
    'D1 if(false) drain')

sub("""  if(t.id==='first_strike'){
    var ar=document.getElementById('arrearsVal');
    if(ar){
      var _arCost=(G._tellState&&G._tellState.totalRollCost)||0;
      ar.textContent='\u2212'+_arCost+'g';
      /* Pop animation each time it ticks */
      ar.classList.remove('tb-pop');void ar.offsetWidth;ar.classList.add('tb-pop');
    }
  }
""",
    "", 'D2 inert arrearsVal HUD leg')

sub("""  /* B3: Corvus In-Arrears refund \u2014 beating Corvus refunds every gold piece
     he drained from you across the match. Computed here, applied once
     either in the patron-gold path (folded into _patronGold above) or the
     boss-gold path below. Player feedback: \"Maybe you win Corvus lost
     gold through the match when you beat him, makes it sweeter\". */
  var _arrearsRefund=0;
  if(win&&G&&G._tell&&G._tell.id==='first_strike'&&G._tellState&&G._tellState.totalRollCost>0){
    _arrearsRefund=G._tellState.totalRollCost;
    if(!isBoss){
      /* Fold into the patron-gold count-up so it reads as a single reward */
      _patronGold+=_arrearsRefund;
      _getS();S.run.gold=(S.run.gold||0)+_arrearsRefund;save();
    }
    /* Boss path adds it inside the boss-gold block below to avoid double-count. */
  }
""",
    "", 'D3 win refund block')

sub("""    /* Fold any first_strike refund into the boss payout too, in case a future
       boss form ever uses Corvus's tell. Today only patron Corvus does, but
       the refund block above runs unconditionally so we mirror it here. */
    if(_arrearsRefund>0)_bossGold+=_arrearsRefund;
""",
    "", 'D4 boss fold satellite')

sub("""        /* B3: if part of the gold was a Corvus refund, append a small
           \"REFUNDED!\" suffix so the player feels the recovery. */
        if(_arrearsRefund>0){
          var _suf=document.createElement('span');
          _suf.className='res-gold-refund';
          _suf.textContent=' ('+_arrearsRefund+'g recovered)';
          _suf.style.cssText='display:block;font-size:11px;color:#a0e0ff;letter-spacing:1px;margin-top:2px;opacity:0;animation:fadeInRefund .5s ease .2s forwards;text-shadow:0 0 8px rgba(140,200,255,.55)';
          resGoldText.appendChild(_suf);
        }
""",
    "", 'D5 recovered-suffix satellite')

sub("""      if(t.id==='steeped')G._tellState.bonus=0;
      if(t.id==='first_strike')G._tellState.totalRollCost=0;
      if(t.id==='reckoning')G._tellState.lastNpcBank=0;""",
    """      if(t.id==='steeped')G._tellState.bonus=0;
      if(t.id==='reckoning')G._tellState.lastNpcBank=0;""",
    'D6 zero-init leg 1')

sub("""    if(t){G._tell=t;
      if(t.id==='first_strike')G._tellState.totalRollCost=0;
    }""",
    """    if(t){G._tell=t;
    }""",
    'D7 zero-init leg 2')

sub("""    case 'first_strike': G._tellState.totalRollCost=0; break;""",
    """    case 'first_strike':/* pure information, no state (P843) */ break;""",
    'D8 zero-init leg 3')

sub("""/* Corvus In-Arrears refund suffix appended to .res-gold-text on victory. */
@keyframes fadeInRefund{
  0%  {opacity:0;transform:translateY(4px)}
  100%{opacity:1;transform:translateY(0)}
}
""",
    "", 'D9 orphaned CSS keyframes')

# ── post-asserts: zero survivors of every deleted identifier ─────────
for dead in ['_featBanks', '_featActivesUsed', '_featFullStraight',
             '_featTemptingFate', '_featWinBankRolls', '_featTwoTriplets',
             '_featTrailedDeep', '_turnTriple1Scored', '_rolledAfterTriple1',
             '_arrearsRefund', 'totalRollCost', 'arrearsVal', 'fadeInRefund',
             'res-gold-refund']:
    n = s.count(dead)
    if n:
        sys.exit('SURVIVOR: %s x%d (nothing written)' % (dead, n))
# and the keepers must still be present
for alive in ['_featHotDiceCount', '_featMaxBank', '_featBusts',
              'featState:{', '_rdFt']:
    if alive not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % alive)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
