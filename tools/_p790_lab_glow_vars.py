# -*- coding: utf-8 -*-
"""P790: the lab's CARD HALO panel drives the prototype's vars.

P789 made the card glow Denis's own CSS prototype - every look dial a
var on #cardGlowLayer. The lab row follows: core width (--halo), bloom
width (--bloom), master (--intensity), plus the arm ramp's floor (the
one JS number left). The full board - colours, sharpness, motion - is
his own tools/card_glow_test.html; approved numbers get baked into the
game CSS, the established lab workflow.
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


sub("""    /* P786/P787: the card RUNS THE DICE RECIPE (P784, Denis: "same
       effect as on the dice") - reach/core/line/strength are the GLOW
       sliders ABOVE, shared by design. The card's own dials: fit (trim
       - the hull sits on the ART's edge, inside the webp's transparent
       margin), core blur (the breathed line), floor (drag ramp start). */
    +'<br><label>fit <input type="range" id="cgTrim" min="90" max="100" value="96.7" step="0.1" oninput="cardDial(&quot;trim&quot;,this.value/100)"></label>'
    +'<label>core blur <input type="range" id="cgLB" min="0" max="6" value="2" step="0.5" oninput="cardDial(&quot;lineBlur&quot;,+this.value)"></label>'
    +'<label>floor <input type="range" id="cgFloor" min="0" max="100" value="42" oninput="cardDial(&quot;floor&quot;,this.value/100)"></label>'
    +'<span style="font-size:10px;color:#9a8a68">body = the dice dials above</span>'""",
    """    /* P790: the card glow is Denis's CSS prototype (P789) - these
       sliders write the #cardGlowLayer vars. The full board (colours,
       sharpness, motion) is tools/card_glow_test.html; approved
       numbers get baked into the game CSS. */
    +'<br><label>core <input type="range" id="cgHalo" min="0" max="26" value="5" step="0.5" oninput="cardDial(&quot;halo&quot;,+this.value)"></label>'
    +'<label>bloom <input type="range" id="cgBloom" min="0" max="70" value="17" step="1" oninput="cardDial(&quot;bloom&quot;,+this.value)"></label>'
    +'<label>master <input type="range" id="cgInt" min="0" max="200" value="100" oninput="cardDial(&quot;intensity&quot;,this.value/100)"></label>'
    +'<label>floor <input type="range" id="cgFloor" min="0" max="100" value="42" oninput="cardDial(&quot;floor&quot;,this.value/100)"></label>'
    +'<span style="font-size:10px;color:#9a8a68">full board: tools/card_glow_test.html</span>'""",
    'the sliders drive the vars')

sub("""function cardDial(field,v){
  E('D3X.CARD_GLOW.'+field+'='+v);
  E('D3X._drawCardGlows&&D3X._drawCardGlows()');
  saveLook();
}""",
    """function cardDial(field,v){
  /* P790: look dials are vars on #cardGlowLayer (Denis's prototype);
     only the arm ramp's floor stays a JS number. */
  if(field==='floor')E('D3X.CARD_GLOW.floor='+v);
  else E("(function(){var l=window.D3X&&D3X._cardGlowLayer&&D3X._cardGlowLayer();if(l)l.style.setProperty('--"+field+"','"+v+"');})()");
  E('D3X._drawCardGlows&&D3X._drawCardGlows()');
  saveLook();
}""",
    'cardDial writes the vars')

sub("""  [['round',0.075],['floor',0.42],['trim',0.967],['lineBlur',2]]
    .forEach(function(p){E('D3X.CARD_GLOW.'+p[0]+'='+p[1]);});/* P787: the P784-786 card dials */""",
    """  E('D3X.CARD_GLOW.floor=0.42');/* P790: the CSS defaults are authored
     in the game stylesheet - clearing inline vars restores them */
  E("(function(){var l=window.D3X&&D3X._cardGlowLayer&&D3X._cardGlowLayer();if(!l)return;['halo','bloom','intensity'].forEach(function(k){l.style.removeProperty('--'+k);});})()");""",
    'reset clears to the stylesheet')

sub("""  set('cgTrim',96.7);set('cgLB',2);set('cgFloor',42);""",
    """  set('cgHalo',5);set('cgBloom',17);set('cgInt',100);set('cgFloor',42);""",
    'reset moves the sliders')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
