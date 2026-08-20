# -*- coding: utf-8 -*-
"""P814: retort's SECOND trigger, wired - the cardHit seam.

Card audit (SILVER): text and spec both promise "when you bust OR are
hit by an opponent card, they lose 400" and the spec doubles down -
"fully automatic on either trigger". Driven: with retort held, a real
hex hit paid 0; no 'hit' seam existed anywhere. The bust half paid 400
on the nose (both owners - a boss bust cost the player exactly 400,
once).

The seam: famFire('cardHit',{actor:<victim>,src:<id>}) at the sites
where an opponent card takes something from a seat - the NPC hex, the
NPC confiscation, and the shared theft branches (pickpocket, reprisal,
ill_omen landing) for both owners. Retort's own payment fires no seam,
so retort-vs-retort cannot chain. Ward's spec names the same event, so
the seam is deliberately consumer-agnostic.

Coverage is the taking sites, not every rival annoyance - see the
OPEN.md note for the taxonomy question left with Denis.
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


# 1) retort: one payer, two seams
sub("""CFX.retort={
  bust:function(ev){if(!ev.mine)return;
    if(ev.owner==='p'){G.oPts=Math.max(0,G.oPts-ev.P);famLog('RETORT — THEY LOSE '+ev.P);}
    else{G.pPts=Math.max(0,G.pPts-ev.P);setStatusMsg('THEIR RETORT — YOU LOSE '+ev.P,'red');}
    try{updHUD();}catch(e){}}
};""",
    """/* P814: the card's SECOND trigger. Text and spec promise "bust OR hit
   by an opponent card"; only bust paid (driven: a hex hit paid 0 with
   retort held). One payer, two seams. cardHit's actor is the VICTIM -
   retort belongs to the seat that was hit. Retort's own payment fires
   no seam, so retort-vs-retort cannot chain. */
function _retortPay(ev){
  if(ev.owner==='p'){G.oPts=Math.max(0,G.oPts-ev.P);famLog('RETORT — THEY LOSE '+ev.P);}
  else{G.pPts=Math.max(0,G.pPts-ev.P);setStatusMsg('THEIR RETORT — YOU LOSE '+ev.P,'red');}
  try{updHUD();}catch(e){}
}
CFX.retort={
  bust:function(ev){if(!ev.mine)return;_retortPay(ev);},
  cardHit:function(ev){if(!ev.mine)return;_retortPay(ev);}
};""",
    'retort pays on both seams')

# 2) the NPC hex hit
sub("""  if(G._npcHexArmed){G._npcHexArmed=false;G.numDice=Math.max(3,G.numDice-1);triggerCard('whispers_hex',G.rung.name+" HEX — YOU HAVE "+G.numDice+" DICE",false);}""",
    """  if(G._npcHexArmed){G._npcHexArmed=false;G.numDice=Math.max(3,G.numDice-1);triggerCard('whispers_hex',G.rung.name+" HEX — YOU HAVE "+G.numDice+" DICE",false);try{famFire('cardHit',{actor:'p',src:'whispers_hex'});}catch(e){}}""",
    'hex fires cardHit')

# 3) the NPC confiscation
sub("""        spawnPop('✝️ CONFISCATED');
        setTimeout(function(){if(window.DLG)DLG.triggerCard(cid,false);},600);""",
    """        spawnPop('✝️ CONFISCATED');
        try{famFire('cardHit',{actor:'p',src:'confiscate'});}catch(e){}/* P814 */
        setTimeout(function(){if(window.DLG)DLG.triggerCard(cid,false);},600);""",
    'confiscation fires cardHit')

# 4) pickpocket: the lifted seat was hit
sub("""      if(_meP){G.oPts-=lift;G.pPts+=lift;famLog('PICKPOCKET LIFTS '+lift);
        cardFx('steal',{row:'oppDice'},{to:{row:'score'}});}
      else{G.pPts-=lift;G.oPts+=lift;
        setStatusMsg('THEIR FINGERS — '+lift+' LIFTED FROM YOU','red');}
      try{updHUD();}catch(e){}}}""",
    """      if(_meP){G.oPts-=lift;G.pPts+=lift;famLog('PICKPOCKET LIFTS '+lift);
        cardFx('steal',{row:'oppDice'},{to:{row:'score'}});
        try{famFire('cardHit',{actor:'o',src:'pickpocket'});}catch(e){}/* P814 */}
      else{G.pPts-=lift;G.oPts+=lift;
        setStatusMsg('THEIR FINGERS — '+lift+' LIFTED FROM YOU','red');
        try{famFire('cardHit',{actor:'p',src:'pickpocket'});}catch(e){}/* P814 */}
      try{updHUD();}catch(e){}}}""",
    'pickpocket fires cardHit')

# 5) reprisal: the stolen-from seat was hit
sub("""      if(_meP){G.oPts-=steal;G.pPts+=steal;famLog('REPRISAL TAKES '+steal+' FROM THEM');}
      else{G.pPts-=steal;G.oPts+=steal;setStatusMsg('THEIR REPRISAL — '+steal+' TAKEN FROM YOU','red');}
      try{updHUD();}catch(e){}}}""",
    """      if(_meP){G.oPts-=steal;G.pPts+=steal;famLog('REPRISAL TAKES '+steal+' FROM THEM');
        try{famFire('cardHit',{actor:'o',src:'reprisal'});}catch(e){}/* P814 */}
      else{G.pPts-=steal;G.oPts+=steal;setStatusMsg('THEIR REPRISAL — '+steal+' TAKEN FROM YOU','red');
        try{famFire('cardHit',{actor:'p',src:'reprisal'});}catch(e){}/* P814 */}
      try{updHUD();}catch(e){}}}""",
    'reprisal fires cardHit')

# 6) ill_omen LANDING takes points - a hit on the seat that lost them
sub("""      if(_meP){G.oPts-=take;G.pPts+=_ioP[0];
        G._featOmenTrue=true;/* OMENS TRUE */
        famLog('THE OMEN LANDS — YOU TAKE '+_ioP[0]);
        cardFx('steal',{row:'oppDice'},{to:{row:'score'}});}
      else{G.pPts-=take;G.oPts+=_ioP[0];
        famLog('THEIR OMEN LANDS — THEY TAKE '+_ioP[0]);}""",
    """      if(_meP){G.oPts-=take;G.pPts+=_ioP[0];
        G._featOmenTrue=true;/* OMENS TRUE */
        famLog('THE OMEN LANDS — YOU TAKE '+_ioP[0]);
        cardFx('steal',{row:'oppDice'},{to:{row:'score'}});
        try{famFire('cardHit',{actor:'o',src:'ill_omen'});}catch(e){}/* P814 */}
      else{G.pPts-=take;G.oPts+=_ioP[0];
        famLog('THEIR OMEN LANDS — THEY TAKE '+_ioP[0]);
        try{famFire('cardHit',{actor:'p',src:'ill_omen'});}catch(e){}/* P814 */}""",
    'ill_omen landing fires cardHit')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
