# -*- coding: utf-8 -*-
u"""The last two ungated seams: commit and deadRoll, scoped together.

Now that patrons hold cards (P473), these two matter for the first time - a
boss with a card that wants a commit moment previously had no card AND no
moment. Scoping them together because they share that precondition.

SIX OF EIGHT OPPONENT SEAMS ALREADY RAISE: turnStart and roll (P459), bust and
bankBonus (P461), rivalTurn (P462), plus the player-side raises throughout.
These are the two left.

WHAT THIS MEASURES, per seam, and it is NOT "how many sites":

  THE PAYLOAD    what the player-side raise carries. A seam is only mirrorable
                 if the opponent's turn can produce the same value - endPTurn
                 needed a turn score that did not exist, and that was the whole
                 blocker until P462 threaded one.
  THE MOMENT     whether a single canonical instant exists on the opponent's
                 side, the way oppTurnCount++ was for turnStart.
  THE CONSUMERS  which CFX handlers would start firing, and whether they gate
                 on _fxMine - because a seam that ungates a card is a behaviour
                 change, not a seam.

The third is the one that decides whether raising is safe on its own. Every
seam raised so far deliberately ungated NOTHING: the hooks still test _fxMine
and return early for an opponent owner. If a handler does not, raising the seam
ships a boss card by accident.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

def line_of(pos):
    return s[:pos].count('\n') + 1

def enclosing_fn(pos):
    best, span = None, None
    for m in re.finditer(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(', s):
        b = s.find('{', m.end() - 1)
        if b < 0:
            continue
        d, j = 0, b
        while j < len(s):
            if s[j] == '{':
                d += 1
            elif s[j] == '}':
                d -= 1
                if d == 0:
                    break
            j += 1
        if b <= pos <= j and (span is None or j - b < span):
            best, span = m.group(1), j - b
    return best

print('%-10s %-8s %-18s %s' % ('seam', 'line', 'raised inside', 'payload'))
print('-' * 78)
info = {}
for hook in ['commit', 'deadRoll']:
    m = re.search(r"famFire\('" + hook + r"',\s*(\w+)", s)
    if not m:
        print('%-10s NOT RAISED' % hook)
        continue
    var = m.group(1)
    fn = enclosing_fn(m.start())
    # what the event object carries
    dm = re.search(r'(?:var|let|const)\s+' + var + r'\s*=\s*\{([^}]*)\}', s)
    payload = re.sub(r'\s+', ' ', dm.group(1))[:46] if dm else '?'
    print('%-10s %-8d %-18s %s' % (hook, line_of(m.start()), fn or '?', payload))
    info[hook] = {'fn': fn, 'var': var, 'payload': payload}

print('\nCONSUMERS - do they gate on _fxMine?')
for hook in ['commit', 'deadRoll']:
    print('  %s:' % hook)
    for m in re.finditer(r'\b' + hook + r':\s*function\s*\(([^)]*)\)\s*\{', s):
        b = s.index('{', m.end() - 1)
        d, j = 0, b
        while j < len(s):
            if s[j] == '{':
                d += 1
            elif s[j] == '}':
                d -= 1
                if d == 0:
                    break
            j += 1
        body = s[b:j + 1]
        head = s[max(0, m.start() - 260):m.start()]
        owner = re.findall(r'CFX\.(\w+)\s*=', head)
        gated = '_fxMine' in body
        print('     %-18s %s' % (owner[-1] if owner else '?',
                                 'gates on _fxMine' if gated else '*** UNGATED - would fire for a boss ***'))

print('\nTHE OPPONENT SIDE - does an equivalent moment exist?')
opp = None
m = re.search(r'\bfunction\s+runOppTurn\s*\(', s)
if m:
    b = s.index('{', m.end() - 1)
    d, j = 0, b
    while j < len(s):
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                break
        j += 1
    opp = s[b:j + 1]
for hook, pat, what in [
        ('commit',   r'oppBank\s*\+=|bank\s*\+=\s*total', 'the rival adding a scored group to its bank'),
        ('deadRoll', r'out\.busted\s*=\s*true|!total\|\|total<=0', 'the rival rolling nothing')]:
    hits = [(opp[:mm.start()].count('\n') + 1, re.sub(r'\s+', ' ', opp.split('\n')[opp[:mm.start()].count('\n')]).strip()[:58])
            for mm in re.finditer(pat, opp)] if opp else []
    print('  %-10s %-2d candidate site(s)  (%s)' % (hook, len(hits), what))
    for ln, tx in hits[:3]:
        print('        +%-5d %s' % (ln, tx.encode('ascii', 'replace').decode()))

print("""
READ THE CONSUMER COLUMN FIRST. A seam whose handlers all gate on _fxMine can be
raised on its own and changes nothing - that is how the other six shipped. One
that does not gate would ship a boss card the moment the seam fires, which is a
design decision wearing a plumbing patch.""")
