# -*- coding: utf-8 -*-
u"""P872 (Denis): patron surnames stop being one long pastoral compound each
and start telling you how the patron plays.

WHAT WAS THERE. Twenty-four family names, and every single one built the same
way - a nature word welded to a landscape feature:

  Thistledown Bramblewick Fernwhistle Mosscreek Tallowmere Hedgeburrow
  Cinderfell Oakhollow Greenmantle Ashgrove Silverbrook Nettlebank
  Longbarrow Willowmarsh Duskwater Honeyfield Emberlane Marrowgate ...

Denis: "all patrons have loooong last names built upon the same kinda vibe.
Change that, make it varied and more memorable, hinting at their
playstyle/personalities." All three complaints are the same root: one
generator, one shape, no information. Twelve syllables of scenery that could
belong to any patron at any seat.

WHAT THEY ARE NOW. The pool is split by PERSONA, and the panel already knows
which one it is looking at (st.pat.persona), so the surname can carry the
thing the player actually wants off this panel - how this seat plays:

  ones      STEADY    banks small and often, never pushes
  hoard     GREEDY    sits on a pile and will not spend it
  aggro     RECKLESS  rolls into anything
  triples   BULLISH   hunts three-of-a-kind
  straights ORDERLY   builds runs, tidy
  combo     CUNNING   plays the angles

VARIED IN SHAPE, not just in content, because that was half the complaint.
Slowhand and Magpie and Sleight are one word and short; Threadneedle and
Pennyweight are long; Deeppurse and Coldfoot and Bullneck are blunt compounds
of a different rhythm to the old ones. Nothing in the new set is
noun-plus-landscape. Foxglove survives out of the old twenty-four and moves to
CUNNING, where a poison that looks like a flower belongs.

DETERMINISM IS UNCHANGED. The existing hash of the given name still chooses,
it just indexes a smaller per-persona pool - so a patron's full name is as
stable as it ever was, and P837's "the same name is mechanically the same
patron every night" still holds. What changes is that the surname is now a
TRUE statement about them rather than decoration.

THE GIVEN NAMES AND THE ART ARE NOT TOUCHED, and that is not caution for its
own sake: `_art` is the portrait FILENAME - thirty files named Corbin_opt.webp,
Golgoth_opt.webp and so on - so renaming the given-name pool would blank every
patron's face. The surname layer is the one that can move freely.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

OLD = u"""  /* panel-only family name: the given name alone leaves the parchment
     empty. Deterministic per patron (hash of the given name). */
  var _FAMN=['Thistledown','Bramblewick','Copperpot','Underbough','Fernwhistle','Mosscreek',
    'Tallowmere','Hedgeburrow','Cinderfell','Oakhollow','Puddifoot','Greenmantle',
    'Ashgrove','Silverbrook','Nettlebank','Longbarrow','Foxglove','Willowmarsh',
    'Duskwater','Honeyfield','Stoutbarrel','Quickstitch','Emberlane','Marrowgate'];
  var _fh=0,_gn=String(st.name||'');
  for(var _fi=0;_fi<_gn.length;_fi++)_fh=(_fh*31+_gn.charCodeAt(_fi))>>>0;
  var _sn=_FAMN[_fh%_FAMN.length];"""

NEW = u"""  /* panel-only family name: the given name alone leaves the parchment empty.
     P872 (Denis: "loooong last names built upon the same kinda vibe... make it
     varied and more memorable, hinting at their playstyle/personalities"):
     THE SURNAME NOW SAYS HOW THEY PLAY. What stood here was twenty-four
     nature-plus-landscape compounds, all the same length, all the same
     construction, and true of nobody in particular. The
     panel already knows the persona, so the name can carry the one thing a
     player opens this panel to learn.
     Shapes are mixed on purpose, because "all the same vibe" was half the
     complaint: Magpie and Sleight and Slowhand are short, Threadneedle and
     Pennyweight are long, and none of them is noun-plus-scenery. */
  var _FAMN_BY_TRAIT={
    /* STEADY - banks small and often, never pushes */
    ones:['Slowhand','Tallyman','Pennyweight','Twicecount','Coldfoot'],
    /* GREEDY - sits on the pile and will not spend it */
    hoard:['Tightfist','Magpie','Deeppurse','Sockful','Neverlends'],
    /* RECKLESS - rolls into anything */
    aggro:['Neverblink','Breakneck','Hotblood','Onemore','Firebrand'],
    /* BULLISH - hunts three-of-a-kind */
    triples:['Threefold','Bullneck','Ironjaw','Thricelucky','Trebles'],
    /* ORDERLY - builds runs, keeps it tidy */
    straights:['Inarow','Straightlace','Dominoes','Ladderman','Onetosix'],
    /* CUNNING - plays the angles. Foxglove is the one survivor of the old
       twenty-four, and it lands here: a poison that looks like a flower. */
    combo:['Sleight','Sidewinder','Threadneedle','Foxglove','Everyangle']
  };
  var _fh=0,_gn=String(st.name||'');
  for(var _fi=0;_fi<_gn.length;_fi++)_fh=(_fh*31+_gn.charCodeAt(_fi))>>>0;
  /* the SAME hash as before, over a smaller per-persona pool - so a patron's
     full name stays as stable as it has always been (P837's identity ruling),
     it just means something now. Falls back to the steady set if a persona
     ever arrives that this table does not know, so an unknown key costs a
     flavour mismatch rather than an undefined surname. */
  var _fpool=(st.pat&&_FAMN_BY_TRAIT[st.pat.persona])||_FAMN_BY_TRAIT.ones;
  var _sn=_fpool[_fh%_fpool.length];"""

if s.count(OLD) != 1:
    pat = re.escape(OLD).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d (nothing written)' % len(ms))
    m = ms[0]
    rep = NEW.replace('\n', '\r\n') if '\r\n' in m.group(0) else NEW
    s = s[:m.start()] + rep + s[m.end():]
else:
    s = s.replace(OLD, NEW)

# ── post-asserts ─────────────────────────────────────────────────────
# The comment inserted above deliberately does NOT name the old surnames it
# replaces. This assert scans the game file, the comment goes INTO the game
# file, and naming them there makes the assert match itself - which it just
# did, for the seventh time today. The lesson has stopped being "be careful"
# and become "put the guard in sub()", which is the next patch's job.
if 'Thistledown' in s or 'Bramblewick' in s or 'Fernwhistle' in s:
    sys.exit('THE OLD PASTORAL POOL SURVIVES (nothing written)')
if s.count('_FAMN_BY_TRAIT=') != 1:
    sys.exit('the new table is not declared exactly once (nothing written)')
# one pool per persona, and the personas must be the ones the game actually uses
for k in ('ones', 'hoard', 'aggro', 'triples', 'straights', 'combo'):
    if not re.search(r'\b%s:\[' % k, s[s.index('_FAMN_BY_TRAIT='):s.index('var _fh=0,_gn=')]):
        sys.exit('persona %s has no surname pool (nothing written)' % k)
# every surname distinct across the whole table, or two seats can collide
_tbl = s[s.index('_FAMN_BY_TRAIT='):s.index('var _fh=0,_gn=')]
_names = re.findall(r"'([A-Za-z]+)'", _tbl)
if len(_names) != 30:
    sys.exit('expected 30 surnames, found %d (nothing written)' % len(_names))
if len(set(_names)) != 30:
    dupes = sorted(set(n for n in _names if _names.count(n) > 1))
    sys.exit('duplicate surnames %s (nothing written)' % dupes)
# and none of them may be a rebuild of the shape being retired
for n in _names:
    if len(n) > 12:
        sys.exit('%s is as long as the ones being replaced (nothing written)' % n)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: 24 pastoral compounds -> 30 playstyle surnames across 6 personas')
