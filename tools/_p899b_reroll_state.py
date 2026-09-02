# -*- coding: utf-8 -*-
u"""P899b: a card's reroll becomes a MARKS row, because it is a state.

THE SHEET WAS ONE MARK AND IS ACTUALLY TWO. The card firing is the beat; the
die being in the air is the state that beat causes. Origin is not lifetime, and
treating the whole thing as a beat is what put a 580ms envelope on a 1017ms
flight. The rim answers "this die is being rerolled by that card" - present
tense, condition-bound - so by the list rule it belongs in MARKS.

`through:true` IS LOAD-BEARING HERE, for the first time outside the enchants.
The other rows survive a roll because their condition happens to outlast one;
this row's condition IS the roll. A row that could not say so would be deleted
by the guard it needs most.

THE PREDICATE CANNOT BE BARE `d.roll` - every die in an ordinary roll has one.
The card tags the die with the cause, and the tag carries the ink. That is a
legitimate parameter where arming-with-an-ink was not: an ink duplicates what
the firing already knows, whereas WHY this die is in the air exists nowhere
else. What separates the lists is condition versus clock, not plain versus
parameterised.

THE TAG'S ONE EXIT IS A TRANSITION, NOT A CLOCK. It is set before the throw is
queued and d.roll appears about 60ms later, so "no roll" cannot mean "landed"
until the die has been seen in the air. The sweep runs at the top of the under
pass - before its wake test, because the frame the last mark goes out on is
exactly the frame that has to clear the tag - and not inside the predicate,
because a predicate with a side effect answers differently depending on who
asked. Left uncleared, the die's next ORDINARY roll would wear the card's ink.

ONE CALL PER DISTINCT INK. A parameterised row cannot share the roster's
one-call-per-row bound, so `_drawMarks` groups a row's dice by resolved ink and
paints each group once - which is the cost bound the brief now states. Rows
without `inkOf` are one group, exactly as before.

UNDER, not over. A state is part of the table and should be occluded by the
dice; only beats sit on top. So this needs none of P897's over-subject cut.

WHAT COMES OUT. The four beat calls and BEAT_ENV.reroll: that shape was
authored for a 400ms budget against a flight three times longer, and re-timing
it is moot once the mark ends when the flight does. The `env` parameter itself
stays - §18 sheets three more shapes that want in/hold/out - but it now has no
caller, which is worth saying out loud rather than leaving to be discovered.

§15's 400ms rule does not bind any of this, and the brief now says so: the
tumble is not a delay before the information, it is the information arriving.
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


# ══ 1. the row ═════════════════════════════════════════════════════
sub(u"""    {id:'blind',layer:'over',through:true,style:'veil',ink:'#1a1a2a',
     on:function(d){return d.chip.classList.contains('die-blind');}},""",
    u"""    {id:'blind',layer:'over',through:true,style:'veil',ink:'#1a1a2a',
     on:function(d){return d.chip.classList.contains('die-blind');}},
    /* P899: A CARD'S REROLL IS A STATE. The card firing is the beat; the die
       being in the air is the state that beat causes, and origin is not
       lifetime. Present tense, condition-bound, so it goes here rather than in
       FX_MARKS - and `through:true` is load-bearing for the first time outside
       the enchants, because this row's condition IS the roll.
       BARE d.roll WOULD MATCH EVERY DIE IN AN ORDINARY ROLL. The tag names the
       cause and carries the ink, which is a legitimate parameter: an ink would
       duplicate what the firing already knows, but WHY this die is in the air
       exists nowhere else. `inkOf` is read per die, and _drawMarks groups by
       resolved ink so the cost stays one call per ink present.
       UNDER, like every state - a state is part of the table and is occluded
       by the dice. Only beats sit on top. */
    {id:'reroll',layer:'under',through:true,style:'rim',fallback:'#ffb428',
     inkOf:function(d){return d.chip._rrInk;},
     on:function(d){return !!d.roll&&!!(d.chip&&d.chip._rrInk);}},""",
    '1 the reroll row')

# ══ 2. one call per distinct ink ═══════════════════════════════════
sub(u"""  _drawMarks:function(layer,cv,x,sc,dpr,rolling){
    var self=this,G=this.GLOW,M=this.MARKS||[],n=0;
    for(var r=0;r<M.length;r++){
      var row=M[r];
      if(row.layer!==layer)continue;
      if(rolling&&!row.through)continue;
      var ds=this._markDice(row);
      if(!ds.length)continue;
      var col=this._markInk(row.ink,row.fallback);""",
    u"""  _drawMarks:function(layer,cv,x,sc,dpr,rolling){
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
    for(var r=0;r<M.length;r++){
      var row=M[r];
      if(row.layer!==layer)continue;
      if(rolling&&!row.through)continue;
      var ds=this._markDice(row);
      if(!ds.length)continue;
      if(row.inkOf){
        /* one group per resolved ink. inkWhen is a SET-level override and does
           not apply here: a row that takes its colour from each die has
           already answered the question inkWhen exists to ask. */
        var byInk={},kk,q;
        for(q=0;q<ds.length;q++){
          try{kk=this._markInk(row.inkOf(ds[q]),row.fallback);}
          catch(e){kk=this._markInk(null,row.fallback);}
          (byInk[kk]||(byInk[kk]=[])).push(ds[q]);
        }
        for(kk in byInk)n+=paintSet(row.style,byInk[kk],kk,kk);
        continue;
      }
      var col=this._markInk(row.ink,row.fallback);""",
    '2a the ink grouping')

sub(u"""      var hulls=[];
      for(var i=0;i<ds.length;i++){
        var h=self._hullOf(ds[i],sc,G.grow);
        if(h)hulls.push(h);
      }
      if(!hulls.length)continue;
      this._paintForm(row.style,cv,x,sc,dpr,hulls,col,soft,1,layer==='over');
      n++;
    }
    return n;
  },""",
    u"""      n+=paintSet(row.style,ds,col,soft);
    }
    return n;
  },""",
    '2b the row body uses it')

# ══ 3. the tag's one exit ══════════════════════════════════════════
sub(u"""  _drawGlow:function(){
    var cv=document.getElementById('dgCanvas');""",
    u"""  _drawGlow:function(){
    /* P899: THE REROLL TAG'S ONE EXIT. A card tags the die it is re-throwing
       so the row can tell its reroll from an ordinary one; left on, the die's
       NEXT ordinary roll would wear the card's ink.
       Cleared on a TRANSITION, not a clock: the tag is set before the throw is
       queued and d.roll appears about 60ms later, so "no roll" cannot mean
       "landed" until this die has been seen in the air.
       Here rather than in the row's predicate, because a predicate with a side
       effect answers differently depending on who asked - and above the wake
       test rather than below it, because the frame the last mark goes out on
       is exactly the frame this has to run on. */
    for(var _q=0;_q<this.dice.length;_q++){
      var _rd=this.dice[_q];
      if(!_rd.chip||!_rd.chip._rrInk)continue;
      if(_rd.roll)_rd._rrSeen=1;
      else if(_rd._rrSeen){_rd.chip._rrInk=null;_rd._rrSeen=0;}
    }
    var cv=document.getElementById('dgCanvas');""",
    '3 the tag sweep')

# ══ 4. the arming helper ═══════════════════════════════════════════
sub(u"""function _dieBeat(el,style,ink,opt){
  try{return (window.D3X&&D3X.beat)?D3X.beat(el,style,ink,opt):false;}
  catch(e){return false;}
}""",
    u"""function _dieBeat(el,style,ink,opt){
  try{return (window.D3X&&D3X.beat)?D3X.beat(el,style,ink,opt):false;}
  catch(e){return false;}
}

/* P899: name the card that is re-throwing this die. Called BEFORE the value
   changes, because the value change is what starts the flight and the row has
   to be able to read its cause from the first frame. The tag is the condition
   AND the ink; D3X clears it when the flight ends. */
function _dieReroll(el,ink){
  try{if(el)el._rrInk=ink||'#ffb428';}catch(e){}
  return !!el;
}""",
    '4 the arming helper')

# ══ 5. the four sites ══════════════════════════════════════════════
sub(u"""    free.forEach(function(d,_i){
      _setDieVal(d,_rollD(d));d.sel=false;
      if(d.el){d.el.classList.remove('selected');
        /* §18: RIM in the card's ink at +140, staggered 70ms, 100/hold/200.
           P828's starstone blue is the card's ink and the motes already use
           it - the rim and the spray are now the same colour by construction
           rather than by two literals agreeing. */
        _dieBeat(d.el,'rim',D3X.BEAT_INK.encore,
                 {delay:140+_i*70,env:D3X.BEAT_ENV.reroll});
        try{_fxSpray(d.el,D3X.BEAT_INK.encore,8,{speed:65,g:-20,size:5,spread:2.0});}catch(e){}}""",
    u"""    free.forEach(function(d){
      /* the tag goes on BEFORE the value changes: _setDieVal is what starts
         the flight, and the row reads its cause from the first frame.
         P828's starstone blue is the card's ink and the motes already use it,
         so the rim and the spray share a colour by construction rather than by
         two literals agreeing. */
      if(d.el)_dieReroll(d.el,D3X.BEAT_INK.encore);
      _setDieVal(d,_rollD(d));d.sel=false;
      if(d.el){d.el.classList.remove('selected');
        try{_fxSpray(d.el,D3X.BEAT_INK.encore,8,{speed:65,g:-20,size:5,spread:2.0});}catch(e){}}""",
    '5a encore')

sub(u"""    _slFree.forEach(function(d,_i){d.val=_rollD(d);
      if(d.el)_dieBeat(d.el,'rim',D3X.BEAT_INK.reroll,
                       {delay:140+_i*70,env:D3X.BEAT_ENV.reroll});
      try{reDrawDieFace(d);}catch(e){}});""",
    u"""    _slFree.forEach(function(d){d.val=_rollD(d);
      if(d.el)_dieReroll(d.el,D3X.BEAT_INK.reroll);/* before reDrawDieFace */
      try{reDrawDieFace(d);}catch(e){}});""",
    '5b sleight, player')

sub(u"""          .forEach(function(d,_i){d.val=rollFace(d.mat);
            /* the rival's seat runs on its own clock, so the stagger does too */
            if(d.el)_dieBeat(d.el,'rim',D3X.BEAT_INK.reroll,
                             {delay:_oppDelay(140+_i*70),env:D3X.BEAT_ENV.reroll});
            try{reDrawDieFace(d);}catch(e){}});""",
    u"""          .forEach(function(d){d.val=rollFace(d.mat);
            /* no _oppDelay: the mark lasts as long as the rival's throw does,
               and their throw is already on their clock. */
            if(d.el)_dieReroll(d.el,D3X.BEAT_INK.reroll);
            try{reDrawDieFace(d);}catch(e){}});""",
    '5c sleight, rival')

sub(u"""  toReroll.forEach((d,_i)=>{
    _setDieVal(d,rollFaceExclude(d.mat,d.val,d));
    /* §18's stagger: die 1 winds up at +140, die 2 at +210. The envelope's
       own timing is under question - see BEAT_ENV.reroll. settleDie stays on
       its timer: it is the flat path's landing, not part of the beat. */
    if(d.el){_dieBeat(d.el,'rim',D3X.BEAT_INK.reroll,
                      {delay:140+_i*70,env:D3X.BEAT_ENV.reroll});
      setTimeout(()=>{settleDie(d.el);},400);}
  });""",
    u"""  toReroll.forEach(d=>{
    /* tag first - _setDieVal is what starts the flight. settleDie keeps its
       own timer: it is the flat path's landing, not part of the mark. */
    if(d.el)_dieReroll(d.el,D3X.BEAT_INK.reroll);
    _setDieVal(d,rollFaceExclude(d.mat,d.val,d));
    if(d.el)setTimeout(()=>{settleDie(d.el);},400);
  });""",
    '5d grogs flask')

# ══ 5e-g. THE THREE REROLLS THE CSS CLASS NEVER COVERED ═══════════
# Found by an assert firing on the wrong occurrence of a repeated string, which
# is the only reason I looked: routing the four sites that happened to carry
# `card-reroll` would have built a row that works on its own built path and is
# invisible on every other way in. A card reroll is a card reroll.
sub(u"""        _setDieVal(d,_rollD(d));d.sel=false;
        if(d.el)d.el.classList.remove('selected');""",
    u"""        if(d.el)_dieReroll(d.el,D3X.BEAT_INK.reroll);
        _setDieVal(d,_rollD(d));d.sel=false;
        if(d.el)d.el.classList.remove('selected');""",
    '5e steady hand')

sub(u"""      d.committed=false;d._frozen=false;d.sel=false;
      _setDieVal(d,_rollD(d));""",
    u"""      d.committed=false;d._frozen=false;d.sel=false;
      /* P828 puts the keg's explosion opposite encore's starstone, so the keg
         takes the plain reroll gold - and it rerolls the KEPT dice too, which
         is the one thing the card has to say. */
      if(d.el)_dieReroll(d.el,D3X.BEAT_INK.reroll);
      _setDieVal(d,_rollD(d));""",
    '5f powder keg')

sub(u"""  _setDieVal(d,_rollD(d));d.sel=false;/* P846: the R1 gap no card list could cover */""",
    u"""  /* P684 recorded this reroll as invisible - "the face just changed" - and
     the spray it added is the only thing that ever marked it. In quicksilver's
     own ink, which is that spray's. */
  if(d.el)_dieReroll(d.el,D3X.BEAT_INK.quicksilver);
  _setDieVal(d,_rollD(d));d.sel=false;/* P846: the R1 gap no card list could cover */""",
    '5g quicksilver')

sub(u"""  BEAT_INK:{gold:'#ffc83c',green:'#3cc85a',red:'#dc3c28',blue:'#50a0f0',
            reroll:'#ffb428',encore:'#8fa8ff',combo:'#ffc850'},""",
    u"""  BEAT_INK:{gold:'#ffc83c',green:'#3cc85a',red:'#dc3c28',blue:'#50a0f0',
            reroll:'#ffb428',encore:'#8fa8ff',combo:'#ffc850',
            /* P899: quicksilver's own, taken from the spray P684 added when it
               recorded that enchant's reroll as invisible. */
            quicksilver:'#eef4fb'},""",
    '5h quicksilver ink')

# ══ 6. the retired envelope ════════════════════════════════════════
sub(u"""  /* §18's card-reroll sheet, as a shape: 100ms in, hold, 200ms out. The
     stagger and the +140 wind-up are per-die and passed as `delay`.
     P898 - MEASURED AND MISTIMED, and left as authored rather than guessed
     at. The sheet budgets the whole card reroll at 400ms with the value
     changing at +210, which reads as a die that snaps to its new face. It
     does not: _setDieVal calls reDrawDieFace, which calls D3.roll, which
     calls _physQueue - the same entry an ordinary roll uses - and the
     solution is 1017 frame-milliseconds of flight against 1433 for an
     ordinary roll. So this envelope is over at 580ms, about 440ms before the
     die lands, and the rim decorates the throw rather than the result.
     All four reroll sites share this shape and all four take that flight, so
     the note is here rather than copied beside each of them.
     Re-timing it is a change to the sheet, which is Denis's - see OPEN.md. */
  BEAT_ENV:{reroll:{'in':100,hold:140,out:200}},""",
    u"""  /* P899: BEAT_ENV.reroll is gone with the beats it timed. It gave the card
     reroll 100/hold/200 from +140 against a measured 1017ms flight, so it was
     over about 440ms before the die landed - and re-timing it turned out to be
     the wrong fix, because the mark is a state whose end is the flight's end.
     The `env` parameter on _fxMark stays and currently has NO CALLER. That is
     said plainly rather than left to be found: §18 sheets three more shapes
     that want an in/hold/out - moment 2's 120ms rim-in, moment 4's lane veil,
     the miss - and deleting a tested evaluator to re-add it next patch is
     churn. If none of them wants it, it should go. */""",
    '6 the retired envelope')

# ── post-asserts, comments stripped ─────────────────────────────────
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)

# the roster: six rows, reroll exactly once, and it is a STATE
mk = code.index('MARKS:[')
roster = code[mk:code.index('\n  ],', mk)]
if roster.count("{id:'") != 6:
    sys.exit('the roster has %d rows, expected 6 (nothing written)'
             % roster.count("{id:'"))
if roster.count("{id:'reroll'") != 1:
    sys.exit('the reroll row is not present exactly once (nothing written)')
rr = roster[roster.index("{id:'reroll'"):]
for need in ("layer:'under'", 'through:true', "style:'rim'", 'inkOf:function'):
    if need not in rr:
        sys.exit('the reroll row is missing %s (nothing written)' % need)
# the predicate must test the TAG as well as the flight
if '!!d.roll&&!!(d.chip&&d.chip._rrInk)' not in rr:
    sys.exit('the reroll predicate does not test the tag - it would match every '
             'die in an ordinary roll (nothing written)')

# the tag has exactly one clear, and it is above the wake test
if code.count('_rrInk=null') != 1:
    sys.exit('the tag has %d exits, expected 1 (nothing written)'
             % code.count('_rrInk=null'))
_fn = code.index('_drawGlow:function')
_body = code[_fn:code.index('_tableRoot:function', _fn)]
if _body.index('_rrInk=null') > _body.index('_marksLive'):
    sys.exit('the tag sweep runs after the wake test, so the landing frame '
             'never clears it (nothing written)')
# and it clears on a transition, not on a bare absence
if '_rd.roll)_rd._rrSeen=1' not in code:
    sys.exit('the sweep does not wait until the die has been seen in the air '
             '(nothing written)')

# the four sites moved from beats to the row
if code.count('function _dieReroll(') != 1:
    sys.exit('the arming helper is not declared exactly once (nothing written)')
if code.count('_dieReroll(') - 1 != 7:
    sys.exit('%d reroll sites, expected 7 - four that carried the CSS class '
             'and three that never did (nothing written)'
             % (code.count('_dieReroll(') - 1))
if code.count('_dieBeat(') - 1 != 14:
    sys.exit('%d beat sites, expected 14 (nothing written)'
             % (code.count('_dieBeat(') - 1))
if 'BEAT_ENV' in code:
    sys.exit('BEAT_ENV survived (nothing written)')
# THE TAG MUST PRECEDE THE THING THAT STARTS THE FLIGHT, at every site.
# Anchored on the TAG, not on the starter: `_setDieVal(d,_rollD(d))` appears
# four times in this file and index() found the first, failing a correct patch
# and - far more usefully - pointing at three reroll paths that had no mark at
# all. Assert in the direction where each occurrence is the thing under test.
for mm in re.finditer(r'_dieReroll\(', code):
    # skip the DECLARATION. Comparing mm.start() to index('function _dieReroll(')
    # compared the offset of the name against the offset of the keyword nine
    # characters earlier, so the declaration never matched and failed its own
    # assert - the third off-by-anchor in this session's asserts.
    if code[max(0, mm.start() - 9):mm.start()] == 'function ':
        continue
    after = code[mm.end():mm.end() + 300]
    if '_setDieVal(' not in after and 'reDrawDieFace(' not in after:
        sys.exit('a tag at offset %d is not followed by anything that starts a '
                 'flight - the row would never light (nothing written)'
                 % mm.start())

# the ink grouping, and one painter
# `var paintSet=function(` does not contain `paintSet(`, so the definition and
# the calls are counted separately rather than as one total.
if code.count('var paintSet=function(') != 1:
    sys.exit('paintSet is not defined exactly once (nothing written)')
if code.count('paintSet(') != 2:
    sys.exit('paintSet has %d call sites, expected 2 - the tagged branch and '
             'the plain one (nothing written)' % code.count('paintSet('))
if code.count('_paintForm(style,cv,x,sc,dpr,hulls,col,soft,1,') != 1:
    sys.exit('the row painter is not a single call (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % len(edits))
for e in edits:
    print('   ' + e)
