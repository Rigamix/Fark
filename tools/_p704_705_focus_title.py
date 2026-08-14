# -*- coding: utf-8 -*-
"""P704 + P705: the win-focus panel un-doubles; boot lands on the title.

P704 (Denis, screenshot): the flown card's own CAPTION (famCardHtml's name
line under the art) rides up with the zoom and lands on the panel's family
line - the doubled ENCORE. It hides while zoomed. And the fname band sat
low enough for the big offer card to overlap it: the name rises (-46cqh)
and the card flies smaller (K 1.9) to a lower landing (0.34 of screen), so
name / card / panel stack clear of each other on both aspects.

P705 (Denis: "instead of bringing me in the match right away, bring me back
to the title screen but make it that the continue button brings me to the
match if I'm in one"): P695's boot-resume reverts to the plain menu, and
_hsContinueTap resumes a pending match before it ever considers the floor.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── P704.1: the caption hides while its card is the zoomed subject ──
sub(u"#end-ov .fo-card,#end-ov .fo-slot{transition:transform .18s ease,opacity .3s ease}",
    u"#end-ov .fo-card,#end-ov .fo-slot{transition:transform .18s ease,opacity .3s ease}\n"
    u"/* P704: the flown card's own caption (famCardHtml's name line) rode the\n"
    u"   zoom up into the panel - the doubled name in Denis's screenshot. The\n"
    u"   panel's fname IS the name now; the caption yields while zoomed. */\n"
    u"#end-ov .fo-card .fcv+div{transition:opacity .25s}\n"
    u"#end-ov .fo-card.zoom .fcv+div{opacity:0}\n"
    u"/* and the name band rises clear of the big card */\n"
    u"#end-ov #foFocusPanel .fname{top:-46cqh}",
    'P704 caption yields + fname rises')

# ── P704.2: smaller flight, lower landing ──
sub(u"  /* K and the landing height are _loCardFocus's numbers - one look */\n"
    u"  var K=2.05,wr=(Math.random()<0.5?-1:1)*(0.6+Math.random()*1.0);\n"
    u"  var ncx=nr.left+nr.width/2,ncy=nr.top+nr.height/2;\n"
    u"  var dx=(gr.left+gr.width/2)-ncx,dy=(gr.top+gr.height*0.365)-ncy;",
    u"  /* P704: NOT _loCardFocus's numbers after all - the offer card is twice\n"
    u"     the shelf card's size, so 2.05 @ .365 overlapped the name above and\n"
    u"     the panel below on a real phone. 1.9 @ .34 stacks name / card /\n"
    u"     panel clear on both aspects. */\n"
    u"  var K=1.9,wr=(Math.random()<0.5?-1:1)*(0.6+Math.random()*1.0);\n"
    u"  var ncx=nr.left+nr.width/2,ncy=nr.top+nr.height/2;\n"
    u"  var dx=(gr.left+gr.width/2)-ncx,dy=(gr.top+gr.height*0.34)-ncy;",
    'P704 K 1.9 @ 0.34')

# ── P705.1: boot lands on the title again ──
sub(u"  _getS();\n"
    u"  /* P695: a waiting match outranks the menu - open the app, be at the\n"
    u"     table (Denis: \"so I don't have to click anything\"). One resume path:\n"
    u"     the same resumeMatch Settings and the room banner use. */\n"
    u"  var _booted=false;\n"
    u"  if(S&&S.pendingMatch){\n"
    u"    try{resumeMatch();_booted=true;}catch(e){console.error('boot resume failed:',e);}\n"
    u"  }\n"
    u"  if(!_booted){try{showScreen('menu');}catch(e){console.error('showScreen failed:',e);}}",
    u"  _getS();\n"
    u"  /* P705: Denis reversed P695 after playing it - boot lands on the TITLE,\n"
    u"     and CONTINUE carries you into a waiting match (_hsContinueTap). Boot\n"
    u"     itself never jumps into play. */\n"
    u"  try{showScreen('menu');}catch(e){console.error('showScreen failed:',e);}",
    'P705 boot to title')

# ── P705.2: CONTINUE resumes a waiting match ──
sub(u"function _hsContinueTap(){\n"
    u"  var stg=document.getElementById('hsStage');\n"
    u"  if(stg&&stg.classList.contains('confirming'))return;/* it's on its way out */\n"
    u"  SFX.nav();showScreen('gauntlet');\n"
    u"}",
    u"function _hsContinueTap(){\n"
    u"  var stg=document.getElementById('hsStage');\n"
    u"  if(stg&&stg.classList.contains('confirming'))return;/* it's on its way out */\n"
    u"  /* P705: CONTINUE means \"back to where I was\" - a waiting match\n"
    u"     outranks the tavern floor. */\n"
    u"  if(S&&S.pendingMatch){SFX.nav();resumeMatch();return;}\n"
    u"  SFX.nav();showScreen('gauntlet');\n"
    u"}",
    'P705 CONTINUE resumes')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
