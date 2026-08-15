# -*- coding: utf-8 -*-
"""P727 (A2): the armed state reads around a thumb; uses live on the card.

Third report of 'no glow, no grey-out'. The machinery was PROVEN working
this pass - a driven touch drag armed the class, computed the gold filter
and photographed a visible halo, and the released cast baked .spent with
the bob off. What the probe cannot photograph is Denis's thumb: at phone
scale the armed halo is a ~7px rim around a card the finger is covering,
so the working glow is physically hidden. And a tier-2/3 active that
keeps a charge after a cast correctly stays bright, which reads as 'it
did not grey out' when the remaining uses only show inside the focus
sheet.

Two fixes: ARMED now pops the card (standalone scale, composing with the
drag's inline translate) under a doubled halo and stronger brightness -
signals that survive a finger. And an active card wears its remaining
uses as pips ON the face, baked by the same famRenderRow pass that bakes
spent, so a 2-charge card visibly drops a pip the moment one is cast.
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


# 1) ARMED reads around a thumb: doubled halo, stronger body, scale pop
sub(u"#famRowP .fcv.armed,#screen-match #famRowO .fcv.armed{\n"
    u"  /* P713: Denis could not see the old single soft shadow under a card in\n"
    u"     hand - a tight hot core plus a wide halo reads as ARMED at a glance */\n"
    u"  filter:drop-shadow(0 0 0.45cqw rgba(255,236,170,.95))\n"
    u"  drop-shadow(0 0 1.8cqw rgba(255,205,95,.85))\n"
    u"  drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))\n"
    u"  brightness(1.12)}/* P576: third of the three */",
    u"#famRowP .fcv.armed,#screen-match #famRowO .fcv.armed{\n"
    u"  /* P713: Denis could not see the old single soft shadow under a card in\n"
    u"     hand - a tight hot core plus a wide halo reads as ARMED at a glance.\n"
    u"     P727: at phone scale that halo is a thin rim UNDER THE PLAYER'S\n"
    u"     THUMB (the drag probe photographed it working; a finger covers it),\n"
    u"     so armed also POPS - standalone scale composes with the drag's\n"
    u"     inline translate - and the halo doubles. */\n"
    u"  scale:1.09;\n"
    u"  filter:drop-shadow(0 0 0.8cqw rgba(255,236,170,1))\n"
    u"  drop-shadow(0 0 3.4cqw rgba(255,200,85,.95))\n"
    u"  drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))\n"
    u"  brightness(1.22)}/* P576: third of the three */",
    'armed pops and doubles the halo')

# 2) the uses pips, worn on the card face
sub(u"#famRowP .fcv.spent .fcvIn{animation:none}\n"
    u"#famRowP .fcv.spent{scale:1 !important}",
    u"#famRowP .fcv.spent .fcvIn{animation:none}\n"
    u"#famRowP .fcv.spent{scale:1 !important}\n"
    u"/* P727: AN ACTIVE WEARS ITS REMAINING USES. The count lived only in the\n"
    u"   focus sheet, so a tier-2/3 card that kept a charge after a cast read\n"
    u"   as 'it did not grey out'. Pips on the face, baked with spent. */\n"
    u".fcvUses{position:absolute;bottom:3%;left:50%;translate:-50% 0;display:flex;gap:0.7cqw;\n"
    u"  pointer-events:none}\n"
    u".fcvUses i{width:1.7cqw;height:1.7cqw;border-radius:50%;background:#ffd98a;\n"
    u"  outline:0.35cqw solid rgba(30,18,8,.85)}",
    'uses pips CSS')

sub(u"    var spent=d.kind==='active'&&inst.charges<=0;\n"
    u"    var cls=(spent?' spent':'')+(inst.state.armed?' armed':'');\n"
    u"    hp+=famCardArt(inst.id,inst.tier,{cls:cls.trim(),onclick:'famCardTap('+i+')'});",
    u"    var spent=d.kind==='active'&&inst.charges<=0;\n"
    u"    var cls=(spent?' spent':'')+(inst.state.armed?' armed':'');\n"
    u"    hp+=famCardArt(inst.id,inst.tier,{cls:cls.trim(),onclick:'famCardTap('+i+')',\n"
    u"      uses:(d.kind==='active'&&inst.charges>0)?inst.charges:undefined});/* P727 */",
    'row bakes the uses')

# (edit 4, the famCardArt pips renderer, was applied separately - the
#  fcvBadge anchor in the live file uses </span>, not the <\span> Grep shows)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
