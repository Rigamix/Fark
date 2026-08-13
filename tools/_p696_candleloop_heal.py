# -*- coding: utf-8 -*-
"""P696: the breathing loop can die at launch and nothing restarts it.

_candleLoop's tick exits the moment screen-match lacks 'active' or _mLight.on
is false - and _mLightCalc says off until matchPlate is displayed, which waits
on the table image. On a slow first load both of _matchDress's restarts (+0ms,
+900ms) hit that window and the loop is dead for the whole match: no candle
breathing, no prop-shadow breathing, and dice shadows only on discrete dirty
marks. Measured: patron match, settled dice, painter called 0 times in 2.8s.

Two revivals at the moments readiness actually arrives, both through the
loop's own idempotence guard (_candleOn):
  - D3X's dirty consumer: any shadow repaint with the loop dead retries it.
  - the P687 table-image load listener: the exact 'image finally arrived'
    moment, which also covers matches the D3X consumer never serves.
A retry that is still too early costs one dead tick and waits for the next.
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


sub(u"    if(this._shDirty){\n"
    u"      this._shDirty=false;\n"
    u"      try{_mLightCalc();_drawDiceShadows(performance.now()/1000);}catch(e){}\n"
    u"    }",
    u"    if(this._shDirty){\n"
    u"      this._shDirty=false;\n"
    u"      try{_mLightCalc();_drawDiceShadows(performance.now()/1000);}catch(e){}\n"
    u"      /* P696: a dirty mark with the breathing loop dead revives it - the\n"
    u"         loop dies whenever it ticks before the plate is ready (slow first\n"
    u"         image load) and nothing else restarts it. _candleOn makes this a\n"
    u"         boolean test per repaint, not a second loop. */\n"
    u"      if(!window._candleOn)try{_candleLoop();}catch(e){}\n"
    u"    }",
    'P696 dirty-consumer revival')

sub(u"    if(!_tblImg.complete)_tblImg.addEventListener('load',function(){_dsDirty();},{once:true});",
    u"    if(!_tblImg.complete)_tblImg.addEventListener('load',function(){_dsDirty();try{_candleLoop();}catch(e){}},{once:true});/* P696 */",
    'P696 image-load revival')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
