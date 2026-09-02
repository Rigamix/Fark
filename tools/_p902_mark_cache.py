# -*- coding: utf-8 -*-
u"""P902: the mark layer repaints only when a marked hull actually changed.

WHAT REGRESSED, precisely. Before P895 `_drawGlow` slept unless a die carried
`selected` and skipped entirely while `_rolling()`, so during a rival's turn it
was asleep for the whole turn. States are `through:true` - correct, a state must
survive a roll - and the consequence measured in apv_fx_cost: one dampened rival
die keeps the pass awake, 1 paint call against 0 before, every frame, for the
whole turn. Nothing about the mark changes between those frames. The blur chain
runs anyway.

That is sustained churn over the scratch chain rather than a larger allocation,
and churn is the profile that makes a renderer start shedding decoded images.

THE FIX IS A CACHE, NOT SURGERY. Build the paint plan - which rows, which dice,
which inks, which hulls - take its signature, and if it matches the last frame's
and the canvas still holds that paint, return without clearing and without
painting. Same painter, same output, same dials. The sleep the guard used to
provide comes back for exactly the case that lost it: a mark that has not moved.

WHILE THE DICE ARE ACTUALLY TUMBLING the hulls change every frame and it
repaints, which is right - that is the mark following its die. A rival's turn is
mostly settled frames, so that is where the saving is.

THE SIGNATURE IS ROUNDED TO A TENTH OF A CSS PIXEL. Below that no difference is
visible, and raw float jitter from the projection would invalidate the cache
every frame for nothing - a cache that never hits is just a slower painter.

BEATS BYPASS IT. A beat rides an envelope, so its alpha moves every frame and a
signature including it would never match. Rather than pretend otherwise, the
state pass takes the cached path only when no beat is live. Simple, and it
cannot go subtly stale: the one thing that animates is the one thing excluded.

WHAT INVALIDATES, and each is in the signature rather than hoped for: the
canvas size, the set of rows, the dice each row matches, every resolved ink, and
every hull coordinate. A class added or removed changes the dice list; a die
moving changes its hull; a reroll tag changes an ink.
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


# ══ 1. _drawMarks splits into plan + paint ═════════════════════════
sub(u"""  _drawMarks:function(layer,cv,x,sc,dpr,rolling){
    var self=this,G=this.GLOW,M=this.MARKS||[],n=0;
    /* P899: collect a set's hulls and paint them once. Pulled out because a
       row can now resolve its ink PER DIE, and a parameterised row cannot
       share the one-call-per-row bound - it is one call per distinct ink
       present instead, which is the bound with beats and tagged states in the
       same table. */
    var paintSet=function(style,list,col,soft){
      var hulls=[],i,h;
      for(i=0;i<list.length;i++){
        h=self._hullOf(list[i],sc,G.grow);
        if(h)hulls.push(h);
      }
      if(!hulls.length)return 0;
      self._paintForm(style,cv,x,sc,dpr,hulls,col,soft,1,layer==='over');
      return 1;
    };
    for(var r=0;r<M.length;r++){""",
    u"""  /* P902: THE PLAN, so a pass can ask "has anything changed?" before it
     repaints. Exactly the grouping _drawMarks used to do inline - one entry per
     distinct ink present, hulls collected - but returned instead of painted, so
     the same object can be hashed and then drawn without doing the work twice.
     _drawMarks below is now these two steps in a row, so every existing caller
     behaves as before. */
  _markPlan:function(layer,sc,rolling){
    var self=this,G=this.GLOW,M=this.MARKS||[],groups=[];
    var addSet=function(style,list,col,soft){
      var hulls=[],i,h;
      for(i=0;i<list.length;i++){
        h=self._hullOf(list[i],sc,G.grow);
        if(h)hulls.push(h);
      }
      if(hulls.length)groups.push({style:style,col:col,soft:soft,hulls:hulls});
    };
    var paintSet=addSet;
    for(var r=0;r<M.length;r++){""",
    '1a the plan builder')

sub(u"""        for(kk in byInk)n+=paintSet(row.style,byInk[kk],kk,kk);
        continue;
      }""",
    u"""        for(kk in byInk)paintSet(row.style,byInk[kk],kk,kk);
        continue;
      }""",
    '1b the tagged branch collects')

sub(u"""      n+=paintSet(row.style,ds,col,soft);
    }
    return n;
  },""",
    u"""      paintSet(row.style,ds,col,soft);
    }
    return groups;
  },
  /* THE SIGNATURE OF A PAINT. Rounded to a tenth of a CSS pixel: below that no
     difference is visible, and the raw floats out of the projection jitter
     enough to invalidate every frame - a cache that never hits is only a
     slower painter. Everything that can change the picture is in here: the
     rows present, the dice each matched, every resolved ink, every hull. */
  _planSig:function(groups){
    var s='',i,j,k,g,h;
    for(i=0;i<groups.length;i++){
      g=groups[i];
      s+=g.style+'|'+g.col+'|'+g.soft+'|';
      for(j=0;j<g.hulls.length;j++){
        h=g.hulls[j];
        for(k=0;k<h.length;k++)s+=h[k][0].toFixed(1)+','+h[k][1].toFixed(1)+' ';
        s+=';';
      }
      s+='#';
    }
    return s;
  },
  _paintPlan:function(groups,cv,x,sc,dpr,layer){
    for(var i=0;i<groups.length;i++){
      var g=groups[i];
      this._paintForm(g.style,cv,x,sc,dpr,g.hulls,g.col,g.soft,1,layer==='over');
    }
    return groups.length;
  },
  _drawMarks:function(layer,cv,x,sc,dpr,rolling){
    return this._paintPlan(this._markPlan(layer,sc,rolling),cv,x,sc,dpr,layer);
  },""",
    '1c the signature and the painter')

# ══ 2. the under pass consults it ══════════════════════════════════
sub(u"""    cv=this._glowCv();if(!cv)return;
    this._glowInk=true;
    var scEl=document.getElementById('screen-match');
    var sc=scEl.getBoundingClientRect();
    if(sc.width<10)return;""",
    u"""    cv=this._glowCv();if(!cv)return;
    var scEl=document.getElementById('screen-match');
    if(!scEl)return;
    var sc=scEl.getBoundingClientRect();
    if(sc.width<10)return;""",
    '2a the under pass stops claiming ink before it has any')

sub(u"""    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    this._drawMarks('under',cv,x,sc,dpr,rolling);
  },""",
    u"""    /* P902: REPAINT ONLY WHAT CHANGED. Through:true is what a state needs and
       what cost this pass its sleep - a dampened rival die kept the whole blur
       chain running every frame for a mark that had not moved a pixel. The plan
       is built first (hull projection, not a blur), hashed, and compared; an
       identical frame returns without clearing and without painting, and the
       canvas still holds the paint that signature describes. */
    var plan=this._markPlan('under',sc,rolling);
    var sig=cv.width+'x'+cv.height+'|'+this._planSig(plan);
    if(this._glowInk&&sig===this._glowSig)return;
    this._glowSig=sig;
    this._glowInk=true;
    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    this._paintPlan(plan,cv,x,sc,dpr,'under');
  },""",
    '2b the under cache')

sub(u"""      if(cv&&this._glowInk){
        var c0=cv.getContext('2d');
        c0.setTransform(1,0,0,1,0,0);c0.clearRect(0,0,cv.width,cv.height);
        this._glowInk=false;
      }
      return;""",
    u"""      if(cv&&this._glowInk){
        var c0=cv.getContext('2d');
        c0.setTransform(1,0,0,1,0,0);c0.clearRect(0,0,cv.width,cv.height);
        this._glowInk=false;
        this._glowSig='';/* the surface is empty; the next wake must paint */
      }
      return;""",
    '2c sleeping drops the signature')

# ══ 3. the over pass, with beats exempt ════════════════════════════
sub(u"""      if(cv&&this._stateInk){
        var c0=cv.getContext('2d');
        c0.setTransform(1,0,0,1,0,0);c0.clearRect(0,0,cv.width,cv.height);
        this._stateInk=false;
      }
      return;""",
    u"""      if(cv&&this._stateInk){
        var c0=cv.getContext('2d');
        c0.setTransform(1,0,0,1,0,0);c0.clearRect(0,0,cv.width,cv.height);
        this._stateInk=false;
        this._stateSig='';/* same as the glow: an empty surface must repaint */
      }
      return;""",
    '3a the over sleep drops its signature')

sub(u"""    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    this._stateInk=true;
    var G=this.GLOW;
    this._drawMarks('over',cv,x,sc,dpr,rolling);""",
    u"""    /* P902: the same cache as the glow, with ONE exemption stated rather than
       hidden - a beat rides an envelope, so its alpha moves every frame and no
       signature that included it could ever match. Rather than pretend, the
       cached path is taken only when no beat is live: the one thing that
       animates is the one thing excluded, which cannot go subtly stale. */
    var plan=this._markPlan('over',sc,rolling);
    if(!beats.length){
      var sig=cv.width+'x'+cv.height+'|'+this._planSig(plan);
      if(this._stateInk&&sig===this._stateSig)return;
      this._stateSig=sig;
    }else{
      this._stateSig='';/* a beat is animating; the next still frame repaints */
    }
    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    this._stateInk=true;
    var G=this.GLOW;
    this._paintPlan(plan,cv,x,sc,dpr,'over');""",
    '3b the over cache')

# ── post-asserts, comments stripped ─────────────────────────────────
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)

for need, n in (('_markPlan:function', 1), ('_planSig:function', 1),
                ('_paintPlan:function', 1), ('_drawMarks:function', 1)):
    if code.count(need) != n:
        sys.exit('%s is not defined exactly %d time(s) (nothing written)' % (need, n))
# the plan must be built BEFORE the clear in both passes, or the cache would
# compare a signature against a surface it has already wiped
for fn, endm, sigvar in (('_drawGlow:function', '_tableRoot:function', '_glowSig'),
                         ('_drawStates:function', '_stateCv:function', '_stateSig')):
    i = code.index(fn)
    j = code.index(endm, i) if endm in code[i:] else len(code)
    body = code[i:j]
    if '_markPlan(' not in body:
        sys.exit('%s does not build a plan (nothing written)' % fn)
    if body.index('_markPlan(') > body.index('clearRect(0,0,sc.width'):
        sys.exit('%s clears before it plans (nothing written)' % fn)
    if body.count(sigvar) < 3:
        sys.exit('%s does not store, compare and drop %s (nothing written)'
                 % (fn, sigvar))
# an early return on a cache hit must exist in both
if code.count("sig===this._glowSig)return") != 1:
    sys.exit('the under cache has no early return (nothing written)')
if code.count("sig===this._stateSig)return") != 1:
    sys.exit('the over cache has no early return (nothing written)')
# beats must bypass, or the one animating thing freezes
_ds = code.index('_drawStates:function')
if 'if(!beats.length){' not in code[_ds:_ds + 3000]:
    sys.exit('beats do not bypass the cache - they would freeze '
             '(nothing written)')
# and the sleep paths must clear the signature, or a wake shows a stale surface
if code.count("_glowSig=''") != 1 or code.count("_stateSig=''") != 2:
    sys.exit('a sleep path does not drop its signature (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
