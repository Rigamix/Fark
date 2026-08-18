# -*- coding: utf-8 -*-
"""P769: legacy cluster 2 - the arm blocks become a table.

Six cards armed themselves through near-identical inline blocks: four at
the head of the rival's turn (the_tab, loan, seven_dice, all_in) and two
mid-roll after the deal (twinning_charm, aldrics_vow). NPC_ARMS keeps
each as one entry - 'is now my moment?' + the arm, spend inside, exactly
the bust-save table's shape - keyed by moment ('turnStart' | 'roll').
ctx carries `left` so seven_dice can widen the hand without reaching
into the closure.

Conditions, spends, announces preserved verbatim. npcCardState untouched.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    c = s.count(old)
    if c != 1:
        o2 = old.replace('\n', '\r\n')
        if s.count(o2) == 1:
            old, new = o2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
    s = s.replace(old, new)
    edits.append(label)


# ── 1. the table ──
sub("""function npcHasActive(cid){""",
    """/* P769: THE ARM TABLE (legacy cluster 2). Each entry answers 'is now
   my moment?' and arms itself - spend inside, like the bust-save
   table's entries. moment 'turnStart' runs once at the head of the
   rival's turn; 'roll' runs in step() after the deal. ctx carries
   `left` (seven_dice widens the hand through it) and, for roll
   entries, oppBank (aldrics_vow's odds test). */
var NPC_ARMS=[
  {id:'the_tab',moment:'turnStart',try:function(ctx){
    if(G._tabArmedVsPlayer||(G._tabHeldPlayer>0)||!G.target)return;
    if(!(G.pPts>=G.target*0.8&&G.pPts>G.oPts))return;
    npcUseActive('the_tab');
    G._tabArmedVsPlayer=true;
    triggerCard('the_tab','RIVAL PUTS YOU ON THE TAB',false);
    setStatusMsg((G.rung?G.rung.name:'RIVAL')+": YOU'RE ON THE TAB — NEXT BANK HELD",'red');}},
  {id:'loan',moment:'turnStart',try:function(ctx){
    if(G.npcCardState.oppTurnCount!==0)return;
    npcUseActive('loan');
    G.oPts+=1500;G._oLoanRemaining=5;updHUD();
    triggerCard('loan','+1500 LOAN',false);
    setStatusMsg(G.rung.name+': LOAN +1500 (−200/TURN)','red');}},
  {id:'seven_dice',moment:'turnStart',try:function(ctx){
    if(G.npcCardState.oppTurnCount!==0)return;
    npcUseActive('seven_dice');
    ctx.left=7;
    triggerCard('seven_dice','7 DICE!',false);
    setStatusMsg(G.rung.name+': SEVEN DICE — 7 DICE!','red');}},
  {id:'all_in',moment:'turnStart',try:function(ctx){
    if(!(G.oPts*2>=G.target&&G.oPts<G.target&&G.npcCardState.oppTurnCount>=2))return;
    npcUseActive('all_in');
    G._oAllInArmed=true;
    triggerCard('all_in','ALL IN ARMED',false);
    setStatusMsg(G.rung.name+': ALL IN — NEXT BANK 2× (OR −500)','red');}},
  {id:'twinning_charm',moment:'roll',try:function(ctx){
    var _f=G.oppDice.filter(function(d){return !d.kept;});
    var _src=_f.filter(function(d){return d.val===1;})[0]||_f.filter(function(d){return d.val===5;})[0];
    var _tgt=_f.filter(function(d){return d.val!==1&&d.val!==5;})[0];
    if(!_src||!_tgt)return;
    npcUseActive('twinning_charm');
    _tgt.val=_src.val;reDrawDieFace(_tgt);
    if(_tgt.el){_tgt.el.classList.add('eff-glow-blue');spawnPixelSparks(_tgt.el,6);
      setTimeout(function(){if(_tgt.el)_tgt.el.classList.remove('eff-glow-blue');},_oppDelay(700));}
    triggerCard('twinning_charm','TWINNING → '+_src.val,false);}},
  {id:'aldrics_vow',moment:'roll',try:function(ctx){
    if(G._oVowArmed)return;
    var _fc=G.oppDice.filter(function(d){return !d.kept;}).length;
    if(!(_fc>=4&&ctx.oppBank>=200&&ctx.oppBank<=500))return;
    npcUseActive('aldrics_vow');
    G._oVowArmed=true;
    triggerCard('aldrics_vow','VOW ARMED',false);
    setStatusMsg(G.rung.name+': VOW — 300+ DOUBLES, ELSE LOSE PTS','red');}}
];
function _npcRunArms(moment,ctx){
  for(var _ai=0;_ai<NPC_ARMS.length;_ai++){
    var _A=NPC_ARMS[_ai];
    if(_A.moment!==moment)continue;
    if(!npcHasActive(_A.id))continue;
    try{_A.try(ctx);}catch(e){}
  }
  return ctx;
}
function npcHasActive(cid){""",
    'the arm table')

# ── 2. the four turn-start blocks become one call ──
sub("""  if(npcHasActive('the_tab')&&!G._tabArmedVsPlayer&&!(G._tabHeldPlayer>0)&&G.target&&G.pPts>=G.target*0.8&&G.pPts>G.oPts){
    npcUseActive('the_tab');
    G._tabArmedVsPlayer=true;
    triggerCard('the_tab','RIVAL PUTS YOU ON THE TAB',false);
    setStatusMsg((G.rung?G.rung.name:'RIVAL')+": YOU'RE ON THE TAB — NEXT BANK HELD",'red');
  }""",
    """  /* P769: the turn-start arms are the TABLE now (NPC_ARMS) - the_tab,
     loan, seven_dice, all_in in the same order, seven_dice widening the
     hand through the ctx. */
  left=_npcRunArms('turnStart',{left:left}).left;""",
    'turn-start consumer')

sub("""  if(npcHasActive('loan')&&G.npcCardState.oppTurnCount===0){
    npcUseActive('loan');
    G.oPts+=1500;G._oLoanRemaining=5;updHUD();
    triggerCard('loan','+1500 LOAN',false);
    setStatusMsg(G.rung.name+': LOAN +1500 (−200/TURN)','red');
  }
  /* SEVEN DICE: NPC's next roll uses 7 dice. Use it on turn 1 for max value. */
  if(npcHasActive('seven_dice')&&G.npcCardState.oppTurnCount===0){
    npcUseActive('seven_dice');
    left=7;
    triggerCard('seven_dice','7 DICE!',false);
    setStatusMsg(G.rung.name+': SEVEN DICE — 7 DICE!','red');
  }
  /* ALL IN: arm next-bank doubling when NPC could win the match in one big bank.
     Heuristic: if oPts is within striking distance (≤target/2 from win) and
     NPC has 1+ score-multiplying cards stacking. Use it on turn ≥3 once
     enough state is built. */
  if(npcHasActive('all_in')&&G.oPts*2>=G.target&&G.oPts<G.target&&G.npcCardState.oppTurnCount>=2){
    npcUseActive('all_in');
    G._oAllInArmed=true;
    triggerCard('all_in','ALL IN ARMED',false);
    setStatusMsg(G.rung.name+': ALL IN — NEXT BANK 2× (OR −500)','red');
  }""",
    """  /* P769: loan, seven_dice and all_in moved to NPC_ARMS with the_tab. */""",
    'three blocks folded')

# ── 3. the two roll-time blocks become one call ──
sub("""      if(npcHasActive('twinning_charm')){
        var _otcFree=G.oppDice.filter(function(d){return !d.kept;});
        var _otcSrc=_otcFree.filter(function(d){return d.val===1;})[0]||_otcFree.filter(function(d){return d.val===5;})[0];
        var _otcTgt=_otcFree.filter(function(d){return d.val!==1&&d.val!==5;})[0];
        if(_otcSrc&&_otcTgt){
          npcUseActive('twinning_charm');
          _otcTgt.val=_otcSrc.val;reDrawDieFace(_otcTgt);
          if(_otcTgt.el){_otcTgt.el.classList.add('eff-glow-blue');spawnPixelSparks(_otcTgt.el,6);setTimeout(function(){if(_otcTgt.el)_otcTgt.el.classList.remove('eff-glow-blue');},_oppDelay(700));}
          triggerCard('twinning_charm','TWINNING → '+_otcSrc.val,false);
        }
      }
      /* ALDRIC'S VOW NPC AI: arm before scoring on a "good odds" roll —
         when there are 4+ unkept dice (high chance of 300+ score) and
         oppBank is moderate (200-500). Effect applied after scoreRoll. */
      if(npcHasActive('aldrics_vow')&&!G._oVowArmed){
        var _ovFreeCount=G.oppDice.filter(function(d){return !d.kept;}).length;
        if(_ovFreeCount>=4&&oppBank>=200&&oppBank<=500){
          npcUseActive('aldrics_vow');
          G._oVowArmed=true;
          triggerCard('aldrics_vow','VOW ARMED',false);
          setStatusMsg(G.rung.name+': VOW — 300+ DOUBLES, ELSE LOSE PTS','red');
        }
      }""",
    """      /* P769: twinning_charm and aldrics_vow arm through NPC_ARMS'
         roll moment - same conditions, same spends, one walker. */
      _npcRunArms('roll',{oppBank:oppBank});""",
    'roll-time consumer')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
