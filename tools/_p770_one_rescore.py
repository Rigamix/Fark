# -*- coding: utf-8 -*-
"""P770: one rescore, five callers; corvus_ledger joins the arm table.

Every effect that mutates the rival's dice mid-roll (encore's reroll,
the rescue table, quick hands, grog's bump, slippery table) ended with
the same tail, copied five times: rebuild vals/mats/enchs from the
unkept dice, _scoreRollBest, then the persona re-picks through
_oppChooseFrom and `used` is remapped. Five copies of one seam is the
drift this whole program deletes - _oppRescore() is the one copy,
declared inside step() (hoisted, reads oppBank/crowsCtx at call time).

corvus_ledger's inline active in finOpp becomes a 'bank'-moment entry of
NPC_ARMS (P769's table), ctx carrying pts in and out. The mechanic-
driven bank riders were already tabled by P470 (_oppFxOwnA/B + BANK_FX)
- cluster 3's remaining piece was just these two.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    """P770 lesson: patched regions can MIX per-line endings (original
    CRLF, inserted LF), so whole-block LF/CRLF variants both miss.
    Match each newline as \\r?\\n instead; replacement keeps LF."""
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    import re
    # re.escape escapes the newline char itself (backslash+newline) -
    # normalise that back to a raw newline before widening it to \r?\n
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# ── 1. the one rescore, declared inside step() (hoisted) ──
sub("""  function step(){
    if(G!==_matchG||!G||G._endMatchFired)return;/* ghost-timer guard */""",
    """  function step(){
    if(G!==_matchG||!G||G._endMatchFired)return;/* ghost-timer guard */
    /* P770: THE ONE RESCORE. Every mid-roll dice mutation (encore, the
       rescue table, quick hands, grog's bump, slippery table) needs the
       same tail: rescore the unkept dice through the real scorer, then
       let the persona re-pick. This was copied five times; hoisted here
       it reads oppBank and crowsCtx at call time. */
    function _oppRescore(){
      var _f=G.oppDice.filter(function(d){return !d.kept;});
      var _r=_scoreRollBest(
        _f.map(function(d){return d.val;}),G.oCards,oppBank,crowsCtx,
        _f.map(function(d){return d.mat;}),
        _f.map(function(d){return d.ench||null;}));
      var _t=_r.total,_u=_r.used;
      var _p=_oppChooseFrom(_f,_t,oppBank);
      if(_p){_t=_p.pts;_u=_f.map(function(d){return _p.sel.indexOf(d)>=0;});}
      return {total:_t,used:_u};
    }""",
    'the one rescore')

# ── 2. the five tails become calls ──
sub("""        var _encFree=G.oppDice.filter(function(d){return !d.kept;});
        if(_oEnc){
          var _encV=_encFree.map(function(d){return d.val;}),_encM=_encFree.map(function(d){return d.mat;});
          var _encE=_encFree.map(function(d){return d.ench||null;});/* P762 */
          var _encRs=_scoreRollBest(_encV,G.oCards,oppBank,crowsCtx,_encM,_encE);
          total=_encRs.total;used=_encRs.used;
          /* P494: the persona chooses. Fog only clouds the FIRST reckoning of a
             turn, so here the rival sees every free seat. */
          var _pk_encRs=G.oppDice.filter(function(d){return !d.kept;});
          var _pc_encRs=_oppChooseFrom(_pk_encRs,total,oppBank);
          if(_pc_encRs){total=_pc_encRs.pts;used=_pk_encRs.map(function(d){return _pc_encRs.sel.indexOf(d)>=0;});}
          try{famRenderRow();}catch(e){}
        }""",
    """        if(_oEnc){
          var _rrE=_oppRescore();total=_rrE.total;used=_rrE.used;/* P770 */
          try{famRenderRow();}catch(e){}
        }""",
    'encore tail')

sub("""          if(_rescued){
            npcUseActive(_rescueCid);
            triggerCard(_rescueCid,_rescueLabel,false);
            setStatusMsg(G.rung.name+': '+_rescueLabel,'gold');
            /* Rescore with mutated dice */
            var _resFV=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.val;});
            var _resFM=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.mat;});
            var _resFE=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.ench||null;});/* P762 */
            var _resR=_scoreRollBest(_resFV,G.oCards,oppBank,crowsCtx,_resFM,_resFE);
            total=_resR.total;used=_resR.used;
          /* P494: the persona chooses. Fog only clouds the FIRST reckoning of a
             turn, so here the rival sees every free seat. */
          var _pk_resR=G.oppDice.filter(function(d){return !d.kept;});
          var _pc_resR=_oppChooseFrom(_pk_resR,total,oppBank);
          if(_pc_resR){total=_pc_resR.pts;used=_pk_resR.map(function(d){return _pc_resR.sel.indexOf(d)>=0;});}
          }""",
    """          if(_rescued){
            npcUseActive(_rescueCid);
            triggerCard(_rescueCid,_rescueLabel,false);
            setStatusMsg(G.rung.name+': '+_rescueLabel,'gold');
            var _rrR=_oppRescore();total=_rrR.total;used=_rrR.used;/* P770 */
          }""",
    'rescue tail')

sub("""          /* Recompute scoring after swap */
          var _qhFV=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.val;});
          var _qhFM=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.mat;});
          var _qhFE=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.ench||null;});/* P761 */
          var _qhR=_scoreRollBest(_qhFV,G.oCards,oppBank,crowsCtx,_qhFM,_qhFE);
          total=_qhR.total;used=_qhR.used;
          /* P494: the persona chooses. Fog only clouds the FIRST reckoning of a
             turn, so here the rival sees every free seat. */
          var _pk_qhR=G.oppDice.filter(function(d){return !d.kept;});
          var _pc_qhR=_oppChooseFrom(_pk_qhR,total,oppBank);
          if(_pc_qhR){total=_pc_qhR.pts;used=_pk_qhR.map(function(d){return _pc_qhR.sel.indexOf(d)>=0;});}""",
    """          var _rrQ=_oppRescore();total=_rrQ.total;used=_rrQ.used;/* P770 */""",
    'quick hands tail')

sub("""          var _gbFV=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.val;});
          var _gbFM=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.mat;});
          var _gbFE=G.oppDice.filter(function(d){return !d.kept;}).map(function(d){return d.ench||null;});/* P761 */
          var _gbR=_scoreRollBest(_gbFV,G.oCards,oppBank,crowsCtx,_gbFM,_gbFE);
          total=_gbR.total;used=_gbR.used;
          /* P494: the persona chooses. Fog only clouds the FIRST reckoning of a
             turn, so here the rival sees every free seat. */
          var _pk_gbR=G.oppDice.filter(function(d){return !d.kept;});
          var _pc_gbR=_oppChooseFrom(_pk_gbR,total,oppBank);
          if(_pc_gbR){total=_pc_gbR.pts;used=_pk_gbR.map(function(d){return _pc_gbR.sel.indexOf(d)>=0;});}""",
    """          var _rrG=_oppRescore();total=_rrG.total;used=_rrG.used;/* P770 */""",
    'grogs bump tail')

sub("""          var _stFV=G.oppDice.map(function(d){return d.val;});
          var _stFM=G.oppDice.map(function(d){return d.mat;});
          var _stFE=G.oppDice.map(function(d){return d.ench||null;});/* P761 */
          var _stR=_scoreRollBest(_stFV,G.oCards,oppBank,crowsCtx,_stFM,_stFE);
          total=_stR.total;used=_stR.used;
          /* P494: the persona chooses. Fog only clouds the FIRST reckoning of a
             turn, so here the rival sees every free seat. */
          var _pk_stR=G.oppDice.filter(function(d){return !d.kept;});
          var _pc_stR=_oppChooseFrom(_pk_stR,total,oppBank);
          if(_pc_stR){total=_pc_stR.pts;used=_pk_stR.map(function(d){return _pc_stR.sel.indexOf(d)>=0;});}
          /* Re-keep based on new scoring */
          G.oppDice.forEach(function(d,i){if(_stR.used[i]){d.kept=true;if(d.el){d.el.classList.add('selected','oppkeep');if(d.el._d3)D3.draw(d.el._d3);}}});""",
    """          /* P770: the slip un-kept everything above, so the unkept set IS
             the full roll - the one rescore covers it */
          var _rrS=_oppRescore();total=_rrS.total;used=_rrS.used;
          /* Re-keep based on new scoring */
          G.oppDice.forEach(function(d,i){if(used[i]){d.kept=true;if(d.el){d.el.classList.add('selected','oppkeep');if(d.el._d3)D3.draw(d.el._d3);}}});""",
    'slippery tail')

# ── 3. corvus_ledger joins the arm table at the bank moment ──
sub("""      /* NPC Corvus's Ledger: activate for +75% on large banks */
      if(npcHasActive('corvus_ledger')&&pts>=400){
        npcUseActive('corvus_ledger');
        var _npcLedgerBonus=Math.floor(pts*0.75);pts+=_npcLedgerBonus;
        triggerCard('corvus_ledger','+'+_npcLedgerBonus+' LEDGER',false);
        setStatusMsg(G.rung.name+": CORVUS'S LEDGER +"+_npcLedgerBonus,'red');
      }""",
    """      /* P770: corvus_ledger arms through NPC_ARMS' bank moment */
      pts=_npcRunArms('bank',{pts:pts}).pts;""",
    'corvus consumer')

sub("""  {id:'twinning_charm',moment:'roll',try:function(ctx){""",
    """  {id:'corvus_ledger',moment:'bank',try:function(ctx){
    if(!(ctx.pts>=400))return;
    npcUseActive('corvus_ledger');
    var _b=Math.floor(ctx.pts*0.75);ctx.pts+=_b;
    triggerCard('corvus_ledger','+'+_b+' LEDGER',false);
    setStatusMsg(G.rung.name+": CORVUS'S LEDGER +"+_b,'red');}},
  {id:'twinning_charm',moment:'roll',try:function(ctx){""",
    'corvus entry')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
