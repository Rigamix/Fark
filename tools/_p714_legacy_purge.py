# -*- coding: utf-8 -*-
"""P714: the previous game's art stops loading. All of it that can.

Denis's rule: nothing in assets/ legacy art should ever be loaded. Measured
first (room census probe + his HAR): the live room is ENTIRELY the new
painted pt-stage - every old-layer piece (sign, pouch fab, marks plaque,
boss shadow, chalkboard, seat frames, tier boss portrait, plate_room2 bg)
is invisible beneath it, yet the static <img> tags fetched at parse time
and the hidden-layer renderer fetched more on room entry. The boss portrait
maps (PORTRAITS/GAUNTLET_PORTRAITS) resolve through the bosses' legacy keys
(GROG -> 'drunkard') to previous-game busts - a style clash on every boss
surface besides being legacy loads; every reader guards on empty, so the
maps empty out and the splash/peek/end screens show name-only until new
boss busts exist.

Removed loads: 4 room statics + 4 nav icons, plate_room2/chalkboard/
plank_green/loadout.png/gameover.png CSS urls, the 8 per-boss ::before
match skins (fully covered by the common matchPlate), the dead body::before
table url (display:none'd since the screen-overrides pass), both portrait
maps, and the hidden legacy roster renderer. The JMH Beda font moves out of
assets/_mockups into Art/Assets/Fonts (same file; the game's main display
font should not live in a mockup folder).

Kept, named plainly: assets/cards, win/, loss/, Audio/, vendor/, models/,
Fonts/Macondo (all CURRENT infrastructure that happens to live in assets/),
and table_commoner.webp - the 07-27 TABLE PLATE painting of the match
brief, the one legacy-folder file that is genuinely current art; it is the
match backdrop under the plate img. Relocation of those is housekeeping for
a quiet pass, not a load fix.
"""
import io, os, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    """The file MIXES line endings (original regions CRLF, patched regions
    LF) - a multiline anchor tries LF first, then the CRLF spelling."""
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


# ── the room statics (all invisible under the pt stage, all parse-time fetches) ──
sub(u"  <div class=\"room-sign\"><img src=\"assets/Night_Art/ui_sign_hang.png\" alt=\"\"><span class=\"rs-txt\">TONIGHT&rsquo;S CROWD</span></div>",
    u"  <div class=\"room-sign\"><span class=\"rs-txt\">TONIGHT&rsquo;S CROWD</span></div><!-- P714: legacy sign art out -->",
    'sign img out')

sub(u"    <img src=\"assets/Menu_Art/pouch.png?v=232\" alt=\"Pouch\" class=\"pouch-fab-img\">",
    u"    <!-- P714: legacy pouch icon out -->",
    'pouch fab img out')

sub(u"    <div class=\"boss-shadow\" id=\"bossShadow\" onclick=\"SFX.nav();openBossPeek()\"><img src=\"assets/Night_Art/char_boss_shadow.png\" alt=\"\"></div>",
    u"    <div class=\"boss-shadow\" id=\"bossShadow\" onclick=\"SFX.nav();openBossPeek()\"><!-- P714: legacy silhouette out --></div>",
    'boss shadow img out')

sub(u"      <img src=\"assets/Night_Art/ui_plaque_marks.png\" alt=\"\"><span class=\"mp-txt\" id=\"marksTxt\"></span>",
    u"      <span class=\"mp-txt\" id=\"marksTxt\"></span><!-- P714: legacy plaque art out -->",
    'marks plaque img out')

sub(u"<img class=\"nav-icon\" src=\"assets/Menu_Art/beer.png\" alt=\"Menu\">",
    u"", 'beer nav icons out (x2)', count=2)
sub(u"<img class=\"nav-icon\" src=\"assets/Menu_Art/Shop.png\" alt=\"Shop\">",
    u"", 'shop nav icon out')
sub(u"<img class=\"nav-icon\" src=\"assets/Menu_Art/Gauntlet2.png\" alt=\"Back\">",
    u"", 'gauntlet nav icon out')

# ── dead CSS urls ──
sub(u"#screen-gauntlet{background:url('assets/Night_Art/plate_room2.png') center top/cover no-repeat #16100a}",
    u"#screen-gauntlet{background:#16100a}/* P714: plate_room2 never won the cascade; the pt stage paints the room */",
    'plate_room2 out')

sub(u"  background:url('assets/Night_Art/ui_board_chalk.png') center/contain no-repeat;\n",
    u"  /* P714: chalkboard art out - the board lives under the pt stage, unseen */\n",
    'chalkboard url out')

sub(u"  background:url('assets/Night_Art/ui_btn_plank_green.png') center/100% 100% no-repeat, rgba(28,56,30,.94);",
    u"  background:rgba(28,56,30,.94);/* P714: plank art out */",
    'plank button url out')

sub(u"  background-image:url('assets/Environment_ART/loadout.png');\n",
    u"  /* P714: loadout.png out - the pt stage paints the room */\n",
    'loadout bg out')

sub(u"plainly rather than reported as a fix. */\n"
    u"  background-image:url('assets/Environment_ART/table_commoner.webp?v=1');",
    u"plainly rather than reported as a fix.\n"
    u"     P714: the url is gone from THIS rule only - body::before is\n"
    u"     display:none'd by the screen-overrides pass, so this fetch fed a\n"
    u"     rule that never painted. The live match ::before copy stays. */",
    'dead body::before table url out')

sub(u"/* Per-boss background overrides — initMatchScreen adds `boss-{name}` to\n"
    u"   #screen-match based on the rung. Bosses without a custom image fall\n"
    u"   back to the default match.png above. */\n"
    u"#screen-match.boss-grog::before{background-image:url('assets/Environment_ART/Grog_match.png?v=2')}\n"
    u"#screen-match.boss-mabel::before{background-image:url('assets/Environment_ART/Mabel_match.png?v=3')}\n"
    u"/* File on disk is Finick_match.png (single 'n'); boss class is finnick (double n). */\n"
    u"#screen-match.boss-finnick::before{background-image:url('assets/Environment_ART/Finick_match.png?v=2')}\n"
    u"#screen-match.boss-corvus::before{background-image:url('assets/Environment_ART/Corvus_match.png?v=3')}\n"
    u"#screen-match.boss-brutus::before{background-image:url('assets/Environment_ART/brutus_match.png?v=1')}\n"
    u"#screen-match.boss-aldric::before{background-image:url('assets/Environment_ART/Aldric_match.png?v=2')}\n"
    u"#screen-match.boss-whisper::before{background-image:url('assets/Environment_ART/whisper_match.png?v=4')}\n"
    u"#screen-match.boss-ambrose::before{background-image:url('assets/Environment_ART/ambrose_match.png?v=3')}",
    u"/* P714: the eight per-boss ::before table skins are gone. P685 dressed\n"
    u"   every match with the common plate + props; the matchPlate img covers\n"
    u"   this layer entirely, so each boss fight fetched a full-screen legacy\n"
    u"   png nobody could see. The boss-{name} class itself stays (other rules\n"
    u"   key on it). */",
    'boss ::before skins out')

sub(u"  background:url('assets/Environment_ART/gameover.png') center top / cover no-repeat;",
    u"  background:#0c0a06;/* P714: the painted GAME OVER art covers this screen */",
    'gameover bg out')

# ── the legacy portrait maps empty out; every reader guards on falsy ──
i = s.find(u"const PORTRAITS={")
j = s.find(u"};", i)
frag = s[i:j + 2]
if i < 0 or j < 0 or frag.count(u"Match_Art") < 8 or len(frag) > 700:
    sys.exit('PORTRAITS block not as expected')
sub(frag,
    u"/* P714: the previous game's framed busts, resolved through the bosses'\n"
    u"   legacy keys (GROG -> 'drunkard'). Emptied per Denis: no assets/ legacy\n"
    u"   art loads. Every reader guards on a falsy lookup, so boss surfaces\n"
    u"   show name-only until new boss busts exist - list in OPEN.md #15. */\n"
    u"const PORTRAITS={};",
    'PORTRAITS emptied')

i = s.find(u"const GAUNTLET_PORTRAITS={")
j = s.find(u"};", i)
frag = s[i:j + 2]
if i < 0 or j < 0 or frag.count(u"Characters_ART") < 9 or len(frag) > 700:
    sys.exit('GAUNTLET_PORTRAITS block not as expected')
sub(frag,
    u"/* P714: emptied with PORTRAITS above - same reasoning, same guards. */\n"
    u"const GAUNTLET_PORTRAITS={};",
    'GAUNTLET_PORTRAITS emptied')

# ── the hidden legacy roster renderer stops fetching patron pngs ──
sub(u"function _renderNightRoster(){",
    u"function _renderNightRoster(){\n"
    u"  /* P714: the old room layer's roster - invisible under the pt stage\n"
    u"     since ROOM V2, but its innerHTML still fetched a seat frame + patron\n"
    u"     png per seat on every room entry. The pt stage renders the crowd. */\n"
    u"  return;",
    '_renderNightRoster retired')

# ── JMH Beda leaves the mockup folder ──
src = os.path.join(ROOT, 'assets', '_mockups', 'new_main', 'JMH Beda.ttf')
dst = os.path.join(ROOT, 'Art', 'Assets', 'Fonts', 'JMH Beda.ttf')
if not os.path.exists(dst):
    shutil.copy2(src, dst)
print('  ok  JMH Beda copied to Art/Assets/Fonts')
sub(u"assets/_mockups/new_main/JMH Beda.ttf",
    u"Art/Assets/Fonts/JMH Beda.ttf",
    'JMH Beda ref moves')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
