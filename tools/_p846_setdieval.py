# -*- coding: utf-8 -*-
"""P846: enrollment by construction - _setDieVal replaces the id roster.

Denis's second review, all verified against the file:
- OPEN.md 1c was STALE (the player-active layer is LIVE since P615's
  pCards revival) and the stale finding was steering a live design
  decision through the code comment at the sacrifice targets filter.
- gamblers_eye: live, obtainable, NOT enrolled - its handleRoll branch
  rerolls the whole free pool and returns before _afterRollImpl, so a
  stargazer promise + ghosts survived a full reroll of the dice they
  cover.
- famQuicksilver: an enchant, no card list could ever cover it - same
  hole.
- rollFaceExclude dropped the die object, so _famHushed(undefined) was
  false and Still Waters was bypassed at both its live call sites.
- The dispatch-roster hook enrolled six retired ids and missed the one
  live card with the worst failure mode; refunded activations
  over-voided (a no-op flask ate the player's promise).

THE FIX (Denis's own shape): _setDieVal(d,v) = write + redraw + R1
void, routed through every player-side out-of-roll face write. The
roster hook is DELETED - a card that writes through _setDieVal is
enrolled by construction, refund paths that write nothing void
nothing, and the new-card checklist item becomes "you already did".
Non-val mutations (a splice, a freeze, a mat swap, a pool teardown)
keep one explicit famTableChanged() at the mutation site. Palm keeps
its own write/redraw choreography (the hardened 840ms reveal) with the
void beside the write - the stated exception.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── the primitive ────────────────────────────────────────────────────
sub("""function famApplyRollForces(){""",
    """/* P846: THE ONE WAY TO REWRITE A DIE'S FACE OUTSIDE A ROLL - write,
   redraw, R1 void, at the MUTATION. Replaces the dispatch id roster,
   which was the defect: it enrolled six retired ids, missed the live
   Gambler's Eye (the worst failure mode - a whole-pool reroll off the
   roll path), could never cover an enchant (quicksilver), and voided
   on refunded no-op activations. A card that writes through this is
   enrolled by construction. The roll path does NOT use this - the
   deal and famApplyRollForces own their own redraw, and their void is
   _clearRollForces at the roll tail. */
function _setDieVal(d,v){
  if(!d)return;
  d.val=v;
  try{reDrawDieFace(d);}catch(e){}
  try{famTableChanged();}catch(e){}
}
function famApplyRollForces(){""",
    'the primitive')

# ── fam layer conversions (drop the now-duplicate redraws + explicit voids) ──
sub("""        d.val=_rollD(d);d.sel=false;
        if(d.el)d.el.classList.remove('selected');
        try{reDrawDieFace(d);}catch(e){}
        try{famLog('STEADY HAND \u2014 '+d.val);}catch(e){}
        try{famTableChanged();}catch(e){}/* P844: the reroll changed the table a promise was read from */""",
    """        _setDieVal(d,_rollD(d));d.sel=false;
        if(d.el)d.el.classList.remove('selected');
        try{famLog('STEADY HAND \u2014 '+d.val);}catch(e){}""",
    'steady tap -> _setDieVal')

sub("""      d.val=_rollD(d);d.sel=false;
      if(d.el){d.el.classList.remove('selected');d.el.classList.add('card-reroll','crr-blue');reDrawDieFace(d);""",
    """      _setDieVal(d,_rollD(d));d.sel=false;
      if(d.el){d.el.classList.remove('selected');d.el.classList.add('card-reroll','crr-blue');""",
    'encore loop -> _setDieVal')
sub("""    famTableChanged();/* P844: these dice are new - every arm and promise was about the old ones */
    /* held across the resolve window, and cleared on every way out of it */""",
    """    /* each _setDieVal above fired the R1 void; nothing left to disarm here */
    /* held across the resolve window, and cleared on every way out of it */""",
    'encore explicit void dropped')

sub("""      d.committed=false;d._frozen=false;d.sel=false;
      d.val=_rollD(d);""",
    """      d.committed=false;d._frozen=false;d.sel=false;
      _setDieVal(d,_rollD(d));""",
    'keg loop -> _setDieVal')
sub("""      if(d.el){d.el.classList.remove('committed','selected','die-frozen');try{reDrawDieFace(d);}catch(e){}}""",
    """      if(d.el){d.el.classList.remove('committed','selected','die-frozen');}""",
    'keg duplicate redraw dropped')
sub("""    famTableChanged();/* P844: these dice are new - every arm and promise was about the old ones */
    var free=G.pool.slice();""",
    """    /* each _setDieVal above fired the R1 void */
    var free=G.pool.slice();""",
    'keg explicit void dropped')

sub("""  inst.charges--;
  d.val=f;d.sel=false;
  if(d.el)d.el.classList.remove('selected');
  try{reDrawDieFace(d);}catch(e){}""",
    """  inst.charges--;
  _setDieVal(d,f);d.sel=false;
  if(d.el)d.el.classList.remove('selected');""",
    'transmute pick -> _setDieVal')
sub("""  famLog('TRANSMUTED TO '+f);
  try{famTableChanged();}catch(e){}/* P844 */
  try{refreshSelUI();}catch(e){}try{famRenderRow();}catch(e){}""",
    """  famLog('TRANSMUTED TO '+f);
  try{refreshSelUI();}catch(e){}try{famRenderRow();}catch(e){}""",
    'transmute explicit void dropped')

sub("""      d.val=_rollD(d);d.sel=false;
      if(d.el){d.el.classList.remove('selected');d.el.classList.add('card-reroll');
        setTimeout(function(){if(d.el)d.el.classList.remove('card-reroll');},700);}
      try{reDrawDieFace(d);}catch(e){}
      famLog('SEVEN DICE \u2014 '+d.val);
      try{famTableChanged();}catch(e){}/* P845b: the reroll is the mutation moment */""",
    """      _setDieVal(d,_rollD(d));d.sel=false;
      if(d.el){d.el.classList.remove('selected');d.el.classList.add('card-reroll');
        setTimeout(function(){if(d.el)d.el.classList.remove('card-reroll');},700);}
      famLog('SEVEN DICE \u2014 '+d.val);""",
    'seven tap -> _setDieVal')

# quicksilver - THE enchant gap
sub("""  d.val=_rollD(d);d.sel=false;try{reDrawDieFace(d);}catch(e){}
  /* P684: the free reroll was invisible - the face just changed */""",
    """  _setDieVal(d,_rollD(d));d.sel=false;/* P846: the R1 gap no card list could cover */
  /* P684: the free reroll was invisible - the face just changed */""",
    'quicksilver -> _setDieVal')

# gamblers_eye branch - the live unenrolled reroll (+ the die object for Still Waters)
sub("""    toReroll.forEach(function(d){
      d.val=rollFaceExclude(d.mat,d.val);d.sel=false;
      if(d.el){d.el.classList.add('card-reroll');reDrawDieFace(d);""",
    """    toReroll.forEach(function(d){
      _setDieVal(d,rollFaceExclude(d.mat,d.val,d));d.sel=false;
      if(d.el){d.el.classList.add('card-reroll');""",
    'gamblers_eye reroll -> _setDieVal + die object')

# ── CARDS layer conversions ──────────────────────────────────────────
sub("""  toReroll.forEach(d=>{
    d.val=rollFaceExclude(d.mat,d.val);
    if(d.el){d.el.classList.add('card-reroll');reDrawDieFace(d);""",
    """  toReroll.forEach(d=>{
    _setDieVal(d,rollFaceExclude(d.mat,d.val,d));
    if(d.el){d.el.classList.add('card-reroll');""",
    'flask -> _setDieVal + die object')

sub("""  target.val=newVal;""",
    """  target.val=newVal;
  try{famTableChanged();}catch(e){}/* P846: void at the write; palm keeps its
     hardened 840ms write/redraw choreography - the stated exception */""",
    'palm void beside its write')

sub("""  target.val=1;
  if(target.el){target.el.classList.add('card-reroll');reDrawDieFace(target);""",
    """  _setDieVal(target,1);
  if(target.el){target.el.classList.add('card-reroll');""",
    'fist -> _setDieVal')

sub("""    d.val=5;
    if(d.el){d.el.classList.add('rolling');reDrawDieFace(d);""",
    """    _setDieVal(d,5);
    if(d.el){d.el.classList.add('rolling');""",
    'grace -> _setDieVal')

sub("""  nonScoring.forEach(function(d){d.val=1;reDrawDieFace(d);});""",
    """  nonScoring.forEach(function(d){_setDieVal(d,1);});""",
    'old_bones -> _setDieVal')

sub("""        victim.val=face;reDrawDieFace(victim);""",
    """        _setDieVal(victim,face);""",
    'wild_die -> _setDieVal')

sub("""  var newVal=d.val>=6?1:d.val+1;
  d.val=newVal;
  reDrawDieFace(d);""",
    """  var newVal=d.val>=6?1:d.val+1;
  _setDieVal(d,newVal);""",
    'nudge -> _setDieVal')

sub("""  var newVal=Math.min(6,d.val*2);
  d.val=newVal;
  reDrawDieFace(d);""",
    """  var newVal=Math.min(6,d.val*2);
  _setDieVal(d,newVal);""",
    'double_down_die -> _setDieVal')

sub("""  d.val=oppositeFace;
  reDrawDieFace(d);""",
    """  _setDieVal(d,oppositeFace);""",
    'coin_flip -> _setDieVal')

sub("""  d.val=5;
  reDrawDieFace(d);""",
    """  _setDieVal(d,5);""",
    'alchemist_touch -> _setDieVal')

sub("""  target.val=src.val;
  reDrawDieFace(target);""",
    """  _setDieVal(target,src.val);""",
    'twinning -> _setDieVal')

# ── non-val mutations: one explicit void at each site ────────────────
sub("""  G.pool=G.pool.filter(function(x){return x!==d;});
  _dropLanes(1);/* P516 */""",
    """  G.pool=G.pool.filter(function(x){return x!==d;});
  _dropLanes(1);/* P516 */
  try{famTableChanged();}catch(e){}/* P846: a die left the table (turn-scoped splice, not _removeDieAt) */""",
    'vanishing splice void')

sub("""  var d=selDice[0];
  d._frozen=true;
  /* Held, NOT committed:""",
    """  var d=selDice[0];
  d._frozen=true;
  try{famTableChanged();}catch(e){}/* P846: freezing removes a die from the free pool a promise was read from */
  /* Held, NOT committed:""",
    'frozen_die void')

sub("""    G.pool=[];
    /* handleRoll creates (numDice \u2212 pool.length) new dice \u2192 a full fresh hand. */""",
    """    G.pool=[];
    try{famTableChanged();}catch(e){}/* P846: the whole table tore down */
    /* handleRoll creates (numDice \u2212 pool.length) new dice \u2192 a full fresh hand. */""",
    'double_down teardown void')

sub("""  leftDie.mat=newMat;
  if(G.matchDice&&G.matchDice[leftPoolIdx]!==undefined)G.matchDice[leftPoolIdx]=newMat;""",
    """  leftDie.mat=newMat;
  if(G.matchDice&&G.matchDice[leftPoolIdx]!==undefined)G.matchDice[leftPoolIdx]=newMat;
  try{famTableChanged();}catch(e){}/* P846: {mat,ench} is the die's identity - a promise pre-rolled from the OLD table */""",
    'chisel mat-swap void')

# ── the roster hook DELETES ITSELF ───────────────────────────────────
sub("""  /* P844/P845b: the dice-mutating actives void pending promises/arms
     - one site, one classified list (each handler verified to write
     d.val, splice the pool, or freeze - and DRIVEN individually, the
     sweep probe). Flag-only and points-only actives stay off it: a
     promise survives a wager. seven_dice is NOT here: it ARMS at
     dispatch and mutates at its die tap, which enrolls there instead
     (the steady_hand/transmute shape). A NEW active that touches dice
     joins this list - docs/CARD_INTERACTION_RULES.md. */
  if(['grogs_flask','finnicks_palm','brutus_fist','ambrose_grace','vanishing_act',
      'old_bones','frozen_die','double_down','wild_die','coin_flip',
      'the_nudge','alchemists_chisel','alchemist_touch','twinning_charm',
      'double_down_die'].indexOf(cardId)>=0){try{famTableChanged();}catch(e){}}""",
    """  /* P846: the P844 id-roster hook that lived here DELETED ITSELF - it
     enrolled six retired ids, missed the live gamblers_eye, and voided
     on refunded no-ops. Enrollment now happens AT the mutation:
     _setDieVal for face writes, one explicit famTableChanged at the
     four non-val mutations (vanishing's splice, frozen_die's freeze,
     double_down's teardown, chisel's mat swap), palm's beside its
     choreographed write. docs/CARD_INTERACTION_RULES.md. */""",
    'roster hook deleted')

# ── Still Waters: the die object reaches the roll table ──────────────
sub("""function rollFaceExclude(mat,exclude){
  /* Reroll that's guaranteed to differ from `exclude` \u2014 used by active cards
     (Grog's Flask, Gambler's Eye) so a reroll always looks like a reroll. */
  const faces=_rollTable(mat).filter(f=>f!==exclude);""",
    """function rollFaceExclude(mat,exclude,d){
  /* Reroll that's guaranteed to differ from `exclude` \u2014 used by active cards
     (Grog's Flask, Gambler's Eye) so a reroll always looks like a reroll.
     P846: takes the DIE, not just its material - _rollTable hands it to
     _famHushed, so without it Still Waters was bypassed on exactly these
     two live rerolls (the same die-shaped-object rule _enchFaces
     documents). Callers without a die keep the old (hush-blind) table. */
  const faces=_rollTable(mat,d).filter(f=>f!==exclude);""",
    'rollFaceExclude carries the die')

# ── the stale justification at the sacrifice filter ──────────────────
sub("""       NO LIVE EFFECT TODAY, measured rather than assumed: _frozen's only two
       writers are Gambler's Eye and activateFrozenDie, both in the legacy
       player-active layer, and a driven check found canActivateCard refusing
       every id in that layer with effectiveCards() and pCards empty. Landmine
       removal - the frozen mechanic is a feature someone will revive.""",
    """       P846: THE JUSTIFICATION ABOVE THIS LINE AGED OUT AND IS REWRITTEN -
       the P568-era note here said _frozen had no live writer because the
       player-active layer was dead (pCards empty). P615 revived the hand;
       Gambler's Eye and Frozen Die are both live and obtainable, so this
       exclusion is now LOAD-BEARING PROTECTION, not landmine removal: a
       frozen die is one the player deliberately HELD, and sacrifice's
       untargeted free[last] pick must never eat it. Decision re-driven on
       the live build, same verdict, stronger reason.""",
    'sacrifice filter justification re-driven')

# ── post-asserts ─────────────────────────────────────────────────────
for needed in ['function _setDieVal(', 'rollFaceExclude(mat,exclude,d)',
               'rollFaceExclude(d.mat,d.val,d)']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
if s.count('_setDieVal(') < 16:
    sys.exit('CONVERSION COUNT %d < 16 (nothing written)' % s.count('_setDieVal('))
if "indexOf(cardId)>=0){try{famTableChanged();}catch(e){}}" in s:
    sys.exit('ROSTER HOOK SURVIVED (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits; _setDieVal sites=%d' % (len(edits), s.count('_setDieVal(')))
