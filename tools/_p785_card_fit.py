# -*- coding: utf-8 -*-
"""P785: the dice recipe, fitted to the card - no lean, art-edge hull,
breathed core.

Denis (2026-08-19): "glow is too tall and too flat. It needs to be
brighter at the center and gradually go a bit brighter. The bright
core layer needs a bit of blur and there is still a dark gap between
it and the card, is it card thickness? If so remove it."

Four notes, four mechanisms - the recipe stays the dice's, these are
caller dials in the painter's existing grammar (like soft/rim/strength
have been since P753):

  TOO TALL   the dice lean (G.sy 1.24) is proportional to the subject:
             +-5px on a die, +-15px on a card. sx/sy join the opts
             dials; the card passes 1/1, the dice pass nothing.
  DARK GAP   not card thickness - the webp's ~1.7%-per-side
             transparent margin. The hull was built on the ELEMENT box
             so the line and the punch sat ~1.5px outside the visible
             art edge, exposing a ring of erased halo (dark wood).
             CG.trim shrinks the hull to the art's true edge.
  CORE BLUR  the 3.2px line was stroked crisp; opts.lineBlur routes it
             through the same mip blur (2px, two passes so it stays
             hot). Dice keep the crisp stroke.
  BRIGHTER AT THE CENTER, GRADUAL OUT
             the blurred double-pass core stacks over soft+rim right
             at the card's edge and hands off into the falloff.

(soft is NOT raised: at dpr3 the mip cap pins the radius at ~10.7 user
px for anything past r~10, so a bigger number would change desktop and
not the phone - the DPR-quantization note in AUDIT_BACKLOG.)
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


# ── 1. sx/sy join the caller dials ──
sub("""    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:G.sx,sy:G.sy});});
    blurOnto(gx,SOFTR,G.softPasses||1);""",
    """    /* P785: sx/sy are caller dials like soft/rim/strength - the lean
       is proportional to the subject, and 1.24 on a card-tall shape is
       Denis's 'too tall'. Dice pass nothing and keep G's lean. */
    var SX=(opts&&opts.sx!==undefined)?opts.sx:G.sx;
    var SY=(opts&&opts.sy!==undefined)?opts.sy:G.sy;
    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:SX,sy:SY});});
    blurOnto(gx,SOFTR,G.softPasses||1);""",
    'the lean is a caller dial')

# ── 2. the line can take a breath of blur ──
sub("""    if(LINE>0){
      gx.strokeStyle=COL;gx.lineWidth=LINE;gx.lineJoin='round';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp)return;
        trace(gx,sh&&sh.hull||sh,0);gx.stroke();
      });
    }""",
    """    if(LINE>0){
      if(opts&&opts.lineBlur){
        /* P785: the hot core takes a breath of blur (Denis) - the same
           line, stroked into the scratch and mip-softened instead of
           drawn crisp. Two passes keep it hot through the blur. */
        sxc.setTransform(dpr,0,0,dpr,0,0);
        sxc.globalCompositeOperation='source-over';
        sxc.clearRect(0,0,sc.width,sc.height);
        sxc.strokeStyle=COL;sxc.lineWidth=LINE;sxc.lineJoin='round';
        sel.forEach(function(sh){
          if(sh&&sh.stamp)return;
          trace(sxc,sh&&sh.hull||sh,0);sxc.stroke();
        });
        blurOnto(gx,opts.lineBlur,2);
      }else{
      gx.strokeStyle=COL;gx.lineWidth=LINE;gx.lineJoin='round';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp)return;
        trace(gx,sh&&sh.hull||sh,0);gx.stroke();
      });
      }
    }""",
    'the core can blur')

# ── 3. the hull sits on the ART's edge; the card passes its dials ──
sub("""      var w=e.el.offsetWidth*scl*self.GLOW.grow,h=e.el.offsetHeight*scl*self.GLOW.grow;
      var ccx=r.left-sc.left+r.width/2,ccy=r.top-sc.top+r.height/2;
      var hull=self._rectHull(ccx-w/2,ccy-h/2,w,h,Math.min(w,h)*CG.round);""",
    """      /* P785: trim to the ART's edge - the webp carries a ~1.7%
         transparent margin per side, and a hull on the element box put
         the line and the punch outside the visible card, exposing a
         dark ring of erased halo (Denis: 'is it card thickness?'). */
      var w=e.el.offsetWidth*scl*self.GLOW.grow*(CG.trim||1),
          h=e.el.offsetHeight*scl*self.GLOW.grow*(CG.trim||1);
      var ccx=r.left-sc.left+r.width/2,ccy=r.top-sc.top+r.height/2;
      var hull=self._rectHull(ccx-w/2,ccy-h/2,w,h,Math.min(w,h)*CG.round);""",
    'the hull sits on the art edge')

sub("""      self._paintHalo(cv,x,sc,dpr,[hull],e.col||self.SEL_COL,e.col||self.SEL_SOFT,
        CG.floor+(1-CG.floor)*Math.min(1,e.k));""",
    """      self._paintHalo(cv,x,sc,dpr,[hull],e.col||self.SEL_COL,e.col||self.SEL_SOFT,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),undefined,
        {sx:1,sy:1,lineBlur:CG.lineBlur});/* P785: no lean, breathed core */""",
    'the card passes its dials')

# ── 4. the card's geometry dials ──
sub("""  CARD_GLOW:{round:0.075, floor:0.42},""",
    """  CARD_GLOW:{round:0.075, floor:0.42, trim:0.967, lineBlur:2},""",
    'trim + lineBlur dials')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
