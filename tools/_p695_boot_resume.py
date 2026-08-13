# -*- coding: utf-8 -*-
"""P695: opening the game lands you back at your table.

Denis: "when I open the game again bring me back to the match I was on rather
than the main menu? So I don't have to click anything."

The bootstrap chooses the menu unconditionally; with a pending match it now
resumes straight into it - the same resumeMatch the Settings button and the
P692 banner call, so there is one resume path, not three. The menu fallback
stays for a resume that throws, and for everyone with no match waiting
nothing changes. (Audio still waits for the first tap - autoplay rules -
which is already how every session starts.)
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = (u"  _getS();\n"
       u"  try{showScreen('menu');}catch(e){console.error('showScreen failed:',e);}")
new = (u"  _getS();\n"
       u"  /* P695: a waiting match outranks the menu - open the app, be at the\n"
       u"     table (Denis: \"so I don't have to click anything\"). One resume path:\n"
       u"     the same resumeMatch Settings and the room banner use. */\n"
       u"  var _booted=false;\n"
       u"  if(S&&S.pendingMatch){\n"
       u"    try{resumeMatch();_booted=true;}catch(e){console.error('boot resume failed:',e);}\n"
       u"  }\n"
       u"  if(!_booted){try{showScreen('menu');}catch(e){console.error('showScreen failed:',e);}}")
c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)' % c)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('  ok  P695 boot resumes')
