# -*- coding: utf-8 -*-
"""P751: one halo body on every engine; the card glow wears the card's
own silhouette.

Denis, this morning: the card halo "does not follow the card shape,
rotation, etc. It needs to be derived from the card alpha at all times" -
and the dice glow is "much larger and softer on phone... it doesn't take
the width or height... the glow color doesn't blend with the outline
like in the lab."

Both complaints are the same root: _paintHalo had TWO bodies. Desktop
takes ctx.filter blur; iOS Safari <18 takes a stroked-rings fallback
with its own dials (fbWide/fbCross/fbA0/fbA1) that sx/sy only partially
reach and whose ramp never blends into the rim line the way stacked blur
does. Whatever is tuned in the lab is tuned on the branch the phone
never runs. And rings are strokes of a POLYGON, which is why the card
halo could only ever be a rounded box.

So the branch dies. The blur becomes a mip chain - downscale by halves,
one bilinear upscale - which is plain drawImage, identical on every
engine there is, needs no capability test, and blurs ANY silhouette:

  hull   a polygon (the dice keep exactly their projected corners)
  stamp  an image drawn at position/rotation/scale - the card's own art,
         so the halo is derived from the card ALPHA, rotated with the
         fan, exactly as asked.

fb* dials are retired (nothing reads them). soft/rim/strength/sx/sy/dy
now drive the one body, so the lab's numbers are the phone's numbers.
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


# ── 1. the whole painter, replaced between hard markers ──
START = "  _paintHalo:function(cv,x,sc,dpr,sel,COL,SOFT,alphaMul,lineW){"
ENDMARK = "  /* the canvas the CARD glow paints on."
i = s.find(START)
j = s.find(ENDMARK)
if i < 0 or j < 0 or j <= i:
    sys.exit('painter markers not found (nothing written)')

NEW = r'''  /* P751: ONE BODY, EVERY ENGINE. This painter had two: ctx.filter blur
     for desktop and a stroked-rings fallback for iOS Safari <18, each
     with its own dials - so the lab tuned a branch the phone never ran,
     sx/sy only half-reached the rings, and the ring ramp never blended
     into the rim line the way stacked blur does. The blur is a mip
     chain now (downscale by halves, one bilinear upscale): plain
     drawImage, identical everywhere, no capability test - and it blurs
     ANY silhouette, which is what lets a card's halo be derived from
     the card's own alpha instead of a rounded box.
     A shape is a hull (array of screen-space points, the dice) or
     {stamp:{img,cx,cy,w,h,rot}} - the subject's own image drawn at its
     screen position, rotation and scale (the cards). */
  _paintHalo:function(cv,x,sc,dpr,sel,COL,SOFT,alphaMul,lineW){
    var self=this,G=this.GLOW;
    var LINE=(lineW===undefined)?G.line:lineW;
    var g=this._glowTmp||(this._glowTmp=document.createElement('canvas'));
    if(g.width!==cv.width||g.height!==cv.height){g.width=cv.width;g.height=cv.height;}
    var gx=g.getContext('2d');
    gx.setTransform(dpr,0,0,dpr,0,0);
    gx.globalCompositeOperation='source-over';
    gx.globalAlpha=1;
    gx.clearRect(0,0,sc.width,sc.height);
    var trace=function(ctx,hull,shrink,dy,sx2,sy2){
      var cx=0,cy=0;
      hull.forEach(function(p){cx+=p[0];cy+=p[1];});
      cx/=hull.length;cy/=hull.length;
      ctx.beginPath();
      hull.forEach(function(p,i){
        var dx=p[0]-cx,dyy=p[1]-cy,L=Math.sqrt(dx*dx+dyy*dyy)||1;
        var k=shrink?Math.max(0,(L-shrink))/L:1;
        /* P731: sx/sy stretch, dy leans - undefined means 1/1/0 */
        var px=cx+dx*k*(sx2||1),py=cy+dyy*k*(sy2||1)+(dy||0);
        if(i)ctx.lineTo(px,py);else ctx.moveTo(px,py);
      });
      ctx.closePath();
    };
    /* lay one shape: a hull is traced and filled, a stamp is drawn from
       its image's own alpha at its element's place in the world */
    var lay=function(ctx,shape,col,o){
      o=o||{};
      if(shape&&shape.stamp){
        var st=shape.stamp;
        ctx.save();
        ctx.translate(st.cx,st.cy+(o.dy||0));
        if(st.rot)ctx.rotate(st.rot);
        var w=st.w*(o.sx||1)*(o.scaleMul||1),h=st.h*(o.sy||1)*(o.scaleMul||1);
        ctx.drawImage(col?self._tintStamp(st.img,col):st.img,-w/2,-h/2,w,h);
        ctx.restore();
      }else{
        var hull=shape&&shape.hull||shape;
        if(col)ctx.fillStyle=col;
        trace(ctx,hull,o.shrink||0,o.dy||0,o.sx,o.sy);
        ctx.fill();
      }
    };
    var S=this._haloS||(this._haloS=document.createElement('canvas'));
    if(S.width!==cv.width||S.height!==cv.height){S.width=cv.width;S.height=cv.height;}
    var sxc=S.getContext('2d');
    /* the mip blur: halve until the step reaches ~r user px, then one
       smooth upscale. The falloff width tracks r, so the lab's soft and
       rim numbers keep their meaning. */
    var blurOnto=function(dst,r,passes){
      var F=Math.max(2,r*dpr);
      var n=Math.max(1,Math.min(5,Math.round(Math.log(F)/Math.LN2)));
      var cur=S,cw=S.width,ch=S.height;
      self._mips=self._mips||[];
      for(var mi=0;mi<n;mi++){
        var m=self._mips[mi]||(self._mips[mi]=document.createElement('canvas'));
        var nw=Math.max(1,Math.ceil(cw/2)),nh=Math.max(1,Math.ceil(ch/2));
        if(m.width!==nw||m.height!==nh){m.width=nw;m.height=nh;}
        var mx=m.getContext('2d');
        mx.setTransform(1,0,0,1,0,0);
        mx.clearRect(0,0,nw,nh);
        mx.imageSmoothingEnabled=true;
        mx.drawImage(cur,0,0,cw,ch,0,0,nw,nh);
        cur=m;cw=nw;ch=nh;
      }
      dst.save();
      dst.setTransform(1,0,0,1,0,0);
      dst.imageSmoothingEnabled=true;
      for(var p=0;p<(passes||1);p++)dst.drawImage(cur,0,0,cw,ch,0,0,S.width,S.height);
      dst.restore();
    };
    /* the wide, soft falloff - P731: this pass alone stretches/leans */
    sxc.setTransform(dpr,0,0,dpr,0,0);
    sxc.globalCompositeOperation='source-over';
    sxc.clearRect(0,0,sc.width,sc.height);
    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:G.dy,sx:G.sx,sy:G.sy});});
    blurOnto(gx,G.soft,G.softPasses||1);
    /* then the bright rim, stacked - the punch-out below throws away the
       inner half of every blur, so a single pass never reads as strong */
    sxc.setTransform(dpr,0,0,dpr,0,0);
    sxc.clearRect(0,0,sc.width,sc.height);
    sel.forEach(function(sh){lay(sxc,sh,COL,{});});
    blurOnto(gx,G.rim,G.rimPasses||1);
    /* cut the subject back out EXACTLY on its painted edge: everything
       left is outside the shape, which is the whole point. clear widens
       the cut a hair past the edge - see the note above GLOW. */
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
    /* the line goes on the SAME surface as the halo, after the cut-out,
       so the two composite as one glow. Hulls only: a stamp's crisp edge
       is the subject's own art. */
    if(LINE>0){
      gx.strokeStyle=COL;gx.lineWidth=LINE;gx.lineJoin='round';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp)return;
        trace(gx,sh&&sh.hull||sh,0);gx.stroke();
      });
    }
    /* additive, so it reads as light rather than paint */
    x.save();
    x.globalCompositeOperation='lighter';
    x.globalAlpha=G.strength*(alphaMul===undefined?1:alphaMul);
    x.drawImage(g,0,0,sc.width,sc.height);
    x.restore();
  },
  /* a stamp tinted to the halo colour: the image's alpha, the glow's
     paint. Cached per image per colour - the art never changes. */
  _tintStamp:function(img,col){
    var tc=img.__fkTints||(img.__fkTints={});
    if(tc[col])return tc[col];
    var w=img.naturalWidth||img.width,h=img.naturalHeight||img.height;
    if(!w||!h)return img;
    var c=document.createElement('canvas');c.width=w;c.height=h;
    var cx=c.getContext('2d');
    cx.drawImage(img,0,0,w,h);
    cx.globalCompositeOperation='source-in';
    cx.fillStyle=col;cx.fillRect(0,0,w,h);
    return (tc[col]=c);
  },
'''
s = s[:i - len("")] if False else s  # no-op guard for readability
# find the true start of the P751 comment block we are replacing: the old
# painter has its own leading comment starting at "  /* P748: THE ONE HALO
# PAINTER." - replace from there.
ci = s.rfind("  /* P748: THE ONE HALO PAINTER.", 0, i)
if ci < 0:
    sys.exit('painter comment marker not found (nothing written)')
s = s[:ci] + NEW + s[j:]
edits.append('one painter body')

# ── 2. the fb dials retire ──
sub("""  /* P603: fb* are the STROKED-RINGS FALLBACK's own dials - the branch phones
     take, because ctx.filter is a silent no-op on iOS Safari before 18. Denis:
     "on phone make the glow a bit tighter and a bit more saturated". They are
     separate from soft/rim/strength on purpose: those feed the blur branch that
     desktop uses, and a shared number would have moved both.
       fbWide  multiplies soft for the widest ring. 2 -> 1.35 pulls the halo's
               reach in from 20px to 13.5px: TIGHTER.
       fbCross where the ramp switches from the pale SOFT to the saturated COL.
               .55 -> .40 puts six of the ten rings on the bright colour
               instead of four: MORE SATURATED, without touching strength,
               which would have brightened desktop too.
       fbA0/A1 the alpha ramp, 0.09..0.32 -> 0.11..0.41, so the accumulated
               rim survives the punch-out that throws away its inner half. */
""",
    """  /* P751: the fb* fallback dials are GONE with the branch they fed -
     one body now, so the lab's numbers are the phone's numbers. */
""",
    'fb comment retired')

sub("""  GLOW:{soft:11, rim:3, rimPasses:5, softPasses:1, line:3.2, grow:1.004, clear:0.7, strength:0.91,
        /* P739: MEASURED against the blur branch in the same browser -
           same reach (mass ratio 1.01) but 1.67x the BRIGHT area, so the
           stroked fallback read heavier and flatter wherever ctx.filter
           is missing. The ramp is divided by that measured factor, so
           both painters lay down the same light. */
        fbWide:1.35, fbCross:0.40, fbA0:0.051, fbA1:0.139,
""",
    """  GLOW:{soft:11, rim:3, rimPasses:5, softPasses:1, line:3.2, grow:1.004, clear:0.7, strength:0.91,
""",
    'fb dials gone')

# ── 3. the card glow lays a STAMP: the card's own art ──
sub("""    Object.keys(this._cardGlows).forEach(function(kk){
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
    """    Object.keys(this._cardGlows).forEach(function(kk){
      var e=self._cardGlows[kk];
      if(!e.el||!e.el.isConnected){delete self._cardGlows[kk];return;}
      var r=e.el.getBoundingClientRect();
      if(r.width<4)return;
      /* P751: THE CARD'S OWN SILHOUETTE. The halo is derived from the
         card art's alpha, at the element's on-screen rotation and scale
         (Denis: "derived from the card alpha at all times so it never
         risks not matching its shape"). The bounding rect's centre is
         the transformed centre; rotate and scale are the standalone CSS
         properties the fan and the drag use. A face-down or imageless
         card falls back to the rounded box. */
      var shape=null;
      var img=e.el.querySelector('.fcvIn img')||e.el.querySelector('img');
      if(img&&img.complete&&img.naturalWidth>0){
        var cs2=getComputedStyle(e.el);
        var rot=parseFloat(cs2.rotate);if(isNaN(rot))rot=0;
        var scl=parseFloat(cs2.scale);if(!(scl>0))scl=1;
        shape={stamp:{img:img,
          cx:r.left-sc.left+r.width/2,cy:r.top-sc.top+r.height/2,
          w:e.el.offsetWidth*scl,h:e.el.offsetHeight*scl,
          rot:rot*Math.PI/180}};
      }else{
        shape={hull:self._rectHull(r.left-sc.left,r.top-sc.top,r.width,r.height,
          Math.min(r.width,r.height)*CG.round)};
      }
      self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.soft,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line);
    });""",
    'card halo from the card alpha')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
