# -*- coding: utf-8 -*-
"""P859: the dim-map textures are handed back. Denis's note 3 - "dice
physics seem much more sticky and clunky after a few rolls? Or after a
few games."

MEASURED, and the shape is not what the first report said. Every
settled die walks an 8-step dim ramp, and each distinct (die value, dim
strength) pair builds a fresh 384x256 CanvasTexture cached on
tex.userData.dimMaps. The whole file contains exactly THREE .dispose()
calls and all three are o.material.dispose() - there is no texture
dispose anywhere, and the cache hangs off the texture's userData where
material disposal could not reach it in any case.

Two corrections to the diagnosis, both measured rather than reasoned:
 1. SIZE. The atlas is 384x256, so a dim texture is 393,216 bytes
    (384KB, ~524KB with mips) - not the 786KB first quoted, which is
    exactly 512x384x4 and was 2x high.
 2. IT IS BOUNDED, NOT UNBOUNDED. The key rounds k to 3dp, which looks
    continuous, but BOTH callers quantise first:
    _kk=(Math.round(_k*steps)/steps)*SIDEDIM_MAX with steps=8. So the
    key space is ~9 strengths (+1.15 for fog) x 6 values = ~60 per
    liveMap. Measured: 42 builds in 12 rolls, climbing then FLAT -
    exactly the saturation that model predicts.
So the leak is not runaway growth inside one match. It is that a
match's ~42-60 textures (~22-31MB) are never released, and each
distinct {mat,ench} pair carries its OWN liveMap and its own cache, so
the retained set multiplies per loadout and survives every match for
the whole page session. That is the phone-side pressure, and it is the
same family as P842's finding.

THE FIX: the caches are registered as they are built and purged when
the 3D layer detaches - which is the match's own teardown, the moment
the dice they belong to stop existing. The liveMap atlases themselves
are module-level and SHARED, so they are deliberately left alone; only
the derived dim textures are freed. _drop also points each material
back at its liveMap on the way out, so no mesh can be left holding a
reference to a texture that is about to be disposed.
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


# 1) register every texture that grows a cache
sub("""    var dm=tex.userData.dimMaps||(tex.userData.dimMaps={});""",
    """    var dm=tex.userData.dimMaps;
    if(!dm){
      dm=tex.userData.dimMaps={};
      /* P859: REGISTER THE OWNER so the cache can be handed back. Nothing
         in this file disposed a texture before - all three .dispose()
         calls are material disposals, and this cache lives on userData
         where a material disposal cannot reach it. */
      (this._dimOwners||(this._dimOwners=[])).push(tex);
    }""",
    '1 register cache owners')

# 2) the purge, next to the builder it undoes
sub("""  _settleDim:function(d){""",
    """  /* P859: HAND THE DIM TEXTURES BACK. Each is a 384x256 CanvasTexture
     (393,216 bytes, ~524KB with mips) and a match builds ~42-60 of them
     per liveMap - bounded, because both callers quantise k to
     SIDEDIM_RAMP.steps before the key is built, but never freed. Every
     distinct {mat,ench} pair has its own liveMap and its own cache, so
     the retained set multiplied per loadout and survived every match for
     the page's whole life. That is Denis's "sticky after a few games".
     The liveMap atlases themselves are module-level and shared by every
     die of that material - they are deliberately NOT touched here; only
     the derived dim textures are released. */
  _purgeDimMaps:function(){
    var freed=0,owners=this._dimOwners||[];
    for(var i=0;i<owners.length;i++){
      var tex=owners[i];
      if(!tex||!tex.userData||!tex.userData.dimMaps)continue;
      var dm=tex.userData.dimMaps;
      for(var k in dm){
        try{if(dm[k]&&dm[k].dispose){dm[k].dispose();freed++;}}catch(e){}
      }
      tex.userData.dimMaps=null;
    }
    this._dimOwners=[];
    return freed;
  },
  _settleDim:function(d){""",
    '2 the purge')

# 3) a dropped die stops pointing at a texture we are about to free
sub("""      if(o.isMesh&&o.material&&o.material.dispose)o.material.dispose();""",
    """      /* P859: point the material back at its shared atlas before the
         material goes - otherwise a dropped mesh is left referencing a
         dim texture that _purgeDimMaps is about to dispose. */
      if(o.isMesh&&o.material&&o.material.userData&&o.material.userData.liveMap){
        try{o.material.map=o.material.userData.liveMap;}catch(e){}
      }
      if(o.isMesh&&o.material&&o.material.dispose)o.material.dispose();""",
    '3 drop resets the map')

# 4) purge at the layer's own teardown
sub("""    this.dice.forEach(function(d){self._drop(d);});
    this.dice=[];
    document.documentElement.classList.remove('fk3d');""",
    """    this.dice.forEach(function(d){self._drop(d);});
    this.dice=[];
    /* P859: the dim textures belong to the dice that just stopped
       existing - free them here, at the layer's own teardown, rather
       than letting a match's ~22-31MB ride to the end of the session. */
    try{this._purgeDimMaps();}catch(e){}
    document.documentElement.classList.remove('fk3d');""",
    '4 purge on detach')

for needed in ['_purgeDimMaps:function()', '_dimOwners', 'this._purgeDimMaps();']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
