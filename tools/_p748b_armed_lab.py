# -*- coding: utf-8 -*-
"""P748b: the armed telegraph joins the one painter; the lab gets its dials.

Two loose ends from P748.

1. `.fcv.armed` still carried gold drop-shadows - the SAME clipped filter
   the drag glow just stopped using, in the same 3D-transformed row. On a
   phone they paint nothing; on desktop they would now double up with the
   canvas halo, which is a platform difference dressed up as a look. The
   armed state keeps its lift (scale is not a filter and works fine) and
   its brightness, and hands the halo to D3X.cardGlow like everything
   else. The player's armed card is registered from the drag, the
   rival's from famRenderRow - both through the one painter.

2. THE LAB FOLLOWS THE GAME (Denis's standing ask). The glow studio drove
   D3X.GLOW only, so the card halo would have been the one effect in the
   game he could not tune. It gets the same treatment: its own dials on
   D3X.CARD_GLOW, plus a button that lights a card in hand so the look
   can be judged without holding a drag open with one hand.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def patch(path, pairs):
    s = io.open(path, encoding='utf-8', newline='').read()
    for old, new, label in pairs:
        c = s.count(old)
        if c != 1:
            o2 = old.replace('\n', '\r\n')
            if s.count(o2) == 1:
                old, new = o2, new.replace('\n', '\r\n')
            else:
                sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
        s = s.replace(old, new)
        edits.append(label)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)


patch(os.path.join(ROOT, 'fark_proto.html'), [
    (u"""  scale:1.09;
  filter:drop-shadow(0 0 0.8cqw rgba(255,236,170,1))
  drop-shadow(0 0 3.4cqw rgba(255,200,85,.95))
  drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))
  brightness(1.22)}/* P576: third of the three */""",
     u"""  /* P748b: THE HALO LEFT THIS RULE. These gold drop-shadows are in the
     same 3D-transformed row as the drag's were, so WebKit clips them to
     the card's own box and a phone sees nothing - and on desktop they
     would now stack on top of the canvas halo, so the two platforms
     would disagree about what armed looks like. D3X.cardGlow paints it
     for both. The lift and the warmth stay: neither is a filter that
     needs to reach outside the card. */
  scale:1.09;
  filter:drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))
  brightness(1.22)}/* P576: third of the three */""",
     'armed halo -> painter'),
])

LAB = os.path.join(ROOT, 'fark_lab.html')
patch(LAB, [
    (u"""    +'<label>lean <input type="range" id="gDy" min="-24" max="24" value="0" oninput="glowDial(&quot;dy&quot;,+this.value)"></label>'
    +'</div>';""",
     u"""    +'<label>lean <input type="range" id="gDy" min="-24" max="24" value="0" oninput="glowDial(&quot;dy&quot;,+this.value)"></label>'
    /* P748b: THE CARD HALO IS THE SAME GLOW, so it is tuned in the same
       place. It runs through D3X._paintHalo exactly as the dice do - what
       differs is only the shape it is given and these dials. */
    +'<br><b style="color:#c8a45c;font-size:11px;margin-right:6px">CARD HALO</b>'
    +'<span style="font-size:10px;color:#9a8a68">(D3X.CARD_GLOW - the drag + armed glow)</span> '
    +'<button onclick="cardGlowDemo()">light a card in hand</button>'
    +'<br><label>floor <input type="range" id="cgFloor" min="0" max="100" value="42" oninput="cardDial(&quot;floor&quot;,this.value/100)"></label>'
    +'<label>corner <input type="range" id="cgRound" min="0" max="30" value="7.5" step="0.5" oninput="cardDial(&quot;round&quot;,this.value/100)"></label>'
    +'<label>rim line <input type="range" id="cgLine" min="0" max="6" value="0" step="0.2" oninput="cardDial(&quot;line&quot;,+this.value)"></label>'
    +'</div>';""",
     'lab card halo dials'),

    (u"""function glowSelAll(on){""",
     u"""/* P748b: the card halo's dials, and a way to SEE it without holding a
   drag open. cardGlowDemo lights the first card in hand at full strength
   and leaves it lit, so the sliders below have something to act on. */
function cardDial(field,v){
  E('D3X.CARD_GLOW.'+field+'='+v);
  E('D3X._drawCardGlows&&D3X._drawCardGlows()');
  saveLook();
}
function cardGlowDemo(){
  var on=E("(function(){var c=document.querySelector('#famRowP .fcv');"
    +"if(!c)return 'no card in hand - add one above';"
    +"if(D3X._cardGlows&&D3X._cardGlows.demo){D3X.cardGlow('demo',null,0);return 'off';}"
    +"D3X.cardGlow('demo',c,1);return 'lit';})()");
  log('card halo: '+on);
}
function glowSelAll(on){""",
     'lab card halo wiring'),
])

print('done: %d (%s)' % (len(edits), ', '.join(edits)))
