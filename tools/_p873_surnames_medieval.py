# -*- coding: utf-8 -*-
u"""P873 (Denis, correcting P872): the surnames sound medieval again. The hint
moves from the DESCRIPTION to the etymology.

Denis: "too on the nose for most of them, they should still sound medieval:
Everyangle or OnetoSix is way, wayyyy too on the nose for example but most of
them are."

He is right and the failure is specific. P872 fixed the wrong half of the
problem. The originals were flat because they all had the SAME construction;
I replaced them with names that had varied construction but were flat in a new
way - they described the mechanic in plain modern English. A name that spells
out what the patron does is a label, not a name, and it stops being a person.

THE RULE THIS SET FOLLOWS: every surname is a real or period-plausible English
or Norman surname, and the playstyle hint lives in what the word MEANS or
connotes - never in a description of the rule.

  STEADY    Prudhomme  Norman "wise man" - the prudent one
            Pettifer   Norman "pied de fer", iron foot - unshakeable
            Reeve      a manor official; careful, administrative
            Thresher   patient repetitive work, the same stroke all day
            Cautley    a real place-name that carries caution in the sound

  GREEDY    Pinchbeck  a real surname, and a pinch of a thing
            Purseglove a real surname that is literally a purse
            Farthing   the smallest coin - he keeps even those
            Chapman    a trader; buys, never sells
            Skinflint  a genuine period word for a miser

  RECKLESS  Hotspur    Harry Hotspur, the byword for impetuous
            Wildgoose  a real surname, and the chase it names
            Armstrong  the border reivers' name; strong-armed, forward
            Rakehell   a period word for a man with no brakes
            Quarrel    a crossbow bolt AND a fight, in one word

  BULLISH   Strongbow  Richard de Clare's own byname
            Bullock    a young bull
            Hardcastle solid, immovable
            Bearward   a bear-keeper; brute company
            Mallet     a real surname and a blunt instrument

  ORDERLY   Marshall   one who marshals - puts things in their order
            Fletcher   arrow-maker; identical shafts, one after another
            Wainwright wagon-building, exact and sequential
            Ordway     a real surname carrying "ord", point/order
            Comber     a wool-comber, who straightens what is tangled

  CUNNING   Reynard    the trickster fox of medieval romance
            Foxglove   a poison that looks like a flower
            Trickett   a real surname with the trick inside it
            Sleight    the hand you do not see
            Slyfield   a real surname with the sly in plain sight

Nothing else changes: the per-persona split, the hash, the determinism and
P837's stable identity are all P872's and all stay. This is the word list.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

OLD = u"""  var _FAMN_BY_TRAIT={
    /* STEADY - banks small and often, never pushes */
    ones:['Slowhand','Tallyman','Pennyweight','Twicecount','Coldfoot'],
    /* GREEDY - sits on the pile and will not spend it */
    hoard:['Tightfist','Magpie','Deeppurse','Sockful','Neverlends'],
    /* RECKLESS - rolls into anything */
    aggro:['Neverblink','Breakneck','Hotblood','Onemore','Firebrand'],
    /* BULLISH - hunts three-of-a-kind */
    triples:['Threefold','Bullneck','Ironjaw','Thricelucky','Trebles'],
    /* ORDERLY - builds runs, keeps it tidy */
    straights:['Inarow','Straightlace','Dominoes','Ladderman','Onetosix'],
    /* CUNNING - plays the angles. Foxglove is the one survivor of the old
       twenty-four, and it lands here: a poison that looks like a flower. */
    combo:['Sleight','Sidewinder','Threadneedle','Foxglove','Everyangle']
  };"""

NEW = u"""  /* P873 (Denis: "too on the nose... they should still sound medieval"). The
     first attempt at this fixed the wrong half. The names it replaced were
     flat because they shared one CONSTRUCTION; what went in was varied in
     construction but flat in a new way - it described the mechanic in plain
     modern English, and a name that states what someone does is a label, not
     a person.
     THE RULE HERE: every entry is a real or period-plausible English or Norman
     surname, and the playstyle hint lives in what the word MEANS - never in a
     description of the rule. Prudhomme is "wise man"; Pettifer is iron-foot;
     Hotspur was a real byname for a man who would not wait; Reynard is the
     fox of the romances. A player who knows none of that still reads a name;
     one who feels the connotation reads a warning. */
  var _FAMN_BY_TRAIT={
    /* STEADY - patient, careful, administrative */
    ones:['Prudhomme','Pettifer','Reeve','Thresher','Cautley'],
    /* GREEDY - coin-words and a genuine period term for a miser */
    hoard:['Pinchbeck','Purseglove','Farthing','Chapman','Skinflint'],
    /* RECKLESS - bynames for men with no brakes */
    aggro:['Hotspur','Wildgoose','Armstrong','Rakehell','Quarrel'],
    /* BULLISH - brute mass, blunt instruments */
    triples:['Strongbow','Bullock','Hardcastle','Bearward','Mallet'],
    /* ORDERLY - trades that put things in sequence */
    straights:['Marshall','Fletcher','Wainwright','Ordway','Comber'],
    /* CUNNING - the fox, the poison that looks like a flower, the unseen hand */
    combo:['Reynard','Foxglove','Trickett','Sleight','Slyfield']
  };"""

if s.count(OLD) == 1:
    s = s.replace(OLD, NEW)
else:
    pat = re.escape(OLD).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d (nothing written)' % len(ms))
    m = ms[0]
    rep = NEW.replace('\n', '\r\n') if '\r\n' in m.group(0) else NEW
    s = s[:m.start()] + rep + s[m.end():]

# ── post-asserts ─────────────────────────────────────────────────────
_tbl = s[s.index('_FAMN_BY_TRAIT='):s.index('var _fh=0,_gn=')]
_names = re.findall(r"'([A-Za-z]+)'", _tbl)
if len(_names) != 30:
    sys.exit('expected 30 surnames, found %d (nothing written)' % len(_names))
if len(set(_names)) != 30:
    sys.exit('duplicate surnames %s (nothing written)'
             % sorted(set(n for n in _names if _names.count(n) > 1)))
for k in ('ones', 'hoard', 'aggro', 'triples', 'straights', 'combo'):
    if not re.search(r'\b%s:\[' % k, _tbl):
        sys.exit('persona %s has no surname pool (nothing written)' % k)

# THE ACTUAL COMPLAINT, made mechanical. A surname may not be built out of
# words that state the mechanic - that is what "on the nose" meant, and it is
# the one thing this patch exists to stop coming back. Checked against the
# NAMES only, never against the surrounding prose, which necessarily discusses
# them.
BANNED = ['one', 'two', 'three', 'thrice', 'twice', 'never', 'every', 'row',
          'straight', 'angle', 'count', 'hand', 'fist', 'blink', 'more',
          'treble', 'domino', 'ladder']
for n in _names:
    low = n.lower()
    for b in BANNED:
        if b in low:
            sys.exit('SURNAME %r CONTAINS THE MECHANIC WORD %r - that is the '
                     '"on the nose" failure this patch is fixing (nothing written)'
                     % (n, b))
for n in _names:
    if len(n) > 12:
        sys.exit('%s is as long as the pastoral set that was retired (nothing written)' % n)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: 30 medieval surnames, hint by etymology not description')
