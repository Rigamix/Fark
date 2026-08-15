# -*- coding: utf-8 -*-
"""P726 (A1a): rest dice read their value; Preserve traps the right die.

Denis: "I preserved a 1 but then it kept a 5." Every data field said 1 -
announce, record, kept vals, _trueVal - and the RENDERED die said 5. The
minted truth-table probe (six still dice, values 1..6) showed the value
landing edge-on in a sliver while the camera face read a neighbour, and
the kept-tray crop showed a kept 1-or-5 rendering as a 6: EVERY rest-posed
die on the match table shows the wrong face, and has since the port -
settled dice read right only because physics orients value-UP inside the
tilted table root. _isoQ's no-lay contract aims the value AT the camera,
which is right for the eye-level shelf and wrong under the high table
camera. The lay variant (value UP, then tipped toward the viewer) IS the
settled look - one argument fixes Preserve's mint, the kept tray and the
pre-roll row together.

Capture side: prefer the 1 (it pays 100 over the 5's 50), and actually
record the seat - `foundLane` was read at the stash line but never
assigned anywhere, so the P691 lane-preservation feature was stillborn.
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


# 1) the rest pose lays the value face UP, like a settled die
sub(u"        var tQ=D3X._isoQ(val,D3X.TILT_MATCH);",
    u"        /* P726: LAY - value face UP then tipped toward the viewer, the\n"
    u"           same reading a settled die gives the high table camera. The\n"
    u"           no-lay contract (value AT the camera) is the eye-level shelf's;\n"
    u"           here it showed a neighbour face on every kept, preserved and\n"
    u"           pre-roll die (Denis's 'preserved a 1 but it kept a 5'). */\n"
    u"        var tQ=D3X._isoQ(val,D3X.TILT_MATCH,true);",
    'rest pose lays the value up')

# 2) the picker prefers the 1, and the seat is actually captured
sub(u"      var _pd=_keptScorers(k).filter(function(dd){return dd&&(dd.val===1||dd.val===5);})[0];",
    u"      /* P726: prefer the 1 - it pays 100 against the 5's 50, and a player\n"
    u"         who kept both means the better one (Denis preserved 'a 1'). */\n"
    u"      var _ps=_keptScorers(k).filter(function(dd){return dd&&(dd.val===1||dd.val===5);});\n"
    u"      var _pd=_ps.filter(function(dd){return dd.val===1;})[0]||_ps[0];",
    'picker prefers the 1')

sub(u"      if(_pd){found=_pd.val;foundMat=_pd.mat||k.mat||'bone';foundEnch=_pd.ench||null;return true;}",
    u"      if(_pd){found=_pd.val;foundMat=_pd.mat||k.mat||'bone';foundEnch=_pd.ench||null;\n"
    u"        foundLane=(typeof _pd.lane==='number')?_pd.lane:null;/* P726: the stash line read\n"
    u"           foundLane but nothing ever assigned it - P691's seat record was stillborn */\n"
    u"        return true;}",
    'the seat is captured')

# 3) declare foundLane with its siblings
sub(u"    var found=null,foundMat=null;\n"
    u"    var foundEnch=null;/* P559 - the brand, captured with the material */",
    u"    var found=null,foundMat=null;\n"
    u"    var foundEnch=null;/* P559 - the brand, captured with the material */\n"
    u"    var foundLane=null;/* P726 - see the capture below */",
    'foundLane declared')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
