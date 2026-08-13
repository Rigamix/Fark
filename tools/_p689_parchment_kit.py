# -*- coding: utf-8 -*-
"""P689: the greybox kit goes parchment - every remaining grey surface at once.

Denis: "NOTHING remaining from last game, including old buttons and screens.
Replace with placeholders if need be."

The census's remaining greybox surfaces all draw from ONE kit (.gbx-*) plus
the #gbSheet default face: the shop's die inspect and enchant list, the patron
and boss peeks, the nights explainer, the innkeep's book, the gbx modals
(new-run confirm, abandon-run, spoils TAKE, enchant confirm), and the shelf
overlay. Restyling the KIT repaints all of them in one edit - the placeholder
Denis asked for, in the game's parchment/ink/gold language instead of wireframe
grey. The card sheet's fam-sheet variant (P671) simply becomes the default
face; its variant rules stay and now agree with the base.

Also: the For Keeps win-card injection loses its debug monospace pink, and the
shelf overlay's flat #4a4a4a ground goes dark tavern wood.
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


# ── the kit ─────────────────────────────────────────────────────────────
sub(u"/* ── flow-spec wireframe kit (fark_greybox.html) ── */\n"
    u".gbx{--panel:#c9c9c9;--panel2:#b0b0b0;--ink:#1c1c1c;--accent:#8a2d2d;--gold:#a58a3c;--ok:#3c7a45}\n"
    u".gbx-box{background:#c9c9c9;border-radius:8px;display:flex;align-items:center;justify-content:center;\n"
    u"  text-align:center;color:#1c1c1c;font-weight:600;flex-direction:column}\n"
    u".gbx-box.sub{background:#b0b0b0;font-weight:500}",
    u"/* ── P689: the wireframe kit wears parchment. One kit serves every\n"
    u"   remaining sheet, peek, modal and overlay, so this single block is the\n"
    u"   whole placeholder pass Denis asked for - ink darker than the trim\n"
    u"   throughout, per the rule. ── */\n"
    u".gbx{--panel:#ead9b4;--panel2:#dcc592;--ink:#2a1808;--accent:#8a2d2d;--gold:#a58a3c;--ok:#3c7a45}\n"
    u".gbx-box{background:#ead9b4;border:1px solid rgba(138,106,44,.55);border-radius:8px;\n"
    u"  display:flex;align-items:center;justify-content:center;\n"
    u"  text-align:center;color:#2a1808;font-weight:600;flex-direction:column}\n"
    u".gbx-box.sub{background:#dcc592;font-weight:500}",
    'P689 boxes')

sub(u".gbx-btn{background:#c9c9c9;border-radius:12px;display:flex;align-items:center;justify-content:center;\n"
    u"  font-weight:700;font-size:16px;cursor:pointer;color:#1c1c1c;flex-direction:column}\n"
    u".gbx-btn:active{transform:scale(.97);background:#d8d8d8}\n"
    u".gbx-btn.primary{background:#e0d6b8;border:2px solid #a58a3c}",
    u".gbx-btn{background:#d9bd84;border:2px solid #8a6a2c;border-radius:12px;\n"
    u"  display:flex;align-items:center;justify-content:center;\n"
    u"  font-weight:700;font-size:16px;cursor:pointer;color:#241505;flex-direction:column}\n"
    u".gbx-btn:active{transform:scale(.97);background:#e3c890}\n"
    u".gbx-btn.primary{background:#c9a24a;border:2px solid #7a5a1c}",
    'P689 buttons')

sub(u".gbx-heart.lost{background:#6a6a6a}",
    u".gbx-heart.lost{background:#5a4a3c}",
    'P689 lost heart')

sub(u".gbx-goldchip{height:30px;min-width:80px;border-radius:15px;background:#c9c9c9;color:#1c1c1c;",
    u".gbx-goldchip{height:30px;min-width:80px;border-radius:15px;background:#d9bd84;color:#241505;",
    'P689 gold chip')

# ── the sheet's default face ────────────────────────────────────────────
sub(u"#gbSheet{position:fixed;left:0;right:0;bottom:0;max-height:80%;background:#d6d6d6;color:#1c1c1c;\n"
    u"  border-radius:18px 18px 0 0;transform:translateY(105%);transition:transform .22s ease;z-index:9610;\n"
    u"  overflow-y:auto;padding:10px 14px 24px;font-family:'JMH Beda',serif}\n"
    u"#gbSheet.on{transform:translateY(0)}\n"
    u"#gbSheet h2{font-size:12px;margin:10px 0 4px;opacity:.75;color:#1c1c1c}",
    u"/* P689: the DEFAULT face is parchment now - the shop's die inspect, the\n"
    u"   enchant list, the peeks and the innkeep's book all open this element,\n"
    u"   and they were the last grey sheets. The fam-sheet variant below stays\n"
    u"   and simply agrees with the base. */\n"
    u"#gbSheet{position:fixed;left:0;right:0;bottom:0;max-height:80%;background:#e7d6ac;color:#2a1808;\n"
    u"  border-top:2px solid #a58a3c;box-shadow:0 -4px 18px rgba(20,12,4,.45);\n"
    u"  border-radius:18px 18px 0 0;transform:translateY(105%);transition:transform .22s ease;z-index:9610;\n"
    u"  overflow-y:auto;padding:10px 14px 24px;font-family:'JMH Beda',serif}\n"
    u"#gbSheet.on{transform:translateY(0)}\n"
    u"#gbSheet h2{font-size:12px;margin:10px 0 4px;opacity:.8;color:#2a1808}\n"
    u"#gbSheet>div:first-child{background:rgba(90,60,20,.35)!important}",
    'P689 the sheet default')

# ── the modal card ──────────────────────────────────────────────────────
c = s.count(u".gbx-card{")
if c == 1:
    i = s.index(u".gbx-card{")
    j = s.index(u"}", i) + 1
    old_card = s[i:j]
    s = s.replace(old_card,
        u".gbx-card{background:#e7d6ac;color:#2a1808;border:2px solid #a58a3c;border-radius:14px;\n"
        u"  padding:16px;max-width:320px;width:86%;font-family:'JMH Beda',serif;\n"
        u"  box-shadow:0 8px 26px rgba(10,6,2,.55)}")
    n += 1
    print('  ok  P689 the modal card (was: %s)' % old_card[:60])
else:
    print('  !! .gbx-card rule count %d - skipped' % c)

# ── the shelf overlay's ground ──────────────────────────────────────────
sub(u"  ov.style.cssText='position:fixed;inset:0;background:#4a4a4a;z-index:9450;overflow:auto;color:#1c1c1c;'",
    u"  /* P689: dark tavern wood behind the parchment boxes, not wireframe grey */\n"
    u"  ov.style.cssText='position:fixed;inset:0;background:#1a120a;z-index:9450;overflow:auto;color:#e8d8b8;'",
    'P689 the shelf ground')

# ── For Keeps loses the debug pink ──────────────────────────────────────
sub(u"  if(rc)rc.innerHTML='<div style=\"font-family:monospace;color:#f8a;padding:30px 10px;text-align:center\">'+msg+'</div>';",
    u"  /* P689: the last debug-styled injection - monospace pink on the win card */\n"
    u"  if(rc)rc.innerHTML='<div style=\"font-family:'+\"'JMH Beda'\"+',serif;font-size:15px;color:#3a2812;padding:30px 12px;text-align:center;line-height:1.5\">'+msg+'</div>';",
    'P689 For Keeps in the game voice')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
