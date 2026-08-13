# -*- coding: utf-8 -*-
"""P680: the boss voice addendum - FARK_DIALOGUE_VOICE_PASS_BOSSES.md.

22 lines trimmed out of 274; every other boss line stays exactly as shipped.
The doc's rule: cut the second clause that restates or justifies the first,
drop self-aware qualifiers, keep the concrete detail. Registers stay distinct
- Aldric formal, Corvus cold, Ambrose grave - only the length changes.

Each Before is an exact-match anchor against the line's t:"..." text, so a
drifted quote fails the chain instead of silently patching nothing. Run with
--check to only report which anchors match.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

PAIRS = [
 # CORVUS
 ("You're a reliable line item at this point. I mean that as a compliment, in my way.",
  "Another reliable line item."),
 ("I could set a clock by how this goes with you.",
  "Could set a clock by you."),
 ("You're the reason I'll be re-reading old pages tonight instead of sleeping.",
  "Costing me sleep, this."),
 ("I'll be thinking about this over supper. Don't take that as flattery.",
  "Thinking about this over supper. Not a compliment."),
 ("You're better than the average. I've updated the file accordingly.",
  "Better than average. Noted."),
 ("Fine. That was earned, not lucky. I can tell the difference.",
  "Fine. Earned, not lucky."),
 # GROG
 ("Pour you an ale on the house. Won't fix the losing, but it'll help.",
  "Pour you an ale on the house. Won't fix it, but it helps."),
 # MABEL
 ("Sit down, I'll bring you something warm. Won't fix the run of luck, but it helps.",
  "Sit down, I'll bring you something warm."),
 ("You look like you need a proper meal more than a win, if I'm honest.",
  "You look like you need a proper meal more than a win."),
 # FINNICK
 ("Almost feel bad. Almost. Then I remember the coin's mine now.",
  "Almost feel bad. Almost."),
 ("Word gets around if I keep losing to the same face. Not good for me.",
  "Word gets around, losing to the same face. Bad for business."),
 # BRUTUS
 ("You're slow to learn, but you keep showing up. That counts for something.",
  "Slow to learn. Keep showing up, though. Counts for something."),
 # ALDRIC
 ("The lesson repeats. Perhaps it will take, eventually.",
  "The lesson repeats. Perhaps it lands eventually."),
 ("Thou'rt slow to learn this one. No matter. I've the patience.",
  "Slow to learn, this one. No matter."),
 ("The candle's near out. Confess quickly, and we're both to bed sooner.",
  "Candle's near out. Confess quickly."),
 ("Thy cleverness wants no further quieting from me, it seems.",
  "Thy cleverness wants no quieting from me anymore."),
 ("I begin to look forward to these, truth be told.",
  "I'm starting to look forward to these."),
 ("I'll mark this one in ink, not chalk. It deserves it.",
  "This one goes in ink, not chalk."),
 # WHISPER
 ("There's a tell in how you hold those dice. I'll keep it to myself, for now.",
  "There's a tell in how you hold those dice. Keeping it to myself."),
 ("I don't often get surprised. Noted, and appreciated.",
  "Don't often get surprised. Noted."),
 # AMBROSE
 ("The house has seen your face enough times now to know it well.",
  "The house knows your face well by now."),
 ("Pour yourself the good wine tonight. You've earned the better bottle.",
  "Pour yourself the good wine tonight. Earned it."),
 ("Take the seat by the fire on your way out. Small comfort, but real.",
  "Take the seat by the fire on your way out."),
]

check = '--check' in sys.argv
missing, multi = [], []
for old, new in PAIRS:
    c = s.count(old)
    if c == 0:
        missing.append(old)
    elif c > 1:
        multi.append((old, c))
print('%d pairs: %d found once, %d missing, %d multiple'
      % (len(PAIRS), len(PAIRS) - len(missing) - len(multi), len(missing), len(multi)))
for m in missing:
    print('  MISSING: %r' % m[:90])
for m, c in multi:
    print('  x%d: %r' % (c, m[:90]))
if check or missing or multi:
    sys.exit(0 if check else ('anchors not clean' if (missing or multi) else 0))

for old, new in PAIRS:
    s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('applied %d trims' % len(PAIRS))
