# -*- coding: utf-8 -*-
"""P671b: the sheet's buttons earn their place on parchment.

Screenshot check after P671: the PLAY button is .gbx-btn.primary, whose greybox
recipe is #e0d6b8 on the sheet's new #e7d6ac - two parchments a shade apart, so
the button reads as a thin outline and nothing else. The variant restyles the
kit buttons it contains: gold plaque fill, ink text darker than the trim, per
the standing rule. Scoped to .fam-sheet, so the shop and the book keep the
greybox buttons they were built against.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = (u"/* the drag pill is written inline as grey; on parchment it goes tea-brown */\n"
       u"#gbSheet.fam-sheet>div:first-child{background:rgba(90,60,20,.35)!important}")
new = (u"/* the drag pill is written inline as grey; on parchment it goes tea-brown */\n"
       u"#gbSheet.fam-sheet>div:first-child{background:rgba(90,60,20,.35)!important}\n"
       u"/* P671b: the kit buttons on parchment. The greybox primary is #e0d6b8 -\n"
       u"   a shade off the sheet's own #e7d6ac, so PLAY rendered as a bare outline.\n"
       u"   Gold plaque fill, ink darker than the trim. */\n"
       u"#gbSheet.fam-sheet .gbx-btn{background:#d9bd84;border:2px solid #8a6a2c;color:#241505}\n"
       u"#gbSheet.fam-sheet .gbx-btn.primary{background:#c9a24a;border-color:#7a5a1c;color:#241505}")
c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)' % c)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('  ok  P671b button contrast')
