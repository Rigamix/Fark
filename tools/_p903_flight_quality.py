# -*- coding: utf-8 -*-
u"""P903: a mark paints cheaper while its die is in the air, and snaps back at
settle - the half of the load the cache cannot reach.

THE CACHE COVERS THE SETTLED FRAMES AND ONLY THOSE. During a roll every hull
moves, so every frame is a miss: about 42 frames of full blur chain per throw,
and a rival turn of four or five throws is a couple of hundred frames that used
to be zero, because before P895 the pass skipped rolls entirely. The settled
case is now free; this is the rest.

`through:true` IS ABOUT PRESENCE, NOT FIDELITY. What surviving a roll means is
that there is no frame where the mark is absent - that is the whole of the
requirement. It does not mean full-quality repainting on every frame of a
flight, and §13 rule 4 says a state is for the settled read: nobody is studying
a CRUST on a tumbling die.

WHAT GETS CHEAPER, and it is the dominant term rather than a guess at one.
blurOnto builds its mip chain once whatever `passes` says - the pyramid down
and back up is about 1.7 screens of traffic - and then composites the result
`passes` times, one full screen each. At the shipped dials that is softPasses 1
plus rimPasses 5, so SIX full-screen composites against 3.4 for the pyramid.
Cutting both to 1 while flying takes the composites from 6 to 2, which is the
single biggest lever available without touching a scratch surface's size.

NO REALLOCATION. The obvious alternative - a smaller scratch while flying -
means resizing the shared canvases twice per throw, and a resize both clears and
reallocates. Trading churn for churn is not a fix.

THE QUALITY LEVEL IS IN THE SIGNATURE, so the transition back is guaranteed
rather than hoped for: the last flying frame and the first settled one differ in
the signature even if the dice happened to stop where they were, so settle
always repaints at full quality.

TABLE-WIDE, NOT PER-DIE. `rolling` is true when ANY match die is in the air, so
a frozen die that is standing still also paints cheap while its neighbours
tumble. That is deliberate and it is what the corollary says: during a throw
nothing on the table is being read closely, and a per-die test would make the
same frame two different qualities for no gain anyone can see.

AND ONE THING NOT CHANGED. Beats keep full quality. A beat is the notification
that something happened, it is bounded by its own clock, and there are few of
them; making the loud short thing quieter to save four composites is the wrong
trade.
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


# ══ 1. the dial ════════════════════════════════════════════════════
sub(u"""  VEIL:{alpha:0.42},""",
    u"""  VEIL:{alpha:0.42},
  /* P903: THE FLIGHT DIAL - what a mark costs while its die is in the air.
     through:true is about PRESENCE, not fidelity: the requirement is that no
     frame is missing the mark, and §13 rule 4 says a state is for the settled
     read. Nobody studies a CRUST on a tumbling die.
     These are the pass counts, and passes are the dominant term: blurOnto
     builds its pyramid once whatever this says (~1.7 screens of traffic) and
     then composites the result once per pass, a full screen each time. The
     shipped 1 + 5 is six full-screen composites; 1 + 1 is two. */
  FLIGHT:{softPasses:1,rimPasses:1},""",
    '1 the flight dial')

# ══ 2. _paintHalo honours per-call pass counts ═════════════════════
sub(u"""    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:G.sx,sy:G.sy});});
    blurOnto(gx,SOFTR,G.softPasses||1);""",
    u"""    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:G.sx,sy:G.sy});});
    /* P903: the caller may spend less here - see FLIGHT. The pyramid is built
       either way; `passes` is how many times its result is composited, which
       is a full screen each and the biggest single cost in this function. */
    blurOnto(gx,SOFTR,(opts&&opts.softPasses)||G.softPasses||1);""",
    '2a the soft pass count')

sub(u"""    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,G.rimPasses||1);""",
    u"""    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,(opts&&opts.rimPasses)||G.rimPasses||1);""",
    '2b the rim pass count')

# ══ 3. _paintForm carries it, and stops aliasing the CRUST dial ════
sub(u"""    var AM=(alphaMul==null?1:alphaMul);
    /* `over` is the caller's canvas, not the form's - see the third-case note
       in _paintHalo. A VEIL needs nothing: it is a fill on the hull and has no
       geometry outside the silhouette to cut. */
    if(style==='crust'){
      var C=this.CRUST;
      this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM,C.line,
        over?{soft:C.soft,rim:C.rim,strength:C.strength,overSubject:1}:C);
      return;
    }""",
    u"""    var AM=(alphaMul==null?1:alphaMul);
    /* `over` is the caller's canvas, not the form's - see the third-case note
       in _paintHalo. A VEIL needs nothing: it is a fill on the hull and has no
       geometry outside the silhouette to cut.
       `cheap` is P903's flight quality, and it is a property of the MOMENT
       rather than of the form or the canvas - the third independent thing this
       call carries, so they are assembled into one opts object here instead of
       being spelled out per branch. */
    var F=cheap?this.FLIGHT:null;
    var opt=function(base){
      var o=base||{};
      if(over)o.overSubject=1;
      if(F){o.softPasses=F.softPasses;o.rimPasses=F.rimPasses;}
      for(var k in o)return o;
      return undefined;/* nothing to say: keep the old undefined-opts path */
    };
    if(style==='crust'){
      var C=this.CRUST;
      /* a FRESH object, never the shared CRUST dial itself - it used to be
         passed straight through as opts, so anything that wrote to opts would
         have retuned every crust in the game */
      this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM,C.line,
        opt({soft:C.soft,rim:C.rim,strength:C.strength}));
      return;
    }""",
    '3a the crust branch')

sub(u"""  _paintForm:function(style,cv,x,sc,dpr,hulls,col,soft,alphaMul,over){""",
    u"""  _paintForm:function(style,cv,x,sc,dpr,hulls,col,soft,alphaMul,over,cheap){""",
    '3b the signature')

sub(u"""    this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM,undefined,
                    over?{overSubject:1}:undefined);
  },""",
    u"""    this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM,undefined,opt());
  },""",
    '3c the rim branch')

# ══ 4. the plan painter passes it through ══════════════════════════
sub(u"""  _paintPlan:function(groups,cv,x,sc,dpr,layer){
    for(var i=0;i<groups.length;i++){
      var g=groups[i];
      this._paintForm(g.style,cv,x,sc,dpr,g.hulls,g.col,g.soft,1,layer==='over');
    }
    return groups.length;
  },
  _drawMarks:function(layer,cv,x,sc,dpr,rolling){
    return this._paintPlan(this._markPlan(layer,sc,rolling),cv,x,sc,dpr,layer);
  },""",
    u"""  _paintPlan:function(groups,cv,x,sc,dpr,layer,cheap){
    for(var i=0;i<groups.length;i++){
      var g=groups[i];
      this._paintForm(g.style,cv,x,sc,dpr,g.hulls,g.col,g.soft,1,
                      layer==='over',cheap);
    }
    return groups.length;
  },
  _drawMarks:function(layer,cv,x,sc,dpr,rolling){
    return this._paintPlan(this._markPlan(layer,sc,rolling),cv,x,sc,dpr,layer,
                           rolling);
  },""",
    '4 the plan painter')

# ══ 5. both passes: quality in the signature, quality in the paint ═
sub(u"""    var plan=this._markPlan('under',sc,rolling);
    var sig=cv.width+'x'+cv.height+'|'+this._planSig(plan);
    if(this._glowInk&&sig===this._glowSig)return;
    this._glowSig=sig;
    this._glowInk=true;
    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    this._paintPlan(plan,cv,x,sc,dpr,'under');""",
    u"""    var plan=this._markPlan('under',sc,rolling);
    /* P903: the quality is IN the signature. The last flying frame and the
       first settled one then differ even if the dice stopped exactly where
       they were, so the snap back to full quality is guaranteed rather than
       inferred from the hulls having moved. */
    var sig=(rolling?'F':'S')+'|'+cv.width+'x'+cv.height+'|'+this._planSig(plan);
    if(this._glowInk&&sig===this._glowSig)return;
    this._glowSig=sig;
    this._glowInk=true;
    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    this._paintPlan(plan,cv,x,sc,dpr,'under',rolling);""",
    '5a the under pass')

sub(u"""    var plan=this._markPlan('over',sc,rolling);
    if(!beats.length){
      var sig=cv.width+'x'+cv.height+'|'+this._planSig(plan);""",
    u"""    var plan=this._markPlan('over',sc,rolling);
    if(!beats.length){
      var sig=(rolling?'F':'S')+'|'+cv.width+'x'+cv.height+'|'+this._planSig(plan);""",
    '5b the over signature')

sub(u"""    this._stateInk=true;
    var G=this.GLOW;
    this._paintPlan(plan,cv,x,sc,dpr,'over');""",
    u"""    this._stateInk=true;
    var G=this.GLOW;
    this._paintPlan(plan,cv,x,sc,dpr,'over',rolling);""",
    '5c the over paint')

# ── post-asserts, comments stripped ─────────────────────────────────
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)

if code.count('FLIGHT:{softPasses:1,rimPasses:1}') != 1:
    sys.exit('the flight dial is not defined exactly once (nothing written)')
# the pass counts must be overridable at BOTH blur builds, or half the saving
# silently is not there
if code.count('(opts&&opts.softPasses)||G.softPasses') != 1:
    sys.exit('the soft pass count is not overridable (nothing written)')
if code.count('(opts&&opts.rimPasses)||G.rimPasses') != 1:
    sys.exit('the rim pass count is not overridable (nothing written)')
# the shared CRUST dial must no longer be handed out as an opts object
if 'strength:C.strength,overSubject:1}:C)' in code:
    sys.exit('the CRUST dial is still passed through as opts (nothing written)')
# quality has to reach the painter AND the signature, in both passes
if code.count("(rolling?'F':'S')") != 2:
    sys.exit('the quality flag is not in both signatures (nothing written)')
if code.count("dpr,'under',rolling)") != 1 or code.count("dpr,'over',rolling)") != 1:
    sys.exit('a pass does not hand its quality to the painter (nothing written)')
# and _paintForm must actually take it
if 'alphaMul,over,cheap)' not in code:
    sys.exit('_paintForm does not take the flight flag (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
