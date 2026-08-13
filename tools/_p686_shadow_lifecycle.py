# -*- coding: utf-8 -*-
"""P686: the dice-shadow lifecycle - one dirty flag, every state change.

Denis: "dice shadows on all matches... they need to work well: animate with
the roll and settle, disappear when a die is kept, disappear when a die
shatters or gets stolen. Follow a die when moved around. ... do an audit and
create a simple sturdy system that uses the same efficient mechanics as the
rest of the game."

THE AUDIT FIRST. The painter is already the right system: every repaint
projects each live die's real cube through the live camera, so shadows follow
dice wherever they are BY CONSTRUCTION, fade on _settleK through the roll, and
the whole canvas clears when the light is off (P665). What was broken is
WHEN repaints happen. _shDirty was set by exactly four writers: landing,
mid-fade, a die leaving the surface (_drop), and the focus return. So:

  - roll/settle: animated correctly (the fade writers cover it)
  - shattered/stolen dice: covered a frame later (_drop fires on removal)
  - KEPT dice: never - commit sets committed=true and moves nothing, so no
    writer fires AND the painter's only skip was the kept-ROW test, which the
    kept-dice-stay-on-the-throw-line design made unreachable. A kept die kept
    its shadow indefinitely: the largest hole, and the one Denis named first.

THE SYSTEM, on the game's own mechanics: one canonical _dsDirty() (the same
mark-dirty idiom the shadow tick already uses), called from the die
lifecycle's canonical sites - the four commit writers, _removeDieAt (the one
exit path every removal already goes through, per the earlier one-exit-path
work), and D3X.shatter's burst start. And ONE new skip in the painter: a die
whose pool record is committed casts nothing - the state test the kept-row
test was standing in for.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    global s, n
    c = s.count(old)
    if c != count:
        sys.exit('ANCHOR x%d (need %d) for %s:\n  %r' % (c, count, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s (x%d)' % (label, count))


# ── the canonical dirty mark ────────────────────────────────────────────
sub(u"function _drawDiceShadows(tSec){",
    u"/* P686: THE one way to say 'a die's state changed, repaint the shadows'.\n"
    u"   Same mark-dirty idiom the shadow tick already runs on; calling it twice\n"
    u"   costs one boolean write. */\n"
    u"function _dsDirty(){try{if(window.D3X)D3X._shDirty=true;}catch(e){}}\n"
    u"function _drawDiceShadows(tSec){",
    'P686 the canonical mark')

# ── the painter learns the committed state ──────────────────────────────
sub(u"        /* Denis: keep the tray simple - the kept dice are out of the light,\n"
    u"           so a cast shadow under them reads as a second light source */\n"
    u"        if(D3X._rowKey(dd)==='keptRow')return;",
    u"        /* Denis: keep the tray simple - the kept dice are out of the light,\n"
    u"           so a cast shadow under them reads as a second light source */\n"
    u"        if(D3X._rowKey(dd)==='keptRow')return;\n"
    u"        /* P686: the STATE test the row test was standing in for - kept dice\n"
    u"           stay on the throw line now, so the row never changes and a kept\n"
    u"           die kept its shadow forever. A committed die casts nothing. */\n"
    u"        try{\n"
    u"          if(G&&G.pool&&G.pool.some(function(p){\n"
    u"            return p.committed&&p.el&&(p.el===dd.chip||p.el.contains(dd.chip));\n"
    u"          }))return;\n"
    u"        }catch(eC){}",
    'P686 committed dice cast nothing')

# ── the lifecycle sites mark dirty ──────────────────────────────────────
sub(u"    selDice.forEach(d=>{d.committed=true;d._frozen=false;d.el.classList.remove('selected','die-frozen');",
    u"    selDice.forEach(d=>{d.committed=true;d._frozen=false;d.el.classList.remove('selected','die-frozen');\n"
    u"      _dsDirty();/* P686: its shadow goes with the keep */",
    'P686 dirty at commit (hold path)')

sub(u"    const d=free[0];d.committed=true;",
    u"    const d=free[0];d.committed=true;_dsDirty();/* P686 */",
    'P686 dirty at commit (auto path)')

sub(u"        selD.forEach(function(d){d.committed=true;d.sel=false;",
    u"        selD.forEach(function(d){d.committed=true;d.sel=false;_dsDirty();/* P686 */",
    'P686 dirty at commit (keep path)')

sub(u"      selD.forEach(d=>{d.committed=true;d._frozen=false;if(d.el){d.el.classList.remove('selected','die-f",
    u"      selD.forEach(d=>{_dsDirty();d.committed=true;d._frozen=false;if(d.el){d.el.classList.remove('selected','die-f",
    'P686 dirty at commit (main keep)')

sub(u"  if(!G||typeof lane!=='number'||!isFinite(lane)||lane<0)return false;",
    u"  if(!G||typeof lane!=='number'||!isFinite(lane)||lane<0)return false;\n"
    u"  /* P686: every removal - shatter, steal, sacrifice, vanish, trade-out -\n"
    u"     already funnels through here (the one-exit-path rule), so this ONE mark\n"
    u"     covers them all. A mark on a removal that later rejects costs nothing:\n"
    u"     the repaint just redraws the same shadows. */\n"
    u"  _dsDirty();",
    'P686 dirty at the one removal path')

sub(u"    d.burst={t0:performance.now(),",
    u"    _dsDirty();/* P686: the shadow tracks the burst instead of outliving it */\n"
    u"    d.burst={t0:performance.now(),",
    'P686 dirty at shatter')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
