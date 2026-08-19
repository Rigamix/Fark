# -*- coding: utf-8 -*-
"""P775: a new run discards the old run's unfinished match.

Denis (2026-08-19): "The save system is broken... It keeps bringing me
back to Grog match even when I start a new run and select a random
patron."

The chain: S.pendingMatch lives on S, NOT on S.run - so startNewRun()
(fresh S.run, fresh npcState) left the dead run's mid-match snapshot
alive. Both NEW RUN buttons (_hsNewRunTap title path, _gbNewRun tavern
modal) route through startNewRun, and launchSeat/launchBossMatch open
with the P693 resume gate:

    if(S&&S.pendingMatch&&!window._fkDiscardOk){resumeMatch();return;}

so the first seat picked in the NEW run teleported back to the OLD
run's snapshot. _fkDiscardOk has no writer anywhere (the comment says
the deliberate-abandon path sets it; abandonMatch actually deletes the
snapshot instead), so nothing could break the loop except finishing or
Settings-abandoning the stale match.

No heart charge on this discard: the boss-abandon charge exists so a
force-close couldn't dodge run death, but here the player is throwing
the ENTIRE run away - hearts included. There is nothing left to
protect.
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


sub("""function startNewRun(){
  S.run=_freshRun();""",
    """function startNewRun(){
  /* P775: A NEW RUN DISCARDS THE OLD RUN'S UNFINISHED MATCH. The snapshot
     lives on S, not S.run, so it survived _freshRun() - and the P693
     resume gate in launchSeat/launchBossMatch outranks every launch, so
     the first seat picked in the new run teleported back to the dead
     run's match. No heart charge: the run that would pay is the one
     being thrown away whole. */
  if(S&&S.pendingMatch)delete S.pendingMatch;
  S.run=_freshRun();""",
    'new run discards the snapshot')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
