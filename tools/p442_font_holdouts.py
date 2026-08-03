# -*- coding: utf-8 -*-
"""P442 - the two the variable pass could not reach, and the comments it stranded.

P441 moved all 159 uses of `var(--font-px)` to JMH Beda and deleted the
variable. Measuring afterwards, 165 elements STILL rendered the previous game's
pixel font. The variable was gone, so those had to be hardcoded - and they were:

    .gcard         font-family:'Press Start 2P'   <- EVERY CARD IN THE GAME
    .buyin-badge   font-family:'Press Start 2P'

`.gcard` is commented "from main game" - ported wholesale from the previous
title, never wired to the variable, so a migration done through the variable
was always going to walk straight past it. That is the whole 165: cards are
dense with text and there are a lot of them on screen at once.

WHY THIS COUNTS AS THE SAME RULING, not scope I invented. "Replace it, all 157,
full pass" is about the game not wearing the previous game's face. 157 was the
count of variable uses, which is what I reported and therefore what was ruled
on; it was never the count of places showing Alagard. Leaving the cards in the
pixel font because they were not on my list would satisfy the number and miss
the instruction.

AND THE STRANDED COMMENTS. Four blocks explain `--font-px` in the present tense
- what it holds, that it is "still the dominant UI face", that it is the entry
most likely to save someone. The variable no longer exists. A comment that
confidently describes something deleted is worse than no comment, and this file
has already burned a session on exactly that: the count in one of these blocks
was itself a correction of an earlier wrong count. Fixed here rather than left
to mislead a third time.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── the two live holdouts ──
PAIRS = [
  # every card in the game
  (u"  font-family:'Press Start 2P',monospace;\n  transition:box-shadow .15s,transform .1s;",
   u"""  /* var(--font-ui), not the literal. This rule is marked "from main game" -
     ported from the previous title with its font baked in, never wired to the
     variable - so P441's variable-wide pass walked past it and left EVERY CARD
     in the previous game's pixel face. It was 165 of the 165 elements still
     rendering Alagard afterwards. */
  font-family:var(--font-ui);
  transition:box-shadow .15s,transform .1s;""", 1),
  (u"font-size:10px;font-family:'Press Start 2P',monospace;padding:3px 5px;",
   u"font-size:10px;font-family:var(--font-ui);padding:3px 5px;", 1),
]
for old, new, want in PAIRS:
    got = s.count(old)
    assert got == want, 'holdout %r matched %d (want %d)' % (old[:40], got, want)
    s = s.replace(old, new)

# ── comments that describe a variable that no longer exists ──
COMMENTS = [
  (u"""/* JMH BEDA, the font the game writes its NEW surfaces in. The count that used
   to sit here - "56 uses against three for Press Start 2P" - was wrong by
   about 26x, and wrong in the way this project keeps catching: it counted the
   LITERAL 'Press Start 2P' (6) instead of var(--font-ui) (157), which is what
   actually applies it. Measured properly: JMH Beda 67, var(--font-ui) 157.
   var(--font-ui) is 'Alagard','Press Start 2P' and it is still the dominant UI
   face - including .hud-score, .hud-target and .hud-turnnum, the three numbers
   a player reads all match. Whether that whole surface migrates is a look call,
   not a cleanup; it is in OPEN.md.""",
   u"""/* JMH BEDA, and now it is the whole game's face rather than the new surfaces'.
   This block has held two wrong counts. The first - "56 uses against three for
   Press Start 2P" - counted the LITERAL font name instead of the variable that
   applied it, and was out by about 26x. The second said 157, which was a
   `grep -c` and therefore a count of LINES; the real figure was 159
   occurrences. Both were wrong in the same direction: measuring the name of a
   thing rather than the thing.
   Settled now, so there is no third count to get wrong: --font-px is DELETED,
   every use moved to --font-ui holding 'JMH Beda', and the two rules that
   hardcoded the pixel font (.gcard, .buyin-badge) went with them."""),
  (u"""  /* NOT A PATH — the family name, and the entry most likely to save someone.
     `--font-px` is 'Alagard','Press Start 2P', the PREVIOUS game's pixel font,
     and it reads as the obvious choice right up until Denis points out the
     score is in the wrong typeface. The game's font is JMH Beda, 56 uses. */""",
   u"""  /* NOT A PATH — the family name. This warned that `--font-px` was the
     previous game's pixel font and the wrong obvious choice; --font-px no
     longer exists, and --font-ui holds 'JMH Beda' everywhere, so the trap it
     described is gone. Kept because the entry is still not a path. */"""),
  (u"""  /* Pixel font (Alagard) — the "1" glyph reads as a proper numeral, not like a serif "I". */""",
   u"""  /* Was the pixel font, kept because its "1" reads as a numeral rather than a
     serif "I". That reason now needs re-checking by eye against JMH Beda,
     which is a blackletter: this is a tooltip NUMBER, so a "1" that reads as
     an "I" is a legibility bug, not a taste call. Flagged in OPEN.md. */"""),
  (u"""  /* Match the perks-panel label font (Alagard pixel) — not all-caps */""",
   u"""  /* Match the perks-panel label font — not all-caps. (Said "Alagard pixel";
     both this and the perks panel are on --font-ui now, so they still match.) */"""),
  (u"""/* 'JMH Beda', not --font-px. --font-px is 'Alagard','Press Start 2P' - the
   PREVIOUS game's pixel font - and this rule put it on the single word the
   loss screen shows. Same mistake already fixed on the win board. */""",
   u"""/* 'JMH Beda' literal, from when this rule alone had to escape --font-px - the
   previous game's pixel font, which it had put on the single word the loss
   screen shows. --font-px is gone and --font-ui is the same face; left as a
   literal only because clamp() sizing here was tuned around it. */"""),
]
for old, new in COMMENTS:
    assert s.count(old) == 1, 'comment matched %d: %r' % (s.count(old), old[:50])
    s = s.replace(old, new)

assert s != orig, 'nothing changed'
# THE @font-face RULES SURVIVE ON PURPOSE and the assert must not fight them:
# 'Alagard' and 'Press Start 2P' still need declaring for as long as anything
# could reference them, and removing a @font-face is a separate call. What must
# be gone is every rule that APPLIES them.
# A NEGATIVE LOOKAHEAD DOES NOT EXCLUDE A BLOCK. The first version tried to
# skip @font-face with a lookahead on the value and caught the two @font-face
# rules anyway - they ARE `font-family:'Alagard'`, textually identical to a rule
# that applies it. The difference is which BLOCK they sit in, which no
# value-level pattern can see. So cut the blocks out first, then search.
import re
probe = re.sub(r'@font-face\s*\{[^}]*\}', '', s)
bad = [a for a in re.findall(r'font-family:[^;\n}]*', probe)
       if 'Alagard' in a or 'Press Start' in a]
assert not bad, 'a rule still applies the old face: %r' % bad[:3]
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P442 applied: .gcard + .buyin-badge moved, 5 stale comments corrected')
