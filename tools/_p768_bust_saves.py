# -*- coding: utf-8 -*-
"""P768: legacy cluster 1b - the bust-mitigation chain becomes a table.

Four mechanics stood between a dead roll and _oppBustOut as inline
blocks: bust_survive / bust_immune_turns (one walker, CARD order),
bust_bank_half, the mabels_stitch special, and second_wind. The table
keeps each as an entry that answers 'can you soften this bust?' with one
of three outcomes:

  survive        the turn CONTINUES (_oResumeAfterBustSave)
  bank(pts)      the turn ends but pts are banked (the finOpp timer)
  pass           next entry

ORDER PRESERVED EXACTLY: the survive/immune walker is ONE entry (the
original checked both mechanics in a single G.oCards loop, so a boss
holding both resolves by CARD order, not mechanic order); bank_half
then stitch then second_wind follow, as before. bust_survive still
halves the surviving bank; bust_immune still spends NO use (it is a
turn-window, not a charge). npcCardState untouched.
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


# ── 1. the table, beside NPC_RESCUES ──
sub("""function npcHasActive(cid){""",
    """/* P768: THE BUST-SAVE TABLE (legacy cluster 1b). Each entry answers
   'can you soften this bust?' with {kind:'survive'} (the turn continues
   via _oResumeAfterBustSave), {kind:'bank',pts,label,cid} (the turn
   ends, pts banked through the finOpp timer), or null (pass). ctx
   carries oppBank in and OUT - bust_survive halves what survives.
   Entry 1 is the survive/immune walker EXACTLY as the old loop was:
   both mechanics in one pass over G.oCards, so a boss holding both
   resolves by card order. bust_immune spends no use (a turn window,
   not a charge). */
var NPC_BUST_SAVES=[
  {name:'surviveOrImmune',try:function(ctx){
    var hit=null;
    (G.oCards||[]).some(function(cid){
      var npc=getNpcCard(cid);if(!npc||!npc.effect)return false;
      var eff=npc.effect;
      if(eff.mechanic==='bust_immune_turns'&&G.npcCardState.oppTurnCount<=(eff.turns||2)){
        hit={cid:cid};return true;
      }
      if(eff.mechanic==='bust_survive'&&(G.npcCardState.usedOnce[cid]||0)<_useCap(cid)&&Math.random()<eff.chance){
        G.npcCardState.usedOnce[cid]=(G.npcCardState.usedOnce[cid]||0)+1;
        /* survival costs half the turn's points - see the card text */
        ctx.oppBank=Math.floor(ctx.oppBank/2);
        hit={cid:cid};return true;
      }
      return false;
    });
    return hit?{kind:'survive',cid:hit.cid}:null;
  }},
  {name:'bankHalf',try:function(ctx){
    var out=null;
    (G.oCards||[]).some(function(cid){
      var npc=getNpcCard(cid);if(!npc)return false;
      if(npc.effect.mechanic==='bust_bank_half'&&(G.npcCardState.usedOnce[cid]||0)<_useCap(cid)&&ctx.oppBank>0){
        G.npcCardState.usedOnce[cid]=(G.npcCardState.usedOnce[cid]||0)+1;
        var half=Math.floor(ctx.oppBank/2);
        out={kind:'bank',pts:half,cid:cid,
          msg:npc.name+'! '+G.rung.name+' SAVES '+half};
        return true;
      }
      return false;
    });
    return out;
  }},
  {name:'stitch',try:function(ctx){
    if(!G.oCards.includes('mabels_stitch'))return null;
    if((G.npcCardState.usedOnce['mabels_stitch']||0)>=_useCap('mabels_stitch'))return null;
    if(ctx.oppBank<=0)return null;
    G.npcCardState.usedOnce['mabels_stitch']=(G.npcCardState.usedOnce['mabels_stitch']||0)+1;
    return {kind:'bank',pts:ctx.oppBank,cid:'mabels_stitch',
      msg:"MABEL'S STITCH — "+G.rung.name+' SAVES '+ctx.oppBank,
      label:'STITCH +'+ctx.oppBank};
  }},
  {name:'secondWind',try:function(ctx){
    if(!npcHasActive('second_wind'))return null;
    npcUseActive('second_wind');
    var vals=[],mats=[];
    for(var i=0;i<3;i++){var m=(G.matchOppDice&&G.matchOppDice[i])||'bone';mats.push(m);vals.push(rollFace(m));}
    var r=_scoreRollBest(vals,G.oCards,0,{crowsLuck:false,crowsLuckRemaining:0},mats);
    return {kind:'bank',pts:(r&&r.total)||0,cid:'second_wind',
      msg:G.rung.name+' — SECOND WIND! ROLLING 3 DICE',
      label:G.rung.name+' SECOND WIND!'};
  }}
];
function npcHasActive(cid){""",
    'the bust-save table')

# ── 2. the inline chain becomes one consumer ──
sub("""      /* Final bust-out: NPC aegis save, the player's on-bust card payouts,""",
    """      /* P768: sentinel comment anchor (consumer inserted above) */
      /* Final bust-out: NPC aegis save, the player's on-bust card payouts,""",
    'anchor sentinel')

# locate the whole inline chain: from the bust-immunity comment to _oppBustOut()
START = "      /* NPC bust immunity (hold_the_line, sundays_rest, one_more_round) */"
END = "        _oppBustOut();return;\n      }"
i = s.find(START)
j = s.find(END)
if j < 0:
    END = END.replace('\n', '\r\n')
    j = s.find(END)
if i < 0 or j < 0 or j <= i:
    sys.exit('chain markers not found (nothing written)')
j2 = j + len(END)
CHAIN = s[i:j2]
if 'second_wind' not in CHAIN or 'mabels_stitch' not in CHAIN or len(CHAIN) > 6000:
    sys.exit('chain slice looks wrong (nothing written)')
NEWCONS = """      /* P768: the mitigation chain is a TABLE now (NPC_BUST_SAVES,
         beside the rescue table) - one walk, first answer wins, same
         priority: survive/immune (card order) > bank-half > stitch >
         second wind > the real bust. The outcomes keep their exact
         plumbing: survive resumes the turn, bank rides the finOpp
         timer, and _oppBustOut stays the one true exit. */
      {
        var _bsCtx={oppBank:oppBank};
        var _bsOut=null;
        for(var _bsI=0;_bsI<NPC_BUST_SAVES.length&&!_bsOut;_bsI++){
          try{_bsOut=NPC_BUST_SAVES[_bsI].try(_bsCtx);}catch(e){_bsOut=null;}
        }
        oppBank=_bsCtx.oppBank;/* bust_survive halves what survives */
        if(_bsOut&&_bsOut.kind==='survive'){
          setStatusMsg(G.rung.name+' SURVIVES BUST!','red');
          if(_bsOut.cid){var _bsCid=_bsOut.cid;triggerCard(_bsCid,getNpcCard(_bsCid).name+'!',false);
            setTimeout(function(){if(window.DLG)DLG.triggerCard(_bsCid,false);},_oppDelay(700));}
          setTimeout(function(){_oResumeAfterBustSave();/* P524 */},_oppDelay(900));return;
        }
        if(_bsOut&&_bsOut.kind==='bank'){
          if(_bsOut.msg)setStatusMsg(_bsOut.msg,'red');
          if(_bsOut.label)triggerCard(_bsOut.cid,_bsOut.label,false);
          var _bsPts=_bsOut.pts;
          setTimeout(function(){clearRow('oppDiceRow');finOpp(_bsPts);},_oppDelay(900));
          return;
        }
        _oppBustOut();return;
      }"""
s = s[:i] + NEWCONS + s[j2:]
edits.append('one consumer for the chain')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
