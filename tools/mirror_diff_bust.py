# -*- coding: utf-8 -*-
"""The bust-path mirrors: do they agree, the way handleBank/finOpp did?

The bar for a table is REMOVES A COPY, not clears a branch count. By that bar
seven mechanics remain, each appearing in a player function AND an opponent one:

  bust_immune_turns, bust_survive   _tryBustSave  + step
  bust_bank_half                    doBust        + step
  gain_pts, punish_busts            doBust        + _oppBustOut
  single1_bonus, single5_bonus      scoreRoll     + step

Same pass that found the challenge double-charge, and that pass has now found
two real bugs and zero false positives once its own errors were cleared. Every
correction it needed is carried over rather than re-earned:

  PRESENTATION STRIPPED before reading numbers - setTimeout delays and spark
  counts are not rule parameters, and counting them reported 9 of 9 pairs
  disagreeing on the first run.
  GUARD SHAPE, not guard name - playerOnce vs usedOnce is which seat's
  bookkeeping, the same category as pPts vs oPts.
  THE CONDITION IS PART OF THE BRANCH - the first version read only the block,
  and the player's once-guard lives in the `if`.

AND A CLEAN SWEEP EITHER WAY IS THE TELL, not the finding. 7 of 7 agreeing is as
suspicious as 0 of 7: it would mean the instrument cannot separate these
functions at all. Anything unanimous gets read by hand before it is reported.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

def fnbody(name):
    for m in re.finditer(r'\bfunction\s+' + re.escape(name) + r'\s*\(', s):
        b = s.index('{', m.end() - 1)
        d, j = 0, b
        while j < len(s):
            if s[j] == '{':
                d += 1
            elif s[j] == '}':
                d -= 1
                if d == 0:
                    return s[b:j + 1]
            j += 1
    return ''

def branch(body, mech):
    """The if-block guarding this mechanic, PLUS its condition."""
    m = re.search(r"mechanic\s*===\s*'" + mech + r"'", body)
    if not m:
        return None
    # WALK BACK ONLY WITHIN THE SAME STATEMENT. rfind('if(') alone jumps over
    # any amount of unrelated code to the nearest earlier `if`, which returned
    # an endMatch call for bust_bank_half's player side and a relic-id list for
    # single1_bonus's. If a `;`, `{` or `}` sits between that `if` and the
    # mechanic test, the test is not in that condition and the block alone is
    # the branch.
    st = body.rfind('if(', 0, m.start())
    if st >= 0 and re.search(r'[;{}]', body[st:m.start()]):
        st = -1
    b = body.find('{', m.end())
    if b < 0:
        return None
    d, j = 0, b
    while j < len(body) and j - b < 3000:
        if body[j] == '{':
            d += 1
        elif body[j] == '}':
            d -= 1
            if d == 0:
                return body[st if st >= 0 else b:j + 1]
        j += 1
    return body[b:b + 600]

def facts(t):
    if t is None:
        return None
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    t = re.sub(r'setTimeout\s*\((?:[^()]|\([^()]*\))*\)', '', t)
    t = re.sub(r'\b(spawnPixelSparks|triggerCard|spawnPop|setStatusMsg|famLog|DLG\.\w+)'
               r'\s*\((?:[^()]|\([^()]*\))*\)', '', t)
    return {
        'eff_fields': ','.join(sorted(set(re.findall(r'effect\.(\w+)|eff\.(\w+)', t)[0] if False else
                                          re.findall(r'(?:eff|effect)\.(\w+)', t)))) or '-',
        'literals': ','.join(sorted(set(re.findall(r'(?<![\w.])(\d{2,4})(?![\w])', t)))[:4]) or '-',
        'guard': ('once' if re.search(r'usedOnce|playerOnce|firstBankDone', t)
                  else 'interval' if re.search(r'playerTurnCount|oppTurnCount|interval', t)
                  else 'none'),
        'capped': 'Math.min' in t or 'Math.max' in t,
    }

PAIRS = [
    ('bust_immune_turns', '_tryBustSave', 'step'),
    ('bust_survive',      '_tryBustSave', 'step'),
    ('bust_bank_half',    'doBust',       'step'),
    ('gain_pts',          'doBust',       '_oppBustOut'),
    ('punish_busts',      'doBust',       '_oppBustOut'),
    ('single1_bonus',     'scoreRoll',    'step'),
    ('single5_bonus',     'scoreRoll',    'step'),
]

cache = {}
def body(n):
    if n not in cache:
        cache[n] = fnbody(n)
    return cache[n]

print('%-20s %-14s %-12s %-7s %s' % ('mechanic', 'player fn', 'opp fn', 'agree?', 'what differs'))
print('-' * 88)
agree, differ, missing = [], [], []
for mech, pfn, ofn in PAIRS:
    pb, ob = body(pfn), body(ofn)
    if not pb or not ob:
        print('%-20s %-14s %-12s %-7s %s' % (mech, pfn, ofn, '-',
                                             'function not found: ' + (pfn if not pb else ofn)))
        missing.append(mech)
        continue
    a, b = facts(branch(pb, mech)), facts(branch(ob, mech))
    if a is None or b is None:
        side = pfn if a is None else ofn
        print('%-20s %-14s %-12s %-7s %s' % (mech, pfn, ofn, '-', 'branch absent in ' + side))
        missing.append(mech)
        continue
    d = [k for k in a if a[k] != b[k]]
    ok = not d
    print('%-20s %-14s %-12s %-7s %s' % (mech, pfn, ofn, 'YES' if ok else 'no',
          ', '.join('%s(%s|%s)' % (k, a[k], b[k]) for k in d)[:38] or '-'))
    (agree if ok else differ).append(mech)

print('\n' + '=' * 88)
print('AGREE:   %d - %s' % (len(agree), ', '.join(agree) or 'none'))
print('DIFFER:  %d - %s' % (len(differ), ', '.join(differ) or 'none'))
print('MISSING: %d - %s' % (len(missing), ', '.join(missing) or 'none'))
n = len(PAIRS) - len(missing)
if n and (len(agree) == n or len(differ) == n):
    print("""
UNANIMOUS - READ BEFORE REPORTING. A clean sweep either way is the shape an
instrument artifact makes, not a finding. 0-of-9 was wrong three times in the
handleBank pass before reading settled it.""")
