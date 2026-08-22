# -*- coding: utf-8 -*-
"""P852: ?vagatest=1 stops being live on the public build.

Denis spotted it while checking the CARDS-layer reachability: the one
real acquisition path into S.run.cards is a DEBUG URL trigger, and its
own comment says "strip if shipping prod". It is live on Pages.

The exposure is worse than handing a stranger a loadout. The block
overwrites S.run wholesale - dice, cards, gold, tier, gauntlet state -
and then calls save(). Anyone who opens rigamix.github.io/Fark with
?vagatest=1 while a run is in progress LOSES THAT RUN, silently and
permanently, before the menu paints.

Gated rather than deleted, deliberately: every probe in tools/ drives
localhost, so a localhost/file gate keeps the trigger fully usable as
an instrument - including as the one HONEST gate for driving the
CARDS-layer actives (a probe that hand-seeds usedCards is not proof
the layer works; this is). The public build gets nothing.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = """function _applyDebugUrlTriggers(){
  try{
    var p=new URLSearchParams(location.search);
    if(p.get('vagatest')==='1'){"""
new = """function _applyDebugUrlTriggers(){
  try{
    /* P852: LOCAL ONLY. This block overwrites S.run (dice, cards, gold,
       tier, gauntlet state) and save()s it, so on the public build a
       ?vagatest=1 link silently destroyed a run in progress before the
       menu painted. The trigger's own comment always said "strip if
       shipping prod"; gating instead of stripping keeps it working for
       every probe (they all drive localhost) - including as the one
       honest way to put cards in S.run.cards for a driven test, rather
       than hand-seeding activeCardState. */
    var _h=location.hostname||'';
    var _dbgLocal=(location.protocol==='file:'||_h==='localhost'||_h==='127.0.0.1'||_h==='[::1]'||_h==='');
    if(!_dbgLocal)return;
    var p=new URLSearchParams(location.search);
    if(p.get('vagatest')==='1'){"""

if s.count(old) == 1:
    s = s.replace(old, new)
else:
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d (nothing written)' % len(ms))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]

for needed in ['P852: LOCAL ONLY', 'if(!_dbgLocal)return;']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: debug URL triggers are localhost-only')
