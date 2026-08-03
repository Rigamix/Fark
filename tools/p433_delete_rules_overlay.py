# -*- coding: utf-8 -*-
"""P433 - delete the dead rules overlay.

RULED. It is stale on five independent axes - a Last Call description that
teaches the handicap while a badge rule of the same name now voids banks under
800, Anchor and Bookends listed as cards when both collapsed into Vanguard,
renown perks that no longer exist, a patron gold formula that is not what the
payout computes, and "losing to a patron costs nothing" when it costs a seat.
Reviving is not on the table: the master brief already rules that the pause
menu is the only rules-reference surface and says outright not to rebuild an
innkeep's book screen.

The park-don't-delete rule applies when a future version might need the thing
intact. Content wrong in five independent ways has no such future, and leaving
it one onclick from live is a hazard, not an archive.

Four pieces, and the last one is why this is a patch and not a delete:
  1. the CSS block
  2. the RULES menu button - its only entry point
  3. the markup
  4. the JS, INCLUDING a reference that lives outside the block: the window
     resize handler in BOOT calls renderRulesScroll(). Deleting the function
     and leaving that call turns every resize into a ReferenceError.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

def cut(hay, start_mark, end_mark, what, keep_end=True):
    """Delete from start_mark up to end_mark. end_mark is kept by default."""
    i = hay.find(start_mark)
    assert i >= 0, 'cut %s: start not found' % what
    j = hay.find(end_mark, i + len(start_mark))
    assert j > i, 'cut %s: end not found after start' % what
    return hay[:i] + (end_mark if keep_end else '') + hay[j + len(end_mark):]

# ── 1. CSS ────────────────────────────────────────────────────────────
# Nothing outside this block uses .rules-* or .rp-* — checked before cutting.
# MedievalSharp survives: .settings-title still uses it.
s = cut(s, u"/* ─── RULES OVERLAY ─── */",
           u"/* ── SETTINGS SHEET ── */", 'css block')

# ── 2. the only entry point ───────────────────────────────────────────
BTN = (u'    <div class="menu-btn" onclick="SFX.nav();openRules()">\n'
       u'      <canvas></canvas>\n'
       u'      <span class="btn-label">RULES</span>\n'
       u'      <img class="btn-icon" src="assets/Menu_Art/Rules.png" alt="Rules">\n'
       u'    </div>\n')
assert s.count(BTN) == 1, 'RULES button matched %d' % s.count(BTN)
s = s.replace(BTN, u'')

# ── 3. the markup ─────────────────────────────────────────────────────
# Sliced by counting div depth rather than by a line number, because the
# preceding comment block (P432) already shifted these once.
i = s.find(u'<!-- UNREACHABLE, AND STALE.')
assert i >= 0, 'overlay comment marker not found'
j = s.find(u'<div class="rules-overlay"', i)
assert j > i, 'overlay div not found after marker'
depth, k = 0, j
while True:
    nxt_open = s.find(u'<div', k)
    nxt_close = s.find(u'</div>', k)
    assert nxt_close >= 0, 'unbalanced overlay markup'
    if nxt_open >= 0 and nxt_open < nxt_close:
        depth += 1; k = nxt_open + 4
    else:
        depth -= 1; k = nxt_close + 6
        if depth == 0:
            break
s = s[:i] + s[k:].lstrip('\n')

# ── 4. the JS, and the stray call in BOOT ─────────────────────────────
s = cut(s, u"/* ═══════════════════════════════════════\n   RULES OVERLAY",
           u"/* ═══════════════════════════════════════\n   BOOT", 'js block')

# THE ONE THAT WOULD HAVE BROKEN AT RUNTIME. renderRulesScroll and
# rulesScrollRendered both die with the block above, but this call sits in the
# BOOT resize handler, outside it. Left alone it throws on every resize.
OLD_RESIZE = (u"  window.addEventListener('resize',()=>{\n"
              u"    initButtons();\n"
              u"    if(rulesScrollRendered)renderRulesScroll();\n"
              u"  });\n")
assert s.count(OLD_RESIZE) == 1, 'resize handler matched %d' % s.count(OLD_RESIZE)
s = s.replace(OLD_RESIZE,
              u"  window.addEventListener('resize',()=>{\n"
              u"    initButtons();\n"
              u"    /* the rules-scroll redraw that used to sit here went with the rules\n"
              u"       overlay (P433). It was the only other thing this handler did. */\n"
              u"  });\n")

# ── post-conditions, measured on the written text ─────────────────────
for gone in ['rulesOverlay', 'openRules', 'closeRules', 'switchRulesTab',
             'renderRulesScroll', 'rulesScrollRendered', 'rulesTrack',
             'rules-overlay', 'rp-note', 'rp-sh']:
    assert gone not in s, 'leftover reference: %s' % gone
assert s != orig, 'nothing changed'
assert u'MedievalSharp' in s, 'MedievalSharp lost - it is still used by .settings-title'
removed = len(orig.split('\n')) - len(s.split('\n'))
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P433 applied: %d lines removed, no dangling references' % removed)
