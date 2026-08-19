# -*- coding: utf-8 -*-
"""P787: the lab's CARD HALO panel catches up with P784-786.

Denis: "is the card glow in the lab?" It is - GLOW STUDIO > CARD HALO,
with cardGlowDemo() to light a card in hand. But after P784 the card
BODY runs the dice's GLOW dials (that is the design: one recipe), so
four of the five card sliders (soft/rim/dyF/strength) wrote fields
nothing reads any more - the lab tuning a branch the game never runs,
the exact P751 lie - and the card's two real dials (trim, lineBlur)
were missing. The reset button also re-applied the retired field set.

Now: the CARD HALO row is fit (trim - the hull sits on the art's
edge), core blur (lineBlur - the breathed line), and floor (the drag
ramp's start). Body shape/strength is tuned with the DICE sliders
above, shared by design - the panel says so. lightsReset writes the
current authored card values.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_lab.html')
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


# ── 1. the sliders: the card's OWN dials only ──
sub("""    /* P753: the dials the STAMP actually reads - corner/rim-line fed the
       retired hull fallback and floor is invisible at the demo's k=1 */
    +'<br><label>reach <input type="range" id="cgSoft" min="2" max="30" value="6" oninput="cardDial(&quot;soft&quot;,+this.value)"></label>'
    +'<label>core <input type="range" id="cgRim" min="1" max="10" value="2.5" step="0.5" oninput="cardDial(&quot;rim&quot;,+this.value)"></label>'
    +'<label>drop <input type="range" id="cgDy" min="0" max="25" value="0" oninput="cardDial(&quot;dyF&quot;,this.value/100)"></label>'
    +'<label>strength <input type="range" id="cgStr" min="10" max="100" value="91" oninput="cardDial(&quot;strength&quot;,this.value/100)"></label>'
    +'<label>floor <input type="range" id="cgFloor" min="0" max="100" value="42" oninput="cardDial(&quot;floor&quot;,this.value/100)"></label>'""",
    """    /* P786/P787: the card RUNS THE DICE RECIPE (P784, Denis: "same
       effect as on the dice") - reach/core/line/strength are the GLOW
       sliders ABOVE, shared by design. The card's own dials: fit (trim
       - the hull sits on the ART's edge, inside the webp's transparent
       margin), core blur (the breathed line), floor (drag ramp start). */
    +'<br><label>fit <input type="range" id="cgTrim" min="90" max="100" value="96.7" step="0.1" oninput="cardDial(&quot;trim&quot;,this.value/100)"></label>'
    +'<label>core blur <input type="range" id="cgLB" min="0" max="6" value="2" step="0.5" oninput="cardDial(&quot;lineBlur&quot;,+this.value)"></label>'
    +'<label>floor <input type="range" id="cgFloor" min="0" max="100" value="42" oninput="cardDial(&quot;floor&quot;,this.value/100)"></label>'
    +'<span style="font-size:10px;color:#9a8a68">body = the dice dials above</span>'""",
    'the card sliders are its real dials')

# ── 2. reset writes the authored current values ──
sub("""  [['soft',6],['rim',2.5],['strength',0.91],['floor',0.42],['dyF',0],
   ['grow',1.05],['round',0.075],['line',0]]
    .forEach(function(p){E('D3X.CARD_GLOW.'+p[0]+'='+p[1]);});""",
    """  [['round',0.075],['floor',0.42],['trim',0.967],['lineBlur',2]]
    .forEach(function(p){E('D3X.CARD_GLOW.'+p[0]+'='+p[1]);});/* P787: the P784-786 card dials */""",
    'reset writes the living fields')

sub("""  set('cgSoft',6);set('cgRim',2.5);set('cgStr',91);set('cgFloor',42);set('cgDy',0);""",
    """  set('cgTrim',96.7);set('cgLB',2);set('cgFloor',42);""",
    'reset moves the living sliders')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
