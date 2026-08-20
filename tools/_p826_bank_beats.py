# -*- coding: utf-8 -*-
"""P826: the bank/score beats - fools_gold's burn, retort's hit,
double_or_nothing's flip, falling_star's streak.

Census: the game's harshest punishment (fool's gold double-fail
burning the bank) was one log line; retort resolved in text both
directions; the DoN flip was instant with no beat; falling_star's
go-again had the turn flash but no celebration. All four beats ride
cardFx/_fxSpray - the FX canvas is body-level z9500, proven above the
3D dice (pickpocket's steal is the audited visible path).
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


# 1) fool's gold: the burn HITS the score and pops the number
sub("""  bust:function(ev){if(!_fxMine(ev)||!ev.me.state.burn)return;
    var burn=ev.lost||0;
    if(burn>0){G.pPts=Math.max(0,G.pPts-burn);famLog("FOOL'S GOLD BURNS "+burn+' MORE FROM YOUR BANK');try{updHUD();}catch(e){}}
    ev.me.state.burn=false;}""",
    """  bust:function(ev){if(!_fxMine(ev)||!ev.me.state.burn)return;
    var burn=ev.lost||0;
    if(burn>0){G.pPts=Math.max(0,G.pPts-burn);famLog("FOOL'S GOLD BURNS "+burn+' MORE FROM YOUR BANK');
      /* P826: the harshest punishment in the game was one log line -
         the score takes a visible hit and the number leaves loudly. */
      cardFx('hit',{row:'score'},{color:'#e8c874'});
      _famPop('-'+burn+" FOOL'S GOLD");
      try{updHUD();}catch(e){}}
    ev.me.state.burn=false;}""",
    "fool's gold burn beat")

# 2) retort: both directions land a visible hit
sub("""function _retortPay(ev){
  if(ev.owner==='p'){G.oPts=Math.max(0,G.oPts-ev.P);famLog('RETORT — THEY LOSE '+ev.P);}
  else{G.pPts=Math.max(0,G.pPts-ev.P);setStatusMsg('THEIR RETORT — YOU LOSE '+ev.P,'red');}
  try{updHUD();}catch(e){}
}""",
    """function _retortPay(ev){
  /* P826: retort must never read as silent (spec) - the losing side's
     surface takes the hit both ways. */
  if(ev.owner==='p'){G.oPts=Math.max(0,G.oPts-ev.P);famLog('RETORT — THEY LOSE '+ev.P);
    cardFx('hit',{row:'oppDice'},{color:'#c4404f'});}
  else{G.pPts=Math.max(0,G.pPts-ev.P);setStatusMsg('THEIR RETORT — YOU LOSE '+ev.P,'red');
    cardFx('hit',{row:'score'},{color:'#c4404f'});}
  try{updHUD();}catch(e){}
}""",
    'retort hits both ways')

# 3) double_or_nothing: the flip has a beat on the card
sub("""  bank:function(ev){if(!ev.mine||!ev.me.state.armed)return;
    ev.me.state.armed=false;
    var _meP=(ev.owner==='p');
    var winFlip=Math.random()<0.5;
    if(winFlip){
      if(_meP){G.pPts+=ev.amt;famLog('THE FLIP LANDS — BANK DOUBLED (+'+ev.amt+')');_famPop('x2 BANK');}
      else{G.oPts+=ev.amt;setStatusMsg('THEY FLIP — DOUBLE ('+(ev.amt*2)+')','red');}
    }else{
      var lose=Math.round(ev.amt*ev.P);
      if(_meP){G.pPts=Math.max(0,G.pPts-lose);famLog('THE FLIP FAILS — '+lose+' GONE');_famPop('-'+lose);}
      else{G.oPts=Math.max(0,G.oPts-lose);setStatusMsg('THEY FLIP AND LOSE — '+lose+' GONE','gold');}
    }
    try{updHUD();}catch(e){}}""",
    """  bank:function(ev){if(!ev.mine||!ev.me.state.armed)return;
    ev.me.state.armed=false;
    var _meP=(ev.owner==='p');
    var winFlip=Math.random()<0.5;
    /* P826: the flip gets a BEAT - the card churns as the coin goes up,
       then swells or takes the hit with the outcome. cardFx is rAF-
       deferred and descriptor-addressed, so it survives the row rebuild
       famUse triggers. */
    if(_meP)cardFx('churn',{myCard:'double_or_nothing'});
    if(winFlip){
      if(_meP){G.pPts+=ev.amt;famLog('THE FLIP LANDS — BANK DOUBLED (+'+ev.amt+')');_famPop('x2 BANK');
        setTimeout(function(){cardFx('gain',{myCard:'double_or_nothing'});},260);}
      else{G.oPts+=ev.amt;setStatusMsg('THEY FLIP — DOUBLE ('+(ev.amt*2)+')','red');}
    }else{
      var lose=Math.round(ev.amt*ev.P);
      if(_meP){G.pPts=Math.max(0,G.pPts-lose);famLog('THE FLIP FAILS — '+lose+' GONE');_famPop('-'+lose);
        setTimeout(function(){cardFx('hit',{myCard:'double_or_nothing'});},260);}
      else{G.oPts=Math.max(0,G.oPts-lose);setStatusMsg('THEY FLIP AND LOSE — '+lose+' GONE','gold');}
    }
    try{updHUD();}catch(e){}}""",
    'the flip has a beat')

# 4) falling_star: stars at the arm and at the go-again
sub("""    if(ev.owner==='p'){
      if(!G._fExtraTurn){G._fExtraTurn=true;
        G._featStarChain=(G._featStarChain||0)+1;/* WISH GRANTED */
        famLog('FALLING STAR — ANOTHER TURN COMES');}""",
    """    if(ev.owner==='p'){
      if(!G._fExtraTurn){G._fExtraTurn=true;
        G._featStarChain=(G._featStarChain||0)+1;/* WISH GRANTED */
        famLog('FALLING STAR — ANOTHER TURN COMES');
        cardFx('gain',{myCard:'falling_star'});/* P826: the wish is granted ON the card */}""",
    'stars at the arm')

sub("""  if(G._fExtraTurn&&G.pPts<G.target&&G.oPts<G.target){
    G._fExtraTurn=false;
    setStatusMsg('FALLING STAR — YOU GO AGAIN','gold');
    flashYourTurn();setTimeout(()=>{setTurnMode(false);startPTurn();},900);
    return;
  }""",
    """  if(G._fExtraTurn&&G.pPts<G.target&&G.oPts<G.target){
    G._fExtraTurn=false;
    setStatusMsg('FALLING STAR — YOU GO AGAIN','gold');
    /* P826: the ruled 'loud, unmissable' beat - a starburst over the
       table alongside the turn flash (the FX canvas sits above all). */
    try{var _fsAnchor=document.getElementById('hud')||document.body;
      _fxSpray(_fsAnchor,'#ffd870',30,{speed:230,g:70,size:9,spread:Math.PI*2});
      _fxSpray(_fsAnchor,'#fff2c0',14,{speed:120,g:40,size:6,spread:Math.PI*2});}catch(e){}
    _famPop('\\u2605 FALLING STAR');
    flashYourTurn();setTimeout(()=>{setTurnMode(false);startPTurn();},900);
    return;
  }""",
    'the go-again starburst')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
