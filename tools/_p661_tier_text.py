# -*- coding: utf-8 -*-
"""P661: every tier's card text says what the card does, on its own.

Denis: "you can't have cards tooltip be 'as tier one but...' as no one will
remember what the previous level did. Change all those."

Ten cards wrote their tier 2 and 3 text as a diff against the tier above -
'As tier one, twice per match.' - which is only readable by someone holding the
tier 1 text in their head, and the player is looking at ONE tooltip. Worse for
tier 3, where four of them referred to tier TWO, so the reader needed a chain of
two they cannot see.

Every string below is now self-contained: the whole effect, at that tier. The
mechanics are unchanged - each is the tier-one sentence with its own numbers
folded in, taken from what the diff already said, not re-invented.

tar_pit's tier 3 was already self-contained and is left exactly as it was.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


FG = "Rolled nothing? Reroll everything. If the second roll fails too, the bust burns your turn AND the same amount from your banked points."
sub(u"        'As tier one, twice per match.','As tier one, three times per match.']},",
    u"        '" + FG + u" Twice per match.',\n"
    u"        '" + FG + u" Three times per match.']},",
    "P661 Fool's Gold")

PR = "Trap one scoring die in amber at the end of your turn. It is still there next turn, already kept and scored."
sub(u"        'As tier one, twice per match.','As tier two, and it cracks free with +100.']},",
    u"        '" + PR + u" Twice per match.',\n"
    u"        '" + PR + u" Twice per match, and it cracks free with +100.']},",
    'P661 Preserve')

HT = "Tap a kept pair. Your next roll pulls one die into matching it. Guaranteed triple."
sub(u"        'As tier one, twice per match.','As tier two, and it stretches kept triples into four-of-a-kinds.']},",
    u"        '" + HT + u" Twice per match.',\n"
    u"        '" + HT + u" Twice per match, and it stretches kept triples into four-of-a-kinds.']},",
    'P661 Honeytrap')

sub(u"        'As tier one, and it holds for two turns.','Trap two of their dice for one turn. Once per match.']},",
    u"        \"Trap one of the opponent's dice for their next two turns. They roll five. Once per match.\",\n"
    u"        'Trap two of their dice for one turn. Once per match.']},",
    'P661 Tar Pit')

SH = "Reroll a single die of your choice. You keep the new result, better or worse."
sub(u"        'As tier one, twice a match.','As tier one, three times a match.']},",
    u"        '" + SH + u" Twice a match.',\n"
    u"        '" + SH + u" Three times a match.']},",
    'P661 Steady Hand')

RP = "While trailing by 1000 or more, your banks TAKE their points instead of just gaining."
sub(u"        'As tier one, but two fifths.','As tier one, but three fifths.']},",
    u"        '" + RP + u" Two fifths of each bank is stolen from them.',\n"
    u"        '" + RP + u" Three fifths of each bank is stolen from them.']},",
    'P661 Reprisal')

FT = "Before you roll, swap one of your six dice for another from your stash."
sub(u"        'As tier one, and the swap lasts the whole turn.','As tier two, twice a match.']},",
    u"        '" + FT + u" The swap lasts the whole turn.',\n"
    u"        '" + FT + u" The swap lasts the whole turn. Twice a match.']},",
    'P661 Fair Trade')

PK = "Blow up your whole roll: every die rerolls, kept ones included."
sub(u"        'As tier one, twice per match.','As tier two, and detonations that land a triple score double.']},",
    u"        '" + PK + u" Twice per match.',\n"
    u"        '" + PK + u" Twice per match, and detonations that land a triple score double.']},",
    'P661 Powder Keg')

SL = "Force your opponent to reroll everything they just rolled."
sub(u"        'As tier one, twice per match.','As tier two, plus once whenever the table rule triggers.']},",
    u"        '" + SL + u" Twice per match.',\n"
    u"        '" + SL + u" Twice per match, plus once whenever the table rule triggers.']},",
    'P661 Sleight')

sub(u"        'As tier one, also usable once mid-match.','As tier two, and breaking it steals 300.']},",
    u"        \"Break one of the opponent's cards for the night. Also usable once mid-match.\",\n"
    u"        \"Break one of the opponent's cards for the night. Also usable once mid-match, and breaking it steals 300.\"]},",
    'P661 Tamper')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d cards rewritten' % n)
