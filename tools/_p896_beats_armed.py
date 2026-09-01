# -*- coding: utf-8 -*-
u"""P896 (FX brief step 8b): the eight inert classes are routed, as ARMED BEATS
rather than roster rows - so the table gets no exception and no new shape.

THE ROSTER SHAPE, settled first because it was cheaper to decide than to undo.
Denis framed the choice as: `ink` accepts a function of the die, or a beat row
is armed with its ink at fire time. It is the second - and the mechanism
already exists, so MARKS is untouched. Three reasons, each from the code:

  1. THE INK BELONGS TO THE FIRING, NOT THE DIE. `effects.forEach` picks its
     colour from the effect TYPE - gold for a triple bonus, green for a wild -
     on whichever die that effect landed on. The same die is gold in one
     firing and green in the next, so no function of the die can answer it
     without reading a field somebody wrote at fire time, which is arming with
     an extra hop and a hidden write.
  2. TWO FIRINGS CAN OVERLAP ON ONE DIE, and the CSS could never express it.
     Two eff-glow-* classes on one element resolve by STYLESHEET SOURCE ORDER
     - blue beats red beats green beats gold - not by which effect fired. A
     per-die ink has exactly the same defect: one die, one value. Two armed
     entries hold two.
  3. LIFETIME. A row is live while its predicate is true; a beat has a clock.
     `effects.forEach` adds eff-glow-gold with NO removal at all - it lives
     until a sweep list happens to clear it, which is also why step 11's sweep
     deletions were unsafe. Arming gives every beat its own clock.

So: MARKS is one row per thing a die can WEAR. FX_MARKS is one entry per
FIRING. Two lists, two lifetimes, no exception in either.

BEATS ARE NOT ROLL-GATED, and this contradicts a line in the brief, so it is
stated rather than done quietly. "A beat has no business surviving a roll" is
right about persistence and wrong as a `_rolling()` gate: the card-reroll beat
exists precisely to play while the dice are being re-thrown, so a roll gate
would delete the first beat in §18's sheet. A beat's clock is what bounds it,
and that is unconditional. (Measured aside: at activateGrogsFlask `_rolling()`
is false anyway - that path calls `_setDieVal` directly and never sets `d.roll`
- so the flask reroll has no tumble in 3D at all. Out of scope here; the sheet
only asks for a rim and a value change, and it gets both.)

THE FORMS ARE NOW ONE VOCABULARY, not two that look alike. The beat painter's
`kind:'glow'` was already `_paintHalo` with an alpha envelope - the same call
_paintForm makes for a RIM - so the two were identical by coincidence and free
to drift. `_paintForm` takes an alpha multiplier now and the beat painter goes
through it. `beam` keeps its own branch: a column out of the die's box is
genuinely not a treatment of the silhouette, and pretending otherwise would be
the exception this patch exists to avoid.

DIM COMES OUT. Denis's correction, and the neighbours confirm it: all three of
DIM's listed jobs already have material routes - `_spentLook` for a spent
brand, `_keptLook` for a committed die, `_trayTint` for one out of play. It was
a table listing three existing mechanisms as one new form. Three forms paint:
RIM, CRUST, VEIL.

THE ENVELOPE IS AUTHORED WHERE THE SHEET IS SPECIFIC. §18 gives the card
reroll 100 ms in, a hold, and a 200 ms fade at +380, staggered 70 ms per die.
A single sine swell would land within about twenty milliseconds of that and
still be a different shape, so beats take an optional {in,hold,out} and the
sine stays the default for everything that has not been sheeted.

INKS ARE THE DELETED RULES' OWN, converted, per §13 rule 2 - never new
colours. #ffc83c IS rgba(255,200,60) from .die.eff-glow-gold, #8fa8ff is
P828's starstone blue from .crr-blue, and so on.

EIGHTEEN CALL SITES, not the six I told Denis. Counting the classes is not
counting the sites: eff-glow alone is thirteen, in five files' worth of card
code, three of them on the opponent's timescale (`_oppDelay`). Every one is a
paired add/remove and both halves come out together.
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


# ══════════ 1. DIM comes out of the form list ══════════════════════
sub(u"""  VEIL:{alpha:0.42},
  DIM:{alpha:0.46,ink:'#12141a'},""",
    u"""  VEIL:{alpha:0.42},""",
    '1a the DIM dial')

sub(u"""    if(style==='veil'||style==='dim'){
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
  },""",
    u"""    if(style==='veil'){
      var self=this;
      x.save();
      x.globalAlpha=this.VEIL.alpha*AM;
      x.fillStyle=col;
      hulls.forEach(function(h){self._traceHull(x,h);x.fill();});
      x.restore();
      return;
    }
    this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM);
  },""",
    '1b the dim branch')

# the alpha multiplier, so the beat painter can share this
sub(u"""  _paintForm:function(style,cv,x,sc,dpr,hulls,col,soft){
    if(style==='crust'){
      var C=this.CRUST;
      this._paintHalo(cv,x,sc,dpr,hulls,col,soft,1,C.line,C);
      return;
    }""",
    u"""  _paintForm:function(style,cv,x,sc,dpr,hulls,col,soft,alphaMul){
    /* P896: the multiplier is what lets a BEAT share this painter. A state is
       either worn or not, so it always passes 1; a beat rides an envelope. It
       existed as a parameter of _paintHalo all along - the forms just never
       passed it through, which left the beat painter making its own identical
       _paintHalo call and free to drift away from the form it was already
       drawing. */
    var AM=(alphaMul==null?1:alphaMul);
    if(style==='crust'){
      var C=this.CRUST;
      this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM,C.line,C);
      return;
    }""",
    '1c the alpha multiplier')

# ══════════ 2. the beat entry: ink, clock, delay, envelope ═════════
sub(u"""  FX_MARKS:[],
  _fxMark:function(d,kind,ink,ms){
    if(!d||!d.obj)return false;
    (this.FX_MARKS||(this.FX_MARKS=[])).push(
      {d:d,kind:kind,ink:ink||'#ffffff',t0:performance.now(),ms:ms||500});
    return true;
  },""",
    u"""  FX_MARKS:[],
  /* P896: an entry is ARMED WITH ITS INK, and that is the whole answer to
     "one form, many colours". eff-glow is not four forms - it is one rim whose
     colour is chosen per firing, from the effect's type, on whichever die that
     firing landed on. A row cannot hold that: a row's ink is a property of the
     thing worn, and this is a property of the event. Two firings can also
     overlap on one die, which the old CSS resolved by stylesheet source order
     rather than by which effect fired; two entries hold two colours.
     `delay` is the sheet's stagger and wind-up. `env` is {in,hold,out} in ms
     for a beat whose shape §18 specifies; without one the alpha is a sine
     swell over `ms`, which is what every beat did before this. */
  _fxMark:function(d,kind,ink,ms,delay,env,tag){
    if(!d||!d.obj)return false;
    var E=env||null;
    var life=E?(E['in']+E.hold+E.out):(ms||500);
    /* A TAG IS "THIS BEAT, AGAIN". The combo fires on every selection change
       while the combo holds, and the CSS version restarted by removing the
       class and forcing a reflow. Arming stacks instead of restarting, and
       stacked rims composite with 'lighter', so a player toggling dice would
       have got a brighter and brighter die. Same die, same tag, one entry. */
    if(tag)this.FX_MARKS=(this.FX_MARKS||[]).filter(function(mk){
      return !(mk.d===d&&mk.tag===tag);
    });
    (this.FX_MARKS||(this.FX_MARKS=[])).push(
      {d:d,kind:kind,ink:ink||'#ffffff',t0:performance.now(),
       ms:life,delay:delay||0,env:E,tag:tag||null});
    return true;
  },
  /* the beat's alpha at `now`, which is the only thing `delay` and `env`
     change. Returns 0 before the delay elapses, so an armed-but-not-yet-due
     beat costs a hull and nothing else. */
  _beatAlpha:function(mk,now){
    var t=now-mk.t0-(mk.delay||0);
    if(t<=0)return 0;
    var E=mk.env;
    if(!E)return Math.sin(Math.min(1,t/mk.ms)*Math.PI);
    if(t<E['in'])return t/E['in'];
    if(t<E['in']+E.hold)return 1;
    var o=(t-E['in']-E.hold)/E.out;
    return o>=1?0:1-o;
  },
  /* THE INKS ARE THE DELETED RULES' OWN, converted. §13 rule 2: one ink per
     idea, and never a new colour picked at the moment of wiring. gold/green/
     red/blue are .die.eff-glow-*'s rgba() triples; reroll is .die.card-reroll;
     encore is P828's starstone blue from .crr-blue; combo is comboGlow's
     brightest stop. */
  BEAT_INK:{gold:'#ffc83c',green:'#3cc85a',red:'#dc3c28',blue:'#50a0f0',
            reroll:'#ffb428',encore:'#8fa8ff',combo:'#ffc850'},
  /* §18's card-reroll sheet, as a shape: 100ms in, hold, 200ms out. The
     stagger and the +140 wind-up are per-die and passed as `delay`. */
  BEAT_ENV:{reroll:{'in':100,hold:140,out:200}},
  /* arm a beat from a CHIP rather than a record, because every call site in
     the card code has an element and none of them has a D3X row. Returns
     false when the die is not in the 3D layer, so a caller can tell "no die"
     from "no beat" - the distinction the eff-glow classes never made. */
  beat:function(el,style,ink,opt){
    if(!el)return false;
    var d=null;
    for(var i=0;i<this.dice.length;i++)
      if(this.dice[i].chip===el){d=this.dice[i];break;}
    if(!d)return false;
    var o=(typeof opt==='number')?{ms:opt}:(opt||{});
    return this._fxMark(d,style==='veil'?'flash':'glow',ink,
                        o.ms||500,o.delay||0,o.env||null,o.tag||null);
  },""",
    '2 the armed beat')

# ══════════ 3. the beat painter goes through _paintForm ════════════
sub(u"""    var beats=this.FX_MARKS=(this.FX_MARKS||[]).filter(function(mk){
      return mk.d&&mk.d.obj&&mk.d.obj.visible&&(_now-mk.t0)<mk.ms;
    });""",
    u"""    var beats=this.FX_MARKS=(this.FX_MARKS||[]).filter(function(mk){
      /* the delay is part of the life, or a staggered beat expires before it
         is due and never paints at all */
      return mk.d&&mk.d.obj&&mk.d.obj.visible&&
             (_now-mk.t0)<((mk.delay||0)+mk.ms);
    });""",
    '3a the delayed expiry')

sub(u"""      var tt=(_now-mk.t0)/mk.ms;
      if(tt<0)tt=0;if(tt>1)tt=1;
      if(mk.kind==='glow'){
        /* the keep glow's own painter, alpha on a sine: it swells and leaves */
        this._paintHalo(cv,x,sc,dpr,[hb],mk.ink,mk.ink,Math.sin(tt*Math.PI));
      }else if(mk.kind==='flash'){
        x.save();
        x.globalAlpha=Math.max(0,1-tt)*0.8;
        x.fillStyle=mk.ink;
        this._traceHull(x,hb);
        x.fill();
        x.restore();
      }else if(mk.kind==='beam'){""",
    u"""      var am=this._beatAlpha(mk,_now);
      if(am<=0&&mk.kind!=='beam')continue;/* armed, not yet due */
      var tt=(_now-mk.t0-(mk.delay||0))/mk.ms;
      if(tt<0)tt=0;if(tt>1)tt=1;
      if(mk.kind==='glow'){
        /* P896: THROUGH THE FORM, not beside it. This was its own _paintHalo
           call with the same arguments _paintForm's rim branch passes - the
           beat and the state were the same drawing by coincidence, and either
           could have been retuned without the other. */
        this._paintForm('rim',cv,x,sc,dpr,[hb],mk.ink,mk.ink,am);
      }else if(mk.kind==='flash'){
        this._paintForm('veil',cv,x,sc,dpr,[hb],mk.ink,mk.ink,am*1.9);
      }else if(mk.kind==='beam'){""",
    '3b the shared painter')

# ══════════ 4. the call-site helper ════════════════════════════════
sub(u"""function mkDie(val,mat,sizeClass,still,ench){""",
    u"""/* P896: ONE GUARD FOR EIGHTEEN CALL SITES. The card code has an element and
   no D3X row, and half of it runs on paths where the 3D layer may not be up.
   Wrapping here means a site is one short line that cannot throw, instead of
   eighteen copies of `try{if(window.D3X&&...)}catch(e){}` - which is the
   hand-maintained shape this brief keeps deleting. */
function _dieBeat(el,style,ink,opt){
  try{return (window.D3X&&D3X.beat)?D3X.beat(el,style,ink,opt):false;}
  catch(e){return false;}
}

function mkDie(val,mat,sizeClass,still,ench){""",
    '4 the call-site helper')

# ══════════ 5. the thirteen eff-glow sites ═════════════════════════
EFF = [
    ("_ftVic", "gold", "700", 'a fool of the table'),
    ("_ldVic", "gold", "700", 'the last drop'),
    ("_ggVic", "blue", "700", "the gambler's glance"),
    ("_gtVic", "green", "700", 'the green thumb'),
    ("_hsV1", "red", "700", "the hex's first victim"),
    ("_hsV5", "red", "700", "the hex's second victim"),
]
for var, col, ms, why in EFF:
    sub(u"""if(%s.el){%s.el.classList.add('eff-glow-%s');spawnPixelSparks(%s.el,4);setTimeout(function(){if(%s.el)%s.el.classList.remove('eff-glow-%s');},%s);}"""
        % (var, var, col, var, var, var, col, ms),
        u"""if(%s.el){_dieBeat(%s.el,'rim',D3X.BEAT_INK.%s,%s);spawnPixelSparks(%s.el,4);}"""
        % (var, var, col, ms, var),
        '5 eff-glow ' + var)

OPP = [("_ohsV1", "red"), ("_ohsV5", "red")]
for var, col in OPP:
    sub(u"""if(%s.el){%s.el.classList.add('eff-glow-%s');setTimeout(function(){if(%s.el)%s.el.classList.remove('eff-glow-%s');},_oppDelay(700));}"""
        % (var, var, col, var, var, col),
        u"""if(%s.el){_dieBeat(%s.el,'rim',D3X.BEAT_INK.%s,_oppDelay(700));}"""
        % (var, var, col),
        '5 eff-glow ' + var)

sub(u"""if(_stVic.el){_stVic.el.classList.add('eff-glow-red');spawnPixelSparks(_stVic.el,4);setTimeout(function(){if(_stVic.el)_stVic.el.classList.remove('eff-glow-red');},_oppDelay(700));}""",
    u"""if(_stVic.el){_dieBeat(_stVic.el,'rim',D3X.BEAT_INK.red,_oppDelay(700));spawnPixelSparks(_stVic.el,4);}""",
    '5 eff-glow _stVic')

sub(u"""            victim.el.classList.add('eff-glow-red');
            spawnPixelSparks(victim.el,8);
            (function(_v){setTimeout(function(){if(_v.el)_v.el.classList.remove('eff-glow-red');},900);})(victim);""",
    u"""            _dieBeat(victim.el,'rim',D3X.BEAT_INK.red,900);
            spawnPixelSparks(victim.el,8);""",
    '5 eff-glow victim')

sub(u"""        document.querySelectorAll('#keptTray .die').forEach(function(el){
          el.classList.add('eff-glow-red');
          spawnPixelSparks(el,6);
        });""",
    u"""        /* P896: this one had NO removal - the class lived until a sweep
           list happened to clear it, which is what an armed clock replaces.
           Staggered, because it is a set and a set that flashes as one block
           reads as a screen effect rather than as something done to dice. */
        document.querySelectorAll('#keptTray .die').forEach(function(el,_i){
          _dieBeat(el,'rim',D3X.BEAT_INK.red,{ms:700,delay:_i*70});
          spawnPixelSparks(el,6);
        });""",
    '5 eff-glow keptTray')

sub(u"""    var glowCls='eff-glow-'+color;
    el.classList.add(glowCls);""",
    u"""    /* P896: THE SITE THAT DECIDED THE ROSTER SHAPE. `color` is chosen from
       the effect's TYPE two dozen lines up - gold for a triple bonus, green
       for a wild - so the ink belongs to this firing, not to this die, and no
       declared row could hold it. Armed instead. It also had no removal at
       all, and two effects on one die used to resolve by stylesheet order
       rather than by which fired; two entries hold two colours. */
    _dieBeat(el,'rim',D3X.BEAT_INK[color]||D3X.BEAT_INK.gold,700);""",
    '5 eff-glow effects.forEach')

sub(u"""    leftDie.el.classList.add('eff-glow-gold');
    spawnPixelSparks(leftDie.el,8);
    setTimeout(function(){if(leftDie.el)leftDie.el.classList.remove('eff-glow-gold');},900);""",
    u"""    _dieBeat(leftDie.el,'rim',D3X.BEAT_INK.gold,900);
    spawnPixelSparks(leftDie.el,8);""",
    '5 eff-glow leftDie')

# ══════════ 6. the four card-reroll sites, on §18's sheet ══════════
sub(u"""      if(d.el){d.el.classList.remove('selected');d.el.classList.add('card-reroll','crr-blue');
        try{_fxSpray(d.el,'#8fa8ff',8,{speed:65,g:-20,size:5,spread:2.0});}catch(e){}/* P828: starstone motes */
        setTimeout(function(){d.el.classList.remove('card-reroll','crr-blue');},400);}""",
    u"""      if(d.el){d.el.classList.remove('selected');
        /* §18: RIM in the card's ink at +140, staggered 70ms, 100/hold/200.
           P828's starstone blue is the card's ink and the motes already use
           it - the rim and the spray are now the same colour by construction
           rather than by two literals agreeing. */
        _dieBeat(d.el,'rim',D3X.BEAT_INK.encore,
                 {delay:140+_i*70,env:D3X.BEAT_ENV.reroll});
        try{_fxSpray(d.el,D3X.BEAT_INK.encore,8,{speed:65,g:-20,size:5,spread:2.0});}catch(e){}}""",
    '6 encore')

sub(u"""    free.forEach(function(d){
      _setDieVal(d,_rollD(d));d.sel=false;""",
    u"""    free.forEach(function(d,_i){
      _setDieVal(d,_rollD(d));d.sel=false;""",
    '6 encore index')

sub(u"""    _slFree.forEach(function(d){d.val=_rollD(d);
      if(d.el){d.el.classList.add('card-reroll');
        setTimeout(function(){if(d.el)d.el.classList.remove('card-reroll');},700);}
      try{reDrawDieFace(d);}catch(e){}});""",
    u"""    _slFree.forEach(function(d,_i){d.val=_rollD(d);
      if(d.el)_dieBeat(d.el,'rim',D3X.BEAT_INK.reroll,
                       {delay:140+_i*70,env:D3X.BEAT_ENV.reroll});
      try{reDrawDieFace(d);}catch(e){}});""",
    '6 sleight player')

sub(u"""          .forEach(function(d){d.val=rollFace(d.mat);
            if(d.el){d.el.classList.add('card-reroll');
              setTimeout(function(){if(d.el)d.el.classList.remove('card-reroll');},700);}
            try{reDrawDieFace(d);}catch(e){}});""",
    u"""          .forEach(function(d,_i){d.val=rollFace(d.mat);
            /* the rival's seat runs on its own clock, so the stagger does too */
            if(d.el)_dieBeat(d.el,'rim',D3X.BEAT_INK.reroll,
                             {delay:_oppDelay(140+_i*70),env:D3X.BEAT_ENV.reroll});
            try{reDrawDieFace(d);}catch(e){}});""",
    '6 sleight opponent')

sub(u"""  toReroll.forEach(d=>{
    _setDieVal(d,rollFaceExclude(d.mat,d.val,d));
    if(d.el){d.el.classList.add('card-reroll');
      setTimeout(()=>{d.el.classList.remove('card-reroll');d.el.classList.add('card-reroll-settle');settleDie(d.el);
        setTimeout(()=>{d.el.classList.remove('card-reroll-settle');},400);},400);}
  });""",
    u"""  toReroll.forEach((d,_i)=>{
    _setDieVal(d,rollFaceExclude(d.mat,d.val,d));
    /* §18's sheet exactly: the card fires, then die 1 winds up at +140 and
       die 2 at +210. settleDie stays on its own timer - it is the flat path's
       landing, not part of the beat. */
    if(d.el){_dieBeat(d.el,'rim',D3X.BEAT_INK.reroll,
                      {delay:140+_i*70,env:D3X.BEAT_ENV.reroll});
      setTimeout(()=>{settleDie(d.el);},400);}
  });""",
    '6 grogs flask')

# ══════════ 7. combo-glow, and the bookkeeping that existed only for it ═══
# G._comboGlow is WRITTEN in four places and READ nowhere; G._comboTimer exists
# only to take the class off again. Both are the class's life-support, so they
# go with it rather than being left as a flag nobody consults.
sub(u"""  /* combo glow sweep */
  const nowCombo=ok&&isCombo(selV);
  G.pool.forEach(d=>{if(!d.sel||d.committed){d.el.classList.remove('combo-glow');d.el.style.removeProperty('--gd');}});
  if(nowCombo){
    // Always restart anim — cancel any pending timer so re-selects retrigger
    clearTimeout(G._comboTimer);
    selD.forEach((d,i)=>{d.el.classList.remove('combo-glow');void d.el.offsetWidth;d.el.style.setProperty('--gd',(i*0.07)+'s');d.el.classList.add('combo-glow');});
    SFX.combo(selD.length);
    G._comboTimer=setTimeout(function(){G.pool.forEach(function(d){d.el.classList.remove('combo-glow');d.el.style.removeProperty('--gd');});G._comboGlow=false;},500+selD.length*70+50);
  }
  else{G.pool.forEach(d=>{d.el.classList.remove('combo-glow');d.el.style.removeProperty('--gd');});clearTimeout(G._comboTimer);}
  G._comboGlow=nowCombo;""",
    u"""  /* P896: THE COMBO GLOW IS A BEAT, and its whole apparatus was life-support
     for a CSS class. The --gd stagger is the beat's delay; the reflow that
     restarted the animation is replaced by re-arming under a tag; the timer
     that took the class off again is replaced by the beat's own clock; and
     G._comboGlow was written in four places and read in none.
     A beat that is armed and then un-combo'd plays out its 450ms rather than
     being cut - §19: a beat finishes on its own layer and never blocks or
     is blocked by input. */
  const nowCombo=ok&&isCombo(selV);
  if(nowCombo){
    selD.forEach((d,i)=>_dieBeat(d.el,'rim',D3X.BEAT_INK.combo,
                                 {ms:450,delay:i*70,tag:'combo'}));
    SFX.combo(selD.length);
  }""",
    '7 combo-glow')

sub(u"""_renderSelTags([],0,true);_clearDieEffects();G.pool.forEach(d=>{d.el.classList.remove('combo-glow');d.el.style.removeProperty('--gd');});G._comboGlow=false;return;}""",
    u"""_renderSelTags([],0,true);_clearDieEffects();return;}""",
    '7 combo-glow empty-selection clear')

# ── post-asserts, comments stripped so a comment cannot satisfy one ──
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)

# every add of the eight inert classes is gone
for cls in ('eff-glow-gold', 'eff-glow-green', 'eff-glow-red', 'eff-glow-blue',
            'card-reroll', 'crr-blue', 'card-reroll-settle', 'combo-glow'):
    for verb in ('add', 'toggle'):
        if re.search(r"classList\.%s\([^)]*'%s'" % (verb, re.escape(cls)), code):
            sys.exit("classList.%s('%s') survived (nothing written)" % (verb, cls))
# and eff-glow is not being built by string concatenation either
if "'eff-glow-'+" in code:
    sys.exit('an eff-glow class is still being composed (nothing written)')

# THE PAIRED REMOVES MUST GO WITH THEIR ADDS. What may survive is a SWEEP -
# one of §9's three hand-written lists, which step 11 deletes and which names
# several classes at once. A remove naming exactly ONE of these classes is the
# orphaned half of a pair, and that is what this catches. (Measured: the two
# survivors are _clearDieEffects' four-name eff-glow list and the six-name
# reset at the wipe, both sweeps, both step 11's.)
INERT = ('eff-glow-gold', 'eff-glow-green', 'eff-glow-red', 'eff-glow-blue',
         'card-reroll', 'crr-blue', 'card-reroll-settle', 'combo-glow')
for call in re.findall(r"classList\.remove\(([^)]*)\)", code):
    args = re.findall(r"'([^']*)'", call)
    if len(args) == 1 and args[0] in INERT:
        sys.exit("an orphaned remove('%s') survived its add (nothing written)"
                 % args[0])
sweeps = [c for c in re.findall(r"classList\.remove\(([^)]*)\)", code)
          if any(a in INERT for a in re.findall(r"'([^']*)'", c))]
if len(sweeps) != 2:
    sys.exit('%d sweeps still name an inert class, expected the 2 that step 11 '
             'deletes (nothing written)' % len(sweeps))

# the combo class's life-support goes with the class
for dead in ('_comboGlow', '_comboTimer', "removeProperty('--gd')"):
    if dead in code:
        sys.exit('%s survived - it existed only to manage combo-glow '
                 '(nothing written)' % dead)

# eighteen routed sites
n = len(re.findall(r'_dieBeat\(', code)) - 1   # minus the declaration
if n != 18:
    sys.exit('%d routed call sites, expected 18 (nothing written)' % n)
if code.count('function _dieBeat(') != 1:
    sys.exit('the helper is not declared exactly once (nothing written)')
if code.count('beat:function(el,style,ink,opt)') != 1:
    sys.exit('D3X.beat is not defined exactly once (nothing written)')

# DIM is gone as a form, and its three material routes are all still here
if 'DIM:{' in code or "style==='dim'" in code:
    sys.exit('DIM survived as a canvas form (nothing written)')
for route in ('_spentLook:function', '_keptLook:function', '_trayTint:function'):
    if route not in code:
        sys.exit('%s is missing - it is one of DIM\'s three real routes '
                 '(nothing written)' % route)

# the beat painter must go through the form, not beside it
if code.count("_paintForm('rim',cv,x,sc,dpr,[hb]") != 1:
    sys.exit('the beat glow does not route through _paintForm (nothing written)')
if '_beatAlpha' not in code or code.count('_beatAlpha:function') != 1:
    sys.exit('the envelope is not defined exactly once (nothing written)')
# the delay must be inside the expiry test, or a staggered beat dies unpainted
if 'mk.delay||0)+mk.ms' not in code:
    sys.exit('the expiry filter ignores the delay (nothing written)')

# THE ROSTER IS UNTOUCHED - that is the claim this patch is making
mk = code.index('MARKS:[')
roster = code[mk:code.index('\n  ],', mk)]
if roster.count("{id:'") != 5:
    sys.exit('the roster changed shape: %d rows (nothing written)'
             % roster.count("{id:'"))
if 'function' in roster.split('on:function')[0]:
    sys.exit('a non-predicate function appeared in a roster row (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % len(edits))
for e in edits:
    print('   ' + e)
