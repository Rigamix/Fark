# -*- coding: utf-8 -*-
"""P840: the game-over FEATS stat counts real feats (Denis: "a
player-facing number that's just wrong" - pulled forward from the
architecture audit's rot list).

The split: _famFeats() granted own_reckoning and keg_triple through
raw ifs outside the FEATS roster and was the SOLE writer of
S.run._featsThisRun - the stat the game-over screen displays. All 23
mainline feats earned through evaluateFeats showed 0 there.

The fix, per the audit's fold note: both side-channel grants become
FEATS rows (same ids, so lifetime records and wall entries stay
valid); evaluateFeats becomes the one writer of the per-run stat;
_famFeats and its caller are deleted. SEMANTICS NOTE, stated: the two
migrated feats were lifetime-once; as roster rows they re-award
per run like every other feat - consistency chosen over the accident.
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
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# 1) the two grants become roster rows (same ids - lifetime records hold)
sub("""const FEATS=[
  /* ── JADE ── */""",
    """const FEATS=[
  /* ── P840: the two side-channel grants join the roster (they lived in
     _famFeats as raw ifs - no per-run dedup, no tab, and their counter
     was the ONLY thing the game-over FEATS stat read, so 23 mainline
     feats displayed as zero). Same ids: lifetime records and wall
     entries stay valid. Roster semantics now apply: per-run re-award,
     like every other feat. */
  {id:'own_reckoning',   label:'Own Reckoning',    desc:'Win a match under your own Reckoning sleeve', renown:30,
    check:function(G){return G._sleeve==='reckoning';}},
  {id:'keg_triple',      label:'Powder Trail',     desc:'A Powder Keg reroll lands a triple', renown:20,
    check:function(G){return !!G._famKegTriple;}},
  /* ── JADE ── */""",
    'the grants become rows')

# 2) evaluateFeats owns the per-run stat
sub("""  if(earned.length){_checkRenownPerks();save();}
  return earned;
}""",
    """  if(earned.length){
    /* P840: the ONE writer of the per-run count the game-over screen
       reads - _famFeats' side-channel counter made the stat show 2 of
       25 at best. */
    try{if(S.run)S.run._featsThisRun=(S.run._featsThisRun||0)+earned.length;}catch(e){}
    _checkRenownPerks();save();
  }
  return earned;
}""",
    'evaluateFeats owns the stat')

# 3) _famFeats dies with its caller
fi = s.find('function _famFeats(win){')
fe = s.find('function famFkTake(i){', fi)
if fi < 0 or fe < 0:
    sys.exit('_famFeats anchors missing')
s = s[:fi] + """/* P840: _famFeats is DELETED - its two grants are FEATS rows now and
   evaluateFeats writes the per-run stat. The side-channel was the whole
   reason the game-over FEATS number ignored the real roster. */
""" + s[fe:]
edits.append('_famFeats deleted')

sub("""  try{_famFeats(win);}catch(e){}""",
    """  /* P840: _famFeats retired - its feats ride evaluateFeats below */""",
    'the caller goes')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
