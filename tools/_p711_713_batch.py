# -*- coding: utf-8 -*-
"""P711 + P712 + P713.

P711 BOSS RESUME RE-ANNOUNCES. Denis resumed Grog: "grog picture and
dialogue disappeared". The in-match HUD deliberately shows no boss portrait
(fresh or resumed) - the picture he misses is the BOSS SPLASH, and the boss
MUSIC layer is started inside it too, so a resumed boss fight also kept the
tavern track. The splash (portrait + name + music) now replays over the
restoring table on resume; the turn starts beneath it as usual.

P712 THE LOAD PASS (from Denis's HAR). Static <img> tags fetch at parse
time even on screens the runtime paints over - so every cold load pulled
~1.9MB of invisible legacy art: main_04.png (962K) and settings.png (767K)
under the painted title, the removed loadout FAB's icon, the game-over
Innkeeper portrait in a display:none wrap, the old menu's GAUNTLET icon.
Those tags go. The title itself loaded six raw MASTERS whose optimized
copies already exist (bg 758K, logo 875K, two buttons, book, cog): swapped
to the optimized paths, as are the Last Orders and game-over buttons. And
the match table loaded TWICE - #matchPlate says Table_new_opt.webp, the
shadow preloader says ?v=1 - two cache entries for one image; the plate
takes the ?v=1. (bg.webp-vs-bg.png and the doubled banner/hands/panel in
the findings doc are name collisions across win/ and loss/ - checked,
different files, no fix needed. table_commoner.webp is the live page
backdrop, kept.)

P713 CARD FEEDBACK (Denis: no glow at the threshold, no grey on a spent
card, and greyed cards keep hovering). The armed glow existed but at 1.1cqw
of soft shadow it read as nothing under a card in hand - it doubles up and
saturates. The spent grey existed too and KEPT BOBBING (the famBob idles on
every .fcvIn unconditionally) - a spent card now sits still and takes no
tap-scale. The grey itself deepens slightly so the state reads at a glance.
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
        sys.exit('ANCHOR x%d (need %d) for %s' % (c, count, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ══ P711 ══
sub(u"  flashYourTurn();\n"
    u"  setTimeout(startPTurn,_matchStartDelay);\n"
    u"}\n"
    u"\n"
    u"/* closeAllChips global dismiss already registered above (line 4156) */",
    u"  /* P711: a resumed BOSS match re-announces itself - the boss splash\n"
    u"     carries the portrait Denis missed AND starts the boss music layer,\n"
    u"     so without it a resumed boss fight also played the tavern track.\n"
    u"     It rides over the restoring table; the turn starts beneath it. */\n"
    u"  if(params._resumeData&&G&&G._isBoss&&rung.key){\n"
    u"    try{_showBossSplash(rung.key,rung.name,null);}catch(e){}\n"
    u"  }\n"
    u"  flashYourTurn();\n"
    u"  setTimeout(startPTurn,_matchStartDelay);\n"
    u"}\n"
    u"\n"
    u"/* closeAllChips global dismiss already registered above (line 4156) */",
    'P711 boss splash on resume')

# ══ P712: dead parse-time fetches ══
sub(u"<img class=\"bg-img\" src=\"assets/Environment_ART/main_04.png\" alt=\"\">",
    u"<!-- P712: main_04.png (962KB) removed - the painted title covers this\n"
    u"     screen and a hidden <img> still fetches at parse time -->",
    'P712 main_04 img out')

sub(u"      <img class=\"btn-icon\" src=\"assets/Menu_Art/Gauntlet2.png\" alt=\"Gauntlet\">",
    u"      <!-- P712: icon removed - covered by the painted title, fetched anyway -->",
    'P712 menu gauntlet icon out')

sub(u"<img class=\"btn-icon\" src=\"Art/Assets/Panels/Settings/settings.png\" alt=\"Set",
    u"<!-- P712: settings.png (767KB master) removed - covered by the painted title --><span style=\"display:none\" alt=\"Set",
    'P712 settings master out')

sub(u"  <img src=\"assets/Match_Art/Loadout.png\" alt=\"Loadout\" class=\"loadout-fab-img\">",
    u"  <!-- P712: the FAB was retired; its icon still fetched -->",
    'P712 loadout fab img out')

sub(u"<div class=\"lo-portrait\"><img src=\"assets/Match_Art/Loadout.png\" alt=\"Pouch\"></div>",
    u"<div class=\"lo-portrait\"><!-- P712: icon fetch removed --></div>",
    'P712 loadout panel img out')

sub(u"        <img class=\"go-portrait\" src=\"assets/Characters_ART/Innkeeper.png\" alt=\"\">",
    u"        <!-- P712: Innkeeper.png (163KB) removed - the wrap is display:none\n"
    u"             and the painted GAME OVER art replaced this portrait -->",
    'P712 innkeeper img out')

# ══ P712: masters -> optimized ══
sub(u"+'<img class=\"env\" id=\"hsBase\" src=\"'+HS+'bg.png\" alt=\"\">'",
    u"+'<img class=\"env\" id=\"hsBase\" src=\"'+HS+'optimized/bg_opt.webp\" alt=\"\">'/* P712 */",
    'P712 title bg -> optimized')

sub(u"+'<img id=\"hsLogo\" src=\"'+HS+'logo_new.png\" alt=\"Far",
    u"+'<img id=\"hsLogo\" src=\"'+HS+'optimized/logo_new_opt.webp\" alt=\"Far",
    'P712 logo -> optimized')

sub(u"'+BT+'Button_new_01.png\"", u"'+BT+'optimized/Button_new_01_opt.webp\"",
    'P712 title button 01 -> optimized (x2)', count=2)

sub(u"'+BT+'Button_new_02.png\"", u"'+BT+'optimized/Button_new_02_opt.webp\"",
    'P712 title button 02 -> optimized (x2)', count=2)

sub(u"<img src=\"'+IC+'book.png\"", u"<img src=\"'+IC+'optimized/book_opt.webp\"",
    'P712 book icon -> optimized')

sub(u"<img src=\"'+IC+'cog.png\"", u"<img src=\"'+IC+'optimized/cog_opt.webp\"",
    'P712 cog icon -> optimized')

sub(u"+'<img class=\"plq\" src=\"Art/Assets/Buttons/Button_new_01.png\" alt=\"\">'",
    u"+'<img class=\"plq\" src=\"Art/Assets/Buttons/optimized/Button_new_01_opt.webp\" alt=\"\">'/* P712 */",
    'P712 Last Orders button -> optimized')

sub(u"'+BTP+'Button_new_01.png\"", u"'+BTP+'optimized/Button_new_01_opt.webp\"",
    'P712 gameover button 01 -> optimized')

sub(u"'+BTP+'Button_new_02.png\"", u"'+BTP+'optimized/Button_new_02_opt.webp\"",
    'P712 gameover button 02 -> optimized')

# ══ P712: one table, one cache entry ══
sub(u"<img id=\"matchPlate\" src=\"Art/Assets/Match/Commoner/optimized/Table_new_opt.webp\" alt=\"\">",
    u"<img id=\"matchPlate\" src=\"Art/Assets/Match/Commoner/optimized/Table_new_opt.webp?v=1\" alt=\"\">"
    u"<!-- P712: same ?v=1 as the shadow preloader - it loaded TWICE as two cache entries -->",
    'P712 matchPlate joins ?v=1')

# ══ P713: the armed glow doubles up ══
sub(u"#famRowP .fcv.armed,#screen-match #famRowO .fcv.armed{\n"
    u"  filter:drop-shadow(0 0 1.1cqw rgba(255,217,138,.85))\n"
    u"  drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))}/* P576: third of the three */",
    u"#famRowP .fcv.armed,#screen-match #famRowO .fcv.armed{\n"
    u"  /* P713: Denis could not see the old single soft shadow under a card in\n"
    u"     hand - a tight hot core plus a wide halo reads as ARMED at a glance */\n"
    u"  filter:drop-shadow(0 0 0.45cqw rgba(255,236,170,.95))\n"
    u"  drop-shadow(0 0 1.8cqw rgba(255,205,95,.85))\n"
    u"  drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))\n"
    u"  brightness(1.12)}/* P576: third of the three */",
    'P713 armed glow doubles up')

# ══ P713: a spent card sits still ══
sub(u"#famRowP .fcv .fcvIn{animation:famBob 4.6s ease-in-out infinite;will-change:transform}",
    u"#famRowP .fcv .fcvIn{animation:famBob 4.6s ease-in-out infinite;will-change:transform}\n"
    u"/* P713: a SPENT card sits still - the bob read as \"still usable\" (Denis:\n"
    u"   \"it should also stop hovering when greyed out\") - and takes no tap-scale */\n"
    u"#famRowP .fcv.spent .fcvIn{animation:none}\n"
    u"#famRowP .fcv.spent{scale:1 !important}",
    'P713 spent card sits still')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
