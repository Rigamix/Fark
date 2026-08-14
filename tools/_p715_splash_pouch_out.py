# -*- coding: utf-8 -*-
"""P715: the boss splash goes; the pouch goes with it.

Denis: "remove the boss splashes for now" - since P714 they were name-only
anyway. The one thing the splash CARRIED besides pixels was the boss music
cue (_setMusicLayer('boss') fired inside it), so the cue moves to both
launch paths and the splash simply stops being called; the tell stays on
its persistent badge as before. And: "We shouldn't have a pouch even with
renown in the new system" - the three pouch surfaces (the end-draft button
next to SKIP, the pouch modal's parse-time icon, the tier-loadout chip)
come out, which also removes the last legacy image the P714 purge had to
keep. The pouch panel code goes dormant with no entrances.
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


# ── the fresh boss launch: music cue, no splash ──
sub(u"    /* Boss fight splash — inlines the Tell info, no second splash needed */\n"
    u"    if(G._isBoss&&rung.key){\n"
    u"      _showBossSplash(rung.key,rung.name,function(){_afterPrimarySplash(true);});\n"
    u"      return;\n"
    u"    }",
    u"    /* P715: the boss splash is OUT (Denis; it was name-only since P714).\n"
    u"       The music cue it carried survives; the tell stays on the\n"
    u"       persistent badge, so the tell-splash skip stays too. */\n"
    u"    if(G._isBoss&&rung.key){\n"
    u"      try{if(typeof _setMusicLayer==='function')_setMusicLayer('boss');}catch(e){}\n"
    u"      _afterPrimarySplash(true);\n"
    u"      return;\n"
    u"    }",
    'boss launch: cue without splash')

# ── the resumed boss: same ──
sub(u"  /* P711: a resumed BOSS match re-announces itself - the boss splash\n"
    u"     carries the portrait Denis missed AND starts the boss music layer,\n"
    u"     so without it a resumed boss fight also played the tavern track.\n"
    u"     It rides over the restoring table; the turn starts beneath it. */\n"
    u"  if(params._resumeData&&G&&G._isBoss&&rung.key){\n"
    u"    try{_showBossSplash(rung.key,rung.name,null);}catch(e){}\n"
    u"  }",
    u"  /* P711/P715: the splash is out per Denis, but its boss music cue stays -\n"
    u"     without it a resumed boss fight keeps the tavern track. */\n"
    u"  if(params._resumeData&&G&&G._isBoss){\n"
    u"    try{if(typeof _setMusicLayer==='function')_setMusicLayer('boss');}catch(e){}\n"
    u"  }",
    'boss resume: cue without splash')

# ── the pouch surfaces ──
sub(u"  <!-- Large pouch icon overlapping the top edge of the panel (like the mid-match loadout portrait) -->\n"
    u"  <img src=\"assets/Menu_Art/pouch.png?v=232\" alt=\"Pouch\" class=\"pouch-portrait\">",
    u"  <!-- P715: pouch icon out - the pouch is not part of the new system -->",
    'pouch modal icon out')

sub(u"  var pouchBtn='';\n"
    u"  if(typeof getPouchCapacity==='function'&&getPouchCapacity()>0){\n"
    u"    pouchBtn='<div class=\"end-draft-pouch-btn\" id=\"endDraftPouchBtn\" onclick=\"togglePouchPanel()\" title=\"Pouch\"><img src=\"assets/Menu_Art/pouch.png?v=232\" alt=\"Pouch\"></div>';\n"
    u"  }",
    u"  /* P715: the pouch button is out - the pouch is not part of the new\n"
    u"     system, even with renown (Denis). Entrances removed; the panel code\n"
    u"     sleeps unreferenced. */\n"
    u"  var pouchBtn='';",
    'end-draft pouch button out')

sub(u"    lc.innerHTML='<div class=\"tier-lo-pouch\" onclick=\"togglePouchPanel()\" title=\"Your cards\">'\n"
    u"      +'<img src=\"assets/Menu_Art/pouch.png?v=232\" alt=\"Cards\">'\n"
    u"      +'<span class=\"tlp-count\">'+_equipped+'</span></div>';",
    u"    /* P715: the pouch chip is out with the pouch itself */\n"
    u"    lc.innerHTML='';",
    'tier-loadout pouch chip out')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
