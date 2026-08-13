# -*- coding: utf-8 -*-
"""P697d: three fits from the first framed look at the win-screen focus.

- The chrome-hide (win-board/skip/end-btns/resDlg/title) goes INSTANT: with
  a transition attached, the plaque numbers painted through the zoomed card
  until the fade's first frame - and the board sits at z3, above the card's
  stacking context, so any lag shows. Nothing needs to see these fade.
- The family line takes _loCardFocus's own 2cqh inline size (I dropped it in
  the copy) and may wrap: TAVERN . ACTIVE . BURNS ON USE overflowed the
  3cqh nowrap band.
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


sub(u"#end-ov.fo-focus>.fo-skip,#end-ov.fo-focus #end-btns,#end-ov.fo-focus .win-board,\n"
    u"#end-ov.fo-focus #resDlg,#end-ov.fo-focus .fo-title{opacity:0 !important;pointer-events:none !important;transition:opacity .3s}",
    u"/* instant, no fade: the board is z3 - ABOVE the card's stacking context -\n"
    u"   so even one lagged frame paints its numbers through the zoomed card */\n"
    u"#end-ov.fo-focus>.fo-skip,#end-ov.fo-focus #end-btns,#end-ov.fo-focus .win-board,\n"
    u"#end-ov.fo-focus #resDlg,#end-ov.fo-focus .fo-title{opacity:0 !important;pointer-events:none !important}",
    'P697d instant chrome hide')

sub(u"#end-ov>#foFocusPanel{position:absolute;z-index:55}",
    u"#end-ov>#foFocusPanel{position:absolute;z-index:55}\n"
    u"#foFocusPanel .ffaces{white-space:normal}",
    'P697d ffaces may wrap')

sub(u"    +'<div class=\"ffaces\"><span style=\"color:'+col+'\">'+FAMILIES[d.fam].name+'</span>'",
    u"    +'<div class=\"ffaces\" style=\"font-size:2cqh\"><span style=\"color:'+col+'\">'+FAMILIES[d.fam].name+'</span>'",
    'P697d ffaces at 2cqh (the _loCardFocus size)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
