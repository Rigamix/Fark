# -*- coding: utf-8 -*-
u"""P910: the three shadowed rules go, now that the check has been done, and the
outcome gate's floor is stated where it lives.

THE CHECK, RUN RATHER THAN TAKEN. Every property the early copies set is re-set
by the .seat-frame definitions:

  .seat-name  early font-size, letter-spacing, color              -> all 3 in
              late margin-top, z-index, font-size, letter-spacing,
              color, background, padding, border-radius,
              box-shadow, transform
  .seat-dice  early display, gap                                  -> all 2 in
              late display, gap, margin-top
  .seat-die   early width, height, border-radius, background,      -> all 6, same
              border, image-rendering                                names, 13px
                                                                     against 10px

No declaration survives into the cascade, so they can go. SHADOWED IS STILL NOT
DEAD, and the distinction is what made stopping right: a block delete of the
whole run would have been correct by luck. .seat-die is the case that looks
obviously safe - identical property names - and .seat-name is the case where
being wrong is invisible, because color:#e8e0d0 against a later color:#2f1f0e
only shows up the day somebody changes the later rule.

THE FLOOR ON THE EASY TIER IS ONE, and it was already one - the code refuses
`ew === 0` and nothing else. But it was implicit in an equality test rather than
stated, and the reasoning belongs next to it: one win proves the driver can win;
zero is indistinguishable from broken; and at zero wins everywhere the two
claims - "the driver is broken" and "the game is far harder than the design
target" - collapse into the same observation, which no gate can separate. So one
is the most it can honestly be, and a floor of two or three would refuse exactly
the finding the ladder exists to produce.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def sub(path, old, new, label):
    s = io.open(path, encoding='utf-8', newline='').read()
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    io.open(path, 'w', encoding='utf-8', newline='').write(
        s[:m.start()] + rep + s[m.end():])
    edits.append(label)


PAGE = os.path.join(ROOT, 'fark_proto.html')
DRV = os.path.join(ROOT, 'tools', 'fark_driver.js')

sub(PAGE,
    u""".seat-name{font-size:13px;letter-spacing:1.5px;color:#e8e0d0}
.seat-dice{display:flex;gap:3px}
.seat-die{width:13px;height:13px;border-radius:2px;background:var(--dface,#888);
  border:1.5px solid var(--dborder,#666);image-rendering:pixelated}""",
    u"""/* P910: the last three of the old seat block, deleted only after the check
   that P909 declined to make. These were SHADOWED, not dead - the classes are
   live on .seat-frame - and a shadowed rule is only safe to remove when every
   property it sets is re-set by the later one. Checked: seat-name's 3 all
   appear among the later 10, seat-dice's 2 among the later 3, and seat-die's 6
   are the same six names at 10px instead of 13px. Nothing survived into the
   cascade.
   seat-die is the one that LOOKS obviously safe and seat-name is the one where
   being wrong stays invisible - color:#e8e0d0 under a later color:#2f1f0e only
   surfaces the day somebody edits the later rule. */""",
    '1 the three shadowed rules')

sub(DRV,
    u"""    const ew = e.filter(r => r.win).length, hw = h.filter(r => r.win).length;
    /* the two that fail on sight, whatever the other cell says */
    if (ew === 0) return {ok: false, easyWins: ew, hardWins: hw,""",
    u"""    const ew = e.filter(r => r.win).length, hw = h.filter(r => r.win).length;
    /* THE FLOOR ON THE EASY TIER IS ONE, and one is the most it can honestly
       be. One win proves the driver can win. Zero is indistinguishable from
       broken - and at zero wins everywhere, "the driver does not play" and "the
       game is several times harder than the design target" become the same
       observation, which no gate can separate. A floor of two or three would
       refuse exactly the finding the ladder exists to produce, which is the
       trap the absolute band fell into one level up. So: easy 1 / hard 0
       PASSES, deliberately. */
    if (ew === 0) return {ok: false, easyWins: ew, hardWins: hw,""",
    '2 the floor is stated where it lives')

# ── post-asserts ────────────────────────────────────────────────────
page = io.open(PAGE, encoding='utf-8', newline='').read()
code = re.sub(r'/\*.*?\*/', '', page, flags=re.S)
# EXACTLY ONE BASE DEFINITION EACH, and "base" has to mean at the start of a
# line. Counting the bare substring called it two: `.seat-frame:nth-child(even)
# .seat-name{` and `.pk-dice .seat-die{` are live descendant selectors, not
# duplicates - the same class-census mistake one level down, on my own assert.
for cls in ('seat-name', 'seat-dice', 'seat-die'):
    n = len(re.findall(r'(?m)^\.' + cls + r'\{', code))
    if n != 1:
        sys.exit('.%s has %d base definitions, expected 1 (already written)'
                 % (cls, n))
# and it must be the LATE one, identifiable by its own values
if 'width:10px;height:10px' not in code:
    sys.exit('the surviving .seat-die is not the live 10px one (already written)')
if 'color:#2f1f0e' not in code:
    sys.exit('the surviving .seat-name is not the live one (already written)')
# the whole dead block is gone
for gone in ('.seat-row', '.seat-main', '.seat-meta', '.seat-hc', '.seat-stamp'):
    if gone in code:
        sys.exit('%s survived (already written)' % gone)
# and the live family is intact
for keep in ('.seat-frame', '.seat-port', '.seat-stake', '.seat-seal'):
    if keep not in code:
        sys.exit('%s was deleted and is live (already written)' % keep)

drv = io.open(DRV, encoding='utf-8', newline='').read()
if 'easy 1 / hard 0' not in drv:
    sys.exit('the floor is not stated (already written)')

print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
