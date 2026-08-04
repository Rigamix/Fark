# -*- coding: utf-8 -*-
"""Is G.turnPts still live when endPTurn runs? Per call site, before threading.

RULED: a bust is a turn worth ZERO, not no turn. Thread the real number, zero on
bust, one signal - not a flag that suppresses the seam.

THE WHOLE PLAN RESTS ON ONE UNMEASURED ASSUMPTION: that capturing G.turnPts at
the top of endPTurn gives the banked total on a bank and 0 on a bust. That is
true only if the BANK path still has turnPts set when it calls endPTurn, and the
BUST path has already cleared it.

IF BOTH PATHS CLEAR IT FIRST, the capture reads 0 every time and the seam ships
looking correct while carrying a constant - the exact failure mode that makes a
number worse than no number, because it renders and nothing errors.

So this walks BACKWARD from each endPTurn call to the top of its enclosing
function, looking for an assignment that zeroes turnPts on the way. That is the
only thing that decides whether the capture point is right, and it is cheaper to
check than to debug a silently-zero card later.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()
lines = s.split('\n')

# every call, excluding the definition and comment mentions
calls = []
for i, ln in enumerate(lines):
    if 'endPTurn' not in ln:
        continue
    if re.search(r'function\s+endPTurn', ln):
        continue
    st = ln.strip()
    if st.startswith('/*') or st.startswith('*') or st.startswith('//'):
        continue
    if re.search(r'endPTurn\s*\(|setTimeout\s*\(\s*endPTurn', ln):
        calls.append((i + 1, st))

def enclosing_fn(idx):
    """Nearest `function name(` at or above idx, and its start line."""
    for j in range(idx, -1, -1):
        m = re.search(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(', lines[j])
        if m:
            return m.group(1), j
    return '(top)', 0

ZERO = re.compile(r'turnPts\s*=\s*0|_turnScoreClear\s*\(')
SET = re.compile(r'turnPts\s*(\+=|=)\s*(?!0\b)')

print('%-6s %-22s %s' % ('line', 'in function', 'is turnPts cleared before this call?'))
print('-' * 78)
verdict = {}
for ln, txt in calls:
    fn, fstart = enclosing_fn(ln - 1)
    before = lines[fstart:ln - 1]
    zeroed = [(fstart + k + 1, b.strip()[:46]) for k, b in enumerate(before) if ZERO.search(b)]
    state = 'CLEARED -> capture reads 0' if zeroed else 'still live -> capture reads the total'
    print('%-6d %-22s %s' % (ln, fn, state))
    print('       %s' % txt[:66])
    for zl, zt in zeroed[:2]:
        print('         cleared at %d: %s' % (zl, zt))
    verdict[ln] = bool(zeroed)

print('\n' + '=' * 78)
n_clear = sum(1 for v in verdict.values() if v)
print('%d of %d call sites clear turnPts before reaching endPTurn.' % (n_clear, len(verdict)))
if n_clear == len(verdict):
    print("""
ALL OF THEM. A capture at the top of endPTurn would read 0 on every path,
including banks. The capture has to move EARLIER than endPTurn, or the value
has to be stashed at the point it is cleared. Do not ship the top-of-endPTurn
version.""")
elif n_clear == 0:
    print("""
NONE. turnPts is live at every call, which means a bust arrives carrying its
pre-bust total - and the ruling wants zero. So the bust paths need an explicit
zero, not a passive read.""")
else:
    print("""
MIXED - and this is the case the plan assumed. The sites that clear are the
bust paths (a bust IS a turn worth zero, so a cleared value is the RIGHT
answer there); the sites that stay live are banks carrying their real total.
One capture at the top of endPTurn then gives exactly the ruled signal.
Confirm the split matches bust-vs-bank below before threading.""")
