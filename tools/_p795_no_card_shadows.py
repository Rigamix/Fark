# -*- coding: utf-8 -*-
"""P795: cards carry NO shadow, in any state.

Denis: "there is a dark shadow line at the bottom that messes with the
card. Remove any shadow or added thickness. Should be the card art
png, the core and glow."

The layer hunt proved the lit state clean (no box-shadow, filter =
brightness only, nothing painting below the card) - but the RESTING
.fcv still carried the two bottom-offset dark drop-shadows, stripped
only by the .fcv-lit class. Any state that shows glow without that
class (a row rebuild race replacing the element, the lab's demo mid-
rebuild) shows glow AND shadows together - the bottom-weighted dark
band in his screenshot, which also reads as fake card thickness.

His spec is cleaner than the state-juggling: the card is the art png,
the core, and the glow - nothing else. The shadow pair goes from the
base rule and from spent (which keeps its grey); .fcv-lit keeps only
the bob-freeze (its brightness lift goes too - nothing but the art).
The P746b/P757 drag and armed states already carry shadow-free filters.
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


sub("""#famRowP .fcv{width:20cqw;cursor:pointer;transition:transform .18s ease,filter .18s ease;
  filter:drop-shadow(0 0.25cqw 0.3cqw rgba(10,6,2,.5)) drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.45))}""",
    """/* P795 (Denis): NO card shadows, any state - 'should be the card art
   png, the core and glow.' The old contact pair also painted over the
   glow whenever a state showed light without the lit class. */
#famRowP .fcv{width:20cqw;cursor:pointer;transition:transform .18s ease,filter .18s ease}""",
    'the resting shadows go')

sub("""#famRowP .fcv.spent,#famRowP .fcv.spent.fcv-drag{filter:saturate(.18) brightness(.48)
  drop-shadow(0 0.25cqw 0.3cqw rgba(10,6,2,.5)) drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.4))}""",
    """#famRowP .fcv.spent,#famRowP .fcv.spent.fcv-drag{filter:saturate(.18) brightness(.48)}""",
    "spent keeps only its grey")

sub("""/* P780: a LIT card (D3X.cardGlow holds an entry for it) drops the dark
   contact shadows - they painted OVER the halo canvas below, the 'hole
   in the alpha' Denis photographed. The glow is the card's grounding
   while it lasts. Same replace-the-filter move as .fcv-drag and
   .armed; spent stays later in the sheet and still wins. */
#famRowP .fcv.fcv-lit{filter:brightness(1.05)}""",
    """/* P780/P795: no shadows exist on cards any more; lit keeps only the
   bob-freeze below - the art itself is untouched. */""",
    'lit needs no filter')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
