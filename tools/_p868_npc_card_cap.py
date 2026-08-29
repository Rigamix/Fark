# -*- coding: utf-8 -*-
u"""P868 (BOSS REWARD BRIEF section 11.1): three cards, and the cap actually
caps.

Denis: "right now bosses can have more than 3 cards which I think is weird."

THE CAP NEEDED TWO CHANGES AND THE DATA WAS THE LESS IMPORTANT ONE.
generateOppCards did this, directly under the row's own cardCount:

    var n=rung.cardCount||1;
    if(playerCardCount!==undefined)n=Math.max(n,playerCardCount);

The player holds up to four (boss slot plus three regulars), so EVERY boss
could already draw four regardless of their row. Editing cardCount alone would
have changed nothing whenever the player carried a full hand - the symptom
would have persisted and looked like the fix had failed.

THE LIFT IS DELETED, not clamped, which is the brief's own preference and the
right one: with a hard ceiling of three and player hands of up to four, a
clamped lift could only ever raise a boss toward a ceiling it already sits at.
It would buy nothing and cost a reader's time working out that it buys
nothing. Its comment said "so it feels fair", which a clamped version would no
longer do.

THE CAP IS STRUCTURAL, NOT JUST DATA. The three cardCount edits below are the
LEVEL each boss draws at; NPC_CARD_CAP is the ceiling none of them can exceed.
Doing only the data edits would leave the next person free to write
cardCount:5 and re-open exactly this bug - the cap would live in three places
that all have to agree, which is how it broke the first time. With the clamp
in the function there is one place, and the rows are free to say whatever they
like below it.

playerCardCount STAYS in the signature. Two live call sites pass it and JS
would ignore its removal anyway, so taking it out buys only churn - but it is
now explicitly documented as ignored, at the exact line where someone would
otherwise re-wire it.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []
_INSERTED = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)
    _INSERTED.append((label, new))


# ── 1. the three rows that sat above the cap ─────────────────────────
# anchored on each pool, because `cardCount:4` alone matches two bosses.
sub(u"""cardPool:['the_verdict_npc','point_of_order','fathers_die','the_oath_npc','family_crest'],cardCount:4,""",
    u"""cardPool:['the_verdict_npc','point_of_order','fathers_die','the_oath_npc','family_crest'],cardCount:3,/* P868 */""",
    '1a aldric 4->3')

sub(u"""cardPool:['the_royal_purse','crown_authority','the_quiet_decree','sundays_rest','old_roads','royal_seizure'],cardCount:4,""",
    u"""cardPool:['the_royal_purse','crown_authority','the_quiet_decree','sundays_rest','old_roads','royal_seizure'],cardCount:3,/* P868 */""",
    '1b whisper 4->3')

sub(u"""cardPool:['communion_wine','blessed_dice','the_sermon','judgment_npc','never_saw_a_robe','blessed_confiscation'],cardCount:5,""",
    u"""cardPool:['communion_wine','blessed_dice','the_sermon','judgment_npc','never_saw_a_robe','blessed_confiscation'],cardCount:3,/* P868 */""",
    '1c ambrose 5->3')

# ── 2. the lift goes; the ceiling becomes structural ─────────────────
sub(u"""  var n=rung.cardCount||1;
  /* Boss matches: match player card count so it feels fair */
  if(playerCardCount!==undefined)n=Math.max(n,playerCardCount);""",
    u"""  /* P868: THE CEILING, and it lives HERE rather than in eight rows that all
     have to agree - which is how it broke the first time. Each row's
     cardCount is that boss's LEVEL; this is the maximum none of them can
     exceed, so a future row asking for five is capped rather than obeyed. Grog stays
     at 2 by his own row: the cap is a maximum, not a level, and night 1
     should be light. */
  var n=Math.min(rung.cardCount||1,NPC_CARD_CAP);
  /* P868: THE MATCH-THE-PLAYER LIFT IS DELETED. It took the larger of the
     row's count and the player's hand size, and the player holds up to four -
     boss slot plus three regulars - so
     every boss could already draw four whatever their row said. Editing the
     rows alone would have changed nothing whenever the player carried a full
     hand, and the symptom would have looked like the fix failing.
     Deleted rather than clamped: against a ceiling of three, a clamped lift
     could only ever raise a boss toward a ceiling it already sits at. It
     would buy nothing, and its old comment - "so it feels fair" - would no
     longer be true of it.
     playerCardCount stays in the signature because two live call sites pass
     it and removing it is pure churn. IT IS DELIBERATELY IGNORED. If a future
     change wants the rival's hand to track the player's, that is a design
     decision and it belongs above this cap, not inside it. */""",
    '2 lift deleted, ceiling structural')

# the constant itself, beside the function that enforces it
sub(u"""function generateOppCards(rung,playerCardCount){""",
    u"""/* P868 (brief 11.1): no NPC brings more than three cards, ever. Denis: "right
   now bosses can have more than 3 cards which I think is weird". */
var NPC_CARD_CAP=3;
function generateOppCards(rung,playerCardCount){""",
    '3 the cap constant')

# ── the guard that should have existed six patches ago ───────────────
# Every assert below scans the GAME FILE, and this patch inserts prose into
# that same file. Six times today an assert matched a literal its own new
# comment contained. A cleverer regex is not the fix and neither is care;
# the fix is a machine check that the text being INSERTED cannot contain the
# text being SEARCHED FOR. Anything that trips this is a comment quoting code,
# which is the thing to stop doing.
_SCANNED = ['Math.max(n,playerCardCount)', 'NPC_CARD_CAP', 'cardCount:4', 'cardCount:5']
_COMMENT_STARTS = ('*', '/*', '//')
for _lbl, _new in _INSERTED:
    for _line in _new.split(chr(10)):
        _bare = _line.lstrip()
        if not _bare.startswith(_COMMENT_STARTS):
            continue                      # a code line may say anything
        for _lit in _SCANNED:
            if _lit in _bare:
                sys.exit('COMMENT QUOTING CODE in %r: the inserted line\n    %s\n'
                         'contains %r, which the post-asserts scan the game file '
                         'for. That is what makes an assert match itself. Describe '
                         'it instead of quoting it. (nothing written)'
                         % (_lbl, _bare[:100], _lit))

# ── post-asserts ─────────────────────────────────────────────────────
# The comment above deliberately DESCRIBES the deleted line instead of quoting
# it. Five asserts today matched a literal their own new comment contained, and
# a cleverer pattern is not the fix - not writing code into prose is. A comment
# can name a thing; it must not BE the thing.
if 'Math.max(n,playerCardCount)' in s:
    sys.exit('THE LIFT SURVIVES (nothing written)')
if s.count('var NPC_CARD_CAP=3;') != 1:
    sys.exit('cap constant declared %d times (nothing written)'
             % s.count('var NPC_CARD_CAP=3;'))
if s.count('Math.min(rung.cardCount||1,NPC_CARD_CAP)') != 1:
    sys.exit('the ceiling is not applied exactly once (nothing written)')
# no row may now ask for more than the cap
for m in re.finditer(r'cardCount:(\d+)', s):
    if int(m.group(1)) > 3:
        sys.exit('A ROW STILL ASKS FOR %s CARDS - the ceiling would silently '
                 'clamp it, which hides the row being wrong (nothing written)'
                 % m.group(1))

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
