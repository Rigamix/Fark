# -*- coding: utf-8 -*-
"""P842: the enchant-crash fix - the shop's focus blur stops
rasterizing seven full-screen layers.

Denis's report cracked OPEN §12: the crash is GPU pressure on phone,
not a JS exception (which is why five exception-hunting probes found
nothing). Measured census of the enchant-focus state: SIX visible
1080x1920 art layers + one opacity-0 ghost still promoted + the live
full-viewport WebGL dice canvas, at phone dpr3 - and the focus state
applies an ANIMATED blur(5px) filter to every art layer separately
(seven+ independent blur rasters, re-run through the .35s transition),
plus a second blur on the enchant shelf in the picker state.

The fix, look-preserving:
 1. The per-layer filters are replaced by BACKDROP-FILTER SCRIMS - one
    blur pass of the composed backdrop instead of seven layer rasters.
    scrimA sits between the art stack and the goods shelf (st-focus:
    art blurred, shelf sharp - exactly today); scrimB sits above the
    shelf (st-epick: everything beneath blurred once). One honest
    delta, stated: in st-epick the art behind the shelf reads ~.42
    brightness instead of .62 - slightly darker behind a modal.
 2. The faded-out tab character stops compositing: visibility:hidden
    lands after the .34s fade (the show direction flips instantly), so
    each tab state carries one full-screen character layer, not two.
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


# 1) the scrims replace the per-layer filters
sub("""#gbShop .stL,#gbShop #stBack,#gbShop .stTabLbl{transition:filter .35s}
/* the enchant picker gets the same recede as the die focus - it used to sit
   on a flat black rectangle that did not even reach the top of the screen */
#gbShop.st-focus .stL,#gbShop.st-focus #stBack,#gbShop.st-focus .stTabLbl,
#gbShop.st-epick .stL,#gbShop.st-epick #stBack,#gbShop.st-epick .stTabLbl{
  filter:blur(5px) brightness(.62) saturate(.9)}
#gbShop.st-epick .stEnch{filter:blur(5px) brightness(.42);transition:filter .3s}""",
    """/* P842: the recede is a BACKDROP scrim, not per-layer filters. The old
   rules blurred seven full-screen 1080x1920 layers independently, with
   the blur re-run through an animated .35s transition, at phone dpr3,
   over a live WebGL canvas - the measured cause of the enchant-screen
   crash (OPEN §12: GPU pressure, never a JS exception). A backdrop
   scrim blurs the COMPOSED region once. scrimA sits under the goods
   shelf (die focus: art recedes, shelf stays sharp - as before);
   scrimB sits above the shelf (enchant picker: everything beneath
   recedes in one pass). Stated delta: epick's art reads ~.42 rather
   than .62 behind the modal. */
#stScrimA,#stScrimB{position:absolute;inset:0;pointer-events:none;opacity:0;
  transition:opacity .35s ease}
#gbShop.st-focus #stScrimA{opacity:1;
  -webkit-backdrop-filter:blur(5px) brightness(.62) saturate(.9);
  backdrop-filter:blur(5px) brightness(.62) saturate(.9)}
#gbShop.st-epick #stScrimB{opacity:1;
  -webkit-backdrop-filter:blur(5px) brightness(.42) saturate(.9);
  backdrop-filter:blur(5px) brightness(.42) saturate(.9)}""",
    'the scrims replace the filters')

# 2) the scrim elements, in the stacking order that reproduces each state
sub("""      +'<div id="stGoods">'+(dOn?goods:_enchShopHTML())+'</div>'
    +'</div>'""",
    """      +'<div id="stScrimA"></div>'/* P842: st-focus backdrop - art recedes, shelf sharp */
      +'<div id="stGoods">'+(dOn?goods:_enchShopHTML())+'</div>'
      +'<div id="stScrimB"></div>'/* P842: st-epick backdrop - all beneath recedes */
    +'</div>'""",
    'the scrim elements')

# 3) the ghost character stops compositing after its fade
sub("""#stChar{transition:opacity .34s ease}
#gbShop.tab-ench #stChar{opacity:0}
#gbShop.tab-ench #stCharE{opacity:1}""",
    """/* P842: the faded-out character leaves the compositor - a 1080x1920
   layer at opacity 0 was still promoted (the transition holds it).
   visibility lands AFTER the fade on the way out and flips instantly
   on the way in. */
#stChar{transition:opacity .34s ease,visibility 0s linear .34s}
#stCharE{transition:opacity .34s ease,visibility 0s linear .34s;visibility:hidden}
#gbShop.tab-ench #stChar{opacity:0;visibility:hidden}
#gbShop.tab-ench #stCharE{opacity:1;visibility:visible;transition:opacity .34s ease,visibility 0s}
#gbShop:not(.tab-ench) #stChar{visibility:visible;transition:opacity .34s ease,visibility 0s}""",
    'the ghost stops compositing')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
