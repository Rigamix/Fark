# -*- coding: utf-8 -*-
"""P428 - the three recycled rule ids, and one genuinely dead font.

TWO APPROVED CLEANUPS, and the second one shrank on measurement.

1. RULE IDS. Three badges still showed a rule name with a different id
   underneath - FIRST STRIKE as `in_arrears`, STILL WATERS as `confession`,
   KINDRED as `counterfeit`. That divergence is what produced the Zero Hour bug
   fixed in P427: a `_RETIRED_RULES` entry naming the OLD rule silently
   switched off the NEW one wearing its id, everywhere except the boss's own
   badge. `_RETIRED_RULES` is empty today, so these three are harmless right
   now - and re-arm the identical trap the next time a rule is retired ahead of
   its replacement.

   SAVES CARRY THESE IDS. `S.run.sleeve` is a rule the player chose to wear and
   `S.run.tells` is a list of rules they WON off bosses, so a bare rename would
   silently orphan both - a player would lose a spoil they had earned. Migrated
   on load, next to the existing card-rename migration.

2. THE FONT. My Phase 5 note claimed "~58 CSS references to fonts that never
   paint", reading `document.fonts.status === 'unloaded'` as "unreferenced".
   Wrong: unloaded means the browser never FETCHED it, which happens whenever
   no rendered text has resolved to it YET. Measured properly - every screen,
   counting elements whose computed font-family names the family FIRST -
   IM Fell English reaches 61 elements, Uncial Antiqua 270, Jacquard 24 nine,
   Macondo seven. All live.

   Exactly ONE family is genuinely unreachable: Metamorphous, whose only
   occurrence in the file is its own @font-face. Press Start 2P is never first
   either, but it is the second entry in --font-px and therefore a real
   fallback, which is a legitimate reason to keep a face loaded.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

RENAMES = [('in_arrears', 'first_strike'),
           ('confession', 'still_waters'),
           ('counterfeit', 'kindred')]

# Every occurrence is the id as a quoted string, a CSS class suffix, or a
# switch case. Counted first so the rename is provably total rather than
# best-effort - a missed site is a rule that silently stops resolving.
# NOTE THE COUNTS ARE OCCURRENCES, NOT LINES. `grep -c` reports 14 for
# counterfeit and this reports 15, because one line names it twice. Pinning the
# grep number would have failed the assert on a correct patch - the kind of
# false alarm that teaches people to delete asserts.
before = {old: len(re.findall(r'\b%s\b' % old, s)) for old, _ in RENAMES}
assert before == {'in_arrears': 14, 'confession': 8, 'counterfeit': 15}, \
    'occurrence counts moved: %r' % before

for old, new in RENAMES:
    s = re.sub(r'\b%s\b' % old, new, s)

for old, new in RENAMES:
    assert not re.search(r'\b%s\b' % old, s), 'old id %s survives' % old
    assert len(re.findall(r'\b%s\b' % new, s)) >= before[old], \
        'new id %s under-applied' % new

# ── the save migration ────────────────────────────────────────────────
anchor = u"    /* Migrate stale boss-inventory state (from a removed earlier design) */\n"
assert s.count(anchor) == 1, 'migration anchor %d' % s.count(anchor)
s = s.replace(anchor,
  u"    /* RULE-ID MIGRATION (P428). Three badges carried a rule under the id of\n"
  u"       the rule it replaced: FIRST STRIKE as in_arrears, STILL WATERS as\n"
  u"       confession, KINDRED as counterfeit. The ids now match the rules.\n"
  u"       THIS RUNS BECAUSE SAVES HOLD THEM. S.run.sleeve is a rule the player\n"
  u"       chose to wear; S.run.tells is the list they WON off bosses. A bare\n"
  u"       rename would orphan both - the sleeve would resolve to nothing and a\n"
  u"       hard-won spoil would vanish off the shelf. Same shape as the\n"
  u"       last_call -> closing_bell card rename above. */\n"
  u"    var _ruleRename={in_arrears:'first_strike',confession:'still_waters',counterfeit:'kindred'};\n"
  u"    if(S.run.sleeve&&_ruleRename[S.run.sleeve])S.run.sleeve=_ruleRename[S.run.sleeve];\n"
  u"    if(Array.isArray(S.run.tells))S.run.tells=S.run.tells.map(function(t){return _ruleRename[t]||t;});\n"
  u"    /* a sealed seat's rule is rebuilt per night, but an in-flight night can\n"
  u"       be holding one across a reload */\n"
  u"    if(S.run.night&&S.run.night.sealTell&&_ruleRename[S.run.night.sealTell])\n"
  u"      S.run.night.sealTell=_ruleRename[S.run.night.sealTell];\n"
  + anchor)

# ── the dead font ─────────────────────────────────────────────────────
font = u"@font-face{font-family:'Metamorphous';src:url('assets/Fonts/Metamorphous.ttf') format('truetype')}\n"
assert s.count(font) == 1, 'Metamorphous face %d' % s.count(font)
s = s.replace(font,
  u"/* Metamorphous DELETED - the only occurrence of the name in this file was\n"
  u"   its own @font-face, so it was a download nothing could ever use. The four\n"
  u"   families reported alongside it were NOT dead: reading fonts.status as\n"
  u"   \"unreferenced\" was the mistake. IM Fell English reaches 61 elements,\n"
  u"   Uncial Antiqua 270, Jacquard 24 nine, Macondo seven, measured across all\n"
  u"   nine screens by computed font-family rather than by load state. The .ttf\n"
  u"   stays on disk; only the declaration goes. */\n")

assert s != orig, 'nothing changed'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P428 applied. renamed %d ids, dropped 1 font face' % len(RENAMES))
