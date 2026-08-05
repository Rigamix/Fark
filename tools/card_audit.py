# -*- coding: utf-8 -*-
u"""The patron card audit: does each card DO what its own text claims?

41 cards went from provably-inert to live in one commit (P473). The measured
difficulty delta says they work IN AGGREGATE - win rate down consistently, tier
0 pinned at zero. An aggregate moving correctly is compatible with several
individual cards being silently wrong in ways that cancel out or are too small
to show. None has been verified on its own.

THIS PASS TAKES THE SHARPEST AUTOMATABLE SLICE, which is the shape that has bitten
twice tonight: THE NUMBERS IN A CARD'S TEXT VERSUS THE NUMBERS ITS EFFECT USES.
`challenge` printed LOST 500 while taking up to 1000; the boss's gain_pts message
read its number from a second copy of the expression. Both were correct-looking
text beside a wrong value, and both survived because nobody compared the two.

FOUR CLASSES REPORTED, and only the first is mechanically decidable:

  MISMATCH   a number appears in the text and NOT in the effect object. Either
             the text is stale or the effect is - both are real bugs.
  NO NUMBERS the text promises no quantity. Nothing to check here; it needs
             reading, and it is listed rather than silently passed.
  NO EFFECT  the card has no effect object at all. It cannot act.
  UNWIRED    the effect's mechanic/type has no dispatch anywhere. It resolves
             and does nothing - the failure that looks like a boss playing badly.

WHAT THIS DOES NOT CLAIM. Matching numbers does not mean the card is correct: a
card can use its stated amount in entirely the wrong direction. This narrows 41
cards to the ones worth reading, it does not replace reading them.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# ── the pooled cards ──
pools = set()
for pm in re.finditer(r'cardPool\s*:\s*\[([^\]]*)\]', s):
    pools |= set(re.findall(r"'([a-z_0-9]+)'", pm.group(1)))

# ── per-card objects out of NPC_CARDS ──
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
        obj = arr[i:k + 1]
        m = re.match(r"\{\s*id\s*:\s*'([a-z_0-9]+)'", obj)
        if m:
            cards[m.group(1)] = obj
        i = k + 1
    else:
        i += 1

dispatched = set(re.findall(r"mechanic\s*===\s*'([a-z_0-9]+)'", s))
dispatched |= set(re.findall(r"type\s*===\s*'([a-z_0-9]+)'", s))
by_id = set(re.findall(r"(?:includes|indexOf)\('([a-z_0-9]+)'\)", s))

def nums(t):
    # STRIP THOUSANDS SEPARATORS FIRST. The card text writes "1,200" and
    # "4,500"; a bare 2-6 digit match splits those into 200 and 500, and
    # "2,000" into 000 -> 0. That reported SIX mismatches, every one the comma.
    #
    # AND THE FIRST FIX DID NOT WORK, which is the part worth recording. It went
    # through a bash heredoc and the `\b` in `\d{3}\b` was written as a LITERAL
    # BACKSPACE BYTE. The pattern became (?=\d{3}<BS>) - prints looking correct,
    # matches nothing, and leaves the false findings in place while appearing
    # repaired. Identical to until_audit.py earlier in this session, which
    # invented eight false findings the same way.
    #
    # Now a plain .replace with no escapes at all, so there is nothing for a
    # quoting layer to corrupt.
    t = t.replace(',', '')
    return set(int(x) for x in re.findall(r'(?<![\w.])(\d{2,6})(?![\w%])', t))

rows = []
for cid in sorted(pools):
    obj = cards.get(cid)
    if obj is None:
        rows.append((cid, 'NO OBJECT', '', '', ''))
        continue
    em = re.search(r'effect\s*:\s*\{([^}]*)\}', obj)
    if not em:
        rows.append((cid, 'NO EFFECT', '', '', ''))
        continue
    eff = em.group(1)
    mech = (re.search(r"mechanic\s*:\s*'([a-z_0-9]+)'", eff) or [None, None])[1] \
        if re.search(r"mechanic\s*:\s*'([a-z_0-9]+)'", eff) else None
    typ = (re.search(r"type\s*:\s*'([a-z_0-9]+)'", eff).group(1)
           if re.search(r"type\s*:\s*'([a-z_0-9]+)'", eff) else None)
    wired = (mech in dispatched) or (typ in dispatched) or (cid in by_id)
    # text vs effect numbers
    text = ' '.join(re.findall(r"(?:eff|desc|playerDesc)\s*:\s*[\"']([^\"']*)[\"']", obj))
    tn, en = nums(text), nums(eff)
    unbacked = sorted(tn - en)
    rows.append((cid, 'UNWIRED' if not wired else ('NO NUMBERS' if not tn else
                 ('MISMATCH' if unbacked else 'ok')),
                 mech or typ or '?', ','.join(map(str, sorted(tn))) or '-',
                 ','.join(map(str, unbacked)) or '-'))

order = {'UNWIRED': 0, 'NO EFFECT': 1, 'NO OBJECT': 2, 'MISMATCH': 3, 'NO NUMBERS': 4, 'ok': 5}
rows.sort(key=lambda r: (order.get(r[1], 9), r[0]))

print('%-22s %-11s %-20s %-12s %s' % ('card', 'verdict', 'mechanic/type', 'text nums', 'unbacked'))
print('-' * 88)
for r in rows:
    print('%-22s %-11s %-20s %-12s %s' % r)

from collections import Counter
c = Counter(r[1] for r in rows)
print('\n' + '=' * 88)
for k in ['UNWIRED', 'NO EFFECT', 'NO OBJECT', 'MISMATCH', 'NO NUMBERS', 'ok']:
    if c.get(k):
        print('  %-11s %d' % (k, c[k]))
print("""
UNWIRED and MISMATCH are findings. NO NUMBERS is a reading list, not a pass -
a card that promises no quantity can still do the wrong thing, and nothing here
would know. `ok` means the numbers line up, which is necessary and not
sufficient.""")
