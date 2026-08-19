# -*- coding: utf-8 -*-
"""P782: the core blooms OVER the card's rim - the dark outline catches
the light.

Denis (2026-08-19): "do you see the thin darker outline between the
card and the glow? why is it there."

Measured, not guessed: the scanline across the card edge shows the
glow peak (L169), then 2-3 device px of near-black (16,13,5), then the
green border (L85). The near-black is THE CARD ART'S OWN PENCIL
OUTLINE - assets/cards/*.webp carries a ~5-natural-px opaque black rim
(18,10,4 @ alpha 255) before the green border. Both glow canvases sit
UNDER the card layer, so the light stops dead at the silhouette and
the black ink stays black against the brightest part of the halo -
which the eye reads as a dark gap. Real rim light BLOOMS over an
object's edge; ours could not, by architecture.

The fix: the CORE canvas moves above the card layer (z 9600 - above
the rows at 42 and the dragged card at 9500, since the drag is the
main lit state), and its punch cuts DEEPER (punchClear 3 user px vs
the default 0.7), so what survives is a ring whose inner ~3px wash
over the pencil rim and whose outer tail falls onto the table. The
card's border ink now catches the gold instead of biting a hole in it.
The interior stays clean - the punch still removes everything deeper
than the rim. The screened SPILL canvas stays under the card,
unchanged. punchClear is opts-aware with G.clear as the default, so
the spill and the dice punches are byte-identical.
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
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# ── 1. punchUnder's inset becomes opts-aware ──
sub("""    if(opts&&opts.punchUnder){
      gx.globalCompositeOperation='destination-out';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp){
          lay(gx,sh,null,{scaleMul:(opts.punchScaleMul||1)
            *(1-(2*G.clear)/Math.max(8,Math.min(sh.stamp.w,sh.stamp.h)))});
        }else{
          lay(gx,sh,null,{shrink:G.clear});
        }
      });
      gx.globalCompositeOperation='source-over';
    }else if(!(opts&&opts.noPunch)){""",
    """    if(opts&&opts.punchUnder){
      /* P782: the inset is the caller's - the rim-bloom core cuts ~3px
         deep so its inner ring washes OVER the card's own dark outline
         (its canvas sits above the card layer); the spill keeps the
         default hair-inside cut. */
      var PCL=(opts.punchClear!==undefined)?opts.punchClear:G.clear;
      gx.globalCompositeOperation='destination-out';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp){
          lay(gx,sh,null,{scaleMul:(opts.punchScaleMul||1)
            *(1-(2*PCL)/Math.max(8,Math.min(sh.stamp.w,sh.stamp.h)))});
        }else{
          lay(gx,sh,null,{shrink:PCL});
        }
      });
      gx.globalCompositeOperation='source-over';
    }else if(!(opts&&opts.noPunch)){""",
    'punch inset is opts-aware')

# ── 2. the core canvas rides above the card layer ──
sub("""      this._glowHiCv();/* the spill canvas first, so core lands above it */
      cv=document.createElement('canvas');cv.id='dgCanvasCore';
      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:41';
      sc.appendChild(cv);""",
    """      this._glowHiCv();/* the spill canvas first, so core lands above it */
      cv=document.createElement('canvas');cv.id='dgCanvasCore';
      /* P782: ABOVE the card layer (rows 42, dragged card 9500) - rim
         light BLOOMS over an object's edge. The card art carries an
         opaque black pencil outline, and a light from underneath can
         never brighten ink; from above, the border catches the gold. */
      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:9600';
      sc.appendChild(cv);""",
    'core above the cards')

# ── 3. the core call cuts deep ──
sub("""      if(_core.length&&x2)self._paintHalo(cv2,x2,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        _am,CG.line,_opts(_core));""",
    """      if(_core.length&&x2){
        var _co=_opts(_core);
        _co.punchClear=(CG.bloomPx!==undefined)?CG.bloomPx:3;/* P782: the rim-bloom depth */
        self._paintHalo(cv2,x2,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
          _am,CG.line,_co);
      }""",
    'the core cuts deep')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
