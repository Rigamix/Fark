# -*- coding: utf-8 -*-
"""P791: plus-lighter reaches the wood - blend at the LAYER, not inside it.

Denis (comparing the game to his test page): "lost color, there is
still a grey outline... The core isn't visible compared to the glow.
Basically it looks exactly like before I gave you the file."

The port broke his blending's SCOPE. mix-blend-mode blends an element
against its backdrop only up to the nearest stacking-context ancestor.
In his page the glow and the stage background share one context, so
plus-lighter ADDS the glow onto the wood - that is the whole heat of
the look. In the game, #cardGlowLayer carries z-index:41, which
CREATES a stacking context: his plus-lighter elements were blending
against the layer's own transparent backdrop - additive onto nothing,
which renders as plain paint. Pale bloom, invisible core, and a grey
transition band where the hot rim should be. (The per-wrapper rotate
was a second context-creator doing the same for fanned cards.)

The blend moves to the LAYER itself: children composite source-over
into the layer's group, and the group blends plus-lighter against the
page - table art included, rows above unaffected. For light-emitting
layers the difference from per-element blending is second-order
(bg+glow+spill vs bg+(glow over spill)); the heat comes back.
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


sub("""#cardGlowLayer{position:absolute;inset:0;pointer-events:none;z-index:41;
  --core:hsl(13 100% 63%);--glow:hsl(36 88% 56%);
  --core-b:1.83;--glow-b:0.40;--core-sharp:0.67;
  --halo:5;--bloom:17;--intensity:1;--speed:1.3;--flick:1;--blend:plus-lighter}""",
    """/* P791: THE BLEND LIVES ON THE LAYER. z-index makes the layer a
   stacking context, so a blend INSIDE it can only see the layer's own
   transparent backdrop - additive onto nothing is plain paint, which
   was the washed-out core Denis compared against his test page. At
   layer level the backdrop is the table itself, exactly like his
   stage. */
#cardGlowLayer{position:absolute;inset:0;pointer-events:none;z-index:41;
  mix-blend-mode:var(--blend);
  --core:hsl(13 100% 63%);--glow:hsl(36 88% 56%);
  --core-b:1.83;--glow-b:0.40;--core-sharp:0.67;
  --halo:5;--bloom:17;--intensity:1;--speed:1.3;--flick:1;--blend:plus-lighter}""",
    'the layer blends')

sub(""".cgw .spill{position:absolute;left:50%;top:50%;width:190%;height:165%;
  translate:-50% -50%;pointer-events:none;
  background:radial-gradient(closest-side,var(--glow),transparent 70%);
  opacity:calc(.22*var(--glow-b)*var(--intensity)*var(--state,1));
  mix-blend-mode:var(--blend);transition:opacity .2s ease}""",
    """.cgw .spill{position:absolute;left:50%;top:50%;width:190%;height:165%;
  translate:-50% -50%;pointer-events:none;
  background:radial-gradient(closest-side,var(--glow),transparent 70%);
  opacity:calc(.22*var(--glow-b)*var(--intensity)*var(--state,1));
  transition:opacity .2s ease}""",
    'spill blends via the layer')

sub(""".cgw .glow{position:absolute;inset:0;mix-blend-mode:var(--blend);opacity:var(--flick)}""",
    """.cgw .glow{position:absolute;inset:0;opacity:var(--flick)}""",
    'glow blends via the layer')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
