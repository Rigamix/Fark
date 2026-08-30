# -*- coding: utf-8 -*-
u"""P880b: the over-canvas had taken the DICE SHADOW canvas's id.

#dsCanvas is declared in the markup (10434) inside #matchShadows, styled
mix-blend-mode:multiply (2246) and drawn by _drawDiceShadows (22712). _stateCv
does getElementById first and only creates when that misses - so it never
created anything. It handed back the shadow canvas, unstyled, still inside
#matchShadows, and _drawStates then resized it to the screen rect, cleared it
every frame and painted rims into a multiply layer. The shadows under the dice
would have gone out.

WHAT MAKES THIS WORTH A COMMENT RATHER THAN A QUIET RENAME: nothing that
guards this file could see it. The parse gate passed, the declaration diff
passed, and the probe's own paint assertions all passed at full strength -
`state.px > 0` was true every time, because the paint was landing on the
shadow canvas. A pixel count cannot tell you WHICH surface it counted. The
only thing that caught it was reading the new canvas's parentElement, which
is now a verdict in the probe rather than a thing I happened to print.

The id is stCanvas, checked unused. The guard below is the general form: a
patch that creates a DOM node by id must first assert the id is free, because
getElementById-then-create silently adopts on collision instead of failing.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

NEW_ID = 'stCanvas'

# ── the guard that would have stopped P880 ───────────────────────────
# count the id OUTSIDE the three sites this patch is about to write, which is
# every occurrence right now, since the rename has not happened yet.
if s.count(NEW_ID) != 0:
    sys.exit('%s is already used %d times - pick another (nothing written)'
             % (NEW_ID, s.count(NEW_ID)))

edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new); edits.append(label); return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


sub(u"""  _stateCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var cv=document.getElementById('dsCanvas');
    if(!cv){
      cv=document.createElement('canvas');cv.id='dsCanvas';""",
    u"""  _stateCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    /* P880b: THIS WAS #dsCanvas AND THAT ID WAS ALREADY THE SHADOW CANVAS
       (10434, inside #matchShadows, multiply-blended, drawn by
       _drawDiceShadows). getElementById-then-create does not fail on a
       collision, it ADOPTS - so this handed back the shadow canvas and the
       pass below resized it, cleared it every frame and painted rims into a
       multiply layer, putting the shadows under the dice out. Nothing caught
       it: the parse gate, the declaration diff and every pixel assertion in
       the probe passed at full strength, because a pixel count cannot say
       WHICH surface it counted. Reading parentElement is what caught it, and
       that is a verdict in the probe now. */
    var cv=document.getElementById('stCanvas');
    if(!cv){
      cv=document.createElement('canvas');cv.id='stCanvas';""",
    '1 the id renamed at the lookup and the create')

sub(u"""  _drawStates:function(){
    this._statePasses=(this._statePasses||0)+1;
    var cv=document.getElementById('dsCanvas'),i,d;""",
    u"""  _drawStates:function(){
    this._statePasses=(this._statePasses||0)+1;
    var cv=document.getElementById('stCanvas'),i,d;""",
    '2 the id renamed in the pass')

# ── post-asserts ─────────────────────────────────────────────────────
if s.count(NEW_ID) != 3:
    sys.exit('%s written %d times, expected 3 (nothing written)'
             % (NEW_ID, s.count(NEW_ID)))
_a = s.index('_stateCv:function(){')
_b = s.index('_hullOf:function(d,sc,grow){', _a)
if "getElementById('dsCanvas')" in s[_a:_b]:
    sys.exit('the state layer still reaches for the shadow canvas '
             '(nothing written)')
# the shadow canvas must still be reachable by everything that owned it
if s.count("getElementById('dsCanvas')") != 2:
    sys.exit('the shadow canvas has %d readers, expected its original 2 '
             '(nothing written)' % s.count("getElementById('dsCanvas')"))

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
