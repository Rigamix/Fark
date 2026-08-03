# -*- coding: utf-8 -*-
"""Every `await until(...)` whose return value is discarded.

`until(fn, ms)` returns TRUE when the condition became true and FALSE when it
timed out. It does not throw. So `await until(...)` on its own line is a probe
saying "wait for this, and carry on regardless of whether it happened" - and
everything after it is then asserting about a state that may never have
arrived.

THREE INSTANCES FOUND ONE AT A TIME IS UNDERSEARCHED, not unlucky:
  apv_preserve      declined-looking failures under suite load; four checks
                    reported false when the match had not finished initialising
  apv_bust_settle   the flapping INDET
  apv_p405_extraturn `stayedOurs` reporting "the extra turn yielded to the
                    rival" when the extra turn simply never began

All three had the same shape and all three produced a CONFIDENT WRONG CLAIM
about the game rather than an honest "could not run". So this sweeps for the
pattern instead of waiting for a fourth.

WHAT COUNTS AS DISCARDED. A call whose result is assigned, tested, returned or
used in a boolean expression is fine - the probe knows the wait might fail.
What is flagged is `await until(...)` as a bare statement.

WHAT THIS CANNOT JUDGE: whether a given discard MATTERS. A wait for an
animation to settle before taking a screenshot can reasonably not care. A wait
for the state an assertion depends on cannot. That is a read, per site - so
this reports what follows each one, and does not pretend to rank them.
"""
import io, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(HERE, 'apv_*.js')))

total, flagged = 0, []
for f in files:
    src = io.open(f, encoding='utf-8').read()
    for m in re.finditer(r'await\s+until\s*\(', src):
        total += 1
        # walk back over whitespace to the previous non-space character
        i = m.start() - 1
        while i >= 0 and src[i] in ' \t':
            i -= 1
        prev = src[i] if i >= 0 else '\n'
        # assigned / returned / inside a condition or expression -> handled
        if prev not in ('\n', ';', '{', '}'):
            continue
        line_no = src[:m.start()].count('\n') + 1
        # what does the probe do next? the reader needs it to judge severity
        after = src[m.start():]
        nxt = [l.strip() for l in after.split('\n')[1:6] if l.strip()][:3]
        flagged.append((os.path.basename(f), line_no, nxt))

print('await until(...) calls: %d   result discarded: %d' % (total, len(flagged)))

# ---- THE ACTIONABLE CUT --------------------------------------------------
# 164 of 184 discarded is too many to act on one at a time, and most are
# navigation waits where a later gate catches the failure anyway. The risk is
# narrower and sharper: a probe that DISCARDS waits and has NO WAY TO DECLINE.
# Such a probe cannot report "I could not run" no matter what happens - so
# every timeout becomes a verdict about the game. That is exactly what
# apv_preserve, apv_bust_settle and apv_p405_extraturn each did.
per = {}
for name, line, nxt in flagged:
    per.setdefault(name, []).append(line)

risky, ok = [], []
for f in files:
    name = os.path.basename(f)
    src = io.open(f, encoding='utf-8').read()
    if 'verdict' not in src:
        continue
    # NO \b HERE, AND THAT IS THE FIX. This line was written through a bash
    # heredoc; its `\b` became a literal BACKSPACE byte (0x08), so the pattern
    # could never match and every probe WITH a decline path was filed as having
    # none - twenty invented findings, silently. Third backslash-in-heredoc
    # failure this session and the first QUIET one: the other two were a syntax
    # error and an unterminated string, which announce themselves. This one just
    # produced a confident wrong list.
    can_decline = bool(re.search(r'return\s*\{\s*(skip|err)', src))
    n = len(per.get(name, []))
    (ok if (can_decline or not n) else risky).append((name, n, can_decline))

print('')
print('PROBES THAT DISCARD WAITS AND CANNOT DECLINE (%d):' % len(risky))
print('every timeout in these becomes a verdict about the game')
print('')
for name, n, _ in sorted(risky, key=lambda r: -r[1]):
    print('  %-34s %2d discarded wait(s)' % (name, n))

print('')
print('PROBES THAT CAN DECLINE, or discard nothing (%d):' % len(ok))
for name, n, cd in sorted(ok):
    print('  %-34s %2d discarded   decline path: %s' % (name, n, 'yes' if cd else 'n/a'))

print("""
NOT AUTO-FIXABLE and deliberately not auto-fixed. The fix per probe is the
same judgement each time: does anything after the wait assert about the state
it waited for? If yes, the probe must decline on timeout. If no - a settle
before a screenshot, say - the discard is correct and should say so.""")
