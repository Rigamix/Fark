# -*- coding: utf-8 -*-
"""P671: the card focus sheet stops being a greybox.

Denis (win screen): "also the focus panel on cards does not follow the style on
win screen, it's still the old greybox stuff..."

WHAT THE MAP FOUND, which reframes the fix: there is no win-screen sheet.
famCardSheet is defined once and every card focus - match tap, win-screen draft
offer, deck row, patron peek's "their cards" - opens the SAME #gbSheet, a
grey bottom sheet (background #d6d6d6, ink #1c1c1c) that also serves the shop's
die inspect, the seat peeks and the innkeep's book. So "fix the win screen" is
really "the card sheet gets its own look wherever it opens", and the other
consumers must keep theirs - a blanket restyle would repaint the shop and the
book unreviewed.

MECHANISM: _gbSheetOpen grows an optional variant class, written fresh on every
open (each open resets className, so a variant can never leak from one caller
to the next - and close does NOT clear it, deliberately, so the sheet keeps its
face while it slides out). famCardSheet and npcOppTap pass 'fam-sheet'; nobody
else passes anything and nobody else changes.

THE LOOK: parchment under the ink the sheet's content already uses - the card
name is #2a1808 and the rules text #3a2812, colours famCardSheet was already
setting against grey. Ink darker than the gold trim, per the standing rule.
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


# ── the variant plumbing ────────────────────────────────────────────────
sub(u"function _gbSheetOpen(html){\n"
    u"  _gbSheetInfra();\n"
    u"  var sh=document.getElementById('gbSheet');\n"
    u"  sh.innerHTML=",
    u"/* P671: `cls` is a per-open variant class. Written fresh on EVERY open, so a\n"
    u"   variant can never leak from one caller to the next; close leaves it alone\n"
    u"   on purpose - the sheet keeps its face while it slides out. */\n"
    u"function _gbSheetOpen(html,cls){\n"
    u"  _gbSheetInfra();\n"
    u"  var sh=document.getElementById('gbSheet');\n"
    u"  sh.className=cls||'';\n"
    u"  sh.innerHTML=",
    'P671 the variant param')

sub(u"    +(opts.btn?'<div class=\"gbx-btn primary\" style=\"margin-top:10px\" onclick=\"_gbSheetClose();('+opts.cb+')()\">'+opts.btn+'</div>':'')\n"
    u"    +'</div>';\n"
    u"  _gbSheetOpen(h);\n"
    u"}",
    u"    +(opts.btn?'<div class=\"gbx-btn primary\" style=\"margin-top:10px\" onclick=\"_gbSheetClose();('+opts.cb+')()\">'+opts.btn+'</div>':'')\n"
    u"    +'</div>';\n"
    u"  _gbSheetOpen(h,'fam-sheet');/* P671: the card sheet wears parchment */\n"
    u"}",
    'P671 famCardSheet wears it')

sub(u"    +'<div style=\"font-size:14px;line-height:1.5;color:#3a2812;margin:10px auto 4px;max-width:88%\">'+_accG(c.desc||_sentenceCase(c.eff||''))+'</div>'\n"
    u"    +'</div>';\n"
    u"  _gbSheetOpen(h);\n"
    u"}",
    u"    +'<div style=\"font-size:14px;line-height:1.5;color:#3a2812;margin:10px auto 4px;max-width:88%\">'+_accG(c.desc||_sentenceCase(c.eff||''))+'</div>'\n"
    u"    +'</div>';\n"
    u"  _gbSheetOpen(h,'fam-sheet');/* P671: same parchment as famCardSheet */\n"
    u"}",
    'P671 npcOppTap wears it')

# ── the look ────────────────────────────────────────────────────────────
sub(u"#gbSheet h2{font-size:12px;margin:10px 0 4px;opacity:.75;color:#1c1c1c}",
    u"#gbSheet h2{font-size:12px;margin:10px 0 4px;opacity:.75;color:#1c1c1c}\n"
    u"/* P671: THE CARD SHEET'S OWN FACE. Every card focus - match tap, win-screen\n"
    u"   draft, deck row, peek - goes through famCardSheet/npcOppTap into this one\n"
    u"   element, which is why the win screen showed \"the old greybox stuff\": the\n"
    u"   sheet IS the greybox, shared with the shop and the innkeep's book. The\n"
    u"   variant class scopes the parchment to the card callers so those other\n"
    u"   surfaces keep the look they were built against. Ink (#2a1808/#3a2812,\n"
    u"   already set by the content) darker than the gold trim, per the rule. */\n"
    u"#gbSheet.fam-sheet{background:#e7d6ac;color:#2a1808;\n"
    u"  border-top:2px solid #a58a3c;\n"
    u"  box-shadow:0 -4px 18px rgba(20,12,4,.45)}\n"
    u"#gbSheet.fam-sheet h2{color:#2a1808}\n"
    u"#gbSheet.fam-sheet .num,#gbSheet.fam-sheet .kw{color:#8a4a18}\n"
    u"/* the drag pill is written inline as grey; on parchment it goes tea-brown */\n"
    u"#gbSheet.fam-sheet>div:first-child{background:rgba(90,60,20,.35)!important}",
    'P671 the parchment')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
