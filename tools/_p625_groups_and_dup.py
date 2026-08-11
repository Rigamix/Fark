# -*- coding: utf-8 -*-
"""P625: Denis's group assignments for the 32 legacy rows, and the duplicate they exposed.

THE DUPLICATE IS A BUG I SHIPPED. P622's generator asserted no line repeated
within its own new content, but never checked the new lines against the rows
ALREADY in the table - so "Twice now. You're becoming genuinely interesting to
me." went in beside an identical legacy row and boss:whisper:loss carried it
twice. Denis flagged it as a lines-too-similar collision; measuring it showed
verbatim. Kept: the LEGACY row, because it is what has actually been in players'
games. Dropped: my copy.

ONE MORE TRIMMED BY JUDGEMENT, and flagged as such rather than slipped in.
Denis: "they're close enough to my own lines in those groups that I'd actually
cut one of mine rather than run both; tell me if you want the legacy or the new
one kept" - and delegated the choice. The legacy cautious-respect row is "I'm
starting to take you seriously. Dangerous, for both of us."; my
"Careful. I'm starting to take you seriously." repeats its first clause almost
word for word, so mine goes. "Well played, twice over..." and "Dangerous, you
turning out to be good at this." both stay - close in theme, not in wording.
Reversible: re-add the two strings below if the call was wrong.

THE GROUPS ARE DENIS'S, ASSIGNED BY READING EACH LINE, not by theme-matching. He
built the taxonomy, so the placements are his - this script only applies them,
and matches on the exact text so a mis-ordered pool cannot silently mislabel.
"""
import io, os, sys, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

# ── 1. drop the two of MY lines that duplicate legacy ones ───────────────
DROP = [
    u'  {p:\'boss:whisper:loss\',s:1,g:\'genuine-interest\','
    u't:"Twice now. You\'re becoming genuinely interesting to me."},\n',
    u'  {p:\'boss:whisper:loss\',s:1,g:\'cautious-respect\','
    u't:"Careful. I\'m starting to take you seriously."},\n',
]
for d in DROP:
    if s.count(d) != 1:
        sys.exit('DROP anchor x%d: %r' % (s.count(d), d[:80]))
    s = s.replace(d, u'')
print('dropped %d duplicate/near-duplicate rows of my own' % len(DROP))

# ── 2. Denis's assignments, keyed on the exact legacy text ───────────────
G = {
 "Back again? Some folk never learn the shape of a losing streak.": 'losing-streak-callout',
 "You're getting predictable to beat. That's not a compliment.": 'backhanded-needling',
 "You again. Starting to think that first win wasn't luck after all.": 'grudging-acceptance',
 "Alright. You've earned the right to stop gloating about it now.": 'reluctant-respect',
 "Back so soon? I do worry about you, you know, even when you keep losing to me.": 'motherly-worry',
 "You're persistent, I'll give you that. Persistent and hungry, probably.": 'gentle-teasing',
 "Twice now. I'm almost proud, in a motherly sort of way.": 'motherly-pride',
 "You keep this up and I'll have to start taking you seriously.": 'warm-surprise',
 "You keep coming back for the same trick. I keep obliging.": 'trick-of-the-trade',
 "At this point I almost feel bad. Almost.": 'light-teasing',
 "Twice you've had my measure now. I'll need a new trick.": 'new-trick-needed',
 "You're becoming a genuine problem for my business, you know that?": 'grudging-business-concern',
 "Another entry in the ledger. You're becoming a reliable line item.": 'ledger-callback',
 "I could set my books by how often you lose to me. Comforting, in its way.": 'player-as-asset',
 "Twice against the numbers now. I'm revising my estimate of you.": 'recalculating',
 "You're an anomaly I haven't priced in yet. Uncomfortable, that.": 'anomaly-discomfort',
 "Back for more drilling? Good. Some of you need it repeated.": 'soldier-address',
 "Still haven't learned the count. We'll keep at it till you do.": 'drilling-metaphor',
 "Twice you've held the line against me. I'm reassessing your training.": 'grudging-training-update',
 "You're drilling well. I'll allow it, this once more.": 'fair-acknowledgment',
 "Thou returnest, still unconfessed. Persistence is its own small virtue, I suppose.": 'quiet-lesson',
 "The same lesson, again. I begin to wonder if it's landing at all.": 'formal-judgment',
 "Twice bested. I begin to suspect thy cleverness needs no quieting at all.": 'growing-respect',
 "A worthy return match. I'll not pretend otherwise.": 'formal-concession',
 "Back again. I do love a repeat performance.": 'detached-observation',
 "Same result, different night. I'm not complaining.": 'knowing-amusement',
 "Twice now. You're becoming genuinely interesting to me.": 'genuine-interest',
 "I'm starting to take you seriously. Dangerous, for both of us.": 'cautious-respect',
 "You keep returning to be reckoned with. I respect the persistence, if nothing else.": 'the-house-remembers',
 "The house remembers every name that's tried and failed. Yours is in good company.": 'grave-formal',
 "Twice you've bested my table. The house is taking notice of you now.": 'the-house-notices',
 "You're no longer a name I'll forget by morning.": 'grave-acknowledgment',
}

applied = 0
for text, grp in G.items():
    esc = text.replace('\\', '\\\\')
    old = u"s:1,g:'stage1-original',t:\"%s\"}" % esc
    if s.count(old) != 1:
        sys.exit('GROUP anchor x%d for %r' % (s.count(old), text[:60]))
    s = s.replace(old, u"s:1,g:'%s',t:\"%s\"}" % (grp, esc))
    applied += 1
print('applied %d of Denis\'s group assignments' % applied)

if "stage1-original" in s:
    sys.exit('some rows still carry the placeholder label')

io.open(P, 'w', encoding='utf-8', newline='').write(s)

# ── 3. no duplicate may survive, anywhere ────────────────────────────────
i = s.index('var PATRON_LINES=['); j = s.index('\n];', i)
rows = re.findall(r"\{p:'([^']+)'[^}]*?t:\"(.*?)\"\}", s[i:j])
dups = [(p, t, n) for (p, t), n in collections.Counter(rows).items() if n > 1]
if dups:
    for p, t, n in dups:
        print('  STILL DUPLICATED x%d  %s  %s' % (n, p, t[:60]))
    sys.exit('duplicates remain')
print('no verbatim duplicates anywhere in %d rows' % len(rows))
