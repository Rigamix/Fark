/* P548: EMPTY ON PURPOSE.

   This held painted sheets for bone and amber, remapped for the old model's 16%
   bevel ("flat face is 87.0% of each island"). Two things retired them:

   1. The die is a hard cube now, so art baked for a bevel paints at 87% of each
      face with the bevel gradient showing as a flat frame around it.
   2. Denis's ruling: the blank Bone/texture set is the ONLY die art, and every
      other material is that art plus a tint.

   Leaving them in was not neutral. _dress hard-replaces m.map with sk.map for
   any material that has a skin, which silently swapped the code-drawn pips back
   out for the old painted ones - measured: bone and amber sampled (91,72,56) and
   (131,47,12) at the pip centre while the other four read pure black.

   Kept as an empty table rather than deleted: _skinFor and _dress both still
   read it, and it is the right hook if a material ever gets bespoke art again. */
window.FK_DIE_SKINS={};
