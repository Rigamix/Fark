# -*- coding: utf-8 -*-
u"""Repair card_audit.nums - its regex contains a literal BACKSPACE byte.

A heredoc turned `\\b` into \\x08, so the pattern read `(?=\\d{3}\\x08)`: prints
correct, matches nothing, leaves six false findings in place while looking
fixed. Same failure as until_audit.py earlier in this session.

Replaces the whole function by LINE RANGE rather than by exact string, because
the string to match contains the control character and cannot be typed.
"""
import io, os, re

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'card_audit.py')
src = io.open(P, encoding='utf-8').read()

start = src.index('def nums(t):')
end = src.index('\n\nrows = []', start)
old = src[start:end]
assert '\x08' in old, 'the backspace byte is not where it was expected'

new = (
    "def nums(t):\n"
    "    # STRIP THOUSANDS SEPARATORS FIRST. The card text writes \"1,200\" and\n"
    "    # \"4,500\"; a bare 2-6 digit match splits those into 200 and 500, and\n"
    "    # \"2,000\" into 000 -> 0. That reported SIX mismatches, every one the comma.\n"
    "    #\n"
    "    # AND THE FIRST FIX DID NOT WORK, which is the part worth recording. It went\n"
    "    # through a bash heredoc and the `\\b` in `\\d{3}\\b` was written as a LITERAL\n"
    "    # BACKSPACE BYTE. The pattern became (?=\\d{3}<BS>) - prints looking correct,\n"
    "    # matches nothing, and leaves the false findings in place while appearing\n"
    "    # repaired. Identical to until_audit.py earlier in this session, which\n"
    "    # invented eight false findings the same way.\n"
    "    #\n"
    "    # Now a plain .replace with no escapes at all, so there is nothing for a\n"
    "    # quoting layer to corrupt.\n"
    "    t = t.replace(',', '')\n"
    "    return set(int(x) for x in re.findall(r'(?<![\\w.])(\\d{2,6})(?![\\w%])', t))"
)
io.open(P, 'w', encoding='utf-8', newline='').write(src[:start] + new + src[end:])

chk = io.open(P, encoding='utf-8').read()
assert '\x08' not in chk, 'a backspace byte survives in the file'
assert "t = t.replace(',', '')" in chk
print('card_audit.nums repaired; no control characters remain')
