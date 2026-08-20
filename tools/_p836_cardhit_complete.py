# -*- coding: utf-8 -*-
"""P836: the cardHit rule is COMPLETE (Denis: "an opponent card that
takes dice or points is a hit - a complete rule, not one that answers
for two cards and stays silent on the rest").

Census (anchor sweep): 14 NPC-side takers were not firing the seam,
plus 4 player-owned mirrors (the player can hold NPC cards via the
post-victory draft). Fires land AT the dock, inside the branch where
the take actually happens (ward fizzles never fire - the P814 rule),
actor = the victim. iron_gate included per the census's read: an
opponent card taking the points you lost is still an opponent card
taking your points. crown_authority/blessed_dice stay out (a reroll
wager, not a take). Consumer: CFX.retort.cardHit -> _retortPay.
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


F = "try{famFire('cardHit',{actor:'p',src:'%s'});}catch(e){}/* P836 */"
FO = "try{famFire('cardHit',{actor:'o',src:'%s'});}catch(e){}/* P836 */"

# ── NPC-side bank docks ──
sub("""      var steal=BANK_TAKE.steal_pct(total,eff);total-=steal;G.oPts+=steal;
      bonusMsg+=' -'+steal+' '+npc.name;
      triggerCard(cid,npc.name+' −'+steal,false);""",
    """      var steal=BANK_TAKE.steal_pct(total,eff);total-=steal;G.oPts+=steal;
      bonusMsg+=' -'+steal+' '+npc.name;
      triggerCard(cid,npc.name+' −'+steal,false);
      """ + F % 'steal_pct',
    'steal_pct')

sub("""      var half=total-BANK_FX.halve_first_bank(total,eff);total-=half;
      bonusMsg+=' -'+half+' '+npc.name;
      triggerCard(cid,npc.name+' −'+half+'!',false);""",
    """      var half=total-BANK_FX.halve_first_bank(total,eff);total-=half;
      bonusMsg+=' -'+half+' '+npc.name;
      triggerCard(cid,npc.name+' −'+half+'!',false);
      """ + F % 'halve_first_bank',
    'halve_first_bank')

sub("""      var _cwHalf=Math.floor(total/2);total-=_cwHalf;
      bonusMsg+=' -'+_cwHalf+' '+npc.name;
      triggerCard(cid,npc.name+' −'+_cwHalf+'!',false);""",
    """      var _cwHalf=Math.floor(total/2);total-=_cwHalf;
      bonusMsg+=' -'+_cwHalf+' '+npc.name;
      triggerCard(cid,npc.name+' −'+_cwHalf+'!',false);
      """ + F % 'halve_big_bank',
    'halve_big_bank')

sub("""      G.npcCardState.usedOnce[cid]=(G.npcCardState.usedOnce[cid]||0)+1;G.oPts+=total;
      bonusMsg+=' STOLEN! '+npc.name;""",
    """      G.npcCardState.usedOnce[cid]=(G.npcCardState.usedOnce[cid]||0)+1;G.oPts+=total;
      """ + F % 'steal_low_bank' + """
      bonusMsg+=' STOLEN! '+npc.name;""",
    'steal_low_bank (fires before the abort)')

sub("""        G.pPts=Math.max(0,(G.pPts||0)-(_chPenP-_chFromBankP));
        bonusMsg+=' -'+_chPenP+' '+npc.name;""",
    """        G.pPts=Math.max(0,(G.pPts||0)-(_chPenP-_chFromBankP));
        """ + F % 'challenge' + """
        bonusMsg+=' -'+_chPenP+' '+npc.name;""",
    'challenge (bank half)')

sub("""      G.pPts=SCORE_DRAIN.periodic_drain(G.pPts,npc.effect);
      bonusMsg+=' -'+npc.effect.amount+' '+npc.name;""",
    """      G.pPts=SCORE_DRAIN.periodic_drain(G.pPts,npc.effect);
      """ + F % 'periodic_drain' + """
      bonusMsg+=' -'+npc.effect.amount+' '+npc.name;""",
    'periodic_drain')

sub("""    if(_cbCut>0){total-=_cbCut;bonusMsg+=' -'+_cbCut+" COWARD'S BELL";triggerCard('cowards_bell','-'+_cbCut,false);}""",
    """    if(_cbCut>0){total-=_cbCut;bonusMsg+=' -'+_cbCut+" COWARD'S BELL";triggerCard('cowards_bell','-'+_cbCut,false);""" + F % 'cowards_bell' + """}""",
    'cowards_bell')

# ── NPC-side bust docks ──
sub("""      G.pPts=Math.max(0,G.pPts-BUST_FX.punish_busts.penalty(eff));
      _pendingBustTriggers.push({cid:cid,msg:npc.name+' −'+BUST_FX.punish_busts.penalty(eff)+'!'});""",
    """      G.pPts=Math.max(0,G.pPts-BUST_FX.punish_busts.penalty(eff));
      """ + F % 'punish_busts' + """
      _pendingBustTriggers.push({cid:cid,msg:npc.name+' −'+BUST_FX.punish_busts.penalty(eff)+'!'});""",
    'punish_busts')

sub("""  if(G.npcCardState.challengeActive){
    G.npcCardState.challengeActive=false;
    G.pPts=Math.max(0,G.pPts-G.npcCardState.challengePenalty);
  }""",
    """  if(G.npcCardState.challengeActive){
    G.npcCardState.challengeActive=false;
    G.pPts=Math.max(0,G.pPts-G.npcCardState.challengePenalty);
    """ + F % 'challenge' + """
  }""",
    'challenge (bust half)')

sub("""      G.oPts+=_igLost;updHUD();
      triggerCard('iron_gate_npc','IRON GATE +'+_igLost,false);""",
    """      G.oPts+=_igLost;updHUD();
      """ + F % 'steal_on_bust' + """
      triggerCard('iron_gate_npc','IRON GATE +'+_igLost,false);""",
    'iron_gate steal_on_bust')

# ── NPC-side dice docks ──
sub("""        spawnPop('🔄 SWAPPED');""",
    """        spawnPop('🔄 SWAPPED');
        """ + F % 'swap_die',
    'swap_die best_for_worst')

sub("""          spawnPop('📦 ×'+_dgnDowngraded.length+' DOWNGRADED');""",
    """          spawnPop('📦 ×'+_dgnDowngraded.length+' DOWNGRADED');
          """ + F % 'swap_die',
    'swap_die downgrade_best')

sub("""        spawnPop('👑 SEIZED');""",
    """        spawnPop('👑 SEIZED');
        """ + F % 'steal_die',
    'steal_die take_best')

sub("""        var _sbN=eff.swapN||1;
        var _sbTo=eff.swapTo||3;""",
    """        var _sbN=eff.swapN||1;
        var _sbTo=eff.swapTo||3;
        """ + F % 'swap_best_to_3',
    'swap_best_to_3')

sub("""          G.numDice=Math.min(G.numDice,5);
          triggerCard(_rfrId,(_rfrCard?_rfrCard.name:'').toUpperCase()+' — 5 DICE!',false);""",
    """          G.numDice=Math.min(G.numDice,5);
          """ + F % 'reduce_first_roll' + """
          triggerCard(_rfrId,(_rfrCard?_rfrCard.name:'').toUpperCase()+' — 5 DICE!',false);""",
    'reduce_first_roll')

sub("""      _dieLeftSeat(pBestIdx);/* P564 */
      triggerCard('sleight_of_hand',G.rung.name+' SLEIGHT',false);""",
    """      _dieLeftSeat(pBestIdx);/* P564 */
      """ + F % 'sleight_of_hand' + """
      triggerCard('sleight_of_hand',G.rung.name+' SLEIGHT',false);""",
    'sleight_of_hand')

# ── player-owned mirrors (actor: the RIVAL is hit) ──
sub("""          var steal=BANK_TAKE.steal_pct(pts,eff);pts-=steal;G.pPts+=steal;
          triggerCard(cid,npc.name+' +'+steal,true);""",
    """          var steal=BANK_TAKE.steal_pct(pts,eff);pts-=steal;G.pPts+=steal;
          """ + FO % 'steal_pct' + """
          triggerCard(cid,npc.name+' +'+steal,true);""",
    'steal_pct mirror')

sub("""          G.pPts+=pts;pts=0;
          triggerCard(cid,npc.name+' STOLE!',true);spawnPop('STOLEN!');""",
    """          G.pPts+=pts;pts=0;
          """ + FO % 'steal_low_bank' + """
          triggerCard(cid,npc.name+' STOLE!',true);spawnPop('STOLEN!');""",
    'steal_low mirror')

sub("""            G.oPts=Math.max(0,G.oPts-(penalty-_chFromBank));
            triggerCard(cid,npc.name+' −'+penalty,true);""",
    """            G.oPts=Math.max(0,G.oPts-(penalty-_chFromBank));
            """ + FO % 'challenge' + """
            triggerCard(cid,npc.name+' −'+penalty,true);""",
    'challenge mirror')

sub("""          var half=pts-BANK_FX.halve_first_bank(pts,eff);pts-=half;
          triggerCard(cid,npc.name+' −'+half,true);""",
    """          var half=pts-BANK_FX.halve_first_bank(pts,eff);pts-=half;
          """ + FO % 'halve_first_bank' + """
          triggerCard(cid,npc.name+' −'+half,true);""",
    'halve_first mirror')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d fires (%s)' % (len(edits), ', '.join(edits)))
