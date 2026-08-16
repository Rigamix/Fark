# -*- coding: utf-8 -*-
"""P753: smooth halo, no seam, SCREEN-space mask, card dials that drive
the stamp, and the dim arrives earlier.

Five of Denis's morning notes, one region:

1. ALIASED GLOWS. The mip blur went down in halves but came back up in
   ONE bilinear jump - a 16x upscale of a tiny bitmap is exactly the
   stair-step he photographed. The chain now walks back UP in 2x steps
   through a second set of canvases; each step is another smoothing tap,
   which is the standard mip-blur shape.

2. THE SEAM. The world-mask faded off the top face with
   smoothstep(0.55,0.85) of the up-normal - a transition band two
   triangle-rows wide across the rounded corner, reading as a line under
   the rim. The fade now spans the whole corner arc (0.18..0.92), so it
   reads as shading, not an edge.

3. THE AXIS, PER DIE, STILL. World X is one direction in the WORLD, but
   each face shows its projection - foreshortened differently per face
   and per die, which is what Denis's eye caught. The gradient is now
   computed in CLIP space: the fragment's own ndc against the die's
   projected centre, normalised by the die's projected width. Same
   screen direction on every die, every face, mathematically.

4. CARD HALO DIALS DID NOTHING - true: floor is invisible at k=1, and
   round/line only fed the retired hull fallback. CARD_GLOW now carries
   its own soft/rim/strength (the stamp's real knobs), _paintHalo takes
   them as caller opts, and the lab's card row is reach/core/strength/
   floor.

5. THE DIM ARRIVES EARLIER: SIDEDIM_RAMP.lead ends the ramp 140ms before
   the die rests (it used to land exactly WITH it - P720), both the live
   and the resume formulas.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    c = s.count(old)
    if c != 1:
        o2 = old.replace('\n', '\r\n')
        if s.count(o2) == 1:
            old, new = o2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
    s = s.replace(old, new)
    edits.append(label)


# ── 1. the blur comes back up in steps ──
sub("""      dst.save();
      dst.setTransform(1,0,0,1,0,0);
      dst.imageSmoothingEnabled=true;
      for(var p=0;p<(passes||1);p++)dst.drawImage(cur,0,0,cw,ch,0,0,S.width,S.height);
      dst.restore();
    };""",
    """      /* P753: BACK UP IN 2x STEPS. One bilinear jump from 1/16 scale is
         the stair-step Denis photographed - each halving step down gets a
         matching doubling step up, and every step is another smoothing
         tap. A second canvas set, because a canvas cannot cleanly scale
         into itself. */
      self._mups=self._mups||[];
      for(var ui=n-2;ui>=0;ui--){
        var um=self._mups[ui]||(self._mups[ui]=document.createElement('canvas'));
        var uw=self._mips[ui].width,uh=self._mips[ui].height;
        if(um.width!==uw||um.height!==uh){um.width=uw;um.height=uh;}
        var ux=um.getContext('2d');
        ux.setTransform(1,0,0,1,0,0);
        ux.clearRect(0,0,uw,uh);
        ux.imageSmoothingEnabled=true;
        ux.drawImage(cur,0,0,cw,ch,0,0,uw,uh);
        cur=um;cw=uw;ch=uh;
      }
      dst.save();
      dst.setTransform(1,0,0,1,0,0);
      dst.imageSmoothingEnabled=true;
      for(var p=0;p<(passes||1);p++)dst.drawImage(cur,0,0,cw,ch,0,0,S.width,S.height);
      dst.restore();
    };""",
    'up-chain')

# ── 2+3. the shader: clip-space axis, wide corner fade ──
i = s.find("    m.onBeforeCompile=function(sh){")
j = s.find("    m.needsUpdate=true;", i)
if i < 0 or j < 0:
    sys.exit('shader markers not found (nothing written)')
NEWSH = (
    "    m.onBeforeCompile=function(sh){\n"
    "      sh.uniforms.fkK=u.uK;sh.uniforms.fkAmt=u.uAmt;sh.uniforms.fkAxSel=u.uAxSel;\n"
    "      sh.uniforms.fkSpan=u.uSpan;sh.uniforms.fkDim=u.uDim;\n"
    "      /* P753: CLIP SPACE, not world space. World X is one direction in\n"
    "         the world but each face shows its own foreshortened projection\n"
    "         of it - which is exactly 'a different axis per die'. The ramp\n"
    "         is the fragment's ndc against the die's projected centre,\n"
    "         normalised by the die's projected width, so every die wears\n"
    "         the same screen direction by construction. */\n"
    "      sh.vertexShader=sh.vertexShader\n"
    "        .replace('#include <common>',\n"
    "          '#include <common>\\nvarying vec4 vFkClip;varying vec2 vFkC2;varying vec2 vFkSp;varying vec3 vFkN;')\n"
    "        .replace('#include <worldpos_vertex>',\n"
    "          '#include <worldpos_vertex>\\n'\n"
    "          +'vFkClip=projectionMatrix*modelViewMatrix*vec4(position,1.0);\\n'\n"
    "          +'vec4 fkCv=modelViewMatrix*vec4(0.0,0.0,0.0,1.0);\\n'\n"
    "          +'vec4 fkCc=projectionMatrix*fkCv;\\n'\n"
    "          +'vFkC2=fkCc.xy/fkCc.w;\\n'\n"
    "          +'vec4 fkPx=projectionMatrix*(fkCv+viewMatrix*vec4(fkSpanV,0.0,0.0,0.0));\\n'\n"
    "          +'vec4 fkPy=projectionMatrix*(fkCv+viewMatrix*vec4(0.0,0.0,fkSpanV,0.0));\\n'\n"
    "          +'vFkSp=vec2(max(abs(fkPx.x/fkPx.w-vFkC2.x),1e-4),max(abs(fkPy.y/fkPy.w-vFkC2.y),1e-4));\\n'\n"
    "          +'vFkN=normalize(mat3(modelMatrix[0].xyz,modelMatrix[1].xyz,modelMatrix[2].xyz)*normal);')\n"
    "        .replace('#include <common>',\n"
    "          '#include <common>\\nuniform float fkSpanV;')\n"
    "      ;\n"
    "      /* the vertex shader sees the span as fkSpanV; the fragment keeps\n"
    "         fkSpan as its own name - same uniform value, declared twice\n"
    "         under two names would collide, so vertex gets its own */\n"
    "      sh.uniforms.fkSpanV=u.uSpan;\n"
    "      sh.fragmentShader=sh.fragmentShader\n"
    "        .replace('#include <common>',\n"
    "          '#include <common>\\nvarying vec4 vFkClip;varying vec2 vFkC2;varying vec2 vFkSp;varying vec3 vFkN;\\n'\n"
    "          +'uniform float fkK;uniform float fkAmt;uniform float fkAxSel;'\n"
    "          +'uniform float fkSpan;uniform vec3 fkDim;')\n"
    "        .replace('#include <map_fragment>',\n"
    "          '#include <map_fragment>\\n'\n"
    "          +'if(fkK>0.001&&abs(fkAmt)>0.0001){\\n'\n"
    "          +'  vec2 fkD=vFkClip.xy/vFkClip.w-vFkC2;\\n'\n"
    "          +'  float fkT=clamp(0.5+mix(fkD.x/vFkSp.x,-fkD.y/vFkSp.y,fkAxSel),0.0,1.0);\\n'\n"
    "          /* P753: the fade spans the WHOLE corner arc - the old\n"
    "             0.55..0.85 band was two triangle-rows wide and read as a\n"
    "             seam under the top rim */\n"
    "          +'  float fkM=1.0-smoothstep(0.18,0.92,dot(normalize(vFkN),vec3(0.0,1.0,0.0)));\\n'\n"
    "          +'  float fkKt=fkK*(1.0-abs(fkAmt)*(fkAmt>0.0?fkT:(1.0-fkT)));\\n'\n"
    "          +'  vec3 fkA=vec3(1.0)-(vec3(1.0)-fkDim)*fkKt;\\n'\n"
    "          +'  vec3 fkF=vec3(1.0)-(vec3(1.0)-fkDim)*fkK;\\n'\n"
    "          +'  diffuseColor.rgb*=mix(vec3(1.0),fkA/max(fkF,vec3(0.02)),fkM);\\n'\n"
    "          +'}');\n"
    "    };\n"
)
s = s[:i] + NEWSH + s[j:]
edits.append('clip-space shader')

sub("""    var u={uK:{value:0},uAmt:{value:0},uAx:{value:new THREE.Vector3(1,0,0)},
           uSpan:{value:1},uDim:{value:new THREE.Color(this.SIDEDIM)}};""",
    """    var u={uK:{value:0},uAmt:{value:0},uAxSel:{value:0},
           uSpan:{value:1},uDim:{value:new THREE.Color(this.SIDEDIM)}};""",
    'uniforms: axis selector')

sub("""  _syncGrad:function(u){
    var g=this.GRAD;
    u.uAmt.value=g.amt||0;
    if(g.ax==='y')u.uAx.value.set(0,0,1);
    else u.uAx.value.set(1,0,0);
  },""",
    """  _syncGrad:function(u){
    var g=this.GRAD;
    u.uAmt.value=g.amt||0;
    /* P753: a selector between the two SCREEN ramps, not a world vector */
    u.uAxSel.value=(g.ax==='y')?1:0;
  },""",
    'syncGrad selector')

# ── 4. CARD_GLOW's own knobs, _paintHalo takes caller opts ──
sub("  CARD_GLOW:{col:'#ffe6a4', soft:'#ffa93a', round:0.075, line:0, floor:0.42},",
    """  /* P753: the stamp's real knobs - reach/core/strength were GLOW's
     before, so the lab's card sliders drove nothing the card halo read.
     softCol is the outer wash colour (soft is now the blur reach). */
  CARD_GLOW:{col:'#ffe6a4', softCol:'#ffa93a', soft:11, rim:3, strength:0.91,
    round:0.075, line:0, floor:0.42},""",
    'CARD_GLOW knobs')

sub("  _paintHalo:function(cv,x,sc,dpr,sel,COL,SOFT,alphaMul,lineW){\n"
    "    var self=this,G=this.GLOW;",
    "  _paintHalo:function(cv,x,sc,dpr,sel,COL,SOFT,alphaMul,lineW,opts){\n"
    "    var self=this,G=this.GLOW;\n"
    "    /* P753: reach/core/strength are the CALLER's when given - the card\n"
    "       halo tunes independently of the dice without borrowing dials */\n"
    "    var SOFTR=(opts&&opts.soft!==undefined)?opts.soft:G.soft;\n"
    "    var RIMR=(opts&&opts.rim!==undefined)?opts.rim:G.rim;\n"
    "    var STR=(opts&&opts.strength!==undefined)?opts.strength:G.strength;",
    'paintHalo opts')

sub("    blurOnto(gx,G.soft,G.softPasses||1);",
    "    blurOnto(gx,SOFTR,G.softPasses||1);", 'soft uses opts')
sub("    blurOnto(gx,G.rim,G.rimPasses||1);",
    "    blurOnto(gx,RIMR,G.rimPasses||1);", 'rim uses opts')
sub("    x.globalAlpha=G.strength*(alphaMul===undefined?1:alphaMul);",
    "    x.globalAlpha=STR*(alphaMul===undefined?1:alphaMul);", 'strength uses opts')

sub("""      self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.soft,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line);""",
    """      self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line,
        {soft:CG.soft,rim:CG.rim,strength:CG.strength});""",
    'card passes its knobs')

# ── 5. the dim leads the rest ──
sub("  SIDEDIM_RAMP:{delay:0,dur:350,steps:8},/* P720: twice as fast, lands WITH the die */",
    """  /* P720 landed the ramp WITH the die; P753 leads it - the shadow is
     fully on `lead` ms before the die rests (Denis: 'a bit earlier
     still'). */
  SIDEDIM_RAMP:{delay:0,dur:350,steps:8,lead:140},""",
    'ramp lead dial')

sub("    var _k=(performance.now()-((d.phys.t||0)-_R.dur)-_R.delay)/_R.dur;",
    "    var _k=(performance.now()-((d.phys.t||0)-(_R.lead||0)-_R.dur)-_R.delay)/_R.dur;/* P753: leads the rest */",
    'live formula leads')

sub("            var _kL=_lt?(performance.now()-(_lt-D3X.SIDEDIM_RAMP.dur))/D3X.SIDEDIM_RAMP.dur:0;",
    "            var _kL=_lt?(performance.now()-(_lt-(D3X.SIDEDIM_RAMP.lead||0)-D3X.SIDEDIM_RAMP.dur))/D3X.SIDEDIM_RAMP.dur:0;/* P753 */",
    'resume formula leads')

io.open(P, 'w', encoding='utf-8', newline='').write(s)

# ── lab: the card row becomes the stamp's real dials ──
L = os.path.join(ROOT, 'fark_lab.html')
sl = io.open(L, encoding='utf-8', newline='').read()
OLDROW = ("    +'<br><label>floor <input type=\"range\" id=\"cgFloor\" min=\"0\" max=\"100\" value=\"42\" oninput=\"cardDial(&quot;floor&quot;,this.value/100)\"></label>'\n"
          "    +'<label>corner <input type=\"range\" id=\"cgRound\" min=\"0\" max=\"30\" value=\"7.5\" step=\"0.5\" oninput=\"cardDial(&quot;round&quot;,this.value/100)\"></label>'\n"
          "    +'<label>rim line <input type=\"range\" id=\"cgLine\" min=\"0\" max=\"6\" value=\"0\" step=\"0.2\" oninput=\"cardDial(&quot;line&quot;,+this.value)\"></label>'")
NEWROW = ("    /* P753: the dials the STAMP actually reads - corner/rim-line fed the\n"
          "       retired hull fallback and floor is invisible at the demo's k=1 */\n"
          "    +'<br><label>reach <input type=\"range\" id=\"cgSoft\" min=\"2\" max=\"30\" value=\"11\" oninput=\"cardDial(&quot;soft&quot;,+this.value)\"></label>'\n"
          "    +'<label>core <input type=\"range\" id=\"cgRim\" min=\"1\" max=\"10\" value=\"3\" step=\"0.5\" oninput=\"cardDial(&quot;rim&quot;,+this.value)\"></label>'\n"
          "    +'<label>strength <input type=\"range\" id=\"cgStr\" min=\"10\" max=\"100\" value=\"91\" oninput=\"cardDial(&quot;strength&quot;,this.value/100)\"></label>'\n"
          "    +'<label>floor <input type=\"range\" id=\"cgFloor\" min=\"0\" max=\"100\" value=\"42\" oninput=\"cardDial(&quot;floor&quot;,this.value/100)\"></label>'")
c = sl.count(OLDROW)
if c != 1:
    o2 = OLDROW.replace('\n', '\r\n')
    if sl.count(o2) == 1:
        OLDROW, NEWROW = o2, NEWROW.replace('\n', '\r\n')
    else:
        sys.exit('lab card row anchor x%d (game written, lab NOT)' % c)
sl = sl.replace(OLDROW, NEWROW)
io.open(L, 'w', encoding='utf-8', newline='').write(sl)
edits.append('lab card dials')

print('done: %d (%s)' % (len(edits), ', '.join(edits)))
