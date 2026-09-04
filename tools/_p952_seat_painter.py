# -*- coding: utf-8 -*-
u"""P952 (brief 3.12): a table mark needs its own painter, not a better hull.

Denis on the screenshots: "those visual effects are weird... glow with holes in
them, they are not clear enough." Both halves of that are literal.

THE HOLES ARE THE PUNCH. _paintHalo cuts its subject back out of its own glow -
destination-out on the hull - so every form it draws is a RING. P951 routed
around it by moving fog and snuff to `veil`, the one form that fills; the right
answer is that the punch should never have run. It exists so a die's glow does
not wash over the die. A table mark has no subject to protect: the rival's dice
land on top of it by z-order, which is the entire reason the under-canvas was
chosen. So the punch is not avoided here, it is absent.

THE GLOW IS `lighter`. Additive compositing on mid-brown wood can only lighten,
so any ink becomes a pale smear - which is exactly what the fog was. Smoke lying
on a table OCCLUDES: darker in places, lighter in others. source-over is what
makes a thing sit on a surface rather than hover above it glowing.

AND A SOFT BLOB AT UNIFORM ALPHA IS A SMUDGE. A cloud reads as a cloud because
of internal structure - uneven density, a torn edge, wisps. No amount of
silhouette work fixes a single flat shape, which is why P951's three genuinely
different outlines still read as three auras. The body is built from overlapping
puffs at varying radius and alpha instead, some darker than the table and some
lighter, which is what gives it depth on a brown surface.

FOUR THINGS THIS ADDS, in the order they matter:
  1. _paintSeat - its own painter. source-over, no punch, no _paintHalo.
  2. CONTACT. A soft darkening under the mark. It is what sells "on the table"
     rather than "in the air", and it costs one radial gradient.
  3. TEXTURE. 11-14 puffs, jittered from a per-lane seed so a mark is stable
     frame to frame and still unique per seat - Math.random would shimmer.
  4. FOOTPRINT. The mark occupies the lane's seat, not a patch between two.
     P951's forms were narrower than a die, which is why they read as artefacts
     of the dice rather than objects on the table.

SNUFF BECOMES A DARKENING, per Denis taking the proposal. Absence is what snuff
means and a dark patch says it; #b09470 on brown wood cannot be seen at any
alpha, and §11 governs identity across card, brand and beat rather than
obliging an ink that is invisible on the surface it is painted on. The tan
survives in the wisps at the top, where it has the dark body to read against.

SNARE KEEPS ITS SILHOUETTE - it was the one form that worked - but is filled
with a gradient along its length rather than haloed, so the ends fade instead of
being ringed.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# 1 ── the roster describes a MARK, not a halo form ─────────────────
sub(u"""  SEAT_FORMS:{
    _fog:{ink:'fog',style:'veil',shape:'cloud',alpha:1},
    _snare:{ink:'snare',style:'crust',shape:'cord',alpha:1},
    _snuff:{ink:'snuff',style:'veil',shape:'wisp',alpha:0.9}
  },""",
    u"""  /* P952: `body` picks the PAINTER, not a halo form - the halo family is what
     made these read as auras. `dark` says the mark occludes rather than tints:
     snuff means the die is GONE, and on mid-brown wood a darkening says that
     where its own tan cannot be seen at any alpha. The tan survives in the
     wisps, which have the dark body to read against. */
  SEAT_FORMS:{
    _fog:{ink:'fog',body:'cloud',alpha:1,spread:1.55},
    _snare:{ink:'snare',body:'cord',alpha:1,spread:1.30},
    _snuff:{ink:'snuff',body:'smoke',alpha:1,spread:1.20,dark:'#150f0c'}
  },
  /* a hex to rgba, so an ink can carry its own alpha per puff */
  _seatRGBA:function(hex,a){
    var h=(hex||'#ffffff').replace('#','');
    if(h.length===3)h=h[0]+h[0]+h[1]+h[1]+h[2]+h[2];
    var n=parseInt(h,16);
    return 'rgba('+((n>>16)&255)+','+((n>>8)&255)+','+(n&255)+','+
           (Math.max(0,Math.min(1,a))).toFixed(3)+')';
  },
  /* DETERMINISTIC JITTER. A mark must be stable frame to frame - Math.random
     would boil - but every seat should look like its own cloud, so the seed is
     the lane. Cheap LCG, no state. */
  _seatRnd:function(n){
    n=(n*9301+49297)%233280;
    return n/233280;
  },
  /* THE PUFFS. Uneven density and a torn edge are what separate a cloud from a
     smudge, and no silhouette gets there on its own. Radii and alphas vary,
     and a third of them are DARKER than the table so the body has depth on a
     brown surface instead of only adding light to it. */
  _seatPuffs:function(b,seed,phase,dark){
    var out=[],N=dark?11:14,i,r1,r2,r3,ang,rad,px,py;
    for(i=0;i<N;i++){
      r1=this._seatRnd(seed*97+i*31+7);
      r2=this._seatRnd(seed*53+i*17+3);
      r3=this._seatRnd(seed*29+i*11+5);
      ang=r1*Math.PI*2+phase*(0.25+r2*0.5);
      rad=(0.18+0.62*r2);
      px=b.cx+Math.cos(ang)*b.w*(dark?0.22:0.44)*rad;
      py=b.cy+Math.sin(ang)*b.h*(dark?0.40:0.26)*rad;
      /* P952b: the BODY carries the mark, so the light puffs roughly doubled.
         And the shade minority is smaller for a cloud than for smoke: fog is a
         pale thing with a few dark folds, snuff is a dark thing outright, so
         one threshold for both made the fog muddy. */
      /* P952d: PARTIAL overlap, and thin enough that overlapping is what
         builds density. P952c went too far the other way - big radii on a
         tight spread merged into one smooth mass at 138/255 mean alpha, which
         is a brighter smudge rather than smoke. A cloud needs the puffs to
         disagree: varied radius, only partial overlap so the edge tears, and a
         low enough per-puff alpha that two overlapping read differently from
         one alone. */
      out.push({x:px,y:py,
                r:b.w*(dark?0.22:0.27)*(0.45+0.95*r3),
                a:(dark?0.20:0.15)*(0.45+0.9*r1),
                shade:(r3<(dark?0.55:0.30))});
    }
    return out;
  },
  /* THE SEAT PAINTER. source-over, no punch, no _paintHalo - the three halo
     forms exist to ring a die and a table mark has no subject to protect,
     because the dice land on top of it by z-order. */
  _paintSeat:function(x,g){
    var b=g.b,am=g.am,col=g.col,F=g.form,i,p,gr;
    if(!(am>0))return;
    x.save();
    x.globalCompositeOperation='source-over';
    /* CONTACT. What sells "lying on the table" rather than "hovering above it
       glowing", and it is one gradient. */
    /* P952b: TIGHTER AND WEAKER. At 0.34 the contact was the loudest thing on
       the surface - the canvas came back with #000000 as its dominant colour
       and the fog read as a shadow rather than as smoke. Contact is meant to
       seat the mark, not to be it. */
    gr=x.createRadialGradient(b.cx,b.cy+b.h*0.15,1,b.cx,b.cy+b.h*0.15,b.w*0.50);
    gr.addColorStop(0,'rgba(12,7,4,'+(0.15*am).toFixed(3)+')');
    gr.addColorStop(0.55,'rgba(12,7,4,'+(0.06*am).toFixed(3)+')');
    gr.addColorStop(1,'rgba(12,7,4,0)');
    x.fillStyle=gr;
    x.beginPath();
    x.ellipse(b.cx,b.cy+b.h*0.15,b.w*0.50,b.h*0.24,0,0,Math.PI*2);
    x.fill();
    if(F.body==='cord'){
      /* the one silhouette that worked, filled along its length rather than
         ringed, so the ends fade to nothing instead of being outlined */
      var hull=this._seatShape('cord',b,g.phase,g.grow);
      var lg=x.createLinearGradient(b.cx-b.w*0.62,b.cy,b.cx+b.w*0.62,b.cy);
      lg.addColorStop(0,this._seatRGBA(col,0));
      lg.addColorStop(0.22,this._seatRGBA(col,0.62*am));
      lg.addColorStop(0.5,this._seatRGBA(col,0.80*am));
      lg.addColorStop(0.78,this._seatRGBA(col,0.62*am));
      lg.addColorStop(1,this._seatRGBA(col,0));
      x.fillStyle=lg;
      x.beginPath();
      for(i=0;i<hull.length;i++){
        if(i===0)x.moveTo(hull[i][0],hull[i][1]);else x.lineTo(hull[i][0],hull[i][1]);
      }
      x.closePath();x.fill();
      x.restore();
      return;
    }
    /* CLOUD and SMOKE: overlapping puffs, some darker than the table */
    var dark=F.dark||null,puffs=this._seatPuffs(b,g.lane+1,g.phase,!!dark);
    for(i=0;i<puffs.length;i++){
      p=puffs[i];
      var ink=p.shade?(dark||'#3a3026'):col;
      var pa=p.a*(p.shade&&!dark?0.85:1);/* a fold - legible now the body is thinner */
      gr=x.createRadialGradient(p.x,p.y,p.r*0.12,p.x,p.y,p.r);
      gr.addColorStop(0,this._seatRGBA(ink,pa*am));
      gr.addColorStop(0.55,this._seatRGBA(ink,pa*am*0.52));
      gr.addColorStop(1,this._seatRGBA(ink,0));
      x.fillStyle=gr;
      x.beginPath();x.arc(p.x,p.y,p.r,0,Math.PI*2);x.fill();
    }
    /* SMOKE gets its tan back at the top, where the dark body gives it
       something to read against - identity without depending on it to be seen */
    if(dark){
      for(i=0;i<4;i++){
        var t=i/4,r1=this._seatRnd(g.lane*13+i*7+2);
        var wx=b.cx+Math.sin(g.phase*0.8+t*2.2+r1*2)*b.w*0.13*(0.3+t);
        var wy=b.cy-b.h*(0.10+0.34*t);
        gr=x.createRadialGradient(wx,wy,0.5,wx,wy,b.w*0.10*(1-0.45*t));
        gr.addColorStop(0,this._seatRGBA(col,0.30*am*(1-t*0.7)));
        gr.addColorStop(1,this._seatRGBA(col,0));
        x.fillStyle=gr;
        x.beginPath();x.arc(wx,wy,b.w*0.10*(1-0.45*t),0,Math.PI*2);x.fill();
      }
    }
    x.restore();
  },""",
    '1 the seat painter')

# 2 ── the plan describes a seat, not a hull ────────────────────────
sub(u"""      if(!(am>0.02))continue;
      var b=this._seatBounds(+L,sc);
      if(!b)continue;
      var phase=((now-(m.shownAt||now))/1000)*(m.t==='_fog'?0.55:0.95);
      var hull=this._seatShape(F.shape,
        {cx:b.cx+dx,cy:b.cy+dy,w:b.w,h:b.h},phase,grow);
      if(!hull||hull.length<3)continue;""",
    u"""      if(!(am>0.02))continue;
      var b0=this._seatBounds(+L,sc);
      if(!b0)continue;
      /* THE MARK OCCUPIES THE SEAT. P951's forms were narrower than a die and
         sat between two of them, which is why they read as something the dice
         were doing rather than as objects on the table. `spread` widens the
         footprint past the die that would stand there. */
      var sp=(F.spread||1.4)*grow;
      var b={cx:b0.cx+dx,cy:b0.cy+dy,w:b0.w*sp,h:b0.h*sp};
      var phase=((now-(m.shownAt||now))/1000)*(m.t==='_fog'?0.55:0.95);""",
    '2 the plan carries a seat')

sub(u"""      var col=this._seatInk(F.ink);
      groups.push({style:F.style,col:col,soft:col,hulls:[hull],
                   am:am*(F.alpha==null?1:F.alpha)});""",
    u"""      var col=this._seatInk(F.ink);
      var seatAm=am*(F.alpha==null?1:F.alpha);
      /* `seat` routes this past _paintForm entirely - the halo family is what
         made these read as auras. `sig` is its own cache key, because there is
         no hull for _planSig to serialise. */
      groups.push({seat:true,form:F,b:b,lane:+L,col:col,am:seatAm,
                   phase:phase,grow:grow,
                   sig:'seat|'+L+'|'+F.body+'|'+col+'|'+seatAm.toFixed(2)+'|'+
                       b.cx.toFixed(1)+','+b.cy.toFixed(1)+'|'+
                       b.w.toFixed(1)+'|'+phase.toFixed(2)});""",
    '3 the group routes past the halo painter')

# 4 ── the signature understands a seat group ───────────────────────
sub(u"""      /* P951: ALPHA IS PART OF THE PICTURE. It was absent because a state is
         either worn or not, so every group was opaque and the omission cost
         nothing. A seat mark fades in, blooms or thins, and without this the
         cache would hold the first frame of an animation on screen and never
         repaint it - a signature that cannot see the thing that is changing. */
      s+=g.style+'|'+g.col+'|'+g.soft+'|'+((g.am==null?1:g.am).toFixed(2))+'|';""",
    u"""      /* P952: a seat group brings its own key. It has no hull to serialise -
         its body is built from puffs at paint time - so the fields that can
         change the picture are named directly. */
      if(g.seat){s+=g.sig+'#';continue;}
      /* P951: ALPHA IS PART OF THE PICTURE. It was absent because a state is
         either worn or not, so every group was opaque and the omission cost
         nothing. A seat mark fades in, blooms or thins, and without this the
         cache would hold the first frame of an animation on screen and never
         repaint it - a signature that cannot see the thing that is changing. */
      s+=g.style+'|'+g.col+'|'+g.soft+'|'+((g.am==null?1:g.am).toFixed(2))+'|';""",
    '4 the signature understands a seat')

# 5 ── and so does the painter dispatch ─────────────────────────────
sub(u"""      this._paintForm(g.style,cv,x,sc,dpr,g.hulls,g.col,g.soft,
                      (g.am==null?1:g.am),layer==='over',cheap);""",
    u"""      /* P952: a seat mark is painted by its own painter - source-over, no
         punch - because the three forms _paintForm implements are all halos
         and a halo shaped like a cloud is still a halo. */
      if(g.seat){this._paintSeat(x,g);continue;}
      this._paintForm(g.style,cv,x,sc,dpr,g.hulls,g.col,g.soft,
                      (g.am==null?1:g.am),layer==='over',cheap);""",
    '5 the dispatch routes a seat to its painter')

# ── post-asserts ───────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

if code.count('_paintSeat:function') != 1:
    sys.exit('the seat painter is not defined once (nothing written)')
# IT MUST NOT GO THROUGH THE HALO FAMILY. That is the whole patch.
_ps = code.index('_paintSeat:function')
_psEnd = code.index('_seatBounds:function', _ps) if '_seatBounds:function' in code[_ps:] \
         else len(code)
body = code[_ps:_psEnd]
if '_paintHalo' in body:
    sys.exit('the seat painter still routes through _paintHalo (nothing written)')
if "globalCompositeOperation='source-over'" not in body:
    sys.exit('the seat painter does not composite normally (nothing written)')
if 'createRadialGradient' not in body:
    sys.exit('the seat painter has no soft structure (nothing written)')
# CONTACT and TEXTURE both present
if 'rgba(12,7,4,' not in body:
    sys.exit('there is no contact shadow (nothing written)')
if code.count('_seatPuffs:function') != 1 or '_seatPuffs(' not in body:
    sys.exit('the texture pass is missing (nothing written)')
# the dispatch and the signature both know about seat groups, or it paints
# nothing / caches the first frame for ever
if code.count('if(g.seat)') != 2:
    sys.exit('expected the seat branch in both _planSig and _paintPlan, found %d '
             '(nothing written)' % code.count('if(g.seat)'))
# snuff darkens rather than tints
if "dark:'#150f0c'" not in code:
    sys.exit('snuff is not a darkening (nothing written)')
# and the deterministic seed, or the cloud boils frame to frame
if 'Math.random' in body:
    sys.exit('the puffs are randomised per frame and will boil (nothing written)')
# the footprint actually widens
if 'F.spread||1.4' not in code:
    sys.exit('the mark does not take the seat footprint (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
