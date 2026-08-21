# -*- coding: utf-8 -*-
"""P851: patron hands mirror the player's, and every card in them can
actually be played.

Denis: "patrons should get cards earlier... If I have 3 cards or so
they should have similar (and the ability to play them)."

MEASURED FIRST (both halves):
  the player holds THREE family cards, flat, from night 2 to night 8 -
  S.run.fcards is hard-capped at 3 with no growth curve anywhere; only
  card TIER rises. Night 1 runs 0 -> 2 -> 3.
  the patron held 0.5 cards at nights 1-2 (half of them NONE), 1.3 at
  nights 3-5, 2.5 at nights 6-8 (200 patrons sampled per night).
  and 25-31% of every card they were dealt was an active the NPC seat
  can NEVER fire: famUse gates actor 'o' on NPC_FAM_READY, which holds
  7 of the 17 kind:'active' cards. The other ten are player-only UI
  (steady_hand and transmute paint rings and wait for a TAP), pool
  rewriters that would detonate the PLAYER's dice run for 'o'
  (powder_keg, sacrifice), passive-shaped (fools_gold_f has no use()
  at all), or run-scope economy cards (double_stakes, the_tab).

THE FIX, both halves together - raising the count alone would only
deal more inert cards:
  COUNT: night 1 -> 1, night 2 -> 2, nights 3+ -> 3. That tracks the
  player's own curve rather than lagging it by five nights.
  USABILITY: the draw pool only offers what a patron can use - any
  passive (they ride famFire seams and work for either seat), or an
  active in NPC_FAM_READY. Tavern cards leave the pool entirely: their
  domain is the RUN, not the table, so they are inert in a hand - the
  grudge pool already filtered them and the main pool did not, an
  asymmetry that looks unintended.
  PERSONA IS A BIAS, NOT A CEILING: amber/silver/obsidian have only
  2-3 usable cards each, and the draw loop is pool-bounded, so a
  3-card hand would silently under-deal. When the persona's own
  families run dry the draw widens to every usable family.

NOT DONE ON PURPOSE - the ten dead actives are NOT force-added to
NPC_FAM_READY. That registry is load-bearing, not merely unfinished:
CFX.tamper run for 'o' would break the NPC's OWN cards and pay the
PLAYER 300 (its target list is hard-coded to G.oF). Teaching the other
ten an actor branch is the scoped job in AUDIT_BACKLOG; this patch
stops dealing cards that job hasn't reached yet.

The night<5 "at most ONE active" telegraph cap is KEPT - early patrons
now hold a real hand of mostly passives, which is the intent of that
rule rather than a casualty of it.
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


# 1) the count, the usability filter, the widening pool
sub("""  var fams=_TRAIT_FAM[_gp.persona]||['silver'];
  if(night>=3&&Math.random()<0.15){ /* off-diagonal curveball */
    var all=Object.keys(FAMILIES);fams=[all[Math.floor(Math.random()*all.length)]];
  }
  var count=night<=2?(Math.random()<0.5?0:1):(night<=5?(Math.random()<0.4?2:1):(Math.random()<0.5?3:2));
  var pool=FAM_CARDS.filter(function(d){return _famDraftable(d)&&fams.indexOf(d.fam)>=0;});/* P588 */
  var fc=[];
  for(var ci=0;ci<count&&pool.length;ci++){
    var pick=pool.splice(Math.floor(Math.random()*pool.length),1)[0];""",
    """  var fams=_TRAIT_FAM[_gp.persona]||['silver'];
  if(night>=3&&Math.random()<0.15){ /* off-diagonal curveball */
    /* P851: never onto TAVERN - those are run-scope cards, inert in a
       hand. The grudge pool below already excluded them; this one did
       not, so ~2% of night-3+ patrons were handed a dead loadout. */
    var all=Object.keys(FAMILIES).filter(function(f){return f!=='tavern';});
    fams=[all[Math.floor(Math.random()*all.length)]];
  }
  /* P851: THE PATRON'S HAND MIRRORS THE PLAYER'S. Measured: the player
     holds THREE family cards flat from night 2 (S.run.fcards, hard cap
     3, no growth curve - only tier rises), while patrons held 0.5 at
     nights 1-2 (half of them none at all), 1.3 at nights 3-5 and 2.5
     at nights 6-8. Denis: "if I have 3 cards or so they should have
     similar". Night 1 stays light because the player's own night 1
     runs 0 -> 2. */
  var count=night<=1?1:(night<=2?2:3);
  /* P851: A CARD A PATRON CANNOT PLAY IS NOT A CARD. famUse gates
     actor 'o' on NPC_FAM_READY (7 of 17 actives); the other ten are
     player-only UI, player-pool rewriters, passive-shaped, or
     run-scope - measured at 25-31% of every hand dealt, at every
     night. Passives are fine for either seat: they ride famFire
     seams rather than famUse. */
  var _npcUsable=function(d){
    if(!d||d.fam==='tavern')return false;
    if(d.kind!=='active')return true;
    return !!(typeof NPC_FAM_READY!=='undefined'&&NPC_FAM_READY[d.id]);
  };
  var pool=FAM_CARDS.filter(function(d){return _famDraftable(d)&&_npcUsable(d)&&fams.indexOf(d.fam)>=0;});/* P588 */
  /* P851: PERSONA IS A BIAS, NOT A CEILING. amber/silver/obsidian carry
     only 2-3 usable cards each and this loop is pool-bounded, so a
     three-card hand used to silently under-deal. The persona's own
     families are drawn first; the rest of the usable set backs it. */
  var _wide=FAM_CARDS.filter(function(d){return _famDraftable(d)&&_npcUsable(d)&&fams.indexOf(d.fam)<0;});
  var fc=[];
  for(var ci=0;ci<count&&(pool.length||_wide.length);ci++){
    var _src=pool.length?pool:_wide;
    var pick=_src.splice(Math.floor(Math.random()*_src.length),1)[0];""",
    'count + usability + widening')

# 2) the grudge extra card obeys the same usability rule
sub("""      var gPool=FAM_CARDS.filter(function(d){return _famDraftable(d)&&d.fam!=='tavern';});/* P588 */""",
    """      var gPool=FAM_CARDS.filter(function(d){return _famDraftable(d)&&_npcUsable(d);});/* P588; P851: same usability rule as the main draw */""",
    'grudge pool usability')

# post-asserts
if 'var count=night<=1?1:(night<=2?2:3);' not in s:
    sys.exit('COUNT NOT WRITTEN (nothing written)')
for needed in ['_npcUsable', '_wide', "f!=='tavern'"]:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
if s.count('_npcUsable(d)') != 3:
    sys.exit('_npcUsable call count %d != 3 (nothing written)' % s.count('_npcUsable(d)'))

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
