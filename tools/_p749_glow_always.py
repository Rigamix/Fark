# -*- coding: utf-8 -*-
"""P749: the halo shows on EVERY drag, and the painter stops editing GLOW.

Denis, fifth report: "no glow."

THE CASE HE IS IN IS THE CASE I SUPPRESSED. P748 registered the halo as
`cardGlow('drag', why ? null : el, k)` - a card that cannot be played got
no glow at all, by design. And in the same breath he describes the grey
ramp, which ONLY happens when the card cannot be played. So the gesture
he keeps testing is precisely the one branch that draws nothing. Four
reports of "no glow" and my answer each time measured the other branch.

A drag now ALWAYS lights. The colour carries the verdict instead of the
presence: gold when the card will fire, the refusal red when it will not
(the same OPP_INK red the rival's keep and the reason line already use).
That is better feedback than absence anyway - absence is indistinguishable
from a broken effect, which is exactly the position this has been in.

AND THE PAINTER STOPS MUTATING SHARED STATE. _drawCardGlows was setting
D3X.GLOW.line to the card's value, painting, and restoring it in a
finally. GLOW is the DICE's dial object, read by the lab and by the
selection glow; borrowing it per-frame to render a different subject is
the shared-gate trap - one re-entrant call, one thrown error in the wrong
place, and the dice keep a value that was never theirs. `line` is a
parameter of _paintHalo now, so nothing is borrowed.
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


# 1) line becomes a parameter - nothing borrows the dice's dials
sub(u"  _paintHalo:function(cv,x,sc,dpr,sel,COL,SOFT,alphaMul){\n"
    u"    var self=this,G=this.GLOW;",
    u"  _paintHalo:function(cv,x,sc,dpr,sel,COL,SOFT,alphaMul,lineW){\n"
    u"    var self=this,G=this.GLOW;\n"
    u"    /* P749: the rim width is the CALLER's, never GLOW's. The card\n"
    u"       painter used to assign G.line and put it back afterwards -\n"
    u"       borrowing the dice's own dial object to draw something that is\n"
    u"       not a die, which is one re-entrant call away from leaving the\n"
    u"       selection glow with a width nobody chose. */\n"
    u"    var LINE=(lineW===undefined)?G.line:lineW;",
    'line is a parameter')

sub(u"""    gx.strokeStyle=COL;gx.lineWidth=G.line;gx.lineJoin='round';""",
    u"""    gx.strokeStyle=COL;gx.lineWidth=LINE;gx.lineJoin='round';""",
    'painter uses LINE')

sub(u"""    var self=this,CG=this.CARD_GLOW;
    /* the rim line would trace the bounding box rather than the card's
       own angle, so it is off for cards - the halo carries it */
    var G=this.GLOW,keepLine=G.line;G.line=CG.line;
    try{
      Object.keys(this._cardGlows).forEach(function(kk){
        var e=self._cardGlows[kk];
        if(!e.el||!e.el.isConnected){delete self._cardGlows[kk];return;}
        var r=e.el.getBoundingClientRect();
        if(r.width<4)return;
        var hull=self._rectHull(r.left-sc.left,r.top-sc.top,r.width,r.height,
          Math.min(r.width,r.height)*CG.round);
        self._paintHalo(cv,x,sc,dpr,[hull],e.col||CG.col,e.col||CG.soft,
          CG.floor+(1-CG.floor)*Math.min(1,e.k));
      });
    }finally{G.line=keepLine;}""",
    u"""    var self=this,CG=this.CARD_GLOW;
    Object.keys(this._cardGlows).forEach(function(kk){
      var e=self._cardGlows[kk];
      if(!e.el||!e.el.isConnected){delete self._cardGlows[kk];return;}
      var r=e.el.getBoundingClientRect();
      if(r.width<4)return;
      var hull=self._rectHull(r.left-sc.left,r.top-sc.top,r.width,r.height,
        Math.min(r.width,r.height)*CG.round);
      /* P749: the card's own rim width goes in as an argument - the rim
         would trace the bounding box rather than the card's angle, so it
         stays off, and GLOW is left alone. */
      self._paintHalo(cv,x,sc,dpr,[hull],e.col||CG.col,e.col||CG.soft,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line);
    });""",
    'card painter borrows nothing')

# 2) EVERY drag lights; the colour is the verdict
sub(u"""    try{if(window.D3X&&D3X.cardGlow)D3X.cardGlow('drag',_famDrag.why?null:el,_k);}catch(e){}""",
    u"""    /* P749: IT ALWAYS LIGHTS. This passed null for a card that cannot
       be played, so the one gesture Denis kept testing - the one that
       greys, which is by definition the unplayable one - drew nothing at
       all, and "no glow" was the correct outcome of a bad decision. The
       halo is now the drag's own feedback and its COLOUR is the verdict:
       gold if releasing fires the card, the refusal red if it will not. */
    try{if(window.D3X&&D3X.cardGlow)
      D3X.cardGlow('drag',el,_k,_famDrag.why?(window.OPP_INK||'#d94c3d'):null);}catch(e){}""",
    'every drag lights')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
