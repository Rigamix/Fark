# -*- coding: utf-8 -*-
u"""P899a: the harness reports `sized`, because a correct reading and an
off-surface one were the same number.

FIFTH TIME A ZERO HAS NEEDED TO PROVE WHICH ZERO IT WAS. _glowCv creates the
element; _drawGlow is what sets the backing store to sc*dpr, and the sleep path
returns before that. So a freshly created canvas is 300x150, and painting into
it at a dpr transform puts the subject off the surface entirely: the read comes
back 0 lit, with no error anywhere, and it would have reported "the under layer
has no inner line" - the exact inverse of the truth.

`exists` already separates "no canvas" from "empty canvas". `sized` separates
"empty canvas" from "canvas too small to hold what was painted", which is a
third thing and the one that lies. It compares the backing store against what
the painters compute - the screen-match rect times min(devicePixelRatio,
GLOW_DPR_MAX) - rather than against zero, because 300x150 is not zero and is
exactly the case that fooled the probe.

THREE VALUES, NOT TWO. `sized` is null when the canvas does not exist: absence
is not mis-sizing, and collapsing them would rebuild the same conflation one
level up. Same reason px is reported separately from exists.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', '_fxh.js')
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


sub(u"""  /* alpha-coverage of a canvas. `exists` is deliberately separate from `px`:
     a missing canvas and an empty one are different findings, and conflating
     them turns "the canvas is clean" into an assertion that cannot fail. */
  function ink(id){
    const cv = document.getElementById(id || 'dgCanvas');
    if (!cv) return {exists:false, px:0, why:'no canvas'};
    if (!cv.width) return {exists:true, px:0, why:'zero-width canvas'};
    const d = cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;
    let n = 0;
    for (let i = 3; i < d.length; i += 4) if (d[i] > 8) n++;
    return {exists:true, px:n, w:cv.width, h:cv.height};
  }""",
    u"""  /* WHAT THE PAINTERS SIZE THEIR CANVASES TO. Every surface in this layer
     computes the same thing - the match screen's rect at min(dpr, the glow
     cap) - so `sized` can be checked against it rather than against zero.
     Returns null when the screen is not up, so "cannot tell" stays distinct
     from "wrong size". */
  function expectedSize(){
    const el = document.getElementById('screen-match');
    if (!el) return null;
    const r = el.getBoundingClientRect();
    if (r.width < 10) return null;
    const dpr = Math.min(devicePixelRatio || 1,
                         (window.D3X && D3X.GLOW_DPR_MAX) || 3);
    return {w: Math.round(r.width * dpr), h: Math.round(r.height * dpr)};
  }

  /* alpha-coverage of a canvas. `exists` is deliberately separate from `px`:
     a missing canvas and an empty one are different findings, and conflating
     them turns "the canvas is clean" into an assertion that cannot fail.
     P899a: and `sized` is separate from both. _glowCv creates the element,
     _drawGlow sizes the backing store, and the sleep path returns before that
     - so a canvas can exist at its 300x150 default while the painter draws at
     a dpr transform, putting the subject off the surface. That reads 0 lit
     with no error anywhere. 300x150 is not zero, so a width check cannot see
     it; only a comparison with what the painters use can. null when there is
     no canvas to size, because absence is not mis-sizing. */
  function sizedOf(cv){
    if (!cv) return null;
    const e = expectedSize();
    if (!e) return null;
    return cv.width === e.w && cv.height === e.h;
  }

  function ink(id){
    const cv = document.getElementById(id || 'dgCanvas');
    if (!cv) return {exists:false, sized:null, px:0, why:'no canvas'};
    if (!cv.width) return {exists:true, sized:false, px:0, why:'zero-width canvas'};
    const d = cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;
    let n = 0;
    for (let i = 3; i < d.length; i += 4) if (d[i] > 8) n++;
    const e = expectedSize();
    return {exists:true, sized:sizedOf(cv), px:n, w:cv.width, h:cv.height,
            expected:e, why:(sizedOf(cv) === false
              ? 'canvas is ' + cv.width + 'x' + cv.height + ', painters use ' +
                (e ? e.w + 'x' + e.h : '?') + ' - a reading from this surface '
                + 'cannot be trusted'
              : undefined)};
  }""",
    '1 ink reports sized')

sub(u"""  function hue(id, minA){
    const cv = document.getElementById(id || 'dgCanvas');
    if (!cv) return {exists:false, why:'no canvas'};
    if (!cv.width) return {exists:true, why:'zero-width canvas'};""",
    u"""  function hue(id, minA){
    const cv = document.getElementById(id || 'dgCanvas');
    if (!cv) return {exists:false, sized:null, why:'no canvas'};
    if (!cv.width) return {exists:true, sized:false, why:'zero-width canvas'};""",
    '2a hue reports sized on the empty paths')

sub(u"""    if (!n) return {exists:true, lit:0, why:'nothing above alpha floor'};""",
    u"""    if (!n) return {exists:true, sized:sizedOf(cv), lit:0,
                    why:'nothing above alpha floor'};""",
    '2b hue reports sized when unlit')

sub(u"""    return {exists:true, lit:n, hex, rgb:[r,g,b], share:+(best/n).toFixed(3),""",
    u"""    return {exists:true, sized:sizedOf(cv), lit:n, hex, rgb:[r,g,b],
            share:+(best/n).toFixed(3),""",
    '2c hue reports sized when lit')

sub(u"""  return {sleep, until, tap, settled, match, loadDice, rollAndSettle,
          draw, ink, hue, paintWith, clearMarks};""",
    u"""  return {sleep, until, tap, settled, match, loadDice, rollAndSettle,
          draw, ink, hue, paintWith, clearMarks, expectedSize, sizedOf};""",
    '3 export the sizers')

# ── post-asserts, comments stripped ─────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)
if code.count('function sizedOf') != 1 or code.count('function expectedSize') != 1:
    sys.exit('the sizers are not defined exactly once (nothing written)')
# every RETURN out of ink() and hue() must carry sized - a path that omits it
# is the one that will be read by the probe that needed it
for fn, end in (('function ink(', 'function paintWith'),
                ('function hue(', 'const clearMarks')):
    seg = code[code.index(fn):code.index(end)]
    rets = [r for r in re.findall(r'return \{[^;]*\};', seg, re.S)]
    if not rets:
        sys.exit('no returns found in %s (nothing written)' % fn)
    for r in rets:
        if 'sized' not in r:
            sys.exit('a return in %s omits sized: %s (nothing written)'
                     % (fn, r[:70]))
if 'sizedOf' not in code[code.index('return {sleep'):]:
    sys.exit('the sizers are not exported (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
