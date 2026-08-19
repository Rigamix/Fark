# -*- coding: utf-8 -*-
"""P779: the card halo becomes one continuous light - summed octaves.

Denis (2026-08-19, close crop): "it's still aliased, I can see the two
layers (solid and the soft one), and the color is piss color rather
than gold. Should feel like a light, a magical golden glow."

What his crop shows, cause by cause:
  TWO LAYERS   the rim pass (r=2.5 blurred but STACKED x5 via the
               dice's G.rimPasses) plus the solid grow-ring remnant
               (what P777's inward punch leaves between the card edge
               and the grown stamp edge) sit as a hard band against
               the wide soft pass. Two distinct profiles = two visible
               layers.
  ALIASED      the band's steep stacked ramp quantizes, and the solid
               remnant's edge is the stamp's bilinear-scaled alpha.
  PISS         #ffae1f (deep amber) screen-blended over dark brown
               wood lands in ochre. Screen can only brighten toward
               the source colour - a dark gold IS mud over wood.

A light has ONE falloff. The card path now sums OCTAVES - the same
silhouette laid and mip-blurred at three radii, each its own colour:

  r 3   #fff3c4  x2   the hot near-white-gold core at the card's edge
  r 8   #ffd24a       the golden body
  r 20  #ffb238       the faint warm spill (deep: mip cap 6, since
                      the default cap of 5 tops out at ~10.7 user px
                      on a dpr-3 phone - the wide octave literally
                      could not exist there)

Their sum is a smooth exponential-ish curve - no boundary to see, and
the overlapping facet scales of the three mip ladders mask each
other's banding. grow goes 1.02 -> 1.0: with no rim stack there is
nothing for a core ring to seed, so NOTHING solid survives - the punch
cuts a hair inside the true edge and every visible pixel is blur.

The rival's armed telegraph keeps its colour: an e.col override
re-tints all octaves (same red, three radii - the same light grammar).
The dice pass no octaves and take the byte-identical soft+rim path.
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


# ── 1. blurOnto takes a caller mip cap (the wide octave needs 6) ──
sub("""    var blurOnto=function(dst,r,passes){
      var F=Math.max(2,r*dpr);
      var n=Math.max(1,Math.min(5,Math.round(Math.log(F)/Math.LN2)));""",
    """    var blurOnto=function(dst,r,passes,maxN){
      var F=Math.max(2,r*dpr);
      /* P779: the default cap of 5 tops the radius out at 32/dpr user px
         - ~10.7 on a dpr-3 phone. A wide octave passes 6. */
      var n=Math.max(1,Math.min(maxN||5,Math.round(Math.log(F)/Math.LN2)));""",
    'mip cap is caller-aware')

# ── 2. the octave path replaces soft+rim when given ──
sub("""    var SX=(opts&&opts.sx!==undefined)?opts.sx:G.sx;
    var SY=(opts&&opts.sy!==undefined)?opts.sy:G.sy;
    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:SX,sy:SY});});
    blurOnto(gx,SOFTR,(opts&&opts.softPasses)||G.softPasses||1);/* P778b: caller's count */
    /* then the bright rim, stacked - the punch-out below throws away the
       inner half of every blur, so a single pass never reads as strong */
    sxc.setTransform(dpr,0,0,dpr,0,0);
    sxc.clearRect(0,0,sc.width,sc.height);
    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,G.rimPasses||1);""",
    """    var SX=(opts&&opts.sx!==undefined)?opts.sx:G.sx;
    var SY=(opts&&opts.sy!==undefined)?opts.sy:G.sy;
    if(opts&&opts.octaves){
      /* P779: ONE CONTINUOUS LIGHT. The same silhouette, blurred at a
         few radii in a few colours and SUMMED - a smooth curve with no
         rim band and no boundary between layers (Denis: "I can see the
         two layers"). Each octave: {r, col, passes, deep}. */
      opts.octaves.forEach(function(oc){
        sxc.setTransform(dpr,0,0,dpr,0,0);
        sxc.globalCompositeOperation='source-over';
        sxc.clearRect(0,0,sc.width,sc.height);
        sel.forEach(function(sh){lay(sxc,sh,oc.col,{dy:(DY!==null)?DY:0,sx:SX,sy:SY});});
        blurOnto(gx,oc.r,oc.passes||1,oc.deep?6:undefined);
      });
    }else{
    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:SX,sy:SY});});
    blurOnto(gx,SOFTR,(opts&&opts.softPasses)||G.softPasses||1);/* P778b: caller's count */
    /* then the bright rim, stacked - the punch-out below throws away the
       inner half of every blur, so a single pass never reads as strong */
    sxc.setTransform(dpr,0,0,dpr,0,0);
    sxc.clearRect(0,0,sc.width,sc.height);
    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,G.rimPasses||1);
    }""",
    'the octave path')

# ── 3. the card's dials: octaves, nothing solid ──
sub("""  /* P778: retuned AT DENIS'S REQUEST (2026-08-19) - gold not beige,
     tail at the dice's reach, core ring thinned so the edge is all
     falloff. */
  CARD_GLOW:{col:'#ffd84e', softCol:'#ffae1f', soft:11, rim:2.5, strength:0.91,
    grow:1.02, dyF:0, round:0.075, line:0, floor:0.42},""",
    """  /* P779 (Denis: "a magical golden glow"): the card halo is summed
     octaves - hot near-white core, golden body, faint warm spill. grow
     1.0: nothing solid survives the punch, every visible pixel is
     blur. col stays as the tint the drag/armed callers fall back to
     for their own accents. */
  CARD_GLOW:{col:'#ffd84e', softCol:'#ffae1f', soft:11, rim:2.5, strength:0.91,
    grow:1.0, dyF:0, round:0.075, line:0, floor:0.42,
    octaves:[{r:3,col:'#fff3c4',passes:2},{r:8,col:'#ffd24a'},{r:20,col:'#ffb238',deep:true}]},""",
    'octave dials')

# ── 4. the call passes them; an accent override re-tints all three ──
sub("""      self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line,
        {soft:CG.soft,rim:CG.rim,strength:CG.strength,dy:r.height*(CG.dyF||0),
         softPasses:CG.softPasses||2,/* P778b: presence under the screen blend */
         sx:1,sy:1,/* P777: the card does not lean like a die */
         punchUnder:true,punchScaleMul:1/(CG.grow||1)});/* P777: tail-only, tucked under the card */""",
    """      /* P779: a caller accent (the rival's red telegraph) re-tints the
         whole octave stack - same light, their colour. */
      var _oct=CG.octaves;
      if(e.col&&_oct)_oct=_oct.map(function(oc){return {r:oc.r,col:e.col,passes:oc.passes,deep:oc.deep};});
      self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line,
        {soft:CG.soft,rim:CG.rim,strength:CG.strength,dy:r.height*(CG.dyF||0),
         octaves:_oct,/* P779: one continuous light */
         sx:1,sy:1,/* P777: the card does not lean like a die */
         punchUnder:true,punchScaleMul:1/(CG.grow||1)});/* P777: tail-only, tucked under the card */""",
    'cards pass octaves')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
