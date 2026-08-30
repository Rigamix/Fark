# -*- coding: utf-8 -*-
u"""P888: the balance sim gave every silver-bearing loadout permanent bust
immunity, on both seats.

THE LINE. simTurn seeded a per-turn counter from the whole loadout:

    var saves = (dice6.indexOf('silver')>=0 ? 1 : 0) + (cs.charges.ward||0);

and spent it at the bust check, returning bank() instead of bust(). A turn can
only reach that check once - the save banks and ends the turn - so ONE silver
die anywhere in the loadout is a 100% bust save EVERY TURN, for the whole run.
It does not even require the die still to be in hand: `saves` is seeded from
dice6, the full loadout, not from the shrinking `mats`.

SILVER'S SAVE WAS RETIRED, and its own definition says so in as many words:
"RELIABILITY, NOT SAFETY. The old bust-save is gone: a free safe keep made the
last roll of a turn effectively bust-proof and made every bust-reactive card
pointless... It never removes the zero; every roll is still a real roll." Its
`effect` is null. It pays through its weighted rollTable [1,5,1,5,2,3,4,6],
which this sim already gets for free through _rollTable - so the line was
counting a retired mechanic a second time, on top of the weighting.

The file already argued against itself. Twenty lines below, inside bust():
"insurance retired: a bust takes the turn, and Ward - the enchant that replaced
it - halves rather than rescuing, and is not modelled here". And the standalone
harness recorded it from the other side as a known stale assumption in this
sim. Nobody carried either back to the line.

MEASURED. 100 tier-0 matches, one bone swapped for one silver, everything else
identical:
    iron,iron,flint,bone,bone,bone     784 player rolls, 91 scored nothing,
                                       91 busts recorded
    iron,iron,flint,bone,bone,silver   770 player rolls, 84 scored nothing,
                                       0 busts recorded, 84 saves consumed
    iron,iron,flint,bone,bone,silverx  783 player rolls, 80 scored nothing,
                                       80 busts recorded
`silverx` is Silver's roll table copied byte for byte under a different id, so
indexOf('silver') misses it. That isolates the defect to this one line, and it
shows the zero is not the true value: 84 turns really did roll nothing and
every one was swallowed. Silver's legitimate effect is visible and small - the
zero-score rate goes 0.116 to 0.102, not to 0.

AND MY OWN REPORT OF IT WAS WRONG. I wrote that every sim row reads
bustsPerMatch 0. It does not: it is zero exactly when the gear contains
'silver', which is G2-mid and G3-late - half the default table - and non-zero
for G0-bone and G1-early. The rows I was looking at came through callers that
pin a silver-bearing gear, so I generalised from a filtered view.

THE WARD TERM GOES TOO, and it is dead rather than wrong: famDef('ward') is
false - Ward is an ENCH_ICONS enchant, not a family card - and mkCards drops
any id famDef does not know, so cs.charges.ward can never be non-zero. Leaving
it would re-create this same bug the day a ward CARD is added, since the
enchant halves rather than rescues.

BLAST RADIUS, and this is why it is not just a metric. simTurn is shared, so
npcTurn seeds `saves` from rung.dice and the rival gets the same immunity when
its loadout carries silver. Every patronWin and bossWin ever produced for a
silver-bearing loadout on either seat is inflated. Measured at tier 0:
patronWin 18% with no silver, 24% with silver, 22% with the clone - so roughly
half of silver's apparent gain was the retired save rather than the weighting.
This lands before the ladder re-run, alongside the sim's G isolation.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new); edits.append(label); return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. the counter is gone ──────────────────────────────────────────
sub(u"""    var saves=(dice6.indexOf('silver')>=0?1:0)+(cs.charges.ward||0);""",
    u"""    /* P888: A FREE BUST SAVE FOR OWNING SILVER, AND IT IS RETIRED. This
       seeded a per-turn counter from the whole loadout and spent it at the
       bust check - and a turn reaches that check at most once, because the
       save banks and ends the turn. So one silver die anywhere was a 100%
       bust save every turn for the whole run, and it did not even need to
       still be in hand: the seed was dice6, not the shrinking mats.
       Silver's own def says the save is gone - "RELIABILITY, NOT SAFETY...
       It never removes the zero; every roll is still a real roll" - and its
       effect is null. It pays through its weighted rollTable, which this sim
       already gets through _rollTable, so this was counting a retired
       mechanic twice. bust()'s own comment below has said the same thing
       about the retired insurance for as long as it has been there.
       MEASURED, 100 tier-0 matches, one bone swapped for one silver: 84
       player rolls scored nothing and produced zero busts, while the same
       hand with a byte-identical clone of silver's roll table under another
       id produced 80. patronWin ran 18% / 24% / 22% across none / silver /
       clone, so half of silver's apparent gain was this line.
       THE WARD TERM WAS DEAD, not merely wrong: famDef('ward') is false -
       Ward is an enchant, not a family card - and mkCards drops unknown ids,
       so the charge could never be non-zero. It is removed rather than left,
       because the enchant HALVES rather than rescuing and leaving the term
       would re-create this bug the day a ward card exists. */""",
    '1 the free save is gone')

# ── 2. the branch that spent it ─────────────────────────────────────
sub(u"""        else if(saves>0){saves--;return bank();/* ward / silver: the bust is absorbed, the turn stands */}
        else return bust();""",
    u"""        else return bust();""",
    '2 the branch that spent it')

# ── 3. the manifest that advertised it ──────────────────────────────
sub(u"""     double_or_nothing, encore/fool's-gold/transmute as bust mitigation,
     ward + the silver die as bust saves. Unmodeled ids in a loadout are
     simply inert (targeted actives, preserve, honeytrap). \u2550\u2550\u2550 */""",
    u"""     double_or_nothing, encore/fool's-gold/transmute as bust mitigation.
     P888: ward and silver are NOT bust saves and are no longer modelled as
     them - silver's save is retired and its def says so, and ward is an
     enchant that halves rather than rescuing. Unmodeled ids in a loadout are
     simply inert (targeted actives, preserve, honeytrap). \u2550\u2550\u2550 */""",
    '3 the manifest')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
if 'saves' in code[code.index('function simTurn'):code.index('function playerTurn')]:
    sys.exit('the saves counter survives in simTurn (nothing written)')
if "indexOf('silver')" in code:
    sys.exit('a silver special-case survives in code (nothing written)')
if code.count('cs.charges.ward') != 0:
    sys.exit('the dead ward charge survives (nothing written)')
# the bust path must still exist and be reachable
_st = s.index('function simTurn')
_en = s.index('function playerTurn', _st)
if 'return bust();' not in s[_st:_en]:
    sys.exit('the bust path is gone (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
