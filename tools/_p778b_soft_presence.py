# -*- coding: utf-8 -*-
"""P778b: the card's soft pass gets its own count.

Under screen blending the halo's effect scales with its ALPHA - the
blend can only brighten as far as the paint is opaque. One soft pass
at full arm measured 105/255 at the card's edge: correct shape, gentle
presence. The pass count was the dice's dial (G.softPasses=1) with no
per-caller override - the same borrowed-dial hole P777 closed for
sx/sy. opts.softPasses now overrides; cards run 2, dice unchanged.
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


sub("""    blurOnto(gx,SOFTR,G.softPasses||1);""",
    """    blurOnto(gx,SOFTR,(opts&&opts.softPasses)||G.softPasses||1);/* P778b: caller's count */""",
    'softPasses is opts-aware')

sub("""        {soft:CG.soft,rim:CG.rim,strength:CG.strength,dy:r.height*(CG.dyF||0),
         sx:1,sy:1,/* P777: the card does not lean like a die */""",
    """        {soft:CG.soft,rim:CG.rim,strength:CG.strength,dy:r.height*(CG.dyF||0),
         softPasses:CG.softPasses||2,/* P778b: presence under the screen blend */
         sx:1,sy:1,/* P777: the card does not lean like a die */""",
    'cards run 2 soft passes')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
