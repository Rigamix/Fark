# -*- coding: utf-8 -*-
"""P742: the match tooltip speaks short. Only at the table.

Denis: 'rephrase those tooltips to be more concise, less verbose - but
only for in match, not the other screens.' The shelf, the shop and the
peek panels are where a player reads and compares; mid-turn they need
the rule in one breath.

FAM_SHORT is a table of match-only lines - the same rule, said once,
tier variations folded into a suffix rather than three paragraphs. The
match focus asks for one and falls back to the authored text when a
card has none, so nothing can go missing and a new card simply reads
long until someone writes it a short line.
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
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == 1:
            old, new = old2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  ' + label)


SHORT = u"""/* P742: THE TABLE'S OWN WORDING. Short enough to read mid-turn; the
   shelf and shop keep the authored text, where a player is comparing
   rather than deciding. A card with no entry falls back to its own
   text, so nothing is ever missing. */
var FAM_SHORT={
  transmute:'Turn one rolled die to any face.',
  preserve:'Trap a kept 1 or 5 in amber. It is still there next turn, already scored.',
  honeytrap:'Your next roll pulls a die to match your pair. Guaranteed triple.',
  powder_keg:'Reroll everything, kept dice included.',
  sacrifice:'Shatter one of your dice for +800 now.',
  short_fuse:'From your third roll: double score. Bust after it and your bank burns too.',
  stargazer:'Peek at your next roll before you take it.',
  sleight:'Force the rival to reroll what they just rolled.',
  tamper:'Break one of the rival cards for this match.',
  ill_omen:'Their next roll is cursed.',
  cultivate:'Each jade wild that fires grows that die: +50 to its scores. Stacks.',
  bloom:'Straights and triples using a jade die score +300.',
  slow_cook:'Points tick in the longer your turn runs.',
  vanguard_f:'A scorer in the FIRST spot scores +200.',
  anchor_f:'A scorer in the LAST spot scores +200.',
  bookends_f:'Scorers at BOTH ends score +200 each.',
  fools_gold_f:'One die pays like gold, then shows itself false.',
  for_keeps:'Played at the seat: win and take one of their dice, lose and they take one of yours.',
  double_stakes:'Played at the seat: double the buy-in and the pot.',
  the_tab:'250 gold now. Owe 400 by last orders, or it costs a point.',
  hair_of_the_dog:'After a loss your first bank doubles - bust before banking and it costs a point.',
  marked_table:'The table is cursed for both of you tonight.',
  high_table:'Target up 500 for both. Win and the pot pays half again more.'
};
"""

sub(u"var FAM_NEEDS={honeytrap:'pair',preserve:'scorer'};",
    SHORT + u"var FAM_NEEDS={honeytrap:'pair',preserve:'scorer'};",
    'FAM_SHORT table')

sub(u"""  _cardFocusToggle(document.querySelectorAll('#famRowP .fcv')[i],{
    title:d.name.toUpperCase(),/* P673: the card's own pip carries the tier */
    sub:sub,body:d.text[inst.tier-1],col:col});""",
    u"""  /* P742: at the TABLE the short line, everywhere else the authored
     text - famCardHtml, the shelf and the peek panels all read d.text
     and are untouched. */
  var _body=(typeof FAM_SHORT!=='undefined'&&FAM_SHORT[inst.id])||d.text[inst.tier-1];
  _cardFocusToggle(document.querySelectorAll('#famRowP .fcv')[i],{
    title:d.name.toUpperCase(),/* P673: the card's own pip carries the tier */
    sub:sub,body:_body,col:col});""",
    'match focus reads short')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
