# -*- coding: utf-8 -*-
"""Map Denis's per-boss card art onto the game's NPC card ids.

card_art_map.py covers the FAMILY cards and knows nothing about the eight boss
folders that arrived with this batch. Same two failure modes it was written for,
and both are silent:

  * an id with no matching file renders a placeholder forever, and nobody
    notices because a placeholder is what an un-arted card is supposed to show
  * a FILE whose name matches no id renders nowhere and looks like art that was
    never drawn

THE NAMES DO NOT MAP NAIVELY, which is the whole reason this is a tool and not a
loop. The boss folders are camelCase with no prefix while the ids are snake_case,
and three of them lose or gain a word on the way:

    sundayRest    -> sundays_rest        (gains an s)
    quietDecree   -> the_quiet_decree    (gains "the_")
    royalPurse    -> the_royal_purse     (gains "the_")

So a camelCase->snake_case rule alone silently drops those three, and the symptom
is a blank card rather than an error. Matching is therefore done by NORMALISING
BOTH SIDES to bare letters and comparing, with the leading "the_" optional - and
anything still ambiguous or unmatched is REPORTED, never guessed.

  python tools/boss_card_art_map.py            # the report
  python tools/boss_card_art_map.py --write    # also emit assets/cards/<id>.webp
"""
import io, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

BOSSES = ['Aldric', 'Ambrose', 'Brutus', 'Corvus', 'Finnick', 'Grog', 'Mabel', 'Whisper']

# ── every card id the game defines, with the owner where it has one ──
# NOT a single-line {id:...} regex. NPC card literals span several lines, so
# that form matched 1 of 41 and every miss looked like missing art. Take every
# id, then look for an owner in the text that follows it.
ids = {}
for m in re.finditer(r"id:'([a-z0-9_]+)'", s):
    cid = m.group(1)
    tail = s[m.end():m.end() + 400]
    own = re.search(r"owner:'([a-z]+)'", tail)
    if cid not in ids or (ids.get(cid) is None and own):
        ids[cid] = own.group(1) if own else ids.get(cid)

def norm(x, drop_s=False):
    """bare lowercase letters, leading 'the' dropped. drop_s additionally
       ignores every s, and is only ever a SECOND pass - doing it always is
       lossy enough to collide (skim -> kim, severance -> everance)."""
    x = re.sub(r'[^a-zA-Z]', '', x).lower()
    if x.startswith('the'):
        x = x[3:]
    return x.replace('s', '') if drop_s else x

by_norm, by_norm_s = {}, {}
for cid in ids:
    by_norm.setdefault(norm(cid), []).append(cid)
    by_norm_s.setdefault(norm(cid, True), []).append(cid)

# ── EXPLICIT ALIASES, reviewed by hand, for the names no rule can bridge ──
# Every one of these is a word-level difference, not a spelling convention, so
# guessing them mechanically would be inventing a mapping rather than reading
# one. Left as data so the next person can see exactly what was decided.
ALIAS = {
    ('Aldric',  'theOath'):             'the_oath_npc',
    ('Aldric',  'verdict'):             'the_verdict_npc',
    ('Ambrose', 'blessedDie'):          'blessed_dice',
    ('Ambrose', 'judgement'):           'judgment_npc',      # -ement vs -ment
    ('Brutus',  'Veteran'):             'campaign_veteran',
    ('Brutus',  'ironGate'):            'iron_gate_npc',
    ('Brutus',  'oldPartner'):          'old_partners_badge',
    ('Corvus',  'Severance'):           'severance_npc',
    ('Mabel',   'LastStitch'):          'the_last_stitch_npc',
    ('Finnick', 'stickyFingers'):       'sticky_fingers_die',
}

# ── THE OWNER GATE, and it is not belt-and-braces ──
# Without it `stickyFingers.png` matched `sticky_fingers` - the FEAT ("win a
# match after lifting a rival bank"), not Finnick's `sticky_fingers_die` card.
# Two real, distinct ids that differ by a suffix, in a folder that names its
# owner. Denis flagged that exact pair as a conflation risk earlier; this is it
# happening in the tooling. A boss's folder may only map to a card that boss
# owns.
def owner_ok(boss, cid):
    o = ids.get(cid)
    return o is None or o == boss.lower()

rows, unmatched_files, ambiguous = [], [], []
for boss in BOSSES:
    d = os.path.join(ROOT, 'Art', 'Assets', 'Cards', boss)
    if not os.path.isdir(d):
        print('MISSING FOLDER: ' + d)
        continue
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith('.png'):
            continue
        stem = re.sub(r'^card_face_', '', os.path.splitext(f)[0])
        if (boss, stem) in ALIAS:
            rows.append((ALIAS[(boss, stem)], boss, os.path.join(d, f), True))
            continue
        cands = [c for c in by_norm.get(norm(stem), []) if owner_ok(boss, c)]
        if not cands:                       # second pass, plural-insensitive
            cands = [c for c in by_norm_s.get(norm(stem, True), []) if owner_ok(boss, c)]
        if len(cands) == 1:
            rows.append((cands[0], boss, os.path.join(d, f), stem != cands[0]))
        elif len(cands) > 1:
            ambiguous.append((stem, boss, cands))
        else:
            unmatched_files.append((stem, boss, os.path.join(d, f)))

matched_ids = set(r[0] for r in rows)

print('MATCHED (%d)' % len(rows))
for cid, boss, path, renamed in sorted(rows):
    print('  %-24s %-9s %s%s' % (cid, boss, os.path.relpath(path, ROOT),
                                 '   [FILENAME IS NOT THE ID]' if renamed else ''))

if ambiguous:
    print('\nAMBIGUOUS (%d) - normalising collided, resolve by hand:' % len(ambiguous))
    for stem, boss, cands in ambiguous:
        print('  %-24s %-9s -> %s' % (stem, boss, ', '.join(cands)))

if unmatched_files:
    print('\nART FILES MATCHING NO CARD ID (%d) - drawn but unreachable:' % len(unmatched_files))
    for stem, boss, path in unmatched_files:
        print('  %-24s %-9s %s' % (stem, boss, os.path.relpath(path, ROOT)))

# ── which npcOnly / boss-owned ids still have no art ──
owned = sorted(c for c, o in ids.items() if o in [b.lower() for b in BOSSES])
missing = [c for c in owned if c not in matched_ids]
if missing:
    print('\nBOSS-OWNED IDS WITH NO ART (%d):' % len(missing))
    for c in missing:
        print('  %-24s %s' % (c, ids[c]))

print('\nboss art files seen: %d   matched: %d   unmatched: %d   ambiguous: %d'
      % (len(rows) + len(unmatched_files) + len(ambiguous), len(rows),
         len(unmatched_files), len(ambiguous)))

if '--write' in sys.argv:
    print('\n(--write is handled by optimize_card_art.py, which owns the encoding)')
