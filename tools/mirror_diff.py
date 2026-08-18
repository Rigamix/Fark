# -*- coding: utf-8 -*-
"""handleBank vs finOpp: do the nine shared mechanics actually agree?

THE TARGET THE ORDERING CORRECTION POINTED AT. handleBank holds 10 dispatch
branches and finOpp holds 9, and they are the same mechanics twice - the
player's bank and the rival's bank. That is where a keyed table removes
something real: two copies stop being free to drift.

BUT A PAIR THAT HAS ALREADY DRIFTED IS A BUG FOUND, NOT AN OBSTACLE - and it
has to be FOUND rather than merged over. Merging two branches that quietly
disagree does not fix the disagreement; it picks one silently and deletes the
evidence. ill_omen was exactly this an hour ago: the player's copy read
"scored nothing" and the boss's read "busted", and nobody had decided that.

So before any table is written, each mechanic's branch is pulled from BOTH
functions and compared on the things that can differ without looking different:

  THRESHOLD    the number it tests against (eff.threshold, a literal, a tier)
  DIRECTION    who gains and who loses - pPts vs oPts, += vs -=
  GUARD        usedOnce / firstBankDone / interval - whether it can repeat
  CAP          whether a take is clamped to what the other side has

A pair agreeing on all four is a table row. A pair differing on any of them is
a question, and the answer is a ruling rather than a merge.

THIS DELIBERATELY DOES NOT DIFF THE TEXT. The two sides are written against
different variables by construction - one says G.pPts where the other says
G.oPts - so a textual diff reports every pair as different and tells you
nothing. What matters is whether they are the same RULE seen from two seats.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

def fnbody(name):
    m = re.search(r'\bfunction\s+' + name + r'\s*\(', s)
    if not m:
        return ''
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

PB = fnbody('handleBank')
# 2026-08-19: P470 EXTRACTED the rival's mechanic branches out of finOpp
# into named helpers so the sim could share them - scanning finOpp's body
# alone reported every mechanic 'one side only', which was the scanner's
# boundary lying, not the code diverging. The rival's scope is the flow
# shell PLUS its extractions.
OB = (fnbody('finOpp') + fnbody('_oppFxOwnA') + fnbody('_oppFxOwnB')
      + fnbody('_oppFxPlayer'))

def branch(body, mech):
    """The if-block guarding this mechanic."""
    m = re.search(r"mechanic\s*===\s*'" + mech + r"'", body)
    if not m:
        return None
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
                return body[b:j + 1]
        j += 1
    return body[b:b + 600]

def facts(t):
    if t is None:
        return None
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    # STRIP PRESENTATION BEFORE READING NUMBERS. The first run reported 9 of 9
    # pairs disagreeing - a clean sweep, which is where to stop rather than
    # report. steal_low_bank's "literals" on the bank side were 1200, 700 and
    # 800: setTimeout DELAYS and a spark count, not rule parameters. The tool
    # was counting animation timings as game values, which is the same category
    # as every other instrument bug here - measuring any 2-4 digit number
    # instead of the rule's actual arguments.
    t = re.sub(r'setTimeout\s*\((?:[^()]|\([^()]*\))*\)', '', t)
    t = re.sub(r'(spawnPixelSparks|triggerCard|spawnPop|setStatusMsg|famLog|DLG\.\w+)'
               r'\s*\((?:[^()]|\([^()]*\))*\)', '', t)
    return {
        'threshold': ','.join(sorted(set(re.findall(r'eff\.(threshold|amount|pct|interval|uses)', t)))) or '-',
        'literals': ','.join(sorted(set(re.findall(r'(?<![\w.])(\d{2,4})(?![\w])', t)))[:5] or '-'),
        'gainsP': bool(re.search(r'G\.pPts\s*=\s*\(?G\.pPts|G\.pPts\s*\+=', t)),
        'gainsO': bool(re.search(r'G\.oPts\s*=\s*\(?G\.oPts|G\.oPts\s*\+=', t)),
        # GUARD SHAPE, NOT GUARD NAME. The two sides keep SEPARATE once-flags by
        # necessity - npcCardState.playerOnce vs usedOnce is which seat's
        # bookkeeping, not a different rule, exactly like pPts vs oPts. Comparing
        # field names reported six disagreements that were mostly this. What can
        # actually differ is WHETHER it fires once, on an interval, or every time.
        'guard': ('once' if re.search(r'usedOnce|playerOnce|firstBankDone', t)
                  else 'interval' if re.search(r'playerTurnCount|interval', t)
                  else 'none'),
        'capped': 'Math.min' in t,
    }

MECHS = ['challenge', 'double_first_bank', 'flat_bonus', 'gain_when_ahead',
         'steal_pct', 'halve_first_bank', 'steal_low_bank', 'block_low_bank',
         'periodic_drain']

print('handleBank (player bank) vs finOpp (rival bank)\n')
print('%-19s %-9s %-9s %-7s %s' % ('mechanic', 'in bank', 'in opp', 'agree?', 'what differs'))
print('-' * 84)
agree, differ, missing = [], [], []
for mech in MECHS:
    a, b = facts(branch(PB, mech)), facts(branch(OB, mech))
    if a is None or b is None:
        print('%-19s %-9s %-9s %-7s %s' % (mech, 'yes' if a else 'NO', 'yes' if b else 'NO',
                                           '-', 'only on one side'))
        missing.append(mech)
        continue
    d = [k for k in a if a[k] != b[k]]
    # direction is EXPECTED to invert - that is the mirror, not a disagreement
    real = [k for k in d if k not in ('gainsP', 'gainsO')]
    ok = not real
    print('%-19s %-9s %-9s %-7s %s' % (mech, 'yes', 'yes', 'YES' if ok else 'no',
                                       ', '.join('%s(%s/%s)' % (k, a[k], b[k]) for k in real)[:34] or 'direction only'))
    (agree if ok else differ).append(mech)

print('\n' + '=' * 84)
print('AGREE (table rows):        %d - %s' % (len(agree), ', '.join(agree) or 'none'))
print('DIFFER (rulings, not merges): %d - %s' % (len(differ), ', '.join(differ) or 'none'))
print('ONE SIDE ONLY:             %d - %s' % (len(missing), ', '.join(missing) or 'none'))
print("""
Direction inverting (pPts vs oPts) is the MIRROR and is expected - it is what an
owner parameter carries. Anything else differing is two rules wearing one name,
and merging them would pick a winner silently.""")
