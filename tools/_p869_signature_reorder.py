# -*- coding: utf-8 -*-
u"""P869 (BOSS REWARD BRIEF section 11.2): Whisper and Ambrose stop
guaranteeing themselves a third of the target before a die is thrown.

Named bosses ALWAYS draw cardPool[0] - the signature guarantee, added because
a five-card pool drawing three left the signature out ~40% of the time. For
two of the eight, that slot held a flat start bonus:

    WHISPER   the_royal_purse   start +3500   against a target of 11,250  (~31%)
    AMBROSE   communion_wine    start +4500   against a target of 12,500  (~36%)

Those are the two nights the real-match ladder has never won a single game at
- 0/20 and 0/20 - and a guaranteed third of the target before the first roll
is a large part of why. They are also exactly the wrong SHAPE for the synergy
work in 11.3: a flat number interacts with nothing. Not the boss's dice, not
his badge, not the rest of his pool.

REORDERED, NOT DELETED, which is the smallest of the three options Denis was
offered and loses no content. Both start-bonus cards stay in their pools and
stay drawable; they simply stop being certain. What replaces them at slot 0
touches the player's LOADOUT, which is the interaction 11.3 asks for, and both
are BOUNDED - one die, once - rather than a percentage of target:

    WHISPER   royal_seizure          takes your best die, once; you play with five
    AMBROSE   blessed_confiscation   takes your best die AND plays it himself, once

Both new signatures are WEAKER than what they replace, and that is deliberate
on the two nights that have never been won.

Recorded so it is not re-litigated: the_quiet_decree (45% of every bank to
Whisper) reads like the right signature and is WORSE than the flat +3500 over
a full match, because it scales with how well the player plays - on the night
that needs relief. sundays_rest and never_saw_a_robe are defensive and
invisible; a signature the player never sees fire is not a signature.

THE GUARD 11.2 ASKS FOR IS ALREADY SATISFIED and was checked before this ran:
royal_seizure and blessed_confiscation live in NPC_CARDS, which section 2
never touched - it deleted rows from CARDS. Both rows and both player-side
activators are intact.
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
        edits.append(label); _INSERTED.append((label, new))
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label); _INSERTED.append((label, new))


# ── the two pools ────────────────────────────────────────────────────
sub(u"""    cardPool:['the_royal_purse','crown_authority','the_quiet_decree','sundays_rest','old_roads','royal_seizure'],cardCount:3,/* P868 */""",
    u"""    /* P869: SLOT 0 IS THE SIGNATURE and named bosses always draw it. It held
       the_royal_purse - a flat start bonus worth about 31% of his target
       before the first roll, on a night the real-match ladder has never won.
       The purse stays in the pool and stays drawable; it stops being certain.
       royal_seizure takes the player's best die once and is bounded, which is
       both weaker and the right shape - a noble seizing property, touching
       the loadout rather than the scoreboard. */
    cardPool:['royal_seizure','crown_authority','the_quiet_decree','sundays_rest','old_roads','the_royal_purse'],cardCount:3,""",
    'a whisper signature')

sub(u"""    cardPool:['communion_wine','blessed_dice','the_sermon','judgment_npc','never_saw_a_robe','blessed_confiscation'],cardCount:3,/* P868 */""",
    u"""    /* P869: same trade on night 8, where it is starker. communion_wine is a
       flat start bonus worth about 36% of a 12,500 target, guaranteed, every
       time - and the ladder is 0/20 here. It stays in the pool, drawable, no
       longer certain. blessed_confiscation takes the player's best die AND
       plays it against them: bounded, once, and it interacts in both
       directions, which a flat number never can. */
    cardPool:['blessed_confiscation','blessed_dice','the_sermon','judgment_npc','never_saw_a_robe','communion_wine'],cardCount:3,""",
    'b ambrose signature')

# ── the guard: a comment I insert must not contain a literal I scan ──
_SCANNED = ["cardPool:['the_royal_purse'", "cardPool:['communion_wine'",
            "cardPool:['royal_seizure'", "cardPool:['blessed_confiscation'"]
for _lbl, _new in _INSERTED:
    for _line in _new.split(chr(10)):
        _bare = _line.lstrip()
        if not _bare.startswith(('*', '/*', '//')):
            continue
        for _lit in _SCANNED:
            if _lit in _bare:
                sys.exit('COMMENT QUOTING CODE in %r: %r (nothing written)' % (_lbl, _lit))

# ── post-asserts ─────────────────────────────────────────────────────
for gone in ["cardPool:['the_royal_purse'", "cardPool:['communion_wine'"]:
    if gone in s:
        sys.exit('OLD SIGNATURE STILL AT SLOT 0: %s (nothing written)' % gone)
for now in ["cardPool:['royal_seizure'", "cardPool:['blessed_confiscation'"]:
    if now not in s:
        sys.exit('NEW SIGNATURE NOT AT SLOT 0: %s (nothing written)' % now)
# the displaced cards must still be IN their pools - reordered, not deleted
for kept in ["'the_royal_purse']", "'communion_wine']"]:
    if kept not in s:
        sys.exit('A START-BONUS CARD WAS DELETED RATHER THAN MOVED: %s '
                 '(nothing written)' % kept)
# and their NPC_CARDS rows must exist, or the new signatures point at nothing
for row in ["{id:'royal_seizure'", "{id:'blessed_confiscation'"]:
    if row not in s:
        sys.exit('SECTION 11.2 GUARD BROKEN - %s is missing from NPC_CARDS '
                 '(nothing written)' % row)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
