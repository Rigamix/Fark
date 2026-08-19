# -*- coding: utf-8 -*-
"""P796: Mabel's and Finnick's rooms - one painted state, worn for all.

Denis (2026-08-19): "I added a background for Mabel to be used the same
way as Grog... she only has one state for now. I'll add more character
later." Then: "added Finnick as well."

The room loader is already generic (P722): optimized/<Nice>_env_BG_opt
.webp + _env_Foreground_<stage>_opt.webp per boss folder. The masters
are optimized (2.6MB pngs -> 97-199KB webps, dims untouched, Pillow
q84/m6 - the every-picture-gets-a-light-copy process). What code needs
is the STAGE map: the loader asks for idle/curious early in a night,
and a boss with only 'ready' painted would have fallen back to the
mockup tavern instead of their own room. Missing stages wear the
closest painted one; when Denis paints more states, deleting the
boss's entry (or a stage key) turns them on - no other change.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


sub("""  var bossStage=bossReady?'ready':((pts>=Math.ceil(need/2)&&pts>0)?'curious':'idle');""",
    """  var bossStage=bossReady?'ready':((pts>=Math.ceil(need/2)&&pts>0)?'curious':'idle');
  /* P796: which stages a boss has PAINTED - a missing stage wears the
     closest painted one instead of falling back to the mockup tavern.
     Mabel and Finnick have one state for now (Denis, 2026-08-19);
     delete a key here when its painting lands. */
  var _envMap={MABEL:{idle:'ready',curious:'ready'},
               FINNICK:{idle:'ready',curious:'ready'}}[bossName];
  if(_envMap&&_envMap[bossStage])bossStage=_envMap[bossStage];""",
    'missing stages wear the painted one')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
