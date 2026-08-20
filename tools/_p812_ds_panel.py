# -*- coding: utf-8 -*-
"""P812: the room's seat panel shows Double Stakes.

Step 1c's adversarial probe measured the economy HONEST end to end:
unarmed buy 10 -> payout 30 (20 pot + 10 buy-in return); armed buy 20
-> payout 60. The flag reaches the match, the settle doubles, the pot
doubles. The one defect is display: the ROOM's seat panel (_ptSeats,
the surface Denis actually checks) never read _dsArmed, while the
gauntlet sheet (_gbPeek) did - the two-surfaces drift class. The
panel now reads the same flag with the same arithmetic as the settle.
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


sub("""  var n=S.run.night||{roster:[],seatsPlayed:[],results:[]};
  var buy=Math.min(S.run.gold||0,NIGHT_BUYINS[S.run.tier]||0);""",
    """  var n=S.run.night||{roster:[],seatsPlayed:[],results:[]};
  var buy=Math.min(S.run.gold||0,NIGHT_BUYINS[S.run.tier]||0);
  /* P812: the panel reads the SAME flag the settle reads - it showed
     undoubled numbers with Double Stakes armed (the _gbPeek sheet was
     right, this one drifted). Probe-measured: the economy itself was
     honest all along; only this surface lied. */
  var _ds=!!S.run._dsArmed;
  if(_ds)buy=Math.min(S.run.gold||0,(NIGHT_BUYINS[S.run.tier]||0)*2);""",
    'the panel reads the flag')

sub("""      price:buy,target:_seatTarget(pat),
      pot:(20+(S.run.tier||0)*12)*(sealed?2:1)+buy,""",
    """      price:buy,target:_seatTarget(pat),
      pot:(20+(S.run.tier||0)*12)*(sealed?2:1)*(_ds?2:1)+buy,/* P812 */""",
    'the pot doubles on the panel')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
