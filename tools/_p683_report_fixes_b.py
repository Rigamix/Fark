# -*- coding: utf-8 -*-
"""P683: the layout half of the seventeen-notes findings.

1. NPC DICE UNDER THEIR CARDS - the one shared WebGL canvas sits at z 2 in
   the match while #famRowO is 40 and #famRowP 41. The canvas rises to 41 and
   the player's hand to 42: rolling rival dice paint OVER the rival's cards,
   and the player's own hand still paints over any die that strays that far.
   (The dragged card's z 9500 lives inside famRowP's context - untouched.)

2. TABLE PERSPECTIVE ON THE ROWS - both rows carried the SAME positive
   rotateX (top edge away, wider at the bottom). Right for the rival's far
   row - and now a touch stronger (15 -> 19deg). Wrong direction for the
   player's near hand: it pivots at its bottom edge (origin 50% 100%, so the
   cards stay planted on their line) and tilts -9deg - the top edge comes
   toward the viewer, wider at the top, per Denis: "same for mine but the
   other way around".

3. THE JUMPING STATUS LINE - measured ~80px of jitter and one -1215px
   teleport: the bottom strip was placed off the LIVE dice edges, and the 3D
   layer rewrites those translates every frame, so 'ROLLING...' landed
   wherever the meshes happened to be. The top strip was already fixed to the
   throw line (the 0.223 reserve); the bottom strip now mirrors it - fixed
   reserve below the same line that measured constant through 15s of rolling.

4. THE DOUBLED SCORE - #selTotal duplicated the selection sum the per-die
   tags already show. Its scored '+N' state goes; its two OTHER states stay
   (the enchant-cast name and the zero-selection '0', which have no other
   home). The bottom number (#keptTotal) becomes the LIVE turn total -
   written from refreshSelUI, which already computes it - and steps up to
   the gold the removed number wore.
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


# ── 1. dice above the rival's cards ─────────────────────────────────────
# famRowP FIRST, while "z-index:41}" is still unique in the file - the canvas
# edit below introduces a second occurrence of that string.
sub(u"z-index:41}",
    u"z-index:42}/* P683: above the dice canvas at 41 */",
    'P683 player hand above dice')

sub(u"#screen-match #d3xCanvas{z-index:2}",
    u"/* P683: 2 -> 41. At 2 the one shared dice canvas painted UNDER both card\n"
    u"   rows (famRowO 40, famRowP 42) - a rival die crossing their hand vanished\n"
    u"   behind the cards. 41 puts dice over the rival's row; the player's hand\n"
    u"   stays above at 42. */\n"
    u"#screen-match #d3xCanvas{z-index:41}",
    'P683 dice above rival cards')

# ── 2. the perspective ──────────────────────────────────────────────────
sub(u"  transform:translateX(-50%) perspective(900px) rotateX(15deg);",
    u"  /* P683: 15 -> 19deg - \"a touch wider at the bottom\", per Denis */\n"
    u"  transform:translateX(-50%) perspective(900px) rotateX(19deg);",
    'P683 rival taper stronger')

sub(u"  transform:translateX(-50%) perspective(900px) rotateX(13deg);",
    u"  /* P683: REVERSED for the near hand - Denis: \"same for mine but the other\n"
    u"     way around\". Positive rotateX made both rows taper the same way; the\n"
    u"     player's cards now pivot at their bottom edge (so they stay planted on\n"
    u"     their line) and tilt toward the viewer: wider at the top. */\n"
    u"  transform-origin:50% 100%;\n"
    u"  transform:translateX(-50%) perspective(900px) rotateX(-9deg);",
    'P683 player taper reversed')

# ── 3. the bottom strip stops jumping ───────────────────────────────────
sub(u"  var hiY=edge?edge.top:rr.top, loY=edge?edge.bottom:rr.bottom;",
    u"  var hiY=edge?edge.top:rr.top;\n"
    u"  /* P683: loY is set from the FIXED throw line further down - the dice-edge\n"
    u"     reading is dropped for the bottom strip. Measured: placing it off the\n"
    u"     live dice put ~80px of jitter into the player's own status line and\n"
    u"     once teleported it to -1215px, because the 3D layer rewrites the dice\n"
    u"     translates every frame and 'ROLLING...' lands mid-flight. The top strip\n"
    u"     was cured of exactly this with the 0.223 reserve; this is its mirror. */\n"
    u"  var loY=rr.bottom;",
    'P683 loY off the dice')

sub(u"  document.querySelectorAll('.selTag,#selTotal').forEach(function(e){\n"
    u"    var b=e.getBoundingClientRect().bottom;if(b>loY)loY=b;\n"
    u"  });",
    u"  /* P683: a fixed reserve below the throw line instead of chasing the tag\n"
    u"     rects - same datum the top strip anchors to (it measured constant\n"
    u"     through 15s of live rolling), sized to clear the per-die tag band. */\n"
    u"  if(_tl)loY=_tl.getBoundingClientRect().bottom+_mw*0.10;",
    'P683 fixed reserve below the line')

# ── 4. one bottom number, and it is the turn total ──────────────────────
sub(u"  tot.className=_scored?'':(_isCast?'cast':'zero');\n"
    u"  tot.textContent=_scored?('+'+total.toLocaleString())\n"
    u"    :(_isCast?_cast.join(' + ').toUpperCase():'0');",
    u"  /* P683: the scored '+N' state is GONE - it duplicated the per-die tags'\n"
    u"     sum right above the turn total (Denis's screenshot). The cast state\n"
    u"     (enchant names) and the zero state keep the element alive: they carry\n"
    u"     information nothing else shows. */\n"
    u"  tot.className=_scored?'off':(_isCast?'cast':'zero');\n"
    u"  tot.textContent=_scored?''\n"
    u"    :(_isCast?_cast.join(' + ').toUpperCase():'0');",
    'P683 the duplicate number goes')

sub(u"#selTotal.cast{",
    u"#selTotal.off{display:none}/* P683: scored state - the tags + turn total say it */\n"
    u"#selTotal.cast{",
    'P683 the off state')

sub(u"  const ok=_keepIsLegal(pts,_pvIcons.length,false);G.turnPts=locked+(pts>0?pts:0)+(G._turnBonusPot||0);updHUD();",
    u"  const ok=_keepIsLegal(pts,_pvIcons.length,false);G.turnPts=locked+(pts>0?pts:0)+(G._turnBonusPot||0);updHUD();\n"
    u"  /* P683: the bottom gold number IS the live turn total now - written here\n"
    u"     because this line already computes it. visibility cleared so it shows\n"
    u"     before the first keep too. */\n"
    u"  try{var _kt=document.getElementById('keptTotal');\n"
    u"    if(_kt){_kt.textContent=G.turnPts?G.turnPts.toLocaleString():'';if(G.turnPts)_kt.style.visibility='';}}catch(e){}",
    'P683 keptTotal goes live')

sub(u"#screen-match .kept-total{font-size:5.2cqw;margin-top:0.6cqw;margin-left:0.6cqw}",
    u"/* P683: THE turn-total number now - it inherits the prominence (and the\n"
    u"   gold) of the selection sum it replaced */\n"
    u"#screen-match .kept-total{font-size:6.2cqw;margin-top:0.6cqw;margin-left:0.6cqw;color:#ffd98a}",
    'P683 the gold moves down')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
