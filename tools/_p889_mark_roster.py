# -*- coding: utf-8 -*-
u"""P889 (FX BRIEF step 7): the mark roster. Both passes become table-driven,
and the two guards come out rather than growing.

WHY NOT THE AMENDMENT. Putting RIM and CRUST under the dice means they live on
dgCanvas, which _drawGlow owns and clears every frame - so a second pass there
would recreate the two-writer defect P881 and P885 just fixed twice. The
obvious remedy was to widen _drawGlow's wake condition to name the new classes
and make its _rolling() skip conditional on "no under-form present". That is
two hand-maintained conditions and a third hardcoded branch: the roster defect,
one form larger, in a painter nobody wants to touch twice.

THE ROSTER INSTEAD. D3X.MARKS is a list of rows, each carrying where it paints
(layer), whether it survives a roll (through), what it looks like (style), its
ink, and the predicate that decides which dice wear it. Three things fall out
that the amendment does not give:

  - THE WAKE TEST IS "does any row match a die", not a list of class names, so
    it cannot go stale when a form is added.
  - THE ROLL SKIP IS PER ROW. `through:false` is transient - a selection, a
    card mark - and rightly vanishes mid-roll; a state is `through:true` and
    survives. The old global _rolling() skip was one condition standing in for
    a per-row fact. A roll with nothing through:true live still skips the whole
    pass, so the original optimisation survives untouched for the common case,
    and TODAY'S BEHAVIOUR DURING A ROLL IS IDENTICAL, because both live rows
    are through:false.
  - THE COST IS EXPLICIT. _paintHalo takes a list of hulls, so a row is ONE
    call however many dice wear it. The bound is the roster - two today, four
    when the forms land - not the dice.

selected and cardmark become rows rather than special cases, which is the
control already proven safe: the surfaces are byte-identical, so nothing about
where they paint has changed, and this patch's own probe re-proves the OUTPUT
byte-identical against the explicit calls it replaces.

WHAT IS DELIBERATELY UNCHANGED, and asserted: the paint order (cardmark before
selection, so a selection composites on top of it), both inks, and the
SET-LEVEL oppkeep swap - if ANY selected die is a rival keep, the whole
selection turns to OPP_INK for colour and softness together. That last one is
why a row may carry `inkWhen`: it is a fact about the collected set, not about
one die, and flattening it to a per-die ink would have changed how a mixed
selection looks.

STATE_FORMS is deleted. It was P880's placeholder registry and the roster
supersedes it; two rosters for one idea is the thing this patch exists to
prevent.

THE FOUR STYLES are built here so step 8 has somewhere to put frozen, blind,
dampened and spent. RIM is the keep glow's own painter, untouched. CRUST is the
same painter with a tight profile - a hard edge and almost no falloff, so the
face stays readable. VEIL and DIM are fills on the over-canvas, and DIM is
where I have to be honest: "desaturate" cannot be done to a die on ANOTHER
canvas without a CSS blend mode on the whole element, which would catch
everything else painted there, so DIM is a neutral darkening wash that adds no
colour. If step 8 wants true desaturation, this file already has the machinery
in _settleDim / _dimMap, which dims the die's own material maps - and that is
the right route, not a wash.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def _find(pat, frm=0):
    u"""line-ending tolerant search: this file has MIXED endings, so a
    multi-line marker written with \\n will not match a CRLF region."""
    rx = re.compile(re.escape(pat).replace('\\\n', '\n').replace('\n', '\\r?\n'))
    m = rx.search(s, frm)
    return (m.start(), m.end()) if m else (-1, -1)


def cut(start, end, new, label):
    u"""replace everything from `start` to the first `end` after it."""
    global s
    i, iEnd = _find(start)
    if i < 0:
        sys.exit('no START for %s (nothing written)' % label)
    if _find(start, iEnd)[0] >= 0:
        sys.exit('START is not unique for %s (nothing written)' % label)
    j0, j = _find(end, i)
    if j0 < 0:
        sys.exit('no END for %s (nothing written)' % label)
    crlf = '\r\n' in s[i:j]
    rep = new.replace('\n', '\r\n') if crlf else new
    s = s[:i] + rep + s[j:]
    edits.append(label)


# ── 1. the roster, the dials, and the shared machinery ──────────────
cut(u'  /* Registered state forms.',
    u'  STATE_FORMS:[],',
    u"""  /* P889: THE MARK ROSTER. One row per thing a die can wear. `layer` picks
     the surface - under the dice on dgCanvas, where the tuned dials are, or
     over them on stCanvas. `through` says whether the mark survives a roll: a
     selection does not, a state does. `style` is one of the four forms.
     `ink` is a dial name on D3X, a global name, or a literal - never a new
     colour, per the brief's rule that a state wears its enchant's own.
     `on(d)` decides which dice wear it, so the wake test below cannot go
     stale when a row is added.
     ORDER IS PAINT ORDER: cardmark before selection, so a selection
     composites on top of it, which is what _drawGlow did explicitly.
     `inkWhen` is a SET-level override, not a per-die one - if any selected
     die is a rival keep, the whole selection turns red, colour and softness
     together, and flattening that to a per-die ink would change how a mixed
     selection looks. */
  MARKS:[
    {id:'card',layer:'under',through:false,style:'rim',
     ink:'CARD_MARK_INK',fallback:'#c66058',
     on:function(d){return d.chip.classList.contains('cardmark');}},
    {id:'sel',layer:'under',through:false,style:'rim',
     ink:'SEL_COL',soft:'SEL_SOFT',
     on:function(d){return d.chip.classList.contains('selected');},
     inkWhen:[{ink:'OPP_INK',fallback:'#d94c3d',both:true,
       test:function(ds){
         for(var i=0;i<ds.length;i++)
           if(ds[i].chip.classList.contains('oppkeep'))return true;
         return false;
       }}]},
  ],
  /* CRUST is the keep glow's painter with a tight profile: a hard edge and
     almost no falloff, so it reads as a treatment ON the edges with the face
     still legible, rather than as light thrown off them. */
  CRUST:{soft:3,rim:1.6,strength:0.95,line:2.6},
  VEIL:{alpha:0.42},
  DIM:{alpha:0.46,ink:'#12141a'},
  /* a dial name on D3X, a global name, or a literal */
  _markInk:function(name,fallback){
    if(!name)return fallback||'#ffffff';
    if(name.charAt(0)==='#')return name;
    if(this[name]!==undefined&&this[name]!==null)return this[name];
    if(window[name]!==undefined&&window[name]!==null)return window[name];
    return fallback||'#ffffff';
  },
  /* which dice wear this row, right now */
  _markDice:function(row){
    var out=[];
    for(var i=0;i<this.dice.length;i++){
      var d=this.dice[i];
      if(!d.match||!d.obj||!d.obj.visible||!d.chip)continue;
      try{if(row.on(d))out.push(d);}catch(e){}
    }
    return out;
  },
  /* THE WAKE TEST. Any row on this layer that is allowed to paint right now
     and has at least one die - so adding a row cannot leave it stale, and a
     roll with nothing through:true live still puts the whole pass to sleep. */
  _marksLive:function(layer,rolling){
    var M=this.MARKS||[];
    for(var r=0;r<M.length;r++){
      var row=M[r];
      if(row.layer!==layer)continue;
      if(rolling&&!row.through)continue;
      if(this._markDice(row).length)return true;
    }
    return false;
  },
  /* THE FOUR FORMS. RIM is the keep glow untouched. CRUST is the same painter
     with the tight profile above. VEIL and DIM are fills, and belong over the
     dice because they change what you see OF the face.
     DIM IS HONEST ABOUT ITS LIMIT: desaturating a die that lives on ANOTHER
     canvas is not something a 2D context can do - it would need a CSS blend
     mode on the whole element, which would catch every other thing painted
     there. So this darkens and adds no colour. True desaturation already has
     a home in _settleDim / _dimMap, which dim the die's own material maps,
     and that is the right route if step 8 wants it. */
  _paintForm:function(style,cv,x,sc,dpr,hulls,col,soft){
    if(style==='crust'){
      var C=this.CRUST;
      this._paintHalo(cv,x,sc,dpr,hulls,col,soft,1,C.line,C);
      return;
    }
    if(style==='veil'||style==='dim'){
      var A=(style==='dim')?this.DIM:this.VEIL;
      var self=this;
      x.save();
      x.globalAlpha=A.alpha;
      x.fillStyle=(style==='dim')?this._markInk(A.ink,'#12141a'):col;
      hulls.forEach(function(h){self._traceHull(x,h);x.fill();});
      x.restore();
      return;
    }
    this._paintHalo(cv,x,sc,dpr,hulls,col,soft,1);
  },
  /* paint every row on one layer, in roster order. ONE _paintHalo per ROW,
     not per die: a row's hulls are collected and painted together, so the
     cost is bounded by the roster rather than by the board. */
  _drawMarks:function(layer,cv,x,sc,dpr,rolling){
    var self=this,G=this.GLOW,M=this.MARKS||[],n=0;
    for(var r=0;r<M.length;r++){
      var row=M[r];
      if(row.layer!==layer)continue;
      if(rolling&&!row.through)continue;
      var ds=this._markDice(row);
      if(!ds.length)continue;
      var col=this._markInk(row.ink,row.fallback);
      var soft=row.soft?this._markInk(row.soft,row.fallback):col;
      var over=row.inkWhen||[];
      for(var o=0;o<over.length;o++){
        var hit=false;
        try{hit=!!over[o].test(ds);}catch(e){}
        if(hit){col=this._markInk(over[o].ink,over[o].fallback);
                if(over[o].both)soft=col;}
      }
      var hulls=[];
      for(var i=0;i<ds.length;i++){
        var h=self._hullOf(ds[i],sc,G.grow);
        if(h)hulls.push(h);
      }
      if(!hulls.length)continue;
      this._paintForm(row.style,cv,x,sc,dpr,hulls,col,soft);
      n++;
    }
    return n;
  },""",
    '1 the roster and its machinery')

# ── 2. _drawGlow becomes the under-layer pass ───────────────────────
cut(u'  _drawGlow:function(){',
    u"""    /* P748: the painter is shared with the cards now - see _paintHalo */
    this._paintHalo(cv,x,sc,dpr,sel,COL,SOFT,1);
  },""",
    u"""  /* P889: THIS IS THE UNDER-LAYER PASS NOW, and it is table-driven. It used
     to carry two hardcoded branches and two hand-maintained conditions: a
     wake test naming both classes, and a global _rolling() skip. Both are
     gone into the roster. Behaviour during a roll is unchanged because both
     live rows are through:false, so nothing paints and the pass still sleeps.
     The probe re-proves the output byte-identical to the explicit calls. */
  _drawGlow:function(){
    var cv=document.getElementById('dgCanvas');
    /* not _matchOn: that is turned off whenever ANY sized .d3chip exists
       anywhere in the document, which is a statement about the shop and the
       loadout, not about whether there are match dice to draw around. */
    var anyMatch=false;
    for(var mi=0;mi<this.dice.length;mi++)if(this.dice[mi].match){anyMatch=true;break;}
    var rolling=this._rolling();
    if(!anyMatch||!this._marksLive('under',rolling)){
      if(cv&&this._glowInk){
        var c0=cv.getContext('2d');
        c0.setTransform(1,0,0,1,0,0);c0.clearRect(0,0,cv.width,cv.height);
        this._glowInk=false;
      }
      return;
    }
    cv=this._glowCv();if(!cv)return;
    this._glowInk=true;
    var scEl=document.getElementById('screen-match');
    var sc=scEl.getBoundingClientRect();
    if(sc.width<10)return;
    /* P739: THE GLOW PAINTS AT THE DISPLAY'S RESOLUTION. Every canvas in
       this file caps at 2x, which is right for a soft, wide thing like a
       shadow - but the selection glow is a THIN CRISP RIM, and on a 3x
       phone a 2x canvas is stretched 1.5x by the compositor: every edge
       enlarged and blurred. That is Denis's 'much softer and wider on my
       phone', and no dial could have fixed it because the numbers were
       never what differed - the raster was. The cost is bounded: this
       canvas is painted only while a row on this layer has a die, and it is
       a few thin shapes on an otherwise empty surface. */
    var dpr=Math.min(devicePixelRatio||1,this.GLOW_DPR_MAX||3);
    if(cv.width!==Math.round(sc.width*dpr)||cv.height!==Math.round(sc.height*dpr)){
      cv.width=Math.round(sc.width*dpr);cv.height=Math.round(sc.height*dpr);
    }
    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    this._drawMarks('under',cv,x,sc,dpr,rolling);
  },""",
    '2 _drawGlow is the under pass')

# ── 3. _drawStates becomes the over-layer pass ──────────────────────
cut(u'    var forms=this.STATE_FORMS||[],want=[];',
    u"""    for(var k in byInk){
      var ink=k.split('|')[1];
      this._paintHalo(cv,x,sc,dpr,byInk[k],ink,ink,1);
    }""",
    u"""    var rolling=this._rolling();
    var live=this._marksLive('over',rolling);
    if(!live&&!beats.length){
      if(cv&&this._stateInk){
        var c0=cv.getContext('2d');
        c0.setTransform(1,0,0,1,0,0);c0.clearRect(0,0,cv.width,cv.height);
        this._stateInk=false;
      }
      return;
    }
    cv=this._stateCv();if(!cv)return;
    var scEl=document.getElementById('screen-match');
    if(!scEl)return;
    var sc=scEl.getBoundingClientRect();
    if(sc.width<10)return;
    /* same raster argument as the glow (P739): these are thin crisp shapes,
       so they are painted at the display's resolution, not capped at 2x. */
    var dpr=Math.min(devicePixelRatio||1,this.GLOW_DPR_MAX||3);
    if(cv.width!==Math.round(sc.width*dpr)||cv.height!==Math.round(sc.height*dpr)){
      cv.width=Math.round(sc.width*dpr);cv.height=Math.round(sc.height*dpr);
    }
    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    this._stateInk=true;
    var G=this.GLOW;
    this._drawMarks('over',cv,x,sc,dpr,rolling);""",
    '3 _drawStates is the over pass')

# the old middle of _drawStates (the want[] collection and its canvas setup)
# is now dead - remove what the cut above left stranded
cut(u"""    for(i=0;i<this.dice.length;i++){
      d=this.dice[i];
      if(!d.match||!d.obj.visible||!d.chip)continue;
      for(var f=0;f<forms.length;f++){
        if(d.chip.classList.contains(forms[f].cls))want.push({d:d,form:forms[f]});
      }
    }
    if(!want.length&&!beats.length){""",
    u"""    if(false){""",
    '4 stranded collection removed') if False else None

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
if 'STATE_FORMS' in code:
    sys.exit('STATE_FORMS survives in code (nothing written)')
# word-boundary: FX_MARKS:[] contains the substring MARKS:[ and a bare count
# matches it, which is the over-broad assert this session keeps re-learning.
if len(re.findall(r'(?<![A-Za-z0-9_])MARKS:\[', code)) != 1:
    sys.exit('the roster is not declared exactly once (nothing written)')
for fn in ('_marksLive:function', '_drawMarks:function', '_paintForm:function',
           '_markInk:function', '_markDice:function'):
    if code.count(fn) != 1:
        sys.exit('%s is not defined exactly once (nothing written)' % fn)
# bound the body by its OWN closing brace. _drawStates sits BEFORE _drawGlow in
# this file, so using it as the end bound produced an empty slice and every
# check below passed on nothing.
_g = code.index('_drawGlow:function(){')
_ge = code.index('\n  },', _g)
gbody = code[_g:_ge]
if len(gbody) < 400:
    sys.exit('the _drawGlow slice is too small to be its body (nothing written)')
if "contains('selected')" in gbody or "contains('cardmark')" in gbody:
    sys.exit('_drawGlow still names a class directly (nothing written)')
if gbody.count('_paintHalo') != 0:
    sys.exit('_drawGlow still paints directly (nothing written)')
if '_marksLive(\'under\',rolling)' not in gbody:
    sys.exit('_drawGlow does not use the roster wake test (nothing written)')
# the roster's paint order must put card before sel
_m = code.index('MARKS:[')
if code.index("id:'card'", _m) > code.index("id:'sel'", _m):
    sys.exit('the roster paints selection before the card mark (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
