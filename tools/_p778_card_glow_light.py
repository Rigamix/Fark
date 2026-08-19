# -*- coding: utf-8 -*-
"""P778: the card glow becomes LIGHT - blended, golden, soft-edged.

Denis (2026-08-19): "make the card glow effect additive mode or
something so I can see it brightening the set rather than being a
solid color. Also make it a nice golden color not a beige. Make sure
it's soft on the edges so it looks like light."

Why it read as paint: _paintHalo already composites 'lighter' - but
only WITHIN the glow canvas, onto a just-cleared transparent surface,
where 'lighter' is a no-op. The canvas itself is a separate DOM layer
the browser composites source-over, so the gold OCCLUDED the wood
instead of brightening it. The fix is on the ELEMENT: dgCanvasHi gets
mix-blend-mode:screen, so the browser blends the halo with whatever
is underneath - the grain shows through, brightened toward gold.
Screen rather than plus-lighter: gentler shoulder (never clips to
white as fast) and supported everywhere this game runs. The dice
canvas (dgCanvas, z3) is separate and untouched - Denis likes it.

Look values, changed AT HIS REQUEST (his dials, his call):
  col      #ffe6a4 -> #ffd84e   the beige becomes gold (rim)
  softCol  #ffa93a -> #ffae1f   deeper gold for the wide falloff
  soft     6 -> 11              the tail matches the dice's reach -
                                "soft on the edges so it looks like
                                light"
  grow     1.05 -> 1.02         the near-solid 2px core ring (what
                                survives P777's inward punch) thins to
                                ~1px, so falloff dominates the edge
Everything else (rim 2.5, strength .91, floor .42, dyF 0) stays.
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


# ── 1. the canvas blends as light with what is under it ──
sub("""      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:41';
      sc.appendChild(cv);""",
    """      /* P778: SCREEN-BLENDED - the halo brightens the table under it
         (grain showing through) instead of painting over it. This is
         the additive read Denis asked for; the ctx-level 'lighter' in
         _paintHalo only ever blended the glow with its own cleared
         canvas. Cards only: the dice canvas is separate and liked. */
      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:41;mix-blend-mode:screen';
      sc.appendChild(cv);""",
    'the canvas screens onto the table')

# ── 2. gold, not beige; dice-reach tail; the core ring thins ──
sub("""  CARD_GLOW:{col:'#ffe6a4', softCol:'#ffa93a', soft:6, rim:2.5, strength:0.91,
    grow:1.05, dyF:0, round:0.075, line:0, floor:0.42},""",
    """  /* P778: retuned AT DENIS'S REQUEST (2026-08-19) - gold not beige,
     tail at the dice's reach, core ring thinned so the edge is all
     falloff. */
  CARD_GLOW:{col:'#ffd84e', softCol:'#ffae1f', soft:11, rim:2.5, strength:0.91,
    grow:1.02, dyF:0, round:0.075, line:0, floor:0.42},""",
    'gold + soft tail + thin core')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
