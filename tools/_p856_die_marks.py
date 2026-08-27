# -*- coding: utf-8 -*-
"""P856: card die-marks stop being squares, and arms stop painting
every die (Denis's notes 4 and 6).

NOTE 4, as clarified: "when I drag steady hands I think it just
outlines all possible dice I can pick from. But it's not needed. When
I do pick a die then yes an additional outline specific to steady
hands should appear." So the arm marks NOTHING - the status line
already says TAP THE DIE TO REROLL - and the die you actually pick
gets a mark of its own.
Applied to all THREE tap-any-free-die arms, not just steady hand, because
they are literally the same six lines: steady_hand, transmute,
seven_dice. BREAK is deliberately NOT changed in that respect - it
marks a SUBSET (its own `live` list) for a DESTRUCTIVE choice, so
showing which dice are eligible is information the player needs.

NOTE 6: "ensure that all outlines appearing match the shape of the
settled die and not a straight square." Root cause found, and it could
never have been fixed with dials: the mark was
  .die.break-target{outline:2px solid #c66058;outline-offset:2px}
A CSS `outline` is drawn around the element's BORDER BOX - an
axis-aligned rectangle, by specification. The chip is a flat square
that sits under a 3D mesh which lands ROTATED, so the ring can only
ever be square while the die is not.
The fix routes marks through the painter that already solves this:
D3X's selection halo builds each shape from `_hullOf(d,sc,grow)` - the
die's real projected hull - which is why the gold keep-glow follows a
tumbled die correctly today. A second pass in the same loop paints
`.cardmark` dice in the card ink. One glow painter, per the house rule;
no new canvas, no new raster path.
BREAK's marking moves to `.cardmark` too, so the one arm that keeps
its candidate marking gets the hull shape as well.
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


# ── 1. the hull-painted mark, in the one glow painter ────────────────
sub("""    var self=this,G=this.GLOW;
    var sel=[],oppSel=false;
    this.dice.forEach(function(d){
      if(!d.match||!d.obj.visible)return;
      if(!d.chip.classList.contains('selected'))return;
      if(d.chip.classList.contains('oppkeep'))oppSel=true;
      var hull=self._hullOf(d,sc,G.grow);
      if(hull)sel.push(hull);
    });
    if(!sel.length)return;""",
    """    var self=this,G=this.GLOW;
    var sel=[],oppSel=false,marks=[];
    this.dice.forEach(function(d){
      if(!d.match||!d.obj.visible)return;
      /* P856: a CARD MARK is the same shape problem the keep-glow already
         solved. It used to be `outline:2px solid` on the flat chip, which
         is an axis-aligned box by spec, so it could never follow a die
         that landed rotated (Denis: "outlines... match the shape of the
         settled die and not a straight square"). Built from the same
         _hullOf projection as the selection halo. */
      if(d.chip.classList.contains('cardmark')){
        var mh=self._hullOf(d,sc,G.grow);
        if(mh)marks.push(mh);
      }
      if(!d.chip.classList.contains('selected'))return;
      if(d.chip.classList.contains('oppkeep'))oppSel=true;
      var hull=self._hullOf(d,sc,G.grow);
      if(hull)sel.push(hull);
    });
    if(marks.length){
      /* the card ink the square outline used, now on the real silhouette */
      var MK=(window.CARD_MARK_INK||'#c66058');
      this._paintHalo(cv,x,sc,dpr,marks,MK,MK,1);
    }
    if(!sel.length)return;""",
    '1 hull-painted card mark')

# ── 2. the CSS square retires; the class survives only as a hook ─────
sub(""".die.break-target{outline:2px solid #c66058;outline-offset:2px;cursor:pointer}""",
    """/* P856: NO OUTLINE HERE. A CSS outline is an axis-aligned box around the
   border box, so on a die that settles rotated it can only ever be a
   square around a tilted thing. The mark is painted from the die's real
   hull by D3X's halo painter (see .cardmark) - this class now carries
   only the pointer affordance. */
.die.break-target{cursor:pointer}
.die.cardmark{cursor:pointer}""",
    '2 square outline retired')

# ── 3. the three arms stop painting every die ────────────────────────
sub("""    free.forEach(function(d){
      if(!d.el)return;
      d.el.classList.add('break-target');
      d.el.onclick=function(){
        if(!G._steadyArmed)return;
        G._steadyArmed=false;""",
    """    /* P856 (Denis): the ARM marks nothing - the status line above says
       TAP THE DIE TO REROLL, and marking every candidate was noise. The
       die actually PICKED gets the card's own mark, below. */
    free.forEach(function(d){
      if(!d.el)return;
      d.el.classList.add('break-target');/* affordance only - no outline */
      d.el.onclick=function(){
        if(!G._steadyArmed)return;
        G._steadyArmed=false;
        try{d.el.classList.add('cardmark');
          setTimeout(function(){if(d.el)d.el.classList.remove('cardmark');},900);}catch(e){}""",
    '3a steady_hand pick-mark')

sub("""    free.forEach(function(d){
      if(!d.el)return;
      d.el.classList.add('break-target');
      d.el.onclick=function(){
        if(!G._transArmed)return;
        G._transArmed=false;""",
    """    free.forEach(function(d){
      if(!d.el)return;
      d.el.classList.add('break-target');/* P856: affordance only */
      d.el.onclick=function(){
        if(!G._transArmed)return;
        G._transArmed=false;
        try{d.el.classList.add('cardmark');
          setTimeout(function(){if(d.el)d.el.classList.remove('cardmark');},900);}catch(e){}""",
    '3b transmute pick-mark')

sub("""    d.el.classList.add('break-target');
    d.el.onclick=function(){
      if(!G._sevenArmed)return;
      G._sevenArmed=false;""",
    """    d.el.classList.add('break-target');/* P856: affordance only */
    d.el.onclick=function(){
      if(!G._sevenArmed)return;
      G._sevenArmed=false;
      try{d.el.classList.add('cardmark');
        setTimeout(function(){if(d.el)d.el.classList.remove('cardmark');},900);}catch(e){}""",
    '3c seven_dice pick-mark')

# ── 4. BREAK keeps candidate marking (destructive subset) - hull-shaped ──
sub("""  live.forEach(function(d){
    if(!d.el)return;
    d.el.classList.add('break-target');
    d.el.onclick=function(){_breakDie(d);};
  });""",
    """  live.forEach(function(d){
    if(!d.el)return;
    /* P856: BREAK KEEPS ITS CANDIDATE MARKING and is the deliberate
       exception to Denis's note 4 - it marks a SUBSET (`live`) for a
       DESTRUCTIVE pick, so which dice are eligible is information the
       player needs. It moves to .cardmark so the mark is the die's real
       silhouette rather than a square. */
    d.el.classList.add('break-target');
    d.el.classList.add('cardmark');
    d.el.onclick=function(){_breakDie(d);};
  });""",
    '4 BREAK keeps a hull-shaped mark')

# every place that strips break-target must strip the mark too
sub("""    document.querySelectorAll('#playerDiceRow .die.break-target')
      .forEach(function(el){el.classList.remove('break-target');});""",
    """    document.querySelectorAll('#playerDiceRow .die.break-target,#playerDiceRow .die.cardmark')
      .forEach(function(el){el.classList.remove('break-target','cardmark');});/* P856 */""",
    '5a _steadyDisarm strips both')
sub("""  G.pool.forEach(function(q){if(q.el)q.el.classList.remove('break-target');});""",
    """  G.pool.forEach(function(q){if(q.el)q.el.classList.remove('break-target','cardmark');});/* P856 */""",
    '5b break cleanup strips both')
sub("""row.querySelectorAll('.die').forEach(el=>{if(el.classList.contains('die-frozen'))return;el.getAnimations().forEach(a=>a.cancel());el.style.transform='';el.style.opacity='';el.style.animation='';el.classList.remove('scatter','bust','break-target');});""",
    """row.querySelectorAll('.die').forEach(el=>{if(el.classList.contains('die-frozen'))return;el.getAnimations().forEach(a=>a.cancel());el.style.transform='';el.style.opacity='';el.style.animation='';el.classList.remove('scatter','bust','break-target','cardmark');});/* P856 */""",
    '5c roll sweep strips both')
sub("""    if(d.el&&!d.committed){d.el.classList.remove('break-target');d.el.onclick=function(){toggleDie(d);};}""",
    """    if(d.el&&!d.committed){d.el.classList.remove('break-target','cardmark');d.el.onclick=function(){toggleDie(d);};}/* P856 */""",
    '5d transmute disarm strips both')

# post-asserts
if 'outline:2px solid #c66058' in s:
    sys.exit('SQUARE OUTLINE SURVIVED (nothing written)')
if s.count("classList.add('cardmark')") != 4:
    sys.exit('cardmark adds = %d, expected 4 (3 picks + BREAK) (nothing written)'
             % s.count("classList.add('cardmark')"))
for needed in ["d.chip.classList.contains('cardmark')", 'CARD_MARK_INK', "remove('break-target','cardmark')"]:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
