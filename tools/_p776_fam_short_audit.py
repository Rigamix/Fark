# -*- coding: utf-8 -*-
"""P776: the table's own wording stops lying.

Denis's sighting (2026-08-19, screenshot): Fool's Gold's tap-sheet at
the table reads "One die pays like gold, then shows itself false" - a
CUT design. The card's real rule (authored text + CFX.fools_gold_f) is
the dead-roll auto-reroll with the double-fail burn. The audit that
followed found the FAM_SHORT table (P742, famCardTap's body at the
table) wrong in four ways:

  WRONG DESIGN   fools_gold_f (the cut 'false gold die'),
                 pickpocket + vanguard_f (both carry 'First die that
                 scores: +200' - vanguard's OLD chronological rule;
                 vanguard is positional now and pickpocket lifts at
                 the bank), ill_omen ('their next roll is cursed' -
                 it curses nothing; it is a declared wager),
                 marked_table (the old cursed-table-for-both line).
  TIER-BLIND     the table is flat strings, famCardTap shows the same
                 line at every tier: bloom said +300 beside tier 3's
                 +1000, retort 400 vs 700/1000, falling_star 1500+ vs
                 1200/1000, double_or_nothing 'lose half' vs a
                 third/a quarter.
  DEAD ENTRIES   anchor_f/bookends_f - cards cut from FAM_CARDS
                 (folded into vanguard's tiers), entries kept.
  'NOT WIRED UP YET'  _famWhyNot's line for any active without use()
                 - a lie for fools_gold_f (wired, fires on its own)
                 and for_keeps (wired, played at the seat).

The base fix, not the card fix: FAM_SHORT values may now be per-tier
ARRAYS and famCardTap picks by the instance's tier; a plain string
reads exactly as before. Deleted entries fall back to the authored
d.text, which is already tier-correct - so anchor_f/bookends_f/
marked_table simply lose their stale overrides.

NOT touched: tamper's 'for the night' vs the match-scoped break -
bosses are the only family-card holders and are faced once a night,
so the two windows coincide; noted in NPC_AI_BRIEF instead.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# ── 1. famCardTap picks per-tier when the entry is an array ──
sub("""  var _body=(typeof FAM_SHORT!=='undefined'&&FAM_SHORT[inst.id])||d.text[inst.tier-1];""",
    """  /* P776: a FAM_SHORT entry may be a per-tier array - the flat strings
     baked tier-1 numbers into every tier's sheet (bloom said +300
     beside tier 3's +1000). A plain string reads exactly as before. */
  var _sv=(typeof FAM_SHORT!=='undefined')?FAM_SHORT[inst.id]:null;
  if(_sv&&_sv.join)_sv=_sv[inst.tier-1]||_sv[0];
  var _body=_sv||d.text[inst.tier-1];""",
    'per-tier sheet body')

# ── 2. the wrong-design lines ──
sub("""  ill_omen:'Their next roll is cursed.',""",
    """  ill_omen:['Call their next turn a bust. Right: take 800. Wrong: they gain 400.',
            'Call their next turn a bust. Right: take 1200. Wrong: they gain 400.',
            'Call their next turn a bust. Right: take 1600. Wrong: they gain 300.'],""",
    'ill_omen is a wager, not a curse')

sub("""  vanguard_f:'First die that scores: +200.',
  pickpocket:'First die that scores: +200.',""",
    """  vanguard_f:['A scorer in the FIRST spot: +200.',
              'A scorer in either END spot: +350.',
              'End scorers +350 each. Both ends at once: +1200.'],
  pickpocket:['Every bank you make lifts 100 of their points.',
              'Every bank you make lifts 200 of their points.',
              'Every bank you make lifts 300 of their points.'],""",
    'vanguard positional, pickpocket lifts at the bank')

sub("""  fools_gold_f:'One die pays like gold, then shows itself false.',""",
    """  fools_gold_f:'Rolled nothing? Everything rerolls on its own. If the reroll fails too, the bust burns the same amount off your bank.',""",
    "fool's gold says what it does")

# ── 3. the tier-blind numbers ──
sub("""  bloom:'Straights and triples using a jade die score +300.',""",
    """  bloom:['Straights and triples using a jade die score +300.',
         'Straights and triples using a jade die score +600.',
         'Straights and triples using a jade die score +1000.'],""",
    'bloom per tier')

sub("""  retort:'Bust or be hit, and they lose 400.',""",
    """  retort:['Bust or be hit, and they lose 400.',
          'Bust or be hit, and they lose 700.',
          'Bust or be hit, and they lose 1000.'],""",
    'retort per tier')

sub("""  falling_star:'Bank 1500+ in a turn and take another turn at once.',""",
    """  falling_star:['Bank 1500+ in a turn and take another turn at once.',
                'Bank 1200+ in a turn and take another turn at once.',
                'Bank 1000+ in a turn and take another turn at once.'],""",
    'falling_star per tier')

sub("""  double_or_nothing:'After banking, flip: double it or lose half.',""",
    """  double_or_nothing:['After banking, flip: double it or lose half.',
                     'After banking, flip: double it or lose a third.',
                     'After banking, flip: double it or lose a quarter.'],""",
    'double_or_nothing per tier')

# ── 4. dead/stale overrides go; the authored text is the fallback ──
sub("""  anchor_f:'A scorer in the LAST spot scores +200.',
  bookends_f:'Scorers at BOTH ends score +200 each.',
""",
    """""",
    'anchor/bookends dead entries out')

sub("""  marked_table:'The table is cursed for both of you tonight.',
""",
    """""",
    'marked_table stale override out')

# ── 5. honest why-not for wired-but-not-tappable actives ──
sub("""    if(!fx||!fx.use)return 'NOT WIRED UP YET';""",
    """    /* P776: 'not wired' was a lie for cards that ARE wired but not
       tappable - the auto-fire and the seat-played say their moment. */
    if(!fx||!fx.use)return {
      fools_gold_f:'FIRES ON ITS OWN \\u2014 THE MOMENT A ROLL SCORES NOTHING',
      for_keeps:'PLAYED AT THE SEAT, AS YOU SIT DOWN'
    }[inst.id]||'NOT WIRED UP YET';""",
    'honest why-not')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
