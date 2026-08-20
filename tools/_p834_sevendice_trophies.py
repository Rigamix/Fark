# -*- coding: utf-8 -*-
"""P834: two rulings - Seven Dice redesigned; boss relics are trophies.

SEVEN DICE (Denis: "redesign, not a 7th lane... 'Reroll one die free'
preserves the bonus feeling without the risk"). The old +1-die promise
has been a silent no-op since the seat clamps (P521/P529 - the card
announced SEVEN DICE and dealt six; the P523 comment names it), and
the card is currently UNACQUIRABLE (its only path, the legacy
tin/silver/gold draft, has no showScreen('draft') caller). The
redesign is the definition the card carries whenever it returns to a
pool: activation paints the free dice, one tap rerolls that die free
(steady_hand's shape, P535 re-derive included). The dead +1-die
consumers go: handleRoll's arm branch and the NPC_ARMS ctx.left=7
entry (no rung pools the card).

RELIC SPOILS (Denis: "(b), trophies, not dice - a die you'd never
actually equip doesn't feel good to receive"). famSpoilsPick's relic
branch lands in S.trophies (the Ambrose night-8 precedent, rendered
'🏆' on the RUN WON screen) instead of the die inventory, and the
chooser card says what it is: for the shelf.
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


# ── seven dice: the definition says the new design ──
sub(r"""  {id:'seven_dice',name:'SEVEN DICE',icon:'🎲',rarity:'gold',type:'active',maxUses:1,timing:'idle',eff:'NEXT ROLL: 7 DICE INSTEAD OF 6',desc:"Activate before your next roll: throw 7 dice instead of 6. Keep up to 6 scoring dice as normal.",arch:'sharp'},""",
    r"""  {id:'seven_dice',name:'SEVEN DICE',icon:'🎲',rarity:'gold',type:'active',maxUses:1,timing:'idle',eff:'REROLL ONE DIE, FREE',desc:"Activate during your turn: tap one die and it rerolls, free. You keep the new face, better or worse.",arch:'sharp'},/* P834: redesigned per Denis - the 7th-lane promise was a silent no-op since the seat clamps */""",
    'seven dice def redesigned')

# ── the activation becomes the free reroll ──
sub("""/* Seven Dice: arm a flag — next roll uses +1 die */
function activateSevenDice(){
  G._sevenDiceArmed=true;
  setStatusMsg('SEVEN DICE — NEXT ROLL HAS 7','gold');
  triggerCard('seven_dice','ARMED',true);
}""",
    """/* P834: Seven Dice redesigned (Denis) - a free one-die reroll,
   steady_hand's tap shape with the P535 re-derive. The +1-die arm was
   a silent no-op since the seat clamps. */
function activateSevenDice(){
  var free=(G&&G.pool||[]).filter(function(d){return !d.committed&&!d._frozen;});
  if(!free.length){setStatusMsg('SEVEN DICE — NOTHING TO REROLL','red');return;}
  setStatusMsg('SEVEN DICE — TAP THE DIE TO REROLL','gold');
  triggerCard('seven_dice','ARMED',true);
  free.forEach(function(d){
    if(!d.el)return;
    d.el.classList.add('break-target');
    d.el.onclick=function(){
      free.forEach(function(q){if(q.el){q.el.classList.remove('break-target');q.el.onclick=function(){toggleDie(q);};}});
      d.val=_rollD(d);d.sel=false;
      if(d.el){d.el.classList.remove('selected');d.el.classList.add('card-reroll');
        setTimeout(function(){if(d.el)d.el.classList.remove('card-reroll');},700);}
      try{reDrawDieFace(d);}catch(e){}
      famLog('SEVEN DICE — '+d.val);
      /* the table as it is NOW can be a bust (steady_hand's P535 lesson) */
      var _sf=(G.pool||[]).filter(function(x){return !x.committed&&!x._shattered;});
      var fv=_sf.map(function(x){return x.val;}),fm=_sf.map(function(x){return x.mat;});
      if(!anyScoring(fv,effectiveCards(),fm,_sf)){if(!_tryBustSave(_sf))_delayedDoBust(_sf);return;}
      try{refreshSelUI();}catch(e){}
    };
  });
}""",
    'the activation is the free reroll')

# ── the dead +1-die consumers go ──
sub("""  /* Seven Dice (active): bump dice count by 1 for this roll only */
  if(G._sevenDiceArmed){
    G._sevenDiceArmed=false;
    G.numDice=Math.min(G.numDice+1,7);
    triggerCard('seven_dice','SEVEN DICE!',true);
  }""",
    """  /* P834: the Seven Dice +1-die arm is retired with the redesign - it
     was a silent no-op anyway (the P529 seat clamp below never dealt
     the 7th die; P523's comment names the card). */""",
    'player +1-die consumer removed')

sub("""  {id:'seven_dice',moment:'turnStart',try:function(ctx){
    if(G.npcCardState.oppTurnCount!==0)return;
    npcUseActive('seven_dice');
    ctx.left=7;
    triggerCard('seven_dice','7 DICE!',false);
    setStatusMsg(G.rung.name+': SEVEN DICE — 7 DICE!','red');}},""",
    """  /* P834: the NPC seven_dice arm is deleted with the redesign - no
     rung pools the card, and ctx.left=7 was clamped to the six seats
     by the P521 join regardless. */""",
    'NPC arm removed')

# ── relics are trophies ──
sub("""  if(kind==='relic'&&sp.relic){S.run.diceInv=S.run.diceInv||[];S.run.diceInv.push(sp.relic);msg='THE RELIC IS YOURS: '+getDie(sp.relic).name;}""",
    """  if(kind==='relic'&&sp.relic){
    /* P834 (Denis, ruling b): relics are TROPHIES, not dice - they rank
       0 against real dice, so seating one was strictly worse than any
       die the player owns; the value is the shelf story. Same shelf the
       Ambrose night-8 win already uses (the RUN WON screen renders 🏆
       per entry). */
    S.trophies=S.trophies||[];
    if(S.trophies.indexOf(sp.relic)<0)S.trophies.push(sp.relic);
    msg='THE TROPHY GOES ON YOUR SHELF: '+getDie(sp.relic).name;
  }""",
    'relics land on the shelf')

sub("""      +'<div style="font-size:10px;color:#dc5;margin:2px 0">HIS DIE</div>'""",
    """      +'<div style="font-size:10px;color:#dc5;margin:2px 0">HIS DIE — A TROPHY FOR THE SHELF</div>'""",
    'the chooser says what it is')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
