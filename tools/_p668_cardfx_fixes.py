# -*- coding: utf-8 -*-
"""P668: the two reasons P666's feedback did not reach the screen.

P666 shipped the vocabulary and wired Tamper to it. A probe played Tamper for
real in a boss match and read the rival's card off the live row afterwards:

    classes      "fcv oppcard broken"      <- the class is there
    greyApplied  false                     <- the grey is NOT
    hasShake     false                     <- and it never shook
    running      []

Both failures are mine, and both are the kind that a "does the function exist"
check would have called a pass.

── 1. THE RE-RENDER EATS THE BEAT ──
famUse is `if(fx.use(inst)){inst.charges--;famRenderRow();}` - it rebuilds the
row AFTER the effect returns. So a class applied inside use() goes onto an
element that is discarded one line later, and nothing moves. P666 already moved
Tamper's call after ITS OWN famRenderRow; famUse's second one was still to come.

Fixing it per-card would mean every future effect having to know this, which is
the "useless code per effect" Denis asked not to have. So cardFx defers itself
by one frame and re-resolves the target then - after every synchronous re-render
in the call stack has settled. That is why cardFx takes a target DESCRIPTOR
({oppCard:'x'}) rather than an element: a descriptor can be resolved again, an
element cannot be un-discarded.

── 2. THE GREY LOST ON SPECIFICITY ──
    .fcv.broken                     0,2,0   what P666 wrote
    #screen-match #famRowO .fcv     2,1,0   what was already there
The row rule wins, and `filter` REPLACES rather than adds - so the winner's
brightness/saturate/drop-shadow chain was the whole computed value and the
grayscale was simply not in it. The measured filter had no `grayscale` token at
all, which is what the probe reported.

The broken rule now matches the row's specificity, and repeats the two
drop-shadows because replacing means a rule that omits them deletes the card's
shadow. The generic .fcv.broken stays for the player's row, which has no
id-qualified filter to lose to.
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── 1. defer one frame, resolve the target then ─────────────────────────
sub(u"function cardFx(kind,target,opts){\n"
    u"  opts=opts||{};\n"
    u"  var el=_fxEl(target);\n"
    u"  if(!el)return;",
    u"/* P668: ONE FRAME LATER, ALWAYS. famUse is\n"
    u"     if(fx.use(inst)){inst.charges--;famRenderRow();}\n"
    u"   - it rebuilds the row AFTER the effect returns, so a class an effect puts\n"
    u"   on a card is thrown away with the element a line later and nothing moves.\n"
    u"   Measured: Tamper's target came back `fcv oppcard broken` with no fx-shake\n"
    u"   and no running animation.\n"
    u"   Deferring here rather than in each effect is the whole point - otherwise\n"
    u"   every card written from now on has to know about famUse's re-render. It\n"
    u"   is also why the target is a DESCRIPTOR and not an element: a descriptor\n"
    u"   can be resolved again after the rebuild, an element cannot. */\n"
    u"function cardFx(kind,target,opts){\n"
    u"  var f=function(){_cardFxNow(kind,target,opts||{});};\n"
    u"  if(window.requestAnimationFrame)requestAnimationFrame(f);else setTimeout(f,16);\n"
    u"}\n"
    u"function _cardFxNow(kind,target,opts){\n"
    u"  opts=opts||{};\n"
    u"  var el=_fxEl(target);\n"
    u"  if(!el)return;",
    'P668 defer a frame')

# ── 2. the grey has to outrank the row ──────────────────────────────────
sub(u".fcv.broken{filter:grayscale(.92) brightness(.5)}",
    u".fcv.broken{filter:grayscale(.92) brightness(.5)}\n"
    u"/* P668: AND IT HAS TO OUTRANK THE ROW. `.fcv.broken` is 0,2,0 and\n"
    u"   `#screen-match #famRowO .fcv` is 2,1,0, so the row won and - because\n"
    u"   `filter` REPLACES rather than adds - its brightness/saturate/drop-shadow\n"
    u"   chain was the entire computed value with no grayscale in it. Measured: the\n"
    u"   broken card carried the class and rendered at full colour.\n"
    u"   The two drop-shadows are repeated for the same reason: a rule that omits\n"
    u"   them does not inherit them, it deletes them. */\n"
    u"#screen-match #famRowO .fcv.broken{\n"
    u"  filter:grayscale(.95) brightness(.45) saturate(.2)\n"
    u"         drop-shadow(0 0.2cqw 0.3cqw rgba(10,6,2,.55))\n"
    u"         drop-shadow(0 0.9cqw 1.4cqw rgba(10,6,2,.5))}",
    'P668 the grey outranks the row')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
