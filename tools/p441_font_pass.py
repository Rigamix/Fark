# -*- coding: utf-8 -*-
"""P441 - the full font pass. 157 declarations off the previous game's face.

RULED: replace it, all 157, not just the ones already migrated.

MECHANISM, and why it is not 157 literal strings. Every use is
`font-family:var(--font-px)` - checked, no `font:` shorthand anywhere - so the
swap can go through the variable. But `--font-px` NAMES the thing being
removed: "px" is the pixel font. Leaving 157 sites pointing at a variable called
--font-px that no longer holds a pixel font is how the next reader gets misled
the way I was.

So: `--font-ui` is introduced holding 'JMH Beda', all 157 sites move to it, and
`--font-px` is deleted. One place to change in future, and the name tells the
truth.

WHAT THIS CANNOT PROMISE. These sizes and letter-spacings were tuned against
Alagard's metrics. JMH Beda is a different face and will not occupy the same
space at the same numbers - some of the 157 will need their size or spacing
adjusted, and a few may wrap or clip. That is a look pass to do WITH eyes on
the screens, not something this patch can assert. Every screen gets shot after
this and the damage reported rather than quietly shipped.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# 159 OCCURRENCES ACROSS 157 LINES. The number reported to Denis was 157,
# from `grep -c`, which counts LINES - two of them use the variable twice. Same
# lines-versus-occurrences slip as the rule-id rename earlier. The work is the
# same either way; the count in the commit message is not.
before = s.count('var(--font-px)')
assert before == 159, 'expected 159 uses, found %d' % before

# ── the new variable, defined where the old one was ──
OLD_DECL = u"  --font-px:'Alagard','Press Start 2P',monospace;"
assert s.count(OLD_DECL) == 1, 'declaration matched %d' % s.count(OLD_DECL)
s = s.replace(OLD_DECL,
  u"""  /* THE GAME'S FACE, everywhere. Was --font-px:'Alagard','Press Start 2P' -
     the previous game's pixel font - on 157 declarations including .hud-score,
     .hud-target and .hud-turnnum, the three numbers a player reads all match.
     Renamed as well as repointed: a variable called --font-px that no longer
     holds a pixel font is exactly the kind of name that misleads the next
     reader, and did.
     NOTE FOR WHOEVER TUNES TYPE NEXT: these sizes and letter-spacings were set
     against Alagard's metrics. JMH Beda does not occupy the same space at the
     same numbers, so some of the 157 will want their size or spacing adjusted.
     That is a look pass with eyes on the screens, not a find-and-replace. */
  --font-ui:'JMH Beda',serif;""")

s = s.replace('var(--font-px)', 'var(--font-ui)')

assert 'var(--font-px)' not in s, 'a --font-px use survives'
# ASSERT ON THE DECLARATION, NOT ITS NAME. `'--font-px:' not in s` fires
# because the replacement COMMENT quotes the old declaration while explaining
# what was removed. Third time today a check has counted prose as code - a
# patch comment that names what it deleted will always trip a naive search for
# that text. Check the exact statement instead.
assert OLD_DECL not in s, 'the old declaration survives'
after = s.count('var(--font-ui)')
assert after == before, 'use count changed: %d -> %d' % (before, after)
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P441 applied: %d declarations moved to --font-ui (JMH Beda)' % after)
