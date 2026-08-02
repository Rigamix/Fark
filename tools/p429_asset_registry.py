# -*- coding: utf-8 -*-
"""P429 - FK_ART, the asset registry. Phase 5's remaining half.

WHAT THE PLAN ASKED FOR, AND WHY IT IS BUILT DIFFERENTLY. The visual plan says
`assets/` is the previous game's folder and a registry should make it
unreachable. The Phase 5 inventory measured that and it is false: 47 live
references into that tree have NO replacement in the current one - every font,
all audio, nine character portraits, eight match frames, the whole Night_Art UI
set. A registry that banned the folder would have banned the fonts, including
'JMH Beda', the family this project keeps calling "the game's font".

So the registry NAMES rather than bans. Its job is to answer "where does the
coin icon live" in one place, because the failure it exists to stop was never
"the code points at the old tree" - only two paths do that, and one of them
resolves to a .psd. The failure was REACHING FOR THE WRONG SOURCE WHEN WRITING
NEW CODE: the font, the coin and the diamond, three times in one session, each
time by looking in the previous game's folder because nothing said which was
which.

HOW IT AVOIDS BEING DECORATION. A registry nobody calls is a comment. The
thirteen prefix constants scattered through the file are REDEFINED from it -
`var PT_P=FK_ART.patronFrames;` - so every existing call site is untouched
(zero blast radius) while there is exactly one place the strings live. Two of
them, BT and BTP, were the same directory declared twice 20k lines apart; they
are now one entry.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

def sub_once(hay, old, new, what):
    n = hay.count(old)
    assert n == 1, 'anchor %s matched %d times (want 1)' % (what, n)
    return hay.replace(old, new)

REGISTRY = u"""<script>
/* ══ FK_ART — one place the asset paths live ═════════════════════════════
   Phase 5 of the visual-integrity plan.

   THE TWO TREES, stated once so nobody has to work it out again:
     Art/Assets/   the CURRENT art. Everything new goes here.
     assets/       the previous game's tree, and STILL LOAD-BEARING. Measured:
                   47 live references with no replacement anywhere in the
                   current tree — every font, all audio, the nine character
                   portraits, the eight match frames, the Night_Art UI set.
                   "Never look in assets/" is a rule that would break the page.
                   The real rule is narrower: NEW ART GOES IN Art/Assets.

   This table exists because of a specific, repeated failure — reaching for the
   wrong source when writing new code. The font, the coin and the diamond were
   each picked out of the old tree in a single session, not because the code
   pointed there but because nothing said which tree was which. Every entry
   below is either a directory something already used, or a single file that
   has been got wrong before.

   ADDING TO IT: put the path here, not at the call site, and
   tools/apv_asset_registry.js will check it resolves over HTTP on the next
   run. A path that only exists in one function is a path the next person
   guesses at. */
var FK_ART={
  /* ── directories, current tree ── */
  homescreen:   'Art/Assets/Homescreen/',
  buttons:      'Art/Assets/Buttons/',   /* was declared twice, 20k lines apart */
  icons:        'Art/Assets/Icons/',
  newRun:       'Art/Assets/NewRun/',
  store:        'Art/Assets/Store/',
  patronFrames: 'Art/Assets/Frames/Patrons/',
  patronChars:  'Art/Assets/Frames/Patrons/Characters/optimized/',
  traits:       'Art/Assets/traits/',
  props:        'Art/Assets/Match/Commoner/Props/',
  lastOrders:   'Art/Assets/LastOrders/optimized/',
  hearts:       'Art/Assets/Hearts/optimized/',
  bossBg:       'Art/Assets/Backgrounds/MAIN/',
  feats:        'Art/Assets/Feats/',
  winPlates:    'Art/Assets/Icons/Wins/optimized/',
  /* ── directories, OLD tree — deliberate, measured, not stale ── */
  mockups:      'assets/_mockups/new_main/',  /* hearts + the game's font live here */
  enchIcons:    'assets/ench_icons/',
  fonts:        'assets/Fonts/',
  /* ── single files this project has picked wrong before ── */
  coin:         'Art/Assets/Icons/optimized/coin_opt.webp',
  diamond:      'Art/Assets/Panels/optimized/SitDown_diamond_opt.webp',
  shelfBg:      'Art/Assets/Shelf/optimized/shelf_bg_opt.webp',
  /* NOT A PATH — the family name, and the entry most likely to save someone.
     `--font-px` is 'Alagard','Press Start 2P', the PREVIOUS game's pixel font,
     and it reads as the obvious choice right up until Denis points out the
     score is in the wrong typeface. The game's font is JMH Beda, 56 uses. */
  font:         "'JMH Beda'"
};
</script>
<script>
"""

s = sub_once(s, u"<script>\n/* Does this engine implement CanvasRenderingContext2D.filter?",
             REGISTRY + u"/* Does this engine implement CanvasRenderingContext2D.filter?",
             'script start')

# ── redefine the scattered constants from the registry ────────────────
REWIRE = [
    (u"  var NR='Art/Assets/NewRun/';",
     u"  var NR=FK_ART.newRun;", 'NR'),
    (u"  var BG='Art/Assets/Shelf/optimized/shelf_bg_opt.webp';",
     u"  var BG=FK_ART.shelfBg;", 'BG'),
    (u"  var HS='Art/Assets/Homescreen/',BT='Art/Assets/Buttons/',IC='Art/Assets/Icons/';",
     u"  var HS=FK_ART.homescreen,BT=FK_ART.buttons,IC=FK_ART.icons;", 'HS/BT/IC'),
    (u"var PT_A='assets/_mockups/new_main/';",
     u"var PT_A=FK_ART.mockups;", 'PT_A'),
    (u"var PT_P='Art/Assets/Frames/Patrons/';",
     u"var PT_P=FK_ART.patronFrames;", 'PT_P'),
    (u"var PT_CHAR='Art/Assets/Frames/Patrons/Characters/optimized/';",
     u"var PT_CHAR=FK_ART.patronChars;", 'PT_CHAR'),
    (u"var PT_TRAITDIR='Art/Assets/traits/';",
     u"var PT_TRAITDIR=FK_ART.traits;", 'PT_TRAITDIR'),
    (u"  var bossDir='Art/Assets/Backgrounds/MAIN/'+bossName+'/';",
     u"  var bossDir=FK_ART.bossBg+bossName+'/';", 'bossDir'),
    (u"  var PP='Art/Assets/Match/Commoner/Props/';",
     u"  var PP=FK_ART.props;", 'PP'),
    (u"  var ST='Art/Assets/Store/';",
     u"  var ST=FK_ART.store;", 'ST'),
    (u"var ENCH_ICON_DIR='assets/ench_icons/';",
     u"var ENCH_ICON_DIR=FK_ART.enchIcons;", 'ENCH_ICON_DIR'),
    (u"  var LO='Art/Assets/LastOrders/optimized/',HRT='Art/Assets/Hearts/optimized/';",
     u"  var LO=FK_ART.lastOrders,HRT=FK_ART.hearts;", 'LO/HRT'),
    (u"  var BTP='Art/Assets/Buttons/';",
     u"  var BTP=FK_ART.buttons;", 'BTP'),
]
for old, new, what in REWIRE:
    s = sub_once(s, old, new, what)

assert s != orig, 'nothing changed'
assert s.count(u'var FK_ART={') == 1, 'registry declared %d times' % s.count(u'var FK_ART={')
# the registry must be assigned before the first top-level constant reads it
assert s.index(u'var FK_ART={') < s.index(u'var PT_A=FK_ART.mockups;'), \
    'registry defined after a top-level consumer'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P429 applied. %d constants rewired to FK_ART' % len(REWIRE))
