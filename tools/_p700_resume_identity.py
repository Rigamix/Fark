# -*- coding: utf-8 -*-
"""P700: a resumed patron keeps their face and their voice.

Denis: "when brought back into a match the patron lost their portrait image
and they might have lost their dialogues." Driven to the cause: the seat
identity is three window globals (_lastSeatArt / _lastSeatTrait /
_lastSeatColor). _matchDress paints the portrait from the first, the
personality dialogue pools read the first two ('patron:<art>:<moment>',
'trait:<trait>:<moment>'), the disc colour reads the third. ONLY launchSeat
stamped them - and with P693's guard the launcher returns into resumeMatch
before its stamping lines, while the boot resume never runs a launcher at
all. So every resumed match dressed a faceless, silent patron.

One stamper, three callers. The snapshot already carries everything needed:
snap.rung is the deep-cloned patron (_art + persona ride along), snap.seatIdx
and snap.sealRule are serialized. Nothing new enters the snapshot - no
two-writers hazard with _snapDiceOnly. Boss resumes take the null stamp
(P682's hygiene, now including the colour).
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# the helper, beside its principal caller
sub(u"/* P693: _confirmDiscardPending removed - launching over a pending match\n"
    u"   RESUMES it now, per Denis. Abandoning is Settings' job. */\n"
    u"function launchSeat(seatIdx){",
    u"/* P693: _confirmDiscardPending removed - launching over a pending match\n"
    u"   RESUMES it now, per Denis. Abandoning is Settings' job. */\n"
    u"/* P700: THE SEAT IDENTITY IS THREE WINDOW GLOBALS. _matchDress paints the\n"
    u"   portrait from _lastSeatArt, the personality pools read _lastSeatArt +\n"
    u"   _lastSeatTrait, the disc reads _lastSeatColor. One stamper, three\n"
    u"   callers (launchSeat, launchBossMatch, resumeMatch) - a resumed match\n"
    u"   used to skip all three writes and dressed a faceless, silent patron. */\n"
    u"function _stampSeatIdentity(patron,seatIdx,sealed,night){\n"
    u"  window._lastSeatArt=(patron&&patron._art)||null;\n"
    u"  window._lastSeatTrait=patron?(((typeof PT_TRAIT!=='undefined'&&PT_TRAIT[patron.persona])||'steady')):null;\n"
    u"  if(!patron){window._lastSeatColor=null;return;}\n"
    u"  /* the night offset is cosmetic seat-colour bookkeeping; a resume with\n"
    u"     the night gone falls back to the plain index and loses nothing */\n"
    u"  var off=(night&&typeof night.handicapSeat==='number'&&night.sealTell&&seatIdx>night.handicapSeat)?1:0;\n"
    u"  window._lastSeatColor=sealed?'purple':['green','blue','red'][((((seatIdx||0)-off)%3)+3)%3];\n"
    u"}\n"
    u"function launchSeat(seatIdx){",
    'P700 _stampSeatIdentity')

# launchSeat routes through it, behaviour identical
sub(u"  var patron=JSON.parse(JSON.stringify(night.roster[seatIdx]));\n"
    u"  window._lastSeatArt=patron._art||null;\n"
    u"  /* the trait seal, for the in-match reaction pool. Same field the peek sheet\n"
    u"     already draws its seal from, so nothing new is being tracked. */\n"
    u"  window._lastSeatTrait=(typeof PT_TRAIT!=='undefined'&&PT_TRAIT[patron.persona])||'steady';\n"
    u"  var isSealed=(seatIdx===night.handicapSeat)&&!!night.sealTell;\n"
    u"  window._lastSeatColor=isSealed?'purple'\n"
    u"    :['green','blue','red'][(seatIdx-((typeof night.handicapSeat==='number'&&night.sealTell&&seatIdx>night.handicapSeat)?1:0))%3];\n"
    u"  var sealRule=isSealed?night.sealTell:null;",
    u"  var patron=JSON.parse(JSON.stringify(night.roster[seatIdx]));\n"
    u"  var isSealed=(seatIdx===night.handicapSeat)&&!!night.sealTell;\n"
    u"  _stampSeatIdentity(patron,seatIdx,isSealed,night);/* P700: one stamper */\n"
    u"  var sealRule=isSealed?night.sealTell:null;",
    'P700 launchSeat routes through the stamper')

# the boss hygiene keeps its meaning, plus the colour
sub(u"  /* P682: the stale-seat hygiene half of the same fix */\n"
    u"  window._lastSeatArt=null;window._lastSeatTrait=null;",
    u"  /* P682: the stale-seat hygiene half of the same fix (P700 folded it\n"
    u"     into the one stamper, and the stale COLOUR now clears too) */\n"
    u"  _stampSeatIdentity(null,null,null,null);",
    'P700 boss stamps null')

# resume restamps from the snapshot, before the dress runs
sub(u"function resumeMatch(){\n"
    u"  var snap=S&&S.pendingMatch;if(!snap)return;\n"
    u"  SFX.nav();",
    u"function resumeMatch(){\n"
    u"  var snap=S&&S.pendingMatch;if(!snap)return;\n"
    u"  /* P700: restamp the identity the launcher never got to write - the\n"
    u"     snapshot's rung IS the deep-cloned patron, art and persona included.\n"
    u"     Boot, Settings, banner and both launch redirects all pass here. */\n"
    u"  try{\n"
    u"    if(snap.isBoss)_stampSeatIdentity(null,null,null,null);\n"
    u"    else _stampSeatIdentity(snap.rung,(snap.seatIdx!=null)?snap.seatIdx:0,!!snap.sealRule,null);\n"
    u"  }catch(e){}\n"
    u"  SFX.nav();",
    'P700 resume restamps')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
