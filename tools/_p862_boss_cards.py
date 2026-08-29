# -*- coding: utf-8 -*-
u"""P862 (BOSS REWARD BRIEF section 2): the eight boss cards become eight
effects nothing else in the game has, and the other twenty CARDS actives go.

THE DIRECTION OF THE RE-POINT IS THE WHOLE DESIGN DECISION, and the obvious
reading is the wrong one. "Rename and re-point" can mean either

  (a) keep the boss id, alias its switch case onto the source's handler, or
  (b) keep the SOURCE id and give that row the boss's identity.

(a) was measured and it fails. Five of the seven source handlers hardcode
their own id: activateGamblersEye, activateFrozenDie, activateDoubleDown and
activateAlchemistsChisel each name themselves on their no-op refund path, and
activateThePyre names itself FIVE times including the filter that stops the
card burning itself - so an aliased id would appear in its own burn picker and
could delete itself mid-activation. activateAlchemistsChisel also writes
S.run._chiselUsed, a per-RUN lock whose only reader is hardcoded to the
literal, so an alias would be once-per-match where the original is
once-per-run. second_wind and mabels_stitch are worse in a quieter way: both
handlers are two-line flag sets whose ACTUAL effect bodies live in the bust
path and hardcode the id twice each, so triggerCard would look up a
.mcard[data-cid] the player does not hold and the card would fire with no
feedback at all.

(b) has none of those problems because the id never moves. Every self
reference, every refund, every trigger label, every per-run lock, the
usedCards accounting, the timing gate and the maxUses read all keep pointing
at the row they always pointed at. Nothing is aliased, so nothing can be
aliased WRONG.

The cost of (b) is that an internal id stops matching its display name. That
is already this file's idiom and not a new debt: the_ledger renders as RUNNING
TAB and lucky_threes renders as LUCKY FIVES today, and section 5 Pass C says
code identifiers cost nothing to leave alone.

WHY THE SWAPS AT ALL. Six of the eight old boss cards duplicated something the
player can already get - Stitch was a strictly-better Ward, Palm and Fist and
Grace were all Transmute, Vow was literally the Obsidian family card's name
AND effect, Hex was Snuff. Corvus's Ledger was the sharpest: Double or Nothing
with the downside removed, which makes the real card pointless in any run that
holds it. Only Grog's Flask survived on its own merits - two dice rerolled is
a real distinction from Steady Hand's one die chosen - so Grog's row is the
one that does not move.

EACH CARD IS NOW MATCHED TO ITS BOSS'S BADGE, not to a vibe. Aldric's badge
makes every die forget its material and his card is the only thing in the game
that lets you choose one - exact inverse. Corvus charges you gold per roll and
his card lends you points at interest - the merchant, twice.

ROWS ONLY IN THIS PATCH. Section 7 is explicit that the rows go first and the
orphaned handlers are swept afterwards, because a live `case` in activateCard
pointing at a deleted function is the failure mode of doing it the other way
round. P863 does the sweep.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()


def cards_bounds(src):
    u"""The CARDS array's own extent, by bracket matching. Every lookup below
    is scoped to it: `{id:'second_wind'` also matches a FEATS row and
    `{id:'loan'` also matches an NPC_ARMS row, and a file-wide search would
    have deleted the wrong one of each - which is precisely the id-collision
    class section 6 is about, arriving inside section 2's own patch."""
    i = src.find('const CARDS=[')
    if i < 0:
        sys.exit('CARDS DECLARATION NOT FOUND (nothing written)')
    # NOT by bracket matching. The array is interleaved with prose comments
    # full of apostrophes ("the player's", "aren't"), and a scanner that
    # treats those as string delimiters loses its place immediately - which is
    # exactly what the first draft of this did. CARDS_MAP is built from CARDS
    # on the line after the array closes, so it is an unambiguous terminator
    # that needs no lexing at all.
    j = src.find('const CARDS_MAP=', i)
    if j < 0:
        sys.exit('CARDS_MAP MARKER NOT FOUND AFTER CARDS (nothing written)')
    return i, j


def row_span(src, cid):
    u"""Whole row by brace matching, so a row carrying an inline comment or
    spanning lines cannot be half-deleted. Returns (start, end) over the row
    INCLUDING its trailing comma and newline. Scoped to CARDS."""
    lo, hi = cards_bounds(src)
    key = "{id:'%s'" % cid
    i = src.find(key, lo, hi)
    if i < 0:
        sys.exit('ROW NOT FOUND IN CARDS: %s (nothing written)' % cid)
    if src.find(key, i + 1, hi) >= 0:
        sys.exit('ROW AMBIGUOUS x2+ INSIDE CARDS: %s (nothing written)' % cid)
    depth, j, instr, esc = 0, i, None, False
    while j < len(src):
        c = src[j]
        if instr:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == instr: instr = None
        elif c in '"\'':
            instr = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                j += 1
                break
        j += 1
    while j < len(src) and src[j] in ',\r\n':
        j += 1
        if src[j-1] == '\n':
            break
    # back up over the row's own leading indentation
    k = i
    while k > 0 and src[k-1] in ' \t':
        k -= 1
    return k, j


# ── 1. the seven re-pointed rows ─────────────────────────────────────
# (boss, source id, new NAME, icon source, rewardQuote)
# Icons are LIFTED from rows already in the file rather than typed as escapes -
# P861 shipped a chess glyph for a knot because a codepoint was transposed, and
# copying a working emoji cannot make that mistake.
ICON_FROM = {
    'second_wind':       'mabels_stitch',    # the needle and thread
    'gamblers_eye':      None,               # already an eye
    'loan':              'corvus_ledger',    # his book
    'frozen_die':        'brutus_fist',      # the fist
    'alchemists_chisel': None,               # the chisel IS the whetstone
    'double_down':       'whispers_hex',     # her glass
    'the_pyre':          None,               # already fire
}
REPOINT = [
    ('mabel',   'second_wind',       u"MABEL'S STITCH",
     u'\'"Take this. May it mend thy fortune."\'', 'brinksman'),
    ('finnick', 'gamblers_eye',      u"FINNICK'S EYE",
     u'\'"Not bad, mate! Keep this, yeah?"\'', 'sharp'),
    ('corvus',  'loan',              u"CORVUS'S NOTE",
     u'\'"Take the note. Consider it… a dividend."\'', 'hoarder'),
    ('brutus',  'frozen_die',        u"BRUTUS'S GRIP",
     u'\'"Iron in thy bones. Take this, soldier."\'', 'sharp'),
    ('aldric',  'alchemists_chisel', u"ALDRIC'S WHETSTONE",
     u'\'"Thou hast proven worthy. Take the stone that made my edge."\'', 'sharp'),
    ('whisper', 'double_down',       u"WHISPER'S WAGER",
     u'\'"The wager is yours, dear. Spend it well."\'', 'brinksman'),
    ('ambrose', 'the_pyre',          u"AMBROSE'S PYRE",
     u'\'"The heavens smiled upon thee. Accept this fire."\'', 'brinksman'),
]


def icon_of(src, cid):
    a, b = row_span(src, cid)
    m = re.search(r"icon:'([^']*)'", src[a:b])
    if not m:
        sys.exit('NO ICON ON %s (nothing written)' % cid)
    return m.group(1)


changed = []
for boss, cid, newname, quote, arch in REPOINT:
    donor = ICON_FROM[cid]
    icon = icon_of(s, donor) if donor else icon_of(s, cid)
    a, b = row_span(s, cid)
    row = s[a:b]
    # name
    row2 = re.sub(r"name:(\"[^\"]*\"|'[^']*')", 'name:"%s"' % newname, row, count=1)
    if row2 == row:
        sys.exit('NAME NOT REWRITTEN on %s (nothing written)' % cid)
    row = row2
    # icon
    row = re.sub(r"icon:'[^']*'", "icon:'%s'" % icon, row, count=1)
    # the boss tag and his line, inserted right after the icon so the row reads
    # the way the eight original boss rows read
    row = row.replace("icon:'%s'," % icon,
                      "icon:'%s',npc:'%s'," % (icon, boss), 1)
    if 'rewardQuote' in row:
        sys.exit('%s ALREADY HAS A rewardQuote (nothing written)' % cid)
    row = re.sub(r"arch:'[a-z]+'", "rewardQuote:%s,arch:'%s'" % (quote, arch), row, count=1)
    if 'rewardQuote' not in row:
        sys.exit('QUOTE NOT INSERTED on %s (nothing written)' % cid)
    s = s[:a] + row + s[b:]
    changed.append(cid)

# ── 2. the twenty rows go ────────────────────────────────────────────
OLD_BOSS = ['mabels_stitch', 'finnicks_palm', 'corvus_ledger', 'brutus_fist',
            'aldrics_vow', 'whispers_hex', 'ambrose_grace']
RETIRED = ['the_tab', 'seven_dice', 'sleight_of_hand', 'vanishing_act', 'old_bones',
           'coin_flip', 'the_nudge', 'alchemist_touch', 'twinning_charm',
           'double_down_die', 'broken_lantern', 'wild_die', 'all_in']
DELETE = OLD_BOSS + RETIRED
if len(DELETE) != 20:
    sys.exit('DELETE SET IS %d, THE BRIEF SAYS TWENTY (nothing written)' % len(DELETE))

for cid in DELETE:
    a, b = row_span(s, cid)
    s = s[:a] + s[b:]

# ── post-asserts, against the parsed table rather than the text ──────
m = re.search(r"const CARDS=\[", s)
if not m:
    sys.exit('CARDS DECLARATION LOST (nothing written)')
ids = re.findall(r"\{id:'([a-z_]+)'[^\n]*type:'active'", s)
_lo, _hi = cards_bounds(s)
for cid in DELETE:
    if s.find("{id:'%s'" % cid, _lo, _hi) >= 0:
        sys.exit('DELETED ROW SURVIVES IN CARDS: %s (nothing written)' % cid)
for boss, cid, newname, quote, arch in REPOINT:
    if ("npc:'%s'" % boss) not in s:
        sys.exit('BOSS TAG MISSING: %s (nothing written)' % boss)
if s.count('rewardQuote') != 8 + 7:
    # 8 boss ACTIVES (Grog's untouched row plus the seven re-pointed) and 7
    # boss PASSIVES. Seven, not eight: mabels_ward, corvus_book,
    # aldrics_banner, finnicks_trick, ambrose_chalice, brutus_grit and
    # whispers_veil exist, and there is no Grog passive at all. The count was
    # written as 8+8 on the assumption of symmetry and the assert caught it -
    # which is the only reason anyone counted.
    sys.exit('rewardQuote count is %d, expected 15 (8 boss actives + 7 boss '
             'passives) (nothing written)' % s.count('rewardQuote'))

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: re-pointed %d, deleted %d rows' % (len(changed), len(DELETE)))
print('  re-pointed:', ', '.join(changed))
