# -*- coding: utf-8 -*-
"""P607 (rest) + P608: retire playerTitle entirely, and swell the dice at the apex.

P607 REST. Three call sites survived the first pass - the run-won greybox, the
Innkeep's Book "your standing" line, and the BARRED panel. The recon rates all
three unreachable or dead, but "ensure it is removed everywhere" is the ask and
an unreachable caller is exactly what makes a later reader think the ladder is
still live. With those gone, playerTitle() and PLAYER_TITLES have zero callers
and follow them out. _titleFor / TITLE_BANDS / pat.title are the NPC and boss
titles - a separate data path, deliberately untouched.

P608 THE APEX SWELL, and the reason it hangs off _airRamp rather than repeating
the expression: the DARKENING DENIS ASKED FOR ALREADY EXISTS. _airTint ramps a
die's tint on the same height, so a second copy of that ramp for the scale would
give two effects that peak on different frames the moment either constant is
touched. One function owns the height, both read it.
Note on the arc: the recorded solve has NO RISE - the dice are dropped from
dropY 5.4 and y[0] IS the maximum - so "at their highest" is the first ~430ms of
the fall, and the swell decays as they drop, which is the effect asked for.
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:110]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── P607: the last three call sites ──────────────────────────────────────
sub(u"    +'<div style=\"margin-top:14px;color:#ca8\">'+(playerTitle()!=='nobody'?playerTitle():'')+'</div>'\n",
    u"", 'P607 run-won greybox')

sub(u"    +'title: '+playerTitle()+' · renown '+(S.renown||0)+'<br>'",
    u"    +'renown '+(S.renown||0)+'<br>'", 'P607 innkeep book')

sub(u"      +(Object.keys(S.featsDone||{}).length)+' feats · '+playerTitle()+'</div>';",
    u"      +(Object.keys(S.featsDone||{}).length)+' feats</div>';", 'P607 barred panel')

# ── P607: the source, now that nothing calls it ──────────────────────────
sub(u"var PLAYER_TITLES=[[0,'nobody'],[40,'Goodman'],[140,'Master'],[350,'Sir'],[700,'a Name']];\n"
    u"function playerTitle(){\n"
    u"  var r=(S&&S.renown)||0,t='nobody';\n"
    u"  PLAYER_TITLES.forEach(function(row){if(r>=row[0])t=row[1];});\n"
    u"  return t;\n"
    u"}\n",
    u"/* P607: PLAYER_TITLES and playerTitle() are gone - the player has no rank any\n"
    u"   more, only NIGHT n/8. They were pure-derived from S.renown and nothing ever\n"
    u"   consumed the return value except string concatenation, so removing the eight\n"
    u"   call sites left them with none. The save blob never carried a title, so no\n"
    u"   migration is needed. _titleFor / TITLE_BANDS below are the PATRON and BOSS\n"
    u"   titles - a different ladder, still very much in use. */\n",
    'P607 source')

# ── P608: one ramp, two effects ──────────────────────────────────────────
sub(u"  airDarkFrom:1.4, airDarkTo:5.4, airDark:0.35,",
    u"  /* P608: airSwell is the apex scale, and it deliberately shares airDark's\n"
    u"     ramp - see _airRamp. 0.18 means a die is 18% larger at throw height and\n"
    u"     eases back to its own size as it falls, which is the fake perspective\n"
    u"     Denis asked for. airDark 0.35 -> 0.45 because the darkening he also asked\n"
    u"     for ALREADY existed on this ramp and was too faint to read. */\n"
    u"  airDarkFrom:1.4, airDarkTo:5.4, airDark:0.45, airSwell:0.18,",
    'P608 constants')

sub(u"  _airTint:function(d,y){\n"
    u"    var P=this.PHYS;\n"
    u"    var k=(y-P.airDarkFrom)/(P.airDarkTo-P.airDarkFrom);\n"
    u"    k=k<0?0:(k>1?1:k);\n"
    u"    k*=P.airDark;\n",
    u"  /* P608: 0 on the table, 1 at throw height. THE one height ramp - the air\n"
    u"     darkening and the apex swell both read it, so they cannot come to peak on\n"
    u"     different frames. Two copies of this expression is the bug to avoid. */\n"
    u"  _airRamp:function(y){\n"
    u"    var P=this.PHYS,k=(y-P.airDarkFrom)/(P.airDarkTo-P.airDarkFrom);\n"
    u"    return k<0?0:(k>1?1:k);\n"
    u"  },\n"
    u"  _airTint:function(d,y){\n"
    u"    var P=this.PHYS;\n"
    u"    var k=this._airRamp(y)*P.airDark;\n",
    'P608 _airRamp helper')

sub(u"          d.obj.visible=true;\n"
    u"          d.obj.scale.setScalar(1);\n"
    u"          d.obj.position.set(pose.x,pose.y,pose.z);",
    u"          d.obj.visible=true;\n"
    u"          /* P608: fake perspective - a die is airSwell larger at the top of\n"
    u"             the throw and eases back to 1 as it falls, on the SAME ramp that\n"
    u"             darkens it. Purely visual: it writes only obj.scale, which the\n"
    u"             settled branch overwrites on the very next frame, and _burstPose\n"
    u"             below still wins when a burst is running. */\n"
    u"          d.obj.scale.setScalar(1+(D3X.PHYS.airSwell||0)*D3X._airRamp(pose.y));\n"
    u"          d.obj.position.set(pose.x,pose.y,pose.z);",
    'P608 scale hook')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n)
