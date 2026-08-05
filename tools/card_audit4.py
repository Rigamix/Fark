# -*- coding: utf-8 -*-
u"""Card audit pass 4: the dice-movers. Scoped, and checked for refactor blindness FIRST.

Passes 1-3 cleared everything with a score-pool signature. What remains moves
DICE - rerolls, swaps, seizures, activation blocks - and has no `+=` to read.

THE CAUTION COMES FIRST, because pass 3 earned it. Three of its fifteen branches
were invisible to a checker built for the old shape, and all three were code
refactored earlier tonight: SCORE_DRAIN.periodic_drain and P467's challenge
rewrite. A correct refactor made the sign stop LOOKING like a sign.

So before reading anything, this asks: DO TONIGHT'S REFACTORS TOUCH THESE
BRANCHES? Specifically _lm* (lane markers), _rs*/RSX (run-scoped), the _oppFx*
extraction, and the BANK_FX / BUST_FX / BANK_TAKE / SCORE_DRAIN / WILD_LEVEL
tables. A branch that now routes through one of those cannot be read the way the
others were, and assuming otherwise is how pass 3 lost three sites.

THEN the reading list is grouped by what a card actually manipulates, because
"does it do what the text says" is a different question for each:

  DIE IDENTITY   steal_die, swap_die, swap_best_to_3 - which die, whose, to what
  DIE STATE      reroll_all_kept, reroll_scoring - which dice get rerolled
  ACTIVATION     block_activations, limit_activations, immune_modifiers
  VISIBILITY     hidden_cards - a UI effect with no state change at all

Nothing is asserted here. This is the scoping pass that says which cards need
reading and whether the usual way of reading them still works.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

REFACTORS = {
    '_lm* lane markers': r'_lm(?:Arm|Due|Spend|Retire)\s*\(',
    '_rs* run-scoped': r'_rs(?:Toggle|Armed|Take|Fire)\s*\(|RSX\[',
    '_oppFx* extraction': r'_oppFx(?:OwnA|OwnB|Player|Drain)\s*\(',
    'BANK_FX table': r'BANK_FX\.',
    'BUST_FX table': r'BUST_FX\.',
    'BANK_TAKE / SCORE_DRAIN': r'BANK_TAKE\.|SCORE_DRAIN\.',
    'WILD_LEVEL table': r'WILD_LEVEL\[',
    'famFire seam': r"famFire\('",
}

def branch_at(pos):
    b = s.find('{', pos)
    if b < 0:
        return ''
    d, j = 0, b
    while j < len(s) and j - b < 2500:
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[b:j + 1]
        j += 1
    return s[b:b + 600]

pools = set()
for pm in re.finditer(r'cardPool\s*:\s*\[([^\]]*)\]', s):
    pools |= set(re.findall(r"'([a-z_0-9]+)'", pm.group(1)))

am = re.search(r'(?:var|let|const)\s+NPC_CARDS\s*=\s*\[', s)
b = s.index('[', am.end() - 1)
d, j = 0, b
while j < len(s):
    if s[j] == '[':
        d += 1
    elif s[j] == ']':
        d -= 1
        if d == 0:
            break
    j += 1
arr = s[b:j + 1]
cards = {}
i = 0
while i < len(arr):
    if arr[i] == '{':
        d2, k = 0, i
        while k < len(arr):
            if arr[k] == '{':
                d2 += 1
            elif arr[k] == '}':
                d2 -= 1
                if d2 == 0:
                    break
            k += 1
        m = re.match(r"\{\s*id\s*:\s*'([a-z_0-9]+)'", arr[i:k + 1])
        if m:
            cards[m.group(1)] = arr[i:k + 1]
        i = k + 1
    else:
        i += 1

# mechanics of pooled cards that move no points
score_mechs = set()
dice_mechs = collections.defaultdict(list)
for cid in sorted(pools):
    o = cards.get(cid)
    if not o:
        continue
    em = re.search(r'effect\s*:\s*\{([^}]*)\}', o)
    if not em:
        continue
    mech = re.search(r"mechanic\s*:\s*'([a-z_0-9]+)'", em.group(1))
    if not mech:
        continue
    mech = mech.group(1)
    bodies = [re.sub(r'/\*.*?\*/', '', branch_at(mm.end()), flags=re.S)
              for mm in re.finditer(r"mechanic\s*===\s*'" + mech + r"'", s)]
    if any(re.search(r'G\.[po]Pts', bd) for bd in bodies):
        score_mechs.add(mech)
    else:
        txt = ' '.join(re.findall(r"(?:eff)\s*:\s*[\"']([^\"']*)[\"']", o))
        dice_mechs[mech].append((cid, txt))

print('DICE-MOVING MECHANICS (no score-pool signature): %d, across %d cards\n'
      % (len(dice_mechs), sum(len(v) for v in dice_mechs.values())))

print('REFACTOR EXPOSURE - does tonight\'s work run inside these branches?')
print('%-20s %-6s %s' % ('mechanic', 'sites', 'touched by'))
print('-' * 76)
exposed = 0
for mech in sorted(dice_mechs):
    bodies = [re.sub(r'/\*.*?\*/', '', branch_at(mm.end()), flags=re.S)
              for mm in re.finditer(r"mechanic\s*===\s*'" + mech + r"'", s)]
    hits = sorted({name for name, pat in REFACTORS.items()
                   for bd in bodies if re.search(pat, bd)})
    if hits:
        exposed += 1
    print('%-20s %-6d %s' % (mech, len(bodies), ', '.join(hits) or '-'))

print('\n%d of %d dice mechanics route through tonight\'s refactors.' % (exposed, len(dice_mechs)))
print('\nTHE READING LIST, grouped by what the card manipulates:')
GROUPS = {
    'die identity': ['steal_die', 'swap_die', 'swap_best_to_3'],
    'die state': ['reroll_all_kept', 'reroll_scoring', 'reduce_first_roll'],
    'activation': ['block_activations', 'limit_activations', 'immune_modifiers'],
    'visibility': ['hidden_cards'],
}
placed = set()
for g, ms in GROUPS.items():
    rows = [(m, c, t) for m in ms for c, t in dice_mechs.get(m, [])]
    if not rows:
        continue
    print('\n  %s' % g.upper())
    for m, c, t in rows:
        placed.add(m)
        print('     %-18s %-22s %s' % (m, c, t[:44].encode('ascii', 'replace').decode()))
rest = [m for m in dice_mechs if m not in placed]
if rest:
    print('\n  UNGROUPED - need a category before they need a read')
    for m in rest:
        for c, t in dice_mechs[m]:
            print('     %-18s %-22s %s' % (m, c, t[:44].encode('ascii', 'replace').decode()))
