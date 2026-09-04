# -*- coding: utf-8 -*-
u"""P951 (brief 3.12): the mark on the table - three silhouettes, two endings.

The PAINT half; P950 is the state. What this adds is a THIRD ANCHOR, not a third
lifetime: MARKS is one row per thing a DIE wears and cannot hold this (_markDice
requires match && obj.visible && chip), FX_MARKS is die-bound too (_fxMark bails
on !d.obj). A table mark has no die. So it gets its own producer, and joins the
existing pipeline at the one place that is anchor-agnostic: _markPlan returns a
list of {style,col,soft,hulls} groups, and _planSig and _paintPlan walk THE PLAN
rather than the roster - so anything appended there is signed and painted for
free.

_rectHull IS THE BOUNDS, NOT THE MARK. Denis: a rounded rectangle at a lane
reads as "this seat is highlighted" - a debug overlay with an ink applied - and
3.12's whole value is that the armed threat is flavourful rather than a UI state.
So _rectHull is kept for what it is genuinely good at, answering where and how
big, and is used as the FALLBACK silhouette for a type with no shape of its own.
That fallback is deliberately rect-shaped: per P949's principle, a missing form
should look wrong rather than plausible.

THREE SILHOUETTES, BECAUSE THERE ARE THREE OCCUPYING ENCHANTS. §11's one-ink-
per-idea rule carries identity ACROSS surfaces and is not a substitute for the
form differing here; a fog and a snare must not be one shape in two colours.
  CLOUD - fog. Wide, low, irregular, its radius modulated by three sine terms at
    different frequencies so no two lobes match, drifting as its phase advances.
    Painted as `veil`, the only form that FILLS: _paintHalo punches its subject
    out of its own glow, so `rim` can only ever draw the outline of a hull -
    screenshotted, the cloud came out as a cloud-shaped ring.
  CORD - snare. A taut lens spanning the seat, sharp at both ends: the profile
    goes to zero at t=+/-1, which is what makes the ends points rather than
    caps, with a slight sag so it reads as a drawn line under tension. Painted
    as `crust`, whose whole character is a hard edge with almost no falloff.
  WISP - snuff. A narrow curl rising from the seat, tapering as it goes, and
    small enough that the seat around it reads EMPTY. That absence is the point:
    snuff takes the die away, so the mark must not fill the space the die left.
    `veil` for the same reason as fog.

TWO ENDINGS, BUILT IN RATHER THAN ADDED. 3.3 is a ruling and retrofitting a miss
onto a form designed for a fire is how a failure state gets bolted on later. A
FIRE blooms - brighter and larger for a beat, then gone quickly - because the
dice landed in it and it did its work. A MISS thins and drifts off, fading on a
square curve while it widens and slides, the rival's dice untouched. Different
curve, different duration, different motion.

THE LANDING IS THE BANK'S FLAVOUR BEAT. Denis specified that banking "in itself
has a flavour effect", and the mark arriving IS that beat - it is what banking
buys, and what makes 3.13's jeopardy worth taking. A mark that has not landed
paints nothing at all, so an armed-but-unbanked brand is invisible, which is
exactly right now that a bust takes it.

WHERE IT SITS: PREDICT, THEN MEASURE. The empty window has no rival die to
measure, so the centre is predicted from the grid cell - #throwLine, which
P683 established as the datum because the rows collapse to zero. The moment a
die exists for that lane the position is re-derived from the die itself. The
prediction yields; it is never a second authority, which is the objection to
duplicating the seat arithmetic. A small snap as the dice arrive reads as them
settling into the fog.
  AND THE SNUFFED SEAT HAS NO DIE TO MEASURE, ever - that is what snuff does.
  The row is justify-content:center and closes up around the gap, so the full-N
  prediction would put the wisp somewhere no seat is. It is placed at the
  midpoint of its surviving neighbours instead: the spot the row closed over,
  which is precisely where the missing die was.

COST: one _paintHalo per mark rather than one per ink. The roster's grouping
rule exists because ink was the only thing that varied between dice wearing one
row; here alpha varies per mark - each is at its own point in its own entrance
or ending - so grouping is not available. The bound is the number of landed
marks, which _lmArm caps at one per lane and is one or two in practice.
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


# 1 ── the seat-mark machinery, ahead of the wake test that consults it ──
sub(u"""  /* THE WAKE TEST. Any row on this layer that is allowed to paint right now""",
    u"""  /* ═══ P951 (3.12): THE MARK ON THE TABLE ═══
     A third ANCHOR, not a third lifetime. MARKS is one row per thing a DIE
     wears and _markDice requires match && obj.visible && chip; FX_MARKS is
     die-bound too. A table mark has no die, so it produces its own groups and
     joins at _markPlan, which is the one anchor-agnostic point in the pipeline.
     Timings in ms. The miss runs nearly twice as long as the fire: a thing
     dispersing takes longer than a thing being consumed. */
  SEAT_MS:{enter:420,fire:620,miss:1100},
  /* one row per occupying enchant. `ink` names the enchant, so the colour has
     ONE home - ENCH_ICONS - and this cannot drift from the card, the brand or
     the beat. `shape` is a silhouette, not a size: three enchants, three forms,
     because one shape in three colours reads as tooling. */
  /* P951c: FOG AND SNUFF ARE FILLS, AND THIS IS NOT A TASTE CALL.
     _paintHalo punches its subject back out of its own glow - destination-out
     on the hull, widened by GLOW.clear - so it can only ever draw an OUTLINE of
     whatever hull it is given. The brief states it plainly for the die case:
     "the ring is a ring by construction, not by occlusion." Screenshotted, that
     is exactly what happened: the cloud came out as a pale cloud-SHAPED ring
     and read as nothing, while snare's thin lens came out as a curved line and
     read as a taut cord - correct by accident of being thin.
     A cloud has to be filled, and `veil` is the only form that fills. Snuff
     goes with it for the same reason. Snare keeps `crust`, whose hard edge and
     near-zero falloff is what made it the one form that worked at full strength.
     alpha rides ON TOP of VEIL.alpha (0.42), so 1 here is 0.42 on the table. */
  SEAT_FORMS:{
    _fog:{ink:'fog',style:'veil',shape:'cloud',alpha:1},
    _snare:{ink:'snare',style:'crust',shape:'cord',alpha:1},
    _snuff:{ink:'snuff',style:'veil',shape:'wisp',alpha:0.9}
  },
  _seatInk:function(type){
    try{
      var d=ENCH_ICONS[(type||'').replace(/^_/,'')];
      if(d&&d.ink)return d.ink;
    }catch(e){}
    return '#c8b48a';
  },
  /* WHERE LANE N IS, in #screen-match CSS pixels - the space _paintHalo works
     in. Three answers, in descending order of authority. */
  _seatBounds:function(lane,sc){
    var od=[];
    try{od=(typeof G!=='undefined'&&G&&G.oppDice)||[];}catch(e){od=[];}
    var mid=function(el){
      var r=el.getBoundingClientRect();
      if(!(r.width>2))return null;
      return {cx:r.left-sc.left+r.width/2,cy:r.top-sc.top+r.height/2,
              w:r.width,h:r.height};
    };
    /* 1. MEASURED. Their own die in that lane is the position, full stop. */
    var i,b,lo=null,hi=null;
    for(i=0;i<od.length;i++){
      if(!od[i]||!od[i].el||typeof od[i].lane!=='number')continue;
      if(od[i].lane===lane){b=mid(od[i].el);if(b){b.how='die';return b;}}
      if(od[i].lane<lane&&(!lo||od[i].lane>lo.lane))lo=od[i];
      if(od[i].lane>lane&&(!hi||od[i].lane<hi.lane))hi=od[i];
    }
    /* 2. THE GAP THE ROW CLOSED OVER. A snuffed seat has no die by
       definition, and the row is justify-content:center so it shuts the gap -
       the full-grid prediction would point at empty table. The midpoint of the
       surviving neighbours IS where the missing die was. */
    if(od.length){
      var a=lo&&mid(lo.el),c=hi&&mid(hi.el);
      if(a&&c)return {cx:(a.cx+c.cx)/2,cy:(a.cy+c.cy)/2,w:a.w,h:a.h,how:'gap'};
      if(a||c){
        var one=a||c,ref=a?lo:hi,step=one.w*1.28;
        return {cx:one.cx+(a?step:-step)*Math.abs(lane-ref.lane),
                cy:one.cy,w:one.w,h:one.h,how:'edge'};
      }
    }
    /* 3. PREDICTED, for the window where their row does not exist. #throwLine
       is the datum P683 established for exactly this: the rows collapse to
       zero when empty and the cell does not. Die 13cqw, gap 3.8cqw, container
       query unit = #screen-match; measured against real seats to the pixel. */
    var tl=document.getElementById('throwLine');
    if(!tl)return null;
    var T=tl.getBoundingClientRect();
    if(!(T.width>2)||!(sc.width>10))return null;
    var cq=sc.width/100,n=0;
    try{n=((G.matchOppDice||[]).length)||0;}catch(e){}
    if(!n)n=6;
    return {cx:(T.left-sc.left)+T.width/2+(lane-(n-1)/2)*16.8*cq,
            cy:(T.top-sc.top)+T.height/2,w:13*cq,h:13*cq,how:'cell'};
  },
  /* THE SILHOUETTES. Each returns a closed polygon of [x,y] in the same space,
     which is all _paintForm asks of a hull. */
  _seatShape:function(name,b,phase,grow){
    var pts=[],i,t,e,a,k,N;
    if(name==='cloud'){
      /* three frequencies so no two lobes match, and the phase drifts */
      N=30;
      var rx=b.w*0.62*grow,ry=b.h*0.34*grow;
      for(i=0;i<N;i++){
        a=i/N*Math.PI*2;
        k=1+0.20*Math.sin(3*a+phase)+0.12*Math.sin(5*a-phase*1.7)
           +0.06*Math.sin(8*a+phase*0.5);
        pts.push([b.cx+Math.cos(a)*rx*k,b.cy+Math.sin(a)*ry*k]);
      }
      return pts;
    }
    if(name==='cord'){
      /* a lens whose profile reaches zero at both ends - that is what makes
         them points. The sag is small and constant, so it reads as a line
         under tension rather than a hanging rope. */
      N=20;
      var cx2=b.w*0.60*grow,th=b.h*0.15*grow,sag=b.h*0.09;
      for(i=0;i<=N;i++){
        t=-1+2*i/N;e=Math.pow(Math.max(0,1-t*t),0.72);
        pts.push([b.cx+t*cx2,b.cy+sag*e-th*e]);
      }
      for(i=N;i>=0;i--){
        t=-1+2*i/N;e=Math.pow(Math.max(0,1-t*t),0.72);
        pts.push([b.cx+t*cx2,b.cy+sag*e+th*e]);
      }
      return pts;
    }
    if(name==='wisp'){
      /* narrow, rising, tapering, and small enough that the seat around it
         still reads empty - the absence is the mark */
      N=18;
      var wx=b.w*0.26*grow,hh=b.h*0.74*grow,up=[],dn=[],x,y,hw;
      for(i=0;i<=N;i++){
        t=i/N;
        x=b.cx+Math.sin(t*Math.PI*1.7+phase)*wx*(0.22+0.78*t);
        y=b.cy+hh*(0.5-t);
        hw=b.w*0.085*grow*(1-0.72*t)+0.6;
        up.push([x-hw,y]);dn.push([x+hw,y]);
      }
      return up.concat(dn.reverse());
    }
    /* NO SILHOUETTE: fall back to the bounds themselves, deliberately. A
       missing form should look WRONG - a rectangle on the table is obviously
       not a cloud - rather than plausible. Same principle as P949's default. */
    return this._rectHull(b.cx-b.w/2,b.cy-b.h/2,b.w,b.h,Math.min(b.w,b.h)*0.3);
  },
  /* IS ANYTHING WORN BY THE TABLE RIGHT NOW. Geometry-free, because the wake
     test runs before the screen rect is even read. */
  _seatsLive:function(){
    try{
      if(typeof G==='undefined'||!G||!G._laneMark)return false;
      var M=G._laneMark,now=Date.now(),S=this.SEAT_MS;
      for(var L in M){
        if(!M.hasOwnProperty(L))continue;
        var m=M[L];
        if(!m||!m.shownAt||!this.SEAT_FORMS[m.t])continue;
        if(m.live)return true;
        if(m.endedAt&&(now-m.endedAt)<((m.outcome==='miss')?S.miss:S.fire))return true;
      }
    }catch(e){}
    return false;
  },
  /* THE GROUPS. Same shape _markPlan produces, plus `am` - the per-mark alpha,
     which the roster never needed because a state is either worn or not. */
  _seatPlan:function(sc){
    var groups=[];
    if(!sc||!(sc.width>10))return groups;
    var M=null;
    try{
      if(typeof G==='undefined'||!G||!G._laneMark)return groups;
      M=G._laneMark;
    }catch(e){return groups;}
    var now=Date.now(),S=this.SEAT_MS;
    for(var L in M){
      if(!M.hasOwnProperty(L))continue;
      var m=M[L];
      /* NOT LANDED, NOT PAINTED. An armed brand that has not been banked shows
         nothing at all - which is what makes 3.13's jeopardy legible. */
      if(!m||!m.shownAt)continue;
      var F=this.SEAT_FORMS[m.t];
      if(!F)continue;
      var am=1,grow=1,dx=0,dy=0,age;
      if(m.live){
        age=now-m.shownAt;
        if(age<S.enter){
          var p=age/S.enter;
          am=p;grow=0.70+0.30*p;
          /* the flourish is the bank's beat: a mark that arrived on a paying
             bank overshoots on the way in. A voided bank still lands it, flat. */
          if(m.flourish)grow*=1+0.20*Math.sin(p*Math.PI);
        }
      }else{
        if(!m.endedAt)continue;
        var miss=(m.outcome==='miss'),dur=miss?S.miss:S.fire,e=(now-m.endedAt)/dur;
        if(e>=1)continue;
        if(miss){
          /* THINS AND DRIFTS OFF, their dice untouched */
          am=(1-e)*(1-e);grow=1+0.45*e;dx=28*e;dy=-15*e;
        }else{
          /* BLOOMS, then is consumed */
          am=(e<0.28)?(1+0.55*(e/0.28)):Math.max(0,1-(e-0.28)/0.72);
          grow=1+0.32*e;
        }
      }
      if(!(am>0.02))continue;
      var b=this._seatBounds(+L,sc);
      if(!b)continue;
      var phase=((now-(m.shownAt||now))/1000)*(m.t==='_fog'?0.55:0.95);
      var hull=this._seatShape(F.shape,
        {cx:b.cx+dx,cy:b.cy+dy,w:b.w,h:b.h},phase,grow);
      if(!hull||hull.length<3)continue;
      /* P951b: A PER-FORM CEILING, and it is about the PAINTER rather than
         taste. _paintHalo composites with 'lighter', so a pale ink on this
         table adds toward white: screenshotted at full alpha, fog's grey and
         snuff's tan both blew out to a white smear while snare - the one form
         on `crust`, whose profile is a hard edge with almost no falloff -
         read exactly as intended. The two halo forms are pulled down to where
         the ink still reads as its own colour. */
      var col=this._seatInk(F.ink);
      groups.push({style:F.style,col:col,soft:col,hulls:[hull],
                   am:am*(F.alpha==null?1:F.alpha)});
    }
    return groups;
  },
  /* THE WAKE TEST. Any row on this layer that is allowed to paint right now""",
    '1 the seat-mark machinery')

# 2 ── the wake test consults the table ─────────────────────────────
sub(u"""  _marksLive:function(layer,rolling){
    var M=this.MARKS||[];""",
    u"""  _marksLive:function(layer,rolling){
    /* P951: THE TABLE WEARS MARKS TOO, and no `rolling` gate - a seat mark's
       whole job is to be there when their dice land in it, which is the one
       moment a roll is happening. */
    if(layer==='under'&&this._seatsLive())return true;
    var M=this.MARKS||[];""",
    '2 the wake test consults the table')

# 3 ── the plan carries them ────────────────────────────────────────
sub(u"""      paintSet(row.style,ds,col,soft);
    }
    return groups;
  },""",
    u"""      paintSet(row.style,ds,col,soft);
    }
    /* P951: and the marks worn by the TABLE, which have no roster row because
       they have no die. Appended here rather than painted separately because
       _planSig and _paintPlan walk the PLAN - so these are signed and drawn by
       the machinery that already exists, and a second writer to dgCanvas (which
       _drawGlow clears every frame) is avoided by construction. */
    if(layer==='under'){
      var seats=this._seatPlan(sc);
      for(var sg=0;sg<seats.length;sg++)groups.push(seats[sg]);
    }
    return groups;
  },""",
    '3 the plan carries the seat marks')

# 4 ── alpha enters the signature ───────────────────────────────────
sub(u"""      s+=g.style+'|'+g.col+'|'+g.soft+'|';""",
    u"""      /* P951: ALPHA IS PART OF THE PICTURE. It was absent because a state is
         either worn or not, so every group was opaque and the omission cost
         nothing. A seat mark fades in, blooms or thins, and without this the
         cache would hold the first frame of an animation on screen and never
         repaint it - a signature that cannot see the thing that is changing. */
      s+=g.style+'|'+g.col+'|'+g.soft+'|'+((g.am==null?1:g.am).toFixed(2))+'|';""",
    '4 alpha enters the signature')

# 5 ── and reaches the painter ──────────────────────────────────────
sub(u"""      this._paintForm(g.style,cv,x,sc,dpr,g.hulls,g.col,g.soft,1,
                      layer==='over',cheap);""",
    u"""      this._paintForm(g.style,cv,x,sc,dpr,g.hulls,g.col,g.soft,
                      (g.am==null?1:g.am),layer==='over',cheap);""",
    '5 alpha reaches the painter')

# 6 ── the pass may run with no dice on the table at all ────────────
sub(u"""    if(!anyMatch||!this._marksLive('under',rolling)){""",
    u"""    /* P951: anyMatch was a fair precondition while every mark belonged to a
       die. A seat mark outlives the dice - it lands when the player's row is
       cleared at the bank and waits for the rival's row to be dealt - so for
       the whole window it is the only thing on the surface. */
    if(!(anyMatch||this._seatsLive())||!this._marksLive('under',rolling)){""",
    '6 the pass survives an empty table')

# ── post-asserts ───────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

for fn in ('_seatBounds:function', '_seatShape:function', '_seatsLive:function',
           '_seatPlan:function', '_seatInk:function'):
    if code.count(fn) != 1:
        sys.exit('%s is not defined exactly once (nothing written)' % fn)
# THREE FORMS, THREE SHAPES - one shape recoloured is the version this ruling
# exists to prevent, so the shapes are counted rather than assumed.
# SCOPED TO THE ROSTER. A file-wide scan for shape:'...' also finds the dice
# pips - diamond, star, dot - and reported 23 silhouettes. Third time this
# session that a check searched a space far wider than its own claim; the region
# is the unit, the token is not.
_sfStart = code.index('SEAT_FORMS:{')
_sfEnd = code.index('}', code.index('_snuff:{', _sfStart))
shapes = re.findall(r"shape:'([a-z]+)'", code[_sfStart:_sfEnd])
if sorted(shapes) != ['cloud', 'cord', 'wisp']:
    sys.exit('expected three distinct silhouettes, found %s (nothing written)'
             % sorted(shapes))
for shp in ('cloud', 'cord', 'wisp'):
    if ("name==='%s'" % shp) not in code:
        sys.exit('the %s silhouette has no branch (nothing written)' % shp)
# BOTH ENDINGS have their own curve, or 3.3 is not satisfied
if 'S.miss' not in code or 'S.fire' not in code:
    sys.exit('the two endings do not have separate durations (nothing written)')
if not re.search(r'if\(miss\)\{', code):
    sys.exit('the miss has no branch of its own (nothing written)')
# the wake and the precondition both widened - one without the other is a mark
# that paints only while dice happen to be present
if code.count('this._seatsLive()') != 2:
    sys.exit('expected _seatsLive at both the wake test and the precondition, '
             'found %d (nothing written)' % code.count('this._seatsLive()'))
# alpha reaches BOTH the signature and the painter, or it animates once and
# then caches, or it is signed and never drawn
if 'g.am==null?1:g.am' not in code:
    sys.exit('alpha does not reach the painter (nothing written)')
if "+((g.am==null?1:g.am).toFixed(2))+" not in code:
    sys.exit('alpha is not in the signature (nothing written)')
# the ink has ONE home
if "ENCH_ICONS[(type||'').replace" not in code:
    sys.exit('the ink is not read from ENCH_ICONS (nothing written)')
if re.search(r"SEAT_FORMS[\s\S]{0,400}ink:'#", code):
    sys.exit('a seat form carries a literal colour instead of naming its '
             'enchant (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
