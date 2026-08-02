# -*- coding: utf-8 -*-
"""P425b - the third roster.

FTEXT held twelve authored name/description pairs for "images whose feats are
not coded yet". They are coded now, and FTEXT was consulted FIRST, so the
debug feats wall would have gone on describing conditions the game no longer
has - Own the Night as "clear every seat", No Claim as "decline a draft".
Every painting but Bookkeeper now has a real feat, so FTEXT shrinks to that
one orphan and the lookup order flips: the live feat wins, FTEXT is only the
fallback for a painting with no feat behind it.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

i0 = s.find(u"  /* authored texts for images whose feats are not coded yet */")
i1 = s.find(u"  var _artFeat={};Object.keys(FEAT_ART)")
assert i0 > 0 and i1 > i0, 'FTEXT block not found (%d,%d)' % (i0, i1)

NEW = u"""  /* THE ONE PAINTING WITH NO FEAT BEHIND IT. This table used to carry all
     twelve uncoded images and was consulted BEFORE the live feat, so once the
     roster was restored it would have kept describing conditions the game no
     longer has - "Own the Night: clear every seat", "No Claim: decline a
     draft". The roster is the source of truth now; this is the fallback for
     art with nothing behind it, and Bookkeeper is the only such art (Bookends
     collapsed into Vanguard, so its condition has no home). */
  var FTEXT={
    Bookkeeper:['Bookkeeper','Parked \\u2014 Bookends folded into Vanguard.']};
"""
s = s[:i0] + NEW + s[i1:]

old_lookup = (u"  var _ftext=function(n){\n"
              u"    if(FTEXT[n])return{nm:FTEXT[n][0],ds:FTEXT[n][1]};\n"
              u"    var id=_artFeat[n],f=id&&_fd[id];\n"
              u"    return{nm:(f&&f.label)||n.replace(/([A-Z])/g,' $1').trim(),ds:(f&&f.desc)||''};\n"
              u"  };\n")
assert s.count(old_lookup) == 1, 'lookup anchor matched %d' % s.count(old_lookup)
s = s.replace(old_lookup,
              u"  /* LIVE FEAT FIRST, authored text second. The old order let a stale\n"
              u"     hand-written line outrank the condition the game actually checks. */\n"
              u"  var _ftext=function(n){\n"
              u"    var id=_artFeat[n],f=id&&_fd[id];\n"
              u"    if(f)return{nm:f.label,ds:f.desc||''};\n"
              u"    if(FTEXT[n])return{nm:FTEXT[n][0],ds:FTEXT[n][1]};\n"
              u"    return{nm:n.replace(/([A-Z])/g,' $1').trim(),ds:''};\n"
              u"  };\n")

assert s != orig, 'nothing changed'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)

ft = s.split('var FTEXT={')[1].split('};')[0]
assert ft.count('[') == 1, 'FTEXT has %d entries, want 1' % ft.count('[')
print('P425b applied. FTEXT entries: %d' % ft.count('['))
