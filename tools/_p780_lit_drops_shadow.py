# -*- coding: utf-8 -*-
"""P780: a lit card drops its dark contact shadows.

Denis (2026-08-19, second crop): "you can see a hole in the alpha."

The hole is not in the halo - it is the RESTING card's two dark
drop-shadows (the .fcv base filter) compositing OVER the glow canvas
below. P757 removed exactly this from the DRAG state ("the dark ring
Denis circled") and P757's armed note did the same for .armed - both
those states declare their own filter, which REPLACES the shadow pair.
But a glow can be on while the card is AT REST (the ramp's first
frames, FKFX's play flash, any future caller), and there the base
filter still paints its dark fringe over the light.

One writer: D3X.cardGlow already knows every element that has light
under it - it now marks them .fcv-lit, and the CSS swaps the resting
shadows for a small brightness lift while lit. The class reconciles on
every glow add/remove (two elements at most), and a famRenderRow
rebuild re-applies it through the same call that re-keys the glow.

Also: the wide spill octave reaches 24 (from 20) - with the dark ring
gone the pool of light on the table is what sells 'magical'.
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


# ── 1. the CSS: lit replaces the shadow pair (spent still wins - its
#      rule sits later with equal specificity) ──
sub("""#famRowP .fcv{width:20cqw;cursor:pointer;transition:transform .18s ease,filter .18s ease;
  filter:drop-shadow(0 0.25cqw 0.3cqw rgba(10,6,2,.5)) drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.45))}""",
    """#famRowP .fcv{width:20cqw;cursor:pointer;transition:transform .18s ease,filter .18s ease;
  filter:drop-shadow(0 0.25cqw 0.3cqw rgba(10,6,2,.5)) drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.45))}
/* P780: a LIT card (D3X.cardGlow holds an entry for it) drops the dark
   contact shadows - they painted OVER the halo canvas below, the 'hole
   in the alpha' Denis photographed. The glow is the card's grounding
   while it lasts. Same replace-the-filter move as .fcv-drag and
   .armed; spent stays later in the sheet and still wins. */
#famRowP .fcv.fcv-lit{filter:brightness(1.05)}""",
    'lit CSS')

# ── 2. the painter marks its subjects ──
sub("""  cardGlow:function(key,el,k,col){
    this._cardGlows=this._cardGlows||{};
    if(!el||!(k>0))delete this._cardGlows[key];
    else this._cardGlows[key]={el:el,k:k,col:col||null};
    this._drawCardGlows();
  },""",
    """  cardGlow:function(key,el,k,col){
    this._cardGlows=this._cardGlows||{};
    if(!el||!(k>0))delete this._cardGlows[key];
    else this._cardGlows[key]={el:el,k:k,col:col||null};
    /* P780: whoever holds a glow entry is LIT - the class swaps the
       card's dark contact shadows out from over the halo. Reconciled
       here so every caller and every removal path agrees. */
    var _lits=[],_self=this;
    Object.keys(this._cardGlows).forEach(function(kk){
      var e=_self._cardGlows[kk];
      if(e.el&&e.el.isConnected)_lits.push(e.el);
    });
    (this._litEls||[]).forEach(function(le){
      if(_lits.indexOf(le)<0){try{le.classList.remove('fcv-lit');}catch(e){}}
    });
    _lits.forEach(function(le){try{le.classList.add('fcv-lit');}catch(e){}});
    this._litEls=_lits;
    this._drawCardGlows();
  },""",
    'the painter marks lit cards')

# ── 3. the pool of light on the table widens ──
sub("""    octaves:[{r:3,col:'#fff7dc',passes:2},{r:8,col:'#ffd24a'},{r:20,col:'#ff9e30',deep:true}]},""",
    """    octaves:[{r:3,col:'#fff7dc',passes:2},{r:8,col:'#ffd24a'},{r:24,col:'#ff9e30',deep:true}]},""",
    'wider spill')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
