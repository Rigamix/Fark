# -*- coding: utf-8 -*-
"""P853: Corvus bleeds you again — one-way. RULED by Denis.

"Revive the per-roll gold drain. NO refund on beating him: gold he
takes is gone for good. Like Balatro. Forces you to save money before
facing him." So night 4 is a savings problem: arrive with a buffer or
get bled. First Strike has an economy again, just a one-way one.

Revived from the P843 git record (commit 5eae073), with the refund leg
DROPPED per the ruling:
  - the per-roll charge, no longer behind if(false)
  - G._tellState.totalRollCost, and its three zero-inits
  - the gold HUD tick + the gold-debt class (CSS survived P843 intact)
NOT revived: the win refund, its boss-payout fold, and the
"(Ng recovered)" suffix. Those stay deleted - the gold is gone.

TWO THINGS THE ORIGINAL NEVER HAD, fixed on the way in:
 1. A VISIBLE COUNTER. The old running-debt chip rendered into
    #arrearsVal, an element no markup ever created - so the drain was
    invisible even when it was live. It now uses the same inline
    tb-val slot STEEPED and DRILL ORDER use, which is built by
    _updateTellHUD itself and therefore actually exists.
 2. perRoll:5 ON THE TELL ROW. The old code read G._tell.perRoll and
    fell back to 15, but no tell row carries perRoll - so the "5g/roll
    (was 15)" rebalance Denis's own comment describes had silently
    reverted to 15 the moment the drain ran. It is data now.

The desc is rewritten to describe the tax, since there is one again -
the P639 note (name the trigger, don't write metaphor) still applies,
so it names both halves: the reveal AND the toll.
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


# 1) the drain itself
sub("""    /* First Strike is pure information - no gold drain. The In Arrears
       per-roll economy that lived here is deleted (P843) - it was dead
       behind if(false); the revive shape is in git history at P843. */""",
    """    /* P853 (Denis's ruling): THE TOLL IS BACK, AND IT IS ONE-WAY.
       Every roll against Corvus costs gold, it can drive the purse
       negative, and beating him refunds NOTHING - the P843 refund leg
       stays deleted on purpose. The point is that night 4 is a savings
       problem: arrive with a buffer or get bled.
       Charged per ROLL, before the dice are read, so a bust pays the
       toll too - that is the pressure. */
    if(_ruleActive('first_strike','p')&&S&&S.run){
      if(!G._tellState)G._tellState={totalRollCost:0};
      var _iaCost=(G._tell&&G._tell.perRoll)||5;
      S.run.gold=(S.run.gold||0)-_iaCost;
      G._tellState.totalRollCost=(G._tellState.totalRollCost||0)+_iaCost;
      var _gel=document.getElementById('goldAmt');
      if(_gel){_gel.textContent=S.run.gold;_gel.classList.toggle('gold-debt',S.run.gold<0);
        _gel.classList.remove('gold-tick-down');void _gel.offsetWidth;_gel.classList.add('gold-tick-down');}
      try{_updateTellHUD();}catch(e){}
      try{save();}catch(e){}
    }""",
    'the drain')

# 2) the tell row carries its own price + a desc that tells the truth
sub("""    tell:{id:'first_strike',name:'FIRST STRIKE',desc:"\u201cReach across my table with a brand \u2014 Snare, Trade, Snuff, Fog \u2014 and every die on both sides shows.\u201d",icon:'\U0001F4D2'}},""",
    """    /* P853: perRoll is DATA now. The drain read G._tell.perRoll with a
       fallback of 15 while no tell row carried the field, so the "5g a
       roll, was 15" rebalance above had quietly reverted to 15 the
       moment the charger ran. */
    tell:{id:'first_strike',name:'FIRST STRIKE',perRoll:5,desc:"\u201cEvery roll costs you 5 gold, win or lose. And reach across my table with a brand \u2014 Snare, Trade, Snuff, Fog \u2014 and every die on both sides shows.\u201d",icon:'\U0001F4D2'}},""",
    'perRoll + desc')

# 3) the running-debt chip, in a slot that exists
sub("""  /* In Arrears' running-debt chip. First Strike took the id but not the
     economy, so this rendered a permanent "-0g" beside the name. */
  var _arInlineVal='';""",
    """  /* P853: the running-debt chip is BACK, because the economy is. It
     renders into the same inline tb-val slot STEEPED and DRILL ORDER
     use - built right here, so it exists. The pre-P843 version wrote
     into #arrearsVal, an id no markup ever created, which is why the
     drain was invisible even when it was live. */
  var _arInlineVal=(t.id==='first_strike')?' <span class="tb-val tb-val-inline" id="arrearsVal">-'+((G._tellState&&G._tellState.totalRollCost)||0)+'g</span>':'';""",
    'the debt chip')

# 4) the chip updates per roll
sub("""  if(t.id==='drill_order'){""",
    """  if(t.id==='first_strike'){
    /* P853: refreshed from the same _updateTellHUD call the drain makes */
    var _arEl=document.getElementById('arrearsVal');
    if(_arEl){
      _arEl.textContent='-'+((G._tellState&&G._tellState.totalRollCost)||0)+'g';
      _arEl.classList.remove('tb-pop');void _arEl.offsetWidth;_arEl.classList.add('tb-pop');
    }
  }
  if(t.id==='drill_order'){""",
    'chip refresh')

# 5) the three zero-inits come back
sub("""      if(t.id==='steeped')G._tellState.bonus=0;
      if(t.id==='reckoning')G._tellState.lastNpcBank=0;""",
    """      if(t.id==='steeped')G._tellState.bonus=0;
      if(t.id==='first_strike')G._tellState.totalRollCost=0;/* P853 */
      if(t.id==='reckoning')G._tellState.lastNpcBank=0;""",
    'zero-init 1')
sub("""    if(t){G._tell=t;
    }""",
    """    if(t){G._tell=t;
      if(t.id==='first_strike')G._tellState.totalRollCost=0;/* P853 */
    }""",
    'zero-init 2')
sub("""    case 'first_strike':/* pure information, no state (P843) */ break;""",
    """    case 'first_strike': G._tellState.totalRollCost=0; break;/* P853 */""",
    'zero-init 3')

# post-asserts
for needed in ["perRoll:5", "G._tellState.totalRollCost=(G._tellState.totalRollCost||0)+_iaCost",
               "id=\"arrearsVal\""]:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
if '_arrearsRefund' in s:
    sys.exit('REFUND LEG PRESENT - the ruling says one-way (nothing written)')
if s.count('totalRollCost=0') != 3:
    sys.exit('zero-init count %d != 3 (nothing written)' % s.count('totalRollCost=0'))

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
