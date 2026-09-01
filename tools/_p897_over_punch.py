# -*- coding: utf-8 -*-
u"""P897: P777's third case - a canvas OVER the dice - gets its own cut, so
`line` means the same thickness on both layers.

WHAT WAS MEASURED, and it is not what I predicted. I expected a beat's ring to
wash its NEIGHBOURS: _paintHalo punches with the shapes in `sel`, a row passes
every die it applies to and a beat passes only its own, so a beat's glow is cut
by one silhouette and nothing else. On the under canvas a neighbour occludes the
spill; over it, nothing does.

That is wrong, and the geometry says why: the dice sit 77px apart centre to
centre and are 51px wide, so there is a 26px gap between silhouettes, and the
soft pass reaches 11px stretched to about 13.6. Measured: 0 pixels of a beat's
ring land inside any neighbour's silhouette. The prediction was reasoned from
the punch's construction without checking the distances it had to cross.

WHAT IT FOUND INSTEAD is the case Denis named: 1231 of 11350 lit pixels land
inside the beat's OWN die - about 11%, against a 2% threshold. Not the punch
failing. THE LINE. It is stroked AFTER the cut, by design ("the line goes on the
SAME surface as the halo, after the cut-out, so the two composite as one glow"),
at lineWidth 3.2 centred on a hull grown 1.004 - which is 0.1px outside the true
silhouette on a 51px die. So half the line, about 1.5px, falls INSIDE the die.

UNDER the dice that half is occluded and `line:3.2` reads as 1.6px of light
outside the silhouette, which is what the dial was tuned against. OVER them the
whole 3.2 shows and half of it paints on the die's own edge. The defect is not
that it looks bad - it is that one dial now means two different weights
depending on which canvas the caller chose, which is how a tuned number stops
being tuned.

THE CUT LANDS A HAIR INSIDE, per Denis: exactly at the silhouette leaves a seam
to line up perfectly, and a fraction inside hides it under the die's own edge.
`shrink:+G.clear` on the grown hull cuts at true - 0.6px. It runs AFTER the line
and only when the caller says its canvas is over the subject.

THE UNDER LAYER IS NOT TOUCHED. The selection halo is the most tuned thing in
this file and it lives there; the new pass is opt-in and the probe asserts the
under canvas is byte-identical across the change.
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


# ══ 1. the third cut, after the line ═══════════════════════════════
sub(u"""    /* additive, so it reads as light rather than paint */
    x.save();
    x.globalCompositeOperation='lighter';""",
    u"""    /* P897: P777'S THIRD CASE - a canvas that sits OVER its subject.
       That note distinguishes two punches: the dice's, which WIDENS by
       G.clear because their canvas is over the painted TABLE and a wash on
       the die is the failure, and punchUnder, which cuts inward for a canvas
       beneath its subject. A canvas over the DICE is neither, and the reason
       it needs a third cut is the line rather than the punch.
       The line is stroked after the cut-out on purpose, so it and the halo
       composite as one glow. At lineWidth 3.2 centred on a hull grown 1.004 -
       0.1px outside the true silhouette on a 51px die - about 1.5px of it
       falls INSIDE the die. Under the dice that half is occluded and the dial
       reads as 1.6px of light outside the edge, which is what it was tuned
       against; over them the whole 3.2 shows and half paints on the die's own
       face. One dial, two weights, decided by the caller's canvas.
       So: cut once more, after the line, a HAIR inside rather than exactly on
       the silhouette - `shrink:+G.clear` lands at true - 0.6px, and that
       fraction tucks under the die's own edge instead of leaving a seam to
       line up perfectly. Measured at 1231 of 11350 lit pixels inside the
       subject before this. Opt-in, so the under layer - where the selection
       halo lives - is untouched. */
    if(opts&&opts.overSubject){
      gx.globalCompositeOperation='destination-out';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp)return;
        lay(gx,sh,null,{shrink:G.clear});
      });
      gx.globalCompositeOperation='source-over';
    }
    /* additive, so it reads as light rather than paint */
    x.save();
    x.globalCompositeOperation='lighter';""",
    '1 the over-subject cut')

# ══ 2. _paintForm carries the layer ════════════════════════════════
sub(u"""  _paintForm:function(style,cv,x,sc,dpr,hulls,col,soft,alphaMul){""",
    u"""  _paintForm:function(style,cv,x,sc,dpr,hulls,col,soft,alphaMul,over){""",
    '2a the signature')

sub(u"""    var AM=(alphaMul==null?1:alphaMul);
    if(style==='crust'){
      var C=this.CRUST;
      this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM,C.line,C);
      return;
    }""",
    u"""    var AM=(alphaMul==null?1:alphaMul);
    /* `over` is the caller's canvas, not the form's - see the third-case note
       in _paintHalo. A VEIL needs nothing: it is a fill on the hull and has no
       geometry outside the silhouette to cut. */
    if(style==='crust'){
      var C=this.CRUST;
      this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM,C.line,
        over?{soft:C.soft,rim:C.rim,strength:C.strength,overSubject:1}:C);
      return;
    }""",
    '2b the crust branch')

sub(u"""    this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM);
  },""",
    u"""    this._paintHalo(cv,x,sc,dpr,hulls,col,soft,AM,undefined,
                    over?{overSubject:1}:undefined);
  },""",
    '2c the rim branch')

# ══ 3. the over pass says so, in both of its painters ══════════════
sub(u"""      this._paintForm(row.style,cv,x,sc,dpr,hulls,col,soft);
      n++;""",
    u"""      this._paintForm(row.style,cv,x,sc,dpr,hulls,col,soft,1,layer==='over');
      n++;""",
    '3a the rows')

sub(u"""        this._paintForm('rim',cv,x,sc,dpr,[hb],mk.ink,mk.ink,am);
      }else if(mk.kind==='flash'){
        this._paintForm('veil',cv,x,sc,dpr,[hb],mk.ink,mk.ink,am*1.9);""",
    u"""        this._paintForm('rim',cv,x,sc,dpr,[hb],mk.ink,mk.ink,am,true);
      }else if(mk.kind==='flash'){
        this._paintForm('veil',cv,x,sc,dpr,[hb],mk.ink,mk.ink,am*1.9,true);""",
    '3b the beats')

# ── post-asserts, comments stripped ─────────────────────────────────
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)

if code.count('opts.overSubject') != 1:
    sys.exit('the third cut is not present exactly once (nothing written)')
# ORDERING, and the bounds must be _paintHalo's own. A file-wide index() for a
# composite mode that four painters use found one three thousand lines earlier
# and failed a correct patch - the first version of this assert did exactly
# that. Scope first, then order.
_fn = code.index('_paintHalo:function')
_end = code.index('_tintStamp:function', _fn)
body = code[_fn:_end]
_line = body.index("gx.strokeStyle=COL")
_cut = body.index('opts.overSubject')
_comp = body.index("x.globalCompositeOperation='lighter'")
if _cut < _line:
    sys.exit('the over cut runs before the line it exists to trim '
             '(nothing written)')
if _cut > _comp:
    sys.exit('the over cut runs after the composite (nothing written)')
_cut = _fn + _cut
# the cut must go INWARD here - the dice's own punch widens, and copying that
# sign would make this pass do nothing at all
seg = code[_cut:_cut + 400]
if 'shrink:G.clear' not in seg:
    sys.exit('the over cut does not shrink inward (nothing written)')

# THE UNDER LAYER MUST NOT OPT IN
if code.count("over?{overSubject:1}") != 1 or code.count('overSubject:1}') != 2:
    sys.exit('the opt-in is not wired exactly twice (nothing written)')
if "layer==='over'" not in code:
    sys.exit('the row painter does not pass its layer (nothing written)')
# both beat forms declare their canvas
if code.count("mk.ink,am,true)") != 1 or code.count("mk.ink,am*1.9,true)") != 1:
    sys.exit('a beat form does not declare its canvas (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
