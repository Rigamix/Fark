# -*- coding: utf-8 -*-
"""P818: bosses speak - the two-patch contradiction resolved.

Denis (playthrough notes): "No dialogue during his [Grog's] match."
Recon traced a three-layer silence:
  1. OPP_DIALOGUE was deliberately emptied (the ~450 bespoke barks
     moved to the PATRON_LINES lore resolver) - so original getLine's
     first guard `if(!data)return null` nulls for EVERY opponent.
  2. P682 added a boss BYPASS in the lore wrapper that routes bosses
     AROUND the resolver straight into that guaranteed null - directly
     contradicting the older comment five lines below it ("excluding
     bosses would leave them mute").
  3. Bosses get no seat identity (_stampSeatIdentity(null x4) in
     launchBossMatch and resumeMatch), so even past the bypass the
     moment/personal branches key on nulls.
Collateral of guard 1: LEDGER_LINES ("the regulars remember" record
greetings, all 8 bosses) and PATRON_CLASS_LINES sit AFTER the guard -
dead code for everyone.

The cuts:
  a. BOSS_TRAIT map (rung key -> lore trait) beside PT_TRAIT.
  b. _stampSeatIdentity takes a 5th arg: a boss rung stamps its TRAIT
     while art/colour stay null - the P682 stale-patron leak stays
     fixed (personal arcs remain closed to bosses; only the trait
     pools + ambient open up).
  c. launchBossMatch stamps AFTER the boss is derived; resumeMatch's
     isBoss branch passes snap.rung (the deep-cloned boss).
  d. The P682 bypass is deleted.
  e. getLine's guard becomes `||{}` - `if(!data[cat])return null`
     downstream already handles every missing category, and the
     ledger/class branches revive.
DLG.triggerCard stays dead (its pools were content, deleted on
purpose) - OPEN.md carries that and the no-first-meeting-line gap.
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


# a) the trait map, beside PT_TRAIT
sub("""var PT_TRAIT={ones:'steady',hoard:'greedy',aggro:'reckless',triples:'strong',straights:'orderly',combo:'cunning'};""",
    """var PT_TRAIT={ones:'steady',hoard:'greedy',aggro:'reckless',triples:'strong',straights:'orderly',combo:'cunning'};
/* P818: the bosses' lore voice, keyed by rung archetype. Chosen from the
   rung identities (drunkard/soldier/merchant...), flagged in OPEN.md for
   remap if Denis reads any of them differently. */
var BOSS_TRAIT={drunkard:'reckless',peasant:'steady',commoner:'cunning',merchant:'greedy',soldier:'strong',knight:'orderly',noble:'cunning',bishop:'orderly'};""",
    'BOSS_TRAIT map')

# b) the stamper learns bosses
sub("""function _stampSeatIdentity(patron,seatIdx,sealed,night){
  window._lastSeatArt=(patron&&patron._art)||null;
  window._lastSeatTrait=patron?(((typeof PT_TRAIT!=='undefined'&&PT_TRAIT[patron.persona])||'steady')):null;
  if(!patron){window._lastSeatColor=null;return;}""",
    """function _stampSeatIdentity(patron,seatIdx,sealed,night,bossRung){
  window._lastSeatArt=(patron&&patron._art)||null;
  /* P818: a BOSS stamps its TRAIT (BOSS_TRAIT by rung key) while art and
     colour stay null - the personal patron arcs stay closed to bosses
     (the exact leak P682 fixed), but the trait moment pools and the
     ambient line open up. */
  window._lastSeatTrait=patron?(((typeof PT_TRAIT!=='undefined'&&PT_TRAIT[patron.persona])||'steady'))
    :((bossRung&&typeof BOSS_TRAIT!=='undefined'&&BOSS_TRAIT[bossRung.key])||null);
  if(!patron){window._lastSeatColor=null;return;}""",
    'stamper takes a boss rung')

# c1) launchBossMatch: stamp after the boss is known
sub("""  /* P682: the stale-seat hygiene half of the same fix (P700 folded it
     into the one stamper, and the stale COLOUR now clears too) */
  _stampSeatIdentity(null,null,null,null);
  var tier=TIERS[S.run.tier]||TIERS[0];
  var boss=tier.boss;""",
    """  /* P682: the stale-seat hygiene half of the same fix (P700 folded it
     into the one stamper, and the stale COLOUR now clears too).
     P818: the stamp moved below the boss lookup so the trait rides in. */
  var tier=TIERS[S.run.tier]||TIERS[0];
  var boss=tier.boss;
  _stampSeatIdentity(null,null,null,null,boss);""",
    'launch stamps the boss trait')

# c2) resumeMatch: the snapshot's rung IS the boss
sub("""    if(snap.isBoss)_stampSeatIdentity(null,null,null,null);""",
    """    if(snap.isBoss)_stampSeatIdentity(null,null,null,null,snap.rung);/* P818 */""",
    'resume stamps the boss trait')

# d) the bypass dies
sub("""      if(typeof G!=='undefined'&&G&&G._isBoss)return _orig(cat);""",
    """      /* P818: the P682 boss bypass is DELETED. It routed bosses around
         this resolver into original getLine, whose first guard nulls on
         the emptied OPP_DIALOGUE - the comment below already named the
         hazard ("excluding bosses would leave them mute"). The leak P682
         fixed is closed at its source: bosses stamp art=null, so the
         personal branch cannot advance an absent patron's arc. */""",
    'boss bypass deleted')

# e) the guard stops killing the ledger branches
sub("""    getLine(cat){const data=OPP_DIALOGUE[this.oppKey];if(!data)return null;""",
    """    getLine(cat){const data=OPP_DIALOGUE[this.oppKey]||{};/* P818: the
      emptied bark store no longer kills the LEDGER_LINES and class-line
      branches below - `if(!data[cat])return null` already covers every
      missing category. */""",
    'getLine guard softened')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
