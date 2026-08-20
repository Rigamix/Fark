# -*- coding: utf-8 -*-
"""P835: committed dice are NOT reorderable (Denis's §6 ruling; the
seat-wins half already shipped as P520/D19).

The vagabond drag's census (_vgRowInfo) filtered only match/phys/
connected - committed dice entered the order, were lerped aside, and
_commitVagabondDrag permuted their pool entries, lanes, matchDice/
_enchArr rows and DOM wraps like any free die. That moved Finnick's
Palm adjacency mid-turn and let a committed die park at an end to aim
vanguard_f. Ruled a bug on either §6 answer.

The fix treats committed (and frozen) dice EXACTLY like the destroyed-
dice holes the commit already handles: they keep their seat, their
pool position and their home; the free dice permute among the free
homes around them.
 - census: committed/frozen chips excluded (state-true via the pool
   entry, not a class read);
 - pool rewrite: the guard compared poolSeq against the WHOLE pool -
   with an excluded set that always failed. The free entries now
   re-fill the free positions in their new order, committed entries
   stay at their indices;
 - DOM: wraps re-append in the NEW pool order (committed included, in
   place), not seq order - appending only the free wraps would shove
   them all behind the committed ones.
Also fixes the broken coin-flip drag canceller: it nulled the state
using field names the state never had (clone/srcEl), leaving the
carried die lifted (phys.y never restored) and the origin class on.
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


# 1) the census excludes committed/frozen (state-true, via the pool entry)
sub("""function _vgRowInfo(){
  if(!window.D3X||!D3X.dice)return null;
  var mine=D3X.dice.filter(function(d){return d.match&&d.phys&&d.chip&&d.chip.isConnected;});
  if(mine.length<2)return null;""",
    """function _vgRowInfo(){
  if(!window.D3X||!D3X.dice)return null;
  var mine=D3X.dice.filter(function(d){return d.match&&d.phys&&d.chip&&d.chip.isConnected;});
  /* P835 (Denis, §6): COMMITTED DICE ARE NOT REORDERABLE. They held a
     place in the census, so a drag lerped them aside and the commit
     permuted their seats - moving Finnick's Palm adjacency mid-turn and
     letting a scored die park at an end to aim vanguard_f. They now sit
     out like the destroyed-dice holes: seat, pool position and home all
     stay. State-true read via the pool entry, not a class. */
  try{
    if(typeof G!=='undefined'&&G&&G.pool){
      mine=mine.filter(function(d){
        var pd=null;
        for(var i=0;i<G.pool.length;i++)if(G.pool[i].el===d.chip){pd=G.pool[i];break;}
        return !(pd&&(pd.committed||pd._frozen));
      });
    }
  }catch(e){}
  if(mine.length<2)return null;""",
    'census excludes committed')

# 2) the pool rewrite: free entries re-fill free positions
sub("""      var poolSeq=seq.map(function(d){
        for(var i=0;i<G.pool.length;i++)if(G.pool[i].el===d.chip)return G.pool[i];
        return null;
      }).filter(Boolean);
      if(poolSeq.length===G.pool.length){
        G.pool=poolSeq;""",
    """      var poolSeq=seq.map(function(d){
        for(var i=0;i<G.pool.length;i++)if(G.pool[i].el===d.chip)return G.pool[i];
        return null;
      }).filter(Boolean);
      /* P835: the census excludes committed dice, so poolSeq covers the
         FREE entries only - the old whole-pool guard would always fail.
         The free entries re-fill the free positions in their new order;
         committed entries keep their indices (their seats never enter
         _slots below, so their lane/mat/ench are untouched - the same
         leave-the-hole shape the seat loop already uses). */
      var _freeCount=G.pool.filter(function(p){return !(p.committed||p._frozen);}).length;
      if(poolSeq.length===_freeCount&&poolSeq.length===seq.length){
        var _pk=0;
        G.pool=G.pool.map(function(p){return (p.committed||p._frozen)?p:poolSeq[_pk++];});""",
    'free entries re-fill free positions')

# 3) the DOM re-appends in the NEW pool order
sub("""    var row=document.getElementById('playerDiceRow');
    if(row){
      seq.forEach(function(d){
        var w=d.chip.closest?d.chip.closest('.die-wrap'):null;
        if(w&&w.parentNode===row)row.appendChild(w);
      });
    }""",
    """    var row=document.getElementById('playerDiceRow');
    if(row&&typeof G!=='undefined'&&G&&G.pool){
      /* P835: re-append in the NEW POOL order - committed wraps included,
         in place. Appending only the free wraps shoved them all behind
         the committed ones and broke DOM-order == pool-order. */
      G.pool.forEach(function(p){
        var w=(p.el&&p.el.closest)?p.el.closest('.die-wrap'):null;
        if(w&&w.parentNode===row)row.appendChild(w);
      });
    }""",
    'DOM follows the pool order')

# 4) the coin-flip canceller uses the real state shape
sub_done = False
_cf_old = """  if(window._vgDragState){
    try{
      if(_vgDragState.clone)_vgDragState.clone.remove();
      if(_vgDragState.srcEl)_vgDragState.srcEl.classList.remove('vg-drag-origin');
    }catch(e){}
    window._vgDragState=null;
  }"""
if s.count(_cf_old) == 1:
    sub(_cf_old,
        """  if(window._vgDragState){
    /* P835: the old canceller nulled the state through field names it
       never had (clone/srcEl) - the carried die stayed lifted and the
       origin class stuck. Cancel with the real shape. */
    try{
      var _st=window._vgDragState;
      if(_st.raf)cancelAnimationFrame(_st.raf);
      if(_st.onMove){document.removeEventListener('pointermove',_st.onMove,{passive:false});
        document.removeEventListener('touchmove',_st.onMove,{passive:false});}
      if(_st.die)_st.die.classList.remove('vg-drag-origin');
      if(_st.me&&_st.y0!==undefined)_st.me.phys.y=_st.y0;
      if(_st.order&&_st.homes)_st.order.forEach(function(d,i){d.phys.x=_st.homes[i];});
    }catch(e){}
    window._vgDragState=null;
  }""",
        'the canceller uses the real shape')
else:
    print('NOTE: coin-flip canceller anchor not found as guessed - skipped, verify separately')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
