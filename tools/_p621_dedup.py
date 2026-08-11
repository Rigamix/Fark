# -*- coding: utf-8 -*-
"""P621 (Part 2): sentiment-group de-duplication in the resolver.

THE REQUIREMENT: a line carries a sentiment-group label; the resolver must not
pick from the group that fired most recently for that speaker; scoped to within
one match; reusing existing state rather than inventing a tracking system.

THE SPEAKER IS THE POOL. `_dlgPick` already receives it, and pool names are
already speaker-scoped - boss:corvus:win, patron:nell:loss, trait:steady:push.
So the whole mechanism lives inside _dlgPick and no call site has to record
anything, which is the smallest correct shape. The brief anticipated threading
speaker identity through the callers; it turned out not to be needed.

WHY NOT run._dlgHeard. That is the per-RUN set and it persists across matches,
so a group excluded in one match would stay excluded in the next - the opposite
of "scoped to within a single match". This is a plain module-level map cleared
at match start. It is cosmetic state: losing it on a reload is correct rather
than merely tolerable, because a fresh match should not inherit a stale
exclusion.

IT CAN NEVER GO SILENT. If removing the last group would empty the pool, the
exclusion is skipped and the full pool is used. A de-dup that can return null
would turn a repeated line into NO line, which is worse than the repeat it was
added to prevent.

UNLABELLED LINES ARE UNAFFECTED. All 371 existing rows have no `g`, and
`undefined !== lastGroup` keeps them eligible, so this is inert until labelled
content arrives.
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


sub(u"function _dlgPick(pool,stage,skip){\n"
    u"  var live=PATRON_LINES.filter(function(r){\n"
    u"    if(r.p!==pool)return false;\n"
    u"    if(stage<(r.s||0))return false;\n"
    u"    if(skip&&skip[r.t])return false;\n"
    u"    return _dlgCondOk(r);\n"
    u"  });\n"
    u"  if(!live.length)return null;\n"
    u"  var spec=Math.max.apply(null,live.map(function(r){return (r.c||[]).length;}));\n"
    u"  live=live.filter(function(r){return (r.c||[]).length===spec;});\n"
    u"  var flo=Math.max.apply(null,live.map(function(r){return r.s||0;}));\n"
    u"  live=live.filter(function(r){return (r.s||0)===flo;});\n"
    u"  return live[Math.floor(Math.random()*live.length)];\n"
    u"}",
    u"/* P621: WHICH SENTIMENT GROUP THIS SPEAKER USED LAST, cleared at match start.\n"
    u"   Keyed by POOL, because a pool name already identifies the speaker and the\n"
    u"   outcome (boss:corvus:win, patron:nell:loss) - so the de-dup lives entirely\n"
    u"   inside the resolver and no call site has to record anything.\n"
    u"   NOT on run._dlgHeard: that is per-RUN and survives across matches, which is\n"
    u"   the opposite of the per-match scope asked for. Plain module state is right\n"
    u"   here - this is cosmetic, and a fresh match SHOULD forget. */\n"
    u"var _dlgLastG={};\n"
    u"function _dlgResetGroups(){_dlgLastG={};}\n"
    u"function _dlgPick(pool,stage,skip){\n"
    u"  var live=PATRON_LINES.filter(function(r){\n"
    u"    if(r.p!==pool)return false;\n"
    u"    if(stage<(r.s||0))return false;\n"
    u"    if(skip&&skip[r.t])return false;\n"
    u"    return _dlgCondOk(r);\n"
    u"  });\n"
    u"  if(!live.length)return null;\n"
    u"  var spec=Math.max.apply(null,live.map(function(r){return (r.c||[]).length;}));\n"
    u"  live=live.filter(function(r){return (r.c||[]).length===spec;});\n"
    u"  var flo=Math.max.apply(null,live.map(function(r){return r.s||0;}));\n"
    u"  live=live.filter(function(r){return (r.s||0)===flo;});\n"
    u"  /* P621: DROP THE GROUP THAT SPOKE LAST, but never empty the pool. The\n"
    u"     random pick among ties is still the rule the original comment defends;\n"
    u"     this only stops two lines that mean the same thing landing back to back,\n"
    u"     which that rule was written before pools grew past a handful of lines.\n"
    u"     If the exclusion would leave nothing, it is skipped - a de-dup that can\n"
    u"     return null turns a repeated line into NO line, which is worse than the\n"
    u"     repeat. Rows without a `g` are unaffected: undefined never matches. */\n"
    u"  var lastG=_dlgLastG[pool];\n"
    u"  if(lastG){\n"
    u"    var fresh=live.filter(function(r){return r.g!==lastG;});\n"
    u"    if(fresh.length)live=fresh;\n"
    u"  }\n"
    u"  var pick=live[Math.floor(Math.random()*live.length)];\n"
    u"  if(pick&&pick.g)_dlgLastG[pool]=pick.g;\n"
    u"  return pick;\n"
    u"}",
    'P621 resolver de-dup')

# clear it where a match begins - the same place G is rebuilt
sub(u"function initMatchScreen(data){\n"
    u"  /* Nuclear reset — ensure no stale match state bleeds through */\n"
    u"  G=null;",
    u"function initMatchScreen(data){\n"
    u"  /* Nuclear reset — ensure no stale match state bleeds through */\n"
    u"  G=null;\n"
    u"  /* P621: the sentiment-group de-dup is per MATCH, so it clears here with\n"
    u"     everything else. A new table should not inherit which group the last one\n"
    u"     ended on. */\n"
    u"  try{_dlgResetGroups();}catch(e){}",
    'P621 reset at match start')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n)
