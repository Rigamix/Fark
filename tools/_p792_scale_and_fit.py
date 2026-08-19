# -*- coding: utf-8 -*-
"""P792: the prototype's proportions at the card's size; the mask can
never overhang the projected card.

Side-by-side against Denis's test page (same headless renderer), the
in-game glow was wide, pale and core-less while his reference is a
tight hot rim. Three mechanisms:

  SCALE      the prototype is authored at a 200px card: halo 5px is
             2.5% of the width, bloom 17px is 8.5%. The in-game card
             is ~88px, so the same pixel values are DOUBLE the
             proportional reach - a wide wash that buries the core
             ("the core isn't visible compared to the glow"). Every px
             calc now multiplies by --cgs = cardWidth/200, set per
             wrapper, so his numbers mean at any size what they mean
             on his page.
  KEYSTONE   the rows are a perspective stage: the projected card is a
             TRAPEZOID, and a rectangular mask sized to its AABB
             matches the widest edge and overhangs the art near the
             top - the rim painted 1-2px off the edge with the card's
             dark AA in between: the grey outline. The wrapper is now
             anchored to the art's true aspect at the MINIMUM
             projected size (0.99 x projected height x natural ratio),
             so the mask sits just inside the card everywhere and the
             rim's shadows reach out tight against the edge - which is
             also exactly how the reference composes it (shadows from
             the silhouette, body under the face).
  LETTERBOX  'contain' inside a wrapper of a different aspect shrank
             the mask further; the natural-ratio wrapper removes the
             letterbox for straight and fanned cards alike.
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


# ── 1. every px in the look scales by the card's size ──
sub(""".cgw .bloom{opacity:min(1,calc(var(--glow-b)*var(--intensity)*var(--state,1)));
  filter:drop-shadow(0 0 calc(var(--bloom)*1px) var(--glow))
         drop-shadow(0 0 calc(var(--bloom)*0.5px) var(--glow))
         brightness(max(1,calc(var(--glow-b)*var(--intensity)*var(--state,1))));
  animation:cgSwell calc(5.3s/max(var(--speed),.0001)) ease-in-out infinite}""",
    """/* P792: --cgs = cardWidth/200 - the prototype is authored at a 200px
   card, so a px there is a proportion, not a length */
.cgw .bloom{opacity:min(1,calc(var(--glow-b)*var(--intensity)*var(--state,1)));
  filter:drop-shadow(0 0 calc(var(--bloom)*var(--cgs,1)*1px) var(--glow))
         drop-shadow(0 0 calc(var(--bloom)*var(--cgs,1)*0.5px) var(--glow))
         brightness(max(1,calc(var(--glow-b)*var(--intensity)*var(--state,1))));
  animation:cgSwell calc(5.3s/max(var(--speed),.0001)) ease-in-out infinite}""",
    'bloom scales')

sub(""".cgw .halo{z-index:2;opacity:min(1,calc(var(--core-b)*var(--intensity)*var(--state,1)));
  filter:drop-shadow(0 0 calc(var(--halo)*(1 - 0.75*var(--core-sharp))*1px) var(--core))
         drop-shadow(0 0 calc(var(--halo)*0.25*var(--core-sharp)*1px) var(--core))
         drop-shadow(0 0 calc(var(--halo)*0.25*var(--core-sharp)*1px) var(--core))
         drop-shadow(0 0 calc(var(--halo)*0.25*var(--core-sharp)*1px) var(--core))
         brightness(max(1,calc(var(--core-b)*var(--intensity)*var(--state,1))))}""",
    """.cgw .halo{z-index:2;opacity:min(1,calc(var(--core-b)*var(--intensity)*var(--state,1)));
  filter:drop-shadow(0 0 calc(var(--halo)*(1 - 0.75*var(--core-sharp))*var(--cgs,1)*1px) var(--core))
         drop-shadow(0 0 calc(var(--halo)*0.25*var(--core-sharp)*var(--cgs,1)*1px) var(--core))
         drop-shadow(0 0 calc(var(--halo)*0.25*var(--core-sharp)*var(--cgs,1)*1px) var(--core))
         drop-shadow(0 0 calc(var(--halo)*0.25*var(--core-sharp)*var(--cgs,1)*1px) var(--core))
         brightness(max(1,calc(var(--core-b)*var(--intensity)*var(--state,1))))}""",
    'halo scales')

# ── 2. the wrapper anchors to the art's ratio at the minimum projection ──
sub("""      /* the mask IS the card's own art */
      var img=e.el.querySelector('.fcvIn img')||e.el.querySelector('img');
      var src=img?(img.currentSrc||img.src):'';
      if(w._src!==src){w._src=src;w.style.setProperty('--card-src','url("'+src+'")');}
      /* geometry: the untransformed box at the element's screen centre,
         rotated to the fan (an AABB of a rotated card is inflated) */
      var cs2=getComputedStyle(e.el);
      var rot=parseFloat(cs2.rotate);if(isNaN(rot))rot=0;
      var scl=parseFloat(cs2.scale);if(!(scl>0))scl=1;
      /* computed width, not offsetWidth: the row sizes cards in cqw so
         the true width is fractional, and offsetWidth's truncation put
         the mask ~2px inside the art */
      var cw=(parseFloat(cs2.width)||e.el.offsetWidth)*scl,
          ch=(parseFloat(cs2.height)||e.el.offsetHeight)*scl;
      /* the row is a 3D stage (perspective + rotateX), so the PROJECTED
         card is ~2% bigger than its CSS size. Unrotated: the rect IS
         the projected box - exact. Fanned cards keep the computed size
         (their AABB is rotation-inflated); the <=2px keystone error
         hides under 5-17px of shadow. */
      if(!rot){cw=r.width;ch=r.height;}""",
    """      /* the mask IS the card's own art */
      var img=e.el.querySelector('.fcvIn img')||e.el.querySelector('img');
      var src=img?(img.currentSrc||img.src):'';
      if(w._src!==src){w._src=src;w.style.setProperty('--card-src','url("'+src+'")');}
      /* geometry: the untransformed box at the element's screen centre,
         rotated to the fan (an AABB of a rotated card is inflated) */
      var cs2=getComputedStyle(e.el);
      var rot=parseFloat(cs2.rotate);if(isNaN(rot))rot=0;
      var scl=parseFloat(cs2.scale);if(!(scl>0))scl=1;
      var cw=(parseFloat(cs2.width)||e.el.offsetWidth)*scl,
          ch=(parseFloat(cs2.height)||e.el.offsetHeight)*scl;
      /* P792: the rows are a perspective stage - the projected card is
         a TRAPEZOID, and a rect mask sized to its AABB overhangs the
         art at the narrow edge, detaching the rim (the grey outline
         Denis circled). Anchor to the art's true aspect at the MINIMUM
         projection: 0.99 x projected height x natural ratio sits just
         inside the card everywhere, the rim's shadows reach out tight
         against the edge - the reference's own composition. This also
         removes 'contain' letterboxing (the wrapper IS the art's
         shape). */
      if(!rot)ch=r.height;
      ch*=0.99;
      var _nat=(img&&img.naturalWidth>0)?(img.naturalWidth/img.naturalHeight):(cw/ch);
      cw=ch*_nat;
      /* P792: his dials are proportions of his 200px authoring card */
      w.style.setProperty('--cgs',(cw/200).toFixed(4));""",
    'art-ratio wrapper + cgs')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
