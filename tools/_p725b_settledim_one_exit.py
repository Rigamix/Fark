# -*- coding: utf-8 -*-
"""P725b: a material rebuild can no longer flash a settled die bright.

The probe pinned the second flicker: at roll resolution a rebuild path
(_rebrand at enchant-apply, _reskin at texture arrival) re-dresses every
material to the authored map and restamps liveMap - correct - but nothing
re-dims until the NEXT painted frame, so a dimmed die shows one full
bright frame. The settled dim becomes ONE function, _settleDim: frame()'s
settled branch applies it per frame as before, and the rebuild paths call
it synchronously so the bright map never reaches a paint.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    global s, n
    c = s.count(old)
    if c != count and '\n' in old:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == count:
            old, c = old2, count
            new = new.replace('\n', '\r\n')
    if c != count:
        sys.exit('ANCHOR x%d (need %d) for %s' % (c, count, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# 1) the one function, right after _dimMap
sub(u"    dm[key]=out;\n"
    u"    return out;\n"
    u"  },",
    u"    dm[key]=out;\n"
    u"    return out;\n"
    u"  },\n"
    u"  /* P725b: THE SETTLED DIM, ONE EXIT PATH. frame() applies it every\n"
    u"     frame, and the material-rebuild paths (_rebrand, _reskin) call it\n"
    u"     synchronously after restamping liveMap - a rebuild used to land\n"
    u"     authored-bright maps that no code re-dimmed until the next painted\n"
    u"     frame, one full bright flash on every dimmed die (Denis's\n"
    u"     'appears then off then back on'). */\n"
    u"  _settleDim:function(d){\n"
    u"    if(!d||!d.obj||!d.phys||!d.phys.v)return;\n"
    u"    var self=this,_R=this.SIDEDIM_RAMP;\n"
    u"    var _k=(performance.now()-(d.phys.t||0)-_R.delay)/_R.dur;\n"
    u"    _k=_k<0?0:(_k>1?1:_k);\n"
    u"    _k=_k*_k*(3-2*_k);/* smoothstep: no visible start, no visible stop */\n"
    u"    var _kk=(Math.round(_k*_R.steps)/_R.steps)*this.SIDEDIM_MAX;\n"
    u"    d.obj.traverse(function(o){\n"
    u"      if(!o.isMesh||!o.material||o.userData.outline)return;\n"
    u"      var m=o.material;\n"
    u"      if(!m.userData)m.userData={};\n"
    u"      if(!m.userData.liveMap)m.userData.liveMap=m.map;\n"
    u"      var want=(_kk>0?self._dimMap(m.userData.liveMap,d.phys.v,_kk):null)||m.userData.liveMap;\n"
    u"      if(m.map!==want){m.map=want;m.needsUpdate=true;}\n"
    u"    });\n"
    u"  },",
    '_settleDim defined after _dimMap')

# 2) frame()'s settled branch delegates to it
sub(u"          if(d.phys.v){\n"
    u"            var _R=D3X.SIDEDIM_RAMP;\n"
    u"            var _k=(performance.now()-(d.phys.t||0)-_R.delay)/_R.dur;\n"
    u"            _k=_k<0?0:(_k>1?1:_k);\n"
    u"            _k=_k*_k*(3-2*_k);/* smoothstep: no visible start, no visible stop */\n"
    u"            var _kk=(Math.round(_k*_R.steps)/_R.steps)*D3X.SIDEDIM_MAX;\n"
    u"            d.obj.traverse(function(o){\n"
    u"              if(!o.isMesh||!o.material||o.userData.outline)return;\n"
    u"              var m=o.material;\n"
    u"              if(!m.userData)m.userData={};\n"
    u"              if(!m.userData.liveMap)m.userData.liveMap=m.map;\n"
    u"              var want=(_kk>0?D3X._dimMap(m.userData.liveMap,d.phys.v,_kk):null)||m.userData.liveMap;\n"
    u"              if(m.map!==want){m.map=want;m.needsUpdate=true;}\n"
    u"            });\n"
    u"          }",
    u"          D3X._settleDim(d);/* P725b: the one settled-dim path */",
    'frame settled branch delegates')

# 3) _rebrand re-dims synchronously
sub(u"    d.obj.traverse(function(o){\n"
    u"      if(!o.isMesh||o.userData.outline)return;\n"
    u"      self._dress(o.material,d.mat,sk);\n"
    u"      self._faceLayers(o.material,d.mat,ench);/* P552 */\n"
    u"    });\n"
    u"  },\n"
    u"  _idQ:",
    u"    d.obj.traverse(function(o){\n"
    u"      if(!o.isMesh||o.userData.outline)return;\n"
    u"      self._dress(o.material,d.mat,sk);\n"
    u"      self._faceLayers(o.material,d.mat,ench);/* P552 */\n"
    u"    });\n"
    u"    this._settleDim(d);/* P725b: never leave a rebuilt die bright */\n"
    u"  },\n"
    u"  _idQ:",
    '_rebrand re-dims')

# 4) _reskin re-dims each die
sub(u"      d.obj.traverse(function(o){\n"
    u"        if(!o.isMesh||o.userData.outline)return;\n"
    u"        self._dress(o.material,d.mat,sk);\n"
    u"        /* re-apply the layers: _dress resets map to the base, and this is the\n"
    u"           very callback an icon's decode fires, so without this the brand could\n"
    u"           never survive the one event meant to apply it. */\n"
    u"        self._faceLayers(o.material,d.mat,ench);/* P552 */\n"
    u"      });\n"
    u"    });",
    u"      d.obj.traverse(function(o){\n"
    u"        if(!o.isMesh||o.userData.outline)return;\n"
    u"        self._dress(o.material,d.mat,sk);\n"
    u"        /* re-apply the layers: _dress resets map to the base, and this is the\n"
    u"           very callback an icon's decode fires, so without this the brand could\n"
    u"           never survive the one event meant to apply it. */\n"
    u"        self._faceLayers(o.material,d.mat,ench);/* P552 */\n"
    u"      });\n"
    u"      self._settleDim(d);/* P725b: never leave a rebuilt die bright */\n"
    u"    });",
    '_reskin re-dims')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
