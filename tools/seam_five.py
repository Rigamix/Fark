# -*- coding: utf-8 -*-
"""The five remaining seams, sized one at a time.

Two are shipped (roll, turnStart). Five remain: bankBonus, bust, commit,
deadRoll, rivalTurn. This area has had two wrong size estimates already, so
this measures per seam rather than producing a third guess.

THE QUESTION PER SEAM is not "how many sites" - that was the last pass, and it
gave SPREAD for three of them, which only says "a decision is needed". The
question now is what KIND of work each needs:

  GATE      a canonical moment exists, like `oppTurnCount++` was for turnStart.
            One call, same as the two already shipped.
  DECISION  several candidate moments and no obvious canonical one. Someone has
            to choose which instant IS the seam. Code is small; the choice is
            not.
  BEHAVIOUR the opponent's turn has no counterpart at all. Raising it needs the
            NPC to become capable of something it currently cannot do - not a
            hook, a decision it can make.

The test for a canonical moment: does exactly one site sit on the counter or
state-change the seam is ABOUT, the way `G.oppTurnCount=...+1` did? A seam whose
sites are all consumers rather than the event itself has no canonical moment.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

def span(name):
    m = re.search(r'\nfunction ' + name + r'\s*\(', s)
    if not m:
        return None
    b = s.index('{', m.end() - 1)
    d, j = 0, b
    while j < len(s):
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[b:j + 1], s[:b].count('\n') + 1
        j += 1
    return None

opp, oppbase = span('runOppTurn')
lines = opp.count('\n') + 1

# per seam: the EVENT pattern (the thing happening) vs mere consumers
SEAMS = [
    ('bust', r'finOpp\(0\)|oppBust|_oppBusted|bustOpp',
     'the rival losing its turn score'),
    ('commit', r'oppBank\s*\+=|scoreRoll\(',
     'the rival committing dice'),
    ('bankBonus', r'_npcActuallyBanked\s*=\s*true',
     'the rival banking, bonus applied'),
    ('deadRoll', r'anyScoring\(',
     'the rival rolling nothing'),
]
print('runOppTurn: %d lines\n' % lines)
print('%-11s %-6s %s' % ('seam', 'sites', 'the event, if it has one'))
print('-' * 72)
verdict = {}
for name, pat, what in SEAMS:
    hits = [(opp[:m.start()].count('\n') + 1, opp.split('\n')[opp[:m.start()].count('\n')].strip()[:52])
            for m in re.finditer(pat, opp)]
    print('%-11s %-6d %s' % (name, len(hits), what))
    for ln, txt in hits[:4]:
        print('              %-5d %s' % (ln, txt))
    if not hits:
        verdict[name] = 'BEHAVIOUR - no counterpart in the rival turn'
    elif len(hits) == 1:
        verdict[name] = 'GATE - one canonical site'
    else:
        verdict[name] = 'DECISION - %d candidate moments, none canonical' % len(hits)
    print()

# rivalTurn is not a runOppTurn seam at all - for an opponent-held card the
# "rival" is the PLAYER, so its moment is the player's turn ending
pt = span('endPTurn')
rt_here = len(re.findall(r"famFire\('rivalTurn'", s))
verdict['rivalTurn'] = ('BEHAVIOUR - inverts: for a boss-held card the "rival" '
                        'is the PLAYER, so its moment is endPTurn, not '
                        'runOppTurn. Already raised there once (actor p).')

print('=' * 72)
for k in ['bust', 'commit', 'bankBonus', 'deadRoll', 'rivalTurn']:
    print('  %-11s %s' % (k, verdict[k]))
print("""
GATE = one call, same as the two shipped. DECISION = small code, real choice
about which instant is the seam, and it is the seatCommit question again.
BEHAVIOUR = the NPC has to become capable of something it currently cannot do.""")
