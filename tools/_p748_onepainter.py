# -*- coding: utf-8 -*-
"""P748: ONE glow painter. The dice had it; the cards were faking it.

Denis, fourth report: "I don't see any glow, instead the card scales up.
No glow layer, nothing."

ROOT. A card's glow was a CSS `filter: drop-shadow()` on the card itself.
`#famRowP` carries `perspective(900px) rotateX(-9deg)`, so every card in
hand lives inside a 3D-transformed, composited context - and WebKit clips
such an element's filter to the element's own box. saturate() and
brightness() are per-pixel and in-bounds, so the grey ramp survives; a
drop-shadow has to paint OUTSIDE the box, so it is clipped away entirely.
That is exactly the three symptoms: the card scales, it greys, and no
glow ever appears. This file already knew the rule - line ~20453 says
"iOS WebKit ignores filters on a parent of 3D-transformed children" - and
the dice were moved off filters for it long ago. The cards never were.

So the card glow stops being a second, weaker mechanism and becomes a
caller of the one the dice use:

  _paintHalo   the halo builder, lifted VERBATIM out of _drawGlow - the
               blur pass, the iOS stroke-ring fallback, the punch-out and
               the rim line. _drawGlow now calls it with the dice hulls,
               so the dice glow is byte-identical to before.
  cardGlow     registers a shape to glow by key and paints the lot on a
               canvas ABOVE the hand row. Screen-space, so nothing can
               clip it, and it renders through the same fallback that
               makes the selection glow work on Denis's phone.

Two callers now: the drag (key 'drag', riding --arm) and the rival's
armed telegraph (key 'opp'), which was a gold drop-shadow in the SAME
3D row and therefore just as invisible - the parity Denis keeps asking
for, found by checking the other direction rather than by another report.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    """Collect, write ONCE at the end - an exit mid-way leaves earlier
    edits unwritten, which is how two patches this week did nothing."""
    global s
    c = s.count(old)
    if c != 1:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == 1:
            old, new = old2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
    s = s.replace(old, new)
    edits.append(label)


# ── 1. LIFT THE PAINTER OUT, VERBATIM ────────────────────────────────
START = "    /* build the halo on its own surface: blur the silhouettes, then PUNCH"
i = s.find(START)
if i < 0:
    sys.exit('painter start not found (nothing written)')
endmark = "    x.restore();"
j = s.find(endmark, i)
if j < 0:
    sys.exit('painter end not found (nothing written)')
j += len(endmark)
body = s[i:j]
if 'destination-out' not in body or 'fbCross' not in body:
    sys.exit('lifted block is not the painter (nothing written)')

# the one behavioural change inside the lifted body: the caller may dim it
body = body.replace("x.globalAlpha=G.strength;",
                    "x.globalAlpha=G.strength*(alphaMul===undefined?1:alphaMul);")
if 'alphaMul' not in body:
    sys.exit('strength hook missed (nothing written)')

CALL = ("    /* P748: the painter is shared with the cards now - see"
        " _paintHalo */\n"
        "    this._paintHalo(cv,x,sc,dpr,sel,COL,SOFT,1);")
s = s[:i] + CALL + s[j:]

PAINTER = (
    "  /* P748: THE ONE HALO PAINTER. Lifted verbatim out of _drawGlow so\n"
    "     the dice glow is unchanged - the blur pass, the iOS stroke-ring\n"
    "     fallback, the punch-out and the rim line all still live here and\n"
    "     nowhere else. `sel` is a list of screen-space hulls; a die hands\n"
    "     over its projected corners and a card hands over its rounded\n"
    "     rect, and neither knows anything about the other. */\n"
    "  _paintHalo:function(cv,x,sc,dpr,sel,COL,SOFT,alphaMul){\n"
    "    var self=this,G=this.GLOW;\n"
    + body + "\n"
    "  },\n"
    "  /* the canvas the CARD glow paints on. #dgCanvas sits at z-index 3,\n"
    "     under the dice and far under the hand - right for dice, useless\n"
    "     for a card at z 42. This one sits just under the dragged card\n"
    "     (9500) and above everything else it must not hide behind. */\n"
    "  _glowHiCv:function(){\n"
    "    var sc=document.getElementById('screen-match');\n"
    "    if(!sc)return null;\n"
    "    var cv=document.getElementById('dgCanvasHi');\n"
    "    if(!cv){\n"
    "      cv=document.createElement('canvas');cv.id='dgCanvasHi';\n"
    "      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'\n"
    "        +'pointer-events:none;z-index:9400';\n"
    "      sc.appendChild(cv);\n"
    "    }\n"
    "    return cv;\n"
    "  },\n"
    "  /* a card's silhouette as a hull the painter understands: a rounded\n"
    "     rect, corners sampled so the halo follows the card's shape rather\n"
    "     than a hard box. The row's few degrees of rotation are inside the\n"
    "     blur, so the bounding rect is close enough - and CARD_GLOW.line\n"
    "     keeps the crisp rim off, which is the part that would show it. */\n"
    "  _rectHull:function(L,T,W,H,rad){\n"
    "    var pts=[],r=Math.min(rad,W/2,H/2),SEG=4;\n"
    "    var cs=[[L+W-r,T+r,-Math.PI/2],[L+W-r,T+H-r,0],\n"
    "            [L+r,T+H-r,Math.PI/2],[L+r,T+r,Math.PI]];\n"
    "    cs.forEach(function(c){\n"
    "      for(var k=0;k<=SEG;k++){\n"
    "        var a=c[2]+(Math.PI/2)*(k/SEG);\n"
    "        pts.push([c[0]+Math.cos(a)*r,c[1]+Math.sin(a)*r]);\n"
    "      }\n"
    "    });\n"
    "    return pts;\n"
    "  },\n"
    "  /* THE CARD GLOW, THROUGH THE DICE'S PAINTER. Keyed, so the player's\n"
    "     drag and the rival's armed telegraph are two entries in one list\n"
    "     rather than two effects - k<=0 removes an entry. Painted on\n"
    "     demand: a card only moves when something moves it, so there is no\n"
    "     per-frame cost while the hand sits still. */\n"
    "  cardGlow:function(key,el,k,col){\n"
    "    this._cardGlows=this._cardGlows||{};\n"
    "    if(!el||!(k>0))delete this._cardGlows[key];\n"
    "    else this._cardGlows[key]={el:el,k:k,col:col||null};\n"
    "    this._drawCardGlows();\n"
    "  },\n"
    "  _drawCardGlows:function(){\n"
    "    var sc0=document.getElementById('screen-match');\n"
    "    var cv=document.getElementById('dgCanvasHi');\n"
    "    var live=this._cardGlows&&Object.keys(this._cardGlows).length;\n"
    "    if(!sc0||(!live&&!cv))return;\n"
    "    cv=this._glowHiCv();if(!cv)return;\n"
    "    var sc=sc0.getBoundingClientRect();\n"
    "    if(sc.width<10)return;\n"
    "    var dpr=Math.min(devicePixelRatio||1,this.GLOW_DPR_MAX||3);\n"
    "    if(cv.width!==Math.round(sc.width*dpr)||cv.height!==Math.round(sc.height*dpr)){\n"
    "      cv.width=Math.round(sc.width*dpr);cv.height=Math.round(sc.height*dpr);\n"
    "    }\n"
    "    var x=cv.getContext('2d');\n"
    "    x.setTransform(dpr,0,0,dpr,0,0);\n"
    "    x.clearRect(0,0,sc.width,sc.height);\n"
    "    if(!live)return;\n"
    "    var self=this,CG=this.CARD_GLOW;\n"
    "    /* the rim line would trace the bounding box rather than the card's\n"
    "       own angle, so it is off for cards - the halo carries it */\n"
    "    var G=this.GLOW,keepLine=G.line;G.line=CG.line;\n"
    "    try{\n"
    "      Object.keys(this._cardGlows).forEach(function(kk){\n"
    "        var e=self._cardGlows[kk];\n"
    "        if(!e.el||!e.el.isConnected){delete self._cardGlows[kk];return;}\n"
    "        var r=e.el.getBoundingClientRect();\n"
    "        if(r.width<4)return;\n"
    "        var hull=self._rectHull(r.left-sc.left,r.top-sc.top,r.width,r.height,\n"
    "          Math.min(r.width,r.height)*CG.round);\n"
    "        self._paintHalo(cv,x,sc,dpr,[hull],e.col||CG.col,e.col||CG.soft,\n"
    "          CG.floor+(1-CG.floor)*Math.min(1,e.k));\n"
    "      });\n"
    "    }finally{G.line=keepLine;}\n"
    "  },\n"
)
k = s.find("  _drawGlow:function(){")
if k < 0:
    sys.exit('_drawGlow anchor lost (nothing written)')
s = s[:k] + PAINTER + s[k:]
edits.append('painter extracted + card glow')

# ── 2. the card glow's own dials, beside the dice's ──
sub(u"  GLOW_DPR_MAX:3,",
    u"""  GLOW_DPR_MAX:3,
  /* P748: the CARD halo's dials, beside the dice's on purpose - one glow
     language, two shapes. `floor` is why a card lights the moment it
     leaves the row instead of ramping up from invisible; `line:0` keeps
     the crisp rim off a bounding-box hull. */
  CARD_GLOW:{col:'#ffe6a4', soft:'#ffa93a', round:0.075, line:0, floor:0.42},""",
    'card glow dials')

# ── 3. the drag drives it ──
sub(u"""    el.style.setProperty('--arm',_k.toFixed(3));""",
    u"""    el.style.setProperty('--arm',_k.toFixed(3));
    /* P748: THE GLOW IS PAINTED, NOT FILTERED. A drop-shadow on this card
       is clipped away by WebKit because the row is a 3D-transformed
       context - so the halo goes through the dice's own painter, on a
       screen-space canvas nothing can clip. Written here beside the
       transform for the same reason that one is: the card only moves when
       the finger moves it. */
    try{if(window.D3X&&D3X.cardGlow)D3X.cardGlow('drag',_famDrag.why?null:el,_k);}catch(e){}""",
    'drag paints the halo')

sub(u"""    el.classList.remove('fcv-drag','armed','fcv-blocked','fcv-cant');
    el.style.removeProperty('--arm');""",
    u"""    el.classList.remove('fcv-drag','armed','fcv-blocked','fcv-cant');
    el.style.removeProperty('--arm');
    try{if(window.D3X&&D3X.cardGlow)D3X.cardGlow('drag',null,0);}catch(e){}""",
    'the halo clears with the gesture')

# ── 4. the rival's armed telegraph, same painter (parity) ──
sub(u"""  hostO.innerHTML=ho;""",
    u"""  hostO.innerHTML=ho;
  /* P748: THE RIVAL'S ARMED CARD GLOWS THE SAME WAY. It was a gold
     drop-shadow on .fcv.armed in #famRowO - the same 3D-transformed row,
     so just as clipped and just as invisible on a phone. Denis: the
     mechanics are shared, so the visual is too. Their accent, not gold. */
  try{
    if(window.D3X&&D3X.cardGlow){
      var _oa=hostO.querySelector('.fcv.armed');
      D3X.cardGlow('opp',_oa||null,_oa?1:0,window.OPP_INK||'#d94c3d');
    }
  }catch(e){}""",
    'rival armed uses the painter')

# ── 5. the CSS gold shadows go: they never painted here ──
sub(u"""  filter:drop-shadow(0 0 calc(0.35cqw + 0.55cqw*var(--arm,0)) rgba(255,240,190,calc(0.45 + 0.55*var(--arm,0))))
    drop-shadow(0 0 calc(1.6cqw + 2.2cqw*var(--arm,0)) rgba(255,200,85,calc(0.5 + 0.5*var(--arm,0))))
    drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))
    brightness(calc(1.06 + 0.18*var(--arm,0)))}""",
    u"""  /* P748: THE GOLD DROP-SHADOWS ARE GONE. They were the glow, and in
     this row they were never painted on WebKit - a filter on a child of a
     3D-transformed parent is clipped to the child's own box, and a halo
     is by definition outside it. D3X.cardGlow paints it on a canvas now.
     What stays is what works IN bounds: the contact shadow and the lift
     in brightness. */
  filter:drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))
    brightness(calc(1.06 + 0.18*var(--arm,0)))}""",
    'CSS glow retired')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
