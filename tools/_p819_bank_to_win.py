# -*- coding: utf-8 -*-
"""P819: BANK TO WIN stops lying (stage 1 of the label honesty pass).

Denis: "BANK button does not consistently become 'BANK TO WIN'."
Recon (six-agent sweep) found one label writer (setBtns, fed by
_projectedBank) and these specific lies:

 1. DEAD LATCH (P728 regression): the winning press snaps back to a
    disabled plain BANK ~700ms before endMatch. The latch lived in
    handleYield - but a winning bank returns before yielding, and the
    tail setBtns already stripped the class it tested. Latched now at
    the win check itself, then the label re-runs.
 2. LAST CALL NOT MODELED: handleBank refuses sub-threshold banks
    outright, but the projection happily showed 'BANK +300' - and near
    target even 'BANK TO WIN' - for a press that banks ZERO. The
    projection now applies the same rule from the same source.
 3. TAB ESCROW NOT MODELED: with the rival's tab armed, the whole bank
    is held a turn and cannot win now - BANK TO WIN suppressed.
 4. DETERMINISTIC BONUSES UNDER-PROMISED: slow_cook's simmer pot and
    the hair-of-the-dog first-bank double both count toward the win
    check but were never projected - a winning bank read plain BANK.
    (The flip- and rival-dependent rewrites stay unprojected - the
    full dry-run bank oracle is an OPEN.md question.)
 5. STALE PATHS: Loan and tier-3 tamper move pPts with only updHUD,
    which never touched the label. The label block is extracted to
    _refreshBankLabel(), reading enablement from the button's own
    class, and updHUD now calls it - every mutation site heals the
    label with zero per-card work.
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
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# 1) the projection models last_call + the two deterministic bonuses
sub("""function _projectedBank(){
  if(!G)return 0;
  var t=(G.turnPts||0);
  try{
    if(G._tell){
      if(_ruleActive('steeped','p')&&G._tellState&&G._tellState.bonus>0)t+=G._tellState.bonus;
      if(typeof _ruleActive==='function'&&_ruleActive('reckoning','p')
         &&G._tellState&&G._tellState.lastNpcBank>0&&t<G._tellState.lastNpcBank)return 0;
    }
  }catch(e){}
  return t;
}""",
    """function _projectedBank(){
  if(!G)return 0;
  var t=(G.turnPts||0);
  try{
    if(G._tell){
      if(_ruleActive('steeped','p')&&G._tellState&&G._tellState.bonus>0)t+=G._tellState.bonus;
      if(typeof _ruleActive==='function'&&_ruleActive('reckoning','p')
         &&G._tellState&&G._tellState.lastNpcBank>0&&t<G._tellState.lastNpcBank)return 0;
    }
    /* P819: LAST CALL refuses sub-threshold banks outright (handleBank
       zeroes them) - projecting them as bankable was the button lying
       on the exact seat Denis reported. Same rule source, same gate
       (_ruleActive, NOT G._tell - sleeves and seals count). */
    if(typeof _ruleActive==='function'&&_ruleActive('last_call','p')&&t>0){
      var _lcR=(typeof _tellById==='function')?_tellById('last_call'):null;
      if(t<((_lcR&&_lcR.minBank)||800))return 0;
    }
    /* P819: the two DETERMINISTIC post-refusal bonuses the win check
       counts - slow_cook's simmer pot (famFire bankBonus adds state.acc
       flat) and the first-bank hangover double. Escrowed banks skip the
       bonus branch in handleBank, so they skip it here too. Flip- and
       rival-dependent rewrites stay unprojected (OPEN.md). */
    if(t>0&&!G._tabArmedVsPlayer){
      (G.pF||[]).forEach(function(c){
        if(c&&c.id==='slow_cook'&&c.state&&c.state.acc>0&&!c.broken)t+=c.state.acc;});
      if((G._famBankCount||0)===0&&typeof S!=='undefined'&&S&&S.run&&S.run._hotdNext)t*=2;
    }
  }catch(e){}
  return t;
}""",
    'projection models last_call + deterministic bonuses')

# 2) the label block leaves setBtns and learns the escrow gate
sub("""function setBtns(r,b){
  var rollBtn=document.getElementById('btnRoll');
  var bankBtn=document.getElementById('btnBank');
  var wasDisabled=bankBtn.classList.contains('disabled');
  /* flow spec 5: when the bank would cross the target, BANK takes the
     primary weight and says so — the win tap must be unmissable. */
  try{
    var _verb=document.getElementById('bankVerb'),_cap=document.getElementById('bankCap');
    var _bpts=_projectedBank();
    var _wins=!!(G&&b&&_bpts>0&&(G.pPts+_bpts)>=G.target);
    if(G&&G._bankedToWin)_wins=true;/* P728: latched at the winning press */
    /* Nothing to bank and only branded faces picked: the one thing this
       button does is fire them, so it says so. Guarded on _bpts, because
       with points already on the line it really is a bank - that just also
       happens to cast. */
    var _selNow=(G&&G.pool)?G.pool.filter(function(d){return d.sel&&!d.committed;}):[];
    var _castOnly=!!(b&&_bpts<=0&&_selNow.length&&_selNow.every(_dieIsIcon));
    bankBtn.classList.toggle('bank-to-win',_wins);
    /* P599: the same state on the ROW, because the swap needs to size the ROLL
       button too and it is not this button's child. One class, both rules,
       toggled from the flag that already decides everything else about this
       state - so the two buttons cannot disagree about whether the bank wins. */
    try{var _ctl=bankBtn.closest('.controls');
        if(_ctl)_ctl.classList.toggle('bank-to-win',_wins);}catch(e){}
    bankBtn.classList.toggle('bank-cast',_castOnly);
    if(_verb)_verb.textContent=_castOnly?'CAST':(_wins?'BANK TO WIN':'BANK');
    /* no running total on the winning press - the button says what it does */
    if(_cap)_cap.textContent=(b&&_bpts>0&&!_wins)?('+'+_bpts.toLocaleString()):'';
  }catch(e){}
  if(r)rollBtn.classList.remove('disabled');else rollBtn.classList.add('disabled');""",
    """/* P819: THE LABEL IS ITS OWN FUNCTION, fed by the button's live class
   rather than a caller argument, so every site that already calls
   updHUD heals the label for free (Loan and tier-3 tamper moved pPts
   with no label refresh - the structural hole behind 'inconsistently
   becomes BANK TO WIN'). setBtns calls it AFTER the class toggles and
   the drill lock; updHUD calls it after every mutation. */
function _refreshBankLabel(){
  var bankBtn=document.getElementById('btnBank');if(!bankBtn)return;
  var b=!bankBtn.classList.contains('disabled');
  try{
    var _verb=document.getElementById('bankVerb'),_cap=document.getElementById('bankCap');
    var _bpts=_projectedBank();
    /* P819: an escrowed bank (rival's tab) is held a turn and cannot win
       NOW - the caption may promise the amount, the win state may not. */
    var _wins=!!(G&&b&&_bpts>0&&(G.pPts+_bpts)>=G.target&&!G._tabArmedVsPlayer);
    if(G&&G._bankedToWin)_wins=true;/* P728: latched at the winning press */
    /* Nothing to bank and only branded faces picked: the one thing this
       button does is fire them, so it says so. Guarded on _bpts, because
       with points already on the line it really is a bank - that just also
       happens to cast. */
    var _selNow=(G&&G.pool)?G.pool.filter(function(d){return d.sel&&!d.committed;}):[];
    var _castOnly=!!(b&&_bpts<=0&&_selNow.length&&_selNow.every(_dieIsIcon));
    bankBtn.classList.toggle('bank-to-win',_wins);
    /* P599: the same state on the ROW, because the swap needs to size the ROLL
       button too and it is not this button's child. One class, both rules,
       toggled from the flag that already decides everything else about this
       state - so the two buttons cannot disagree about whether the bank wins. */
    try{var _ctl=bankBtn.closest('.controls');
        if(_ctl)_ctl.classList.toggle('bank-to-win',_wins);}catch(e){}
    bankBtn.classList.toggle('bank-cast',_castOnly);
    if(_verb)_verb.textContent=_castOnly?'CAST':(_wins?'BANK TO WIN':'BANK');
    /* no running total on the winning press - the button says what it does */
    if(_cap)_cap.textContent=(b&&_bpts>0&&!_wins)?('+'+_bpts.toLocaleString()):'';
  }catch(e){}
}
function setBtns(r,b){
  var rollBtn=document.getElementById('btnRoll');
  var bankBtn=document.getElementById('btnBank');
  var wasDisabled=bankBtn.classList.contains('disabled');
  if(r)rollBtn.classList.remove('disabled');else rollBtn.classList.add('disabled');""",
    'label extracted, escrow gated')

# 3) setBtns tail: label runs after the classes and the drill lock
sub("""  /* Re-assert the Drill Order lock after every setBtns call — otherwise a
     valid selection (refreshSelUI → setBtns(true,...)) would re-enable a
     roll button that Drill Order should keep locked. */
  _updateDrillLock();
}""",
    """  /* Re-assert the Drill Order lock after every setBtns call — otherwise a
     valid selection (refreshSelUI → setBtns(true,...)) would re-enable a
     roll button that Drill Order should keep locked. */
  _updateDrillLock();
  _refreshBankLabel();/* P819: after the classes and the lock, so it reads truth */
}""",
    'setBtns runs the label last')

# 4) updHUD heals the label
sub("""function updHUD(){
  if(!G)return;""",
    """function updHUD(){
  if(!G)return;
  try{_refreshBankLabel();}catch(e){}/* P819: every mutation site heals the label */""",
    'updHUD heals the label')

# 5) the latch moves to the win check; the dead handleYield copy dies
sub("""  if(G.pPts>=G.target){setTimeout(()=>endMatch(true),700);return;}
  if(G.oPts>=G.target){setTimeout(()=>endMatch(false),700);return;}
  showYieldButton();
}""",
    """  if(G.pPts>=G.target){
    /* P719/P728 (P819 restore): the WINNING press must hold BANK TO WIN
       through the 700ms to endMatch. The old latch lived in handleYield -
       unreachable, because this return skips yielding and the setBtns
       above already stripped the class it tested. Latch on the fact, then
       re-run the label so the class comes back. */
    G._bankedToWin=true;try{_refreshBankLabel();}catch(e){}
    setTimeout(()=>endMatch(true),700);return;}
  if(G.oPts>=G.target){setTimeout(()=>endMatch(false),700);return;}
  showYieldButton();
}""",
    'latch at the win check')

sub("""  /* P728: the bank-to-win scale must not snap back on the press - latch
     it for the rest of this match (the flag dies with G). */
  try{var _bw=document.getElementById('btnBank');
    if(G&&_bw&&_bw.classList.contains('bank-to-win'))G._bankedToWin=true;}catch(e){}""",
    """  /* P728's latch moved to handleBank's win check (P819) - reading the
     class here was dead: the tail setBtns stripped it first, and a
     winning bank never yields at all. */""",
    'dead latch removed')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
