# -*- coding: utf-8 -*-
"""P618: every card carries its family's colour, so the activation cues can use it.

Denis asked for the activation glow and particles to take "the color of their
borders", and P617 wired all four cues to --card-accent, which IS the border.
Measured after that: only 18 card ids define one, against 30 family cards - so
most cards fell back to the deck gold and the family never reached the glow.

A CLASS, NOT AN INLINE STYLE. Setting --card-accent inline would win over the 18
hand-picked per-id rules and flatten deliberate choices (frozen_die's pale blue,
wild_die's violet) back to a family average. A `fam-*` class placed BEFORE those
rules gives the family colour as the default and lets any per-id override keep
winning, which is the ordering the cascade already expects.

The family colours are FAMILIES[fam].color, the same table the shelf focus panel
and the card art already read - so a card's border, its glow, its plume and its
family label cannot disagree.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

FAM = {'jade': '#2f9e5f', 'amber': '#d89a20', 'silver': '#b9c2cc',
       'obsidian': '#e2582f', 'starstone': '#4f74e3', 'vagabond': '#c4404f',
       'tavern': '#b09a72'}

# ── 1. the family default, ahead of the per-id overrides ──────────────────
anchor = u".mcard-active[data-cid=\"frozen_die\"]{--card-accent:rgba(100,180,220,.8);"
if s.count(anchor) != 1:
    sys.exit('per-id block anchor x%d' % s.count(anchor))

rules = [u"/* P618: THE FAMILY'S COLOUR AS THE DEFAULT ACCENT. --card-accent is the",
         u"   card's border, and P617 made the armed glow, the fire flash and the",
         u"   activation plume all read it - but only 18 ids defined one, so most",
         u"   cards glowed deck-gold regardless of family. These sit ABOVE the per-id",
         u"   rules on purpose: same specificity, so the id rules that follow still",
         u"   win and frozen_die keeps its pale blue. Colours are FAMILIES[fam].color",
         u"   verbatim, the table the shelf panel and the card art already read. */"]
for fam, col in FAM.items():
    rules.append(u".mcard.fam-%s{--card-accent:%s}" % (fam, col))
s = s.replace(anchor, u"\n".join(rules) + u"\n" + anchor)

# ── 2. put the class on the element ───────────────────────────────────────
old = (u"    const w=document.createElement('div');"
       u"w.className='mcard rarity-'+_mRar+(isActive?' mcard-active':'');w.dataset.cid=id;")
if s.count(old) != 1:
    sys.exit('buildCBar anchor x%d' % s.count(old))
new = (u"    /* P618: the family tag, so the card's own colour reaches every cue.\n"
       u"       famDef is the family-card table; a card outside it (an NPC or boss\n"
       u"       card) simply gets no fam- class and keeps the deck gold fallback. */\n"
       u"    var _fam='';try{var _fd=(typeof famDef==='function')?famDef(id):null;\n"
       u"      if(_fd&&_fd.fam)_fam=' fam-'+_fd.fam;}catch(e){}\n"
       u"    const w=document.createElement('div');"
       u"w.className='mcard rarity-'+_mRar+(isActive?' mcard-active':'')+_fam;w.dataset.cid=id;")
s = s.replace(old, new)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('P618 applied: %d family accents + the fam- class on every card' % len(FAM))
