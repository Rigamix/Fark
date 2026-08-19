# -*- coding: utf-8 -*-
"""P777: the card halo gets its punch back - cut INWARD, under the card.

Denis (2026-08-19): "Glow around cards still looks really bad on phone.
Around dice looks ok." Measured before reasoning (430x900 @dpr3, drag
glow at full arm): the halo is 232/255 alpha AT the card edge, dead 9px
out on the sides and 21px on top. That is not a glow, it is an orange
sticker - and the asymmetry is a leak.

Two causes, both structural, neither a dial:

1. P756 REMOVED THE PUNCH-OUT ENTIRELY. The dice look right because
   destination-out cuts the subject back out and only the blur's OUTER
   tail survives (~50% alpha at the edge, falling over `soft`). P753's
   card dials were authored WITH that grammar. P756 hit the punch's
   1px dark seam (the cut widens by G.clear - right for the dice's
   over-the-table canvas, wrong for the card's under-the-card canvas)
   and fled to noPunch - which silently changed the authored look into
   the blurred SOLID: everything inside the grown silhouette stays
   ~91% alpha and only the outer ~5px ever fades.
   The fix is punchUnder: cut the card's UN-GROWN silhouette a hair
   INSIDE its edge (punchScaleMul unwinds CG.grow, G.clear shrinks
   further). The halo tucks under the card body - a seam is impossible
   by construction - the 5% grow ring survives as the crisp rim core,
   and the tails read as light, same grammar as the dice.

2. THE DICE'S STRETCH LEAKED. The soft pass hardcoded sx:G.sx,sy:G.sy
   (1.14/1.24, the dice lean) for every shape - P753's own comment
   says the card halo "tunes independently... without borrowing
   dials", and dyF (the card's DELIBERATE vertical bias) is authored
   at 0. On a 124px card the borrowed 1.24 is a 15px top/bottom smear
   - the measured 21px-vs-9px lopsidedness. opts.sx/sy now override;
   the dice pass nothing and keep G.sx/G.sy exactly.

Denis's CARD_GLOW dials (col, soft 6, rim 2.5, strength .91, grow
1.05, floor .42) are untouched - the lab still owns the look.
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


# ── 1. the soft pass stops borrowing the dice's stretch ──
sub("""    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:G.sx,sy:G.sy});});""",
    """    /* P777: opts-aware stretch - the dice keep G.sx/G.sy, the cards
       pass 1/1. The borrowed 1.24 was a 15px top/bottom smear on a
       card (dyF, the card's own vertical dial, is authored at 0). */
    var SX=(opts&&opts.sx!==undefined)?opts.sx:G.sx;
    var SY=(opts&&opts.sy!==undefined)?opts.sy:G.sy;
    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:SX,sy:SY});});""",
    'stretch stops leaking')

# ── 2. punchUnder: the inward cut for an under-the-subject canvas ──
sub("""    if(!(opts&&opts.noPunch)){
      gx.globalCompositeOperation='destination-out';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp){
          lay(gx,sh,null,{scaleMul:1+(2*G.clear)/Math.max(8,Math.min(sh.stamp.w,sh.stamp.h))});
        }else{
          lay(gx,sh,null,{shrink:-G.clear});
        }
      });
      gx.globalCompositeOperation='source-over';
    }""",
    """    /* P777: punchUnder cuts INWARD - for a canvas that sits UNDER its
       subject. The dice's cut widens by G.clear (their canvas is over
       the table, a wash on the die is the failure); widening under a
       card is P756's manufactured seam. Here the cut shrinks instead:
       punchScaleMul unwinds the stamp's baked-in grow back to the
       subject's true edge, G.clear tucks it a hair further in, and the
       card body covers the join. What survives is the grow ring (the
       crisp rim core) plus the blur tails - the dice's grammar. */
    if(opts&&opts.punchUnder){
      gx.globalCompositeOperation='destination-out';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp){
          lay(gx,sh,null,{scaleMul:(opts.punchScaleMul||1)
            *(1-(2*G.clear)/Math.max(8,Math.min(sh.stamp.w,sh.stamp.h)))});
        }else{
          lay(gx,sh,null,{shrink:G.clear});
        }
      });
      gx.globalCompositeOperation='source-over';
    }else if(!(opts&&opts.noPunch)){
      gx.globalCompositeOperation='destination-out';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp){
          lay(gx,sh,null,{scaleMul:1+(2*G.clear)/Math.max(8,Math.min(sh.stamp.w,sh.stamp.h))});
        }else{
          lay(gx,sh,null,{shrink:-G.clear});
        }
      });
      gx.globalCompositeOperation='source-over';
    }""",
    'the inward punch')

# ── 3. the card glow uses it ──
sub("""      self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line,
        {soft:CG.soft,rim:CG.rim,strength:CG.strength,dy:r.height*(CG.dyF||0),
         noPunch:true});/* P756: the card body covers the middle */""",
    """      self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line,
        {soft:CG.soft,rim:CG.rim,strength:CG.strength,dy:r.height*(CG.dyF||0),
         sx:1,sy:1,/* P777: the card does not lean like a die */
         punchUnder:true,punchScaleMul:1/(CG.grow||1)});/* P777: tail-only, tucked under the card */""",
    'cards punch under')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
