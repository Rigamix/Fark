# -*- coding: utf-8 -*-
u"""Card audit pass 2: quantities written as WORDS, which pass 1 could not see.

Pass 1 compared digits in a card's text against digits in its effect and found
nothing. It classified 24 cards "NO NUMBERS" - but several of those state a
quantity in words:

  hold_the_line   "cannot bust during his FIRST TWO turns"
  sundays_rest    "cannot bust during the FIRST THREE turns"
  grogs_bump      "TWICE per match"
  point_of_order  "every 2ND turn"
  the_sermon      "every 4TH turn"

Same mechanic, different claimed durations, and a digit scan sees none of it.
That is pass 1's blind spot rather than a clean result, and it is exactly the
kind of gap that makes "24 need reading" hide a checkable subset.

WORDS AND ORDINALS ARE MAPPED TO NUMBERS and compared against the effect's own
fields - turns, uses, interval, count. A card claiming three turns of immunity
whose effect says turns:2 is a live mismatch of the same class as challenge
announcing 500 while taking 1000.

WHAT THIS STILL CANNOT CHECK: direction, ownership, and whether the effect does
the RIGHT thing with the right number. Those need reading. This only shrinks
the list.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# ORDINALS ARE NOT QUANTITIES. "first two turns" means TWO, not one-and-two -
# and including 'first' made hold_the_line read [1,2] against turns:2 and
# sundays_rest read [1,3] against turns:3, flagging both correct cards. The
# ordinals that ARE quantities keep their entries ('every 2nd turn' really does
# mean an interval of 2); the bare positional words do not.
WORD = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
        'once': 1, 'twice': 2, 'thrice': 3,
        '1st': 1, '2nd': 2, '3rd': 3, '4th': 4, '5th': 5, '6th': 6}

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

print('%-22s %-20s %-26s %-14s %s' % ('card', 'mechanic', 'words found', 'effect nums', 'verdict'))
print('-' * 104)
findings, checked, nowords = [], 0, 0
for cid in sorted(pools):
    obj = cards.get(cid)
    if not obj:
        continue
    em = re.search(r'effect\s*:\s*\{([^}]*)\}', obj)
    if not em:
        continue
    eff = em.group(1)
    mech = re.search(r"mechanic\s*:\s*'([a-z_0-9]+)'", eff)
    typ = re.search(r"type\s*:\s*'([a-z_0-9]+)'", eff)
    label = mech.group(1) if mech else (typ.group(1) if typ else '?')
    text = ' '.join(re.findall(r"(?:eff|desc)\s*:\s*[\"']([^\"']*)[\"']", obj)).lower()
    # only the count-ish fields; amount/penalty are money and were pass 1's job
    enums = set(int(x) for x in re.findall(r'(?:turns|uses|interval|count|max)\s*:\s*(\d+)', eff))
    words = sorted({WORD[w] for w in re.findall(r'\b([a-z0-9]+)\b', text) if w in WORD})
    if not words:
        nowords += 1
        continue
    checked += 1
    # "once per match" is a guard shape, not a tunable - only flag when the
    # effect HAS a count field to disagree with
    unmatched = [w for w in words if enums and w not in enums]
    v = 'ok' if (not enums or not unmatched) else 'CHECK'
    if v == 'CHECK':
        findings.append((cid, label, words, sorted(enums)))
    print('%-22s %-20s %-26s %-14s %s'
          % (cid, label, ','.join(map(str, words)),
             ','.join(map(str, sorted(enums))) or '-', v))

print('\n' + '=' * 104)
print('cards with word-quantities: %d   without: %d   NEEDING A LOOK: %d'
      % (checked, nowords, len(findings)))
for cid, label, w, e in findings:
    print('   %-22s %-20s text says %s, effect carries %s'
          % (cid, label, w, e or 'no count field'))
print("""
A card whose text and effect disagree on a COUNT is the same class as challenge
announcing 500 while taking 1000. A card with no count field in its effect is
not a finding - the number lives in the dispatch instead, and that needs reading.""")
