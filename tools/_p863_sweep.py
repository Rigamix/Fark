# -*- coding: utf-8 -*-
u"""P863 (BOSS REWARD BRIEF section 2, the sweep half): everything P862's
twenty deleted rows left pointing at nothing.

THE ORDER IS THE BRIEF'S AND IT MATTERS. Section 7: delete the rows, run the
parse gate, THEN sweep - "not the other way round, or a live `case` in
activateCard points at a function that no longer exists". So P862 took the
rows, and this takes the references. The now-unreferenced activate* function
bodies are P864: removing a `case` that names a function is safe in either
order, but removing the FUNCTION while a case still names it is not.

THE ORPHAN LIST CAME FROM THE FILE, NOT FROM A GREP. P860's tripwire reported
it on the first boot after P862, by name:
  NPC_RESCUES -> old_bones, ambrose_grace, wild_die, brutus_fist, coin_flip, the_nudge
  NPC_ARMS    -> all_in, corvus_ledger, twinning_charm, aldrics_vow
That is the assertion doing the job it was built for, one patch after landing.

AND IT ALSO SHOWED ITS OWN BLIND SPOT, which is worth writing down. Two more
rows are just as dead and were NOT reported: NPC_RESCUES' finnicks_palm
resolves against the relic DIE of the same name, and NPC_ARMS' the_tab
resolves against the Amber family card of the same name. Both are members of
the six grandfathered collisions, so in each case a surviving row in a
DIFFERENT table vouched for a reference whose real target is gone. A clean
dangling list is not proof a reference is live - it is proof the id resolves
somewhere. Those two are deleted here on the same evidence as the other ten
(npcHasActive gates every rescue and every arm on the rival HOLDING the card,
and the rival can only hold a card the player can hold).

THE SAVE STRIP STOPS BEING A HAND-MAINTAINED LIST. The comment above
_removedCards already promises the right behaviour - "drop any equipped cards
that no longer exist in the catalog (e.g. removed in an update)" - and the
list was a stand-in for it that had drifted: it named 4 of P862's 20, so an
in-progress run holding any of the other 16 would keep a phantom id that
buildCBar counts when it lays out the fan (sizing a 3-card spread and drawing
2) and that _pcSlotHtml paints as a filled, draggable, nameless slot. Asking
the catalog is self-maintaining and cannot drift; the explicit list stays for
the historical ids that were never in the catalog to begin with.
The lookup is wrapped in try/catch rather than a typeof guard because CARDS is
a `const` - `typeof` on a const in its temporal dead zone throws rather than
returning 'undefined', so a typeof guard would be the bug it was meant to
prevent. On a throw the id is KEPT, because losing a real card to a load-order
accident is far worse than carrying a phantom.
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
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


DELETED = ['mabels_stitch', 'finnicks_palm', 'corvus_ledger', 'brutus_fist',
           'aldrics_vow', 'whispers_hex', 'ambrose_grace', 'the_tab', 'seven_dice',
           'sleight_of_hand', 'vanishing_act', 'old_bones', 'coin_flip', 'the_nudge',
           'alchemist_touch', 'twinning_charm', 'double_down_die', 'broken_lantern',
           'wild_die', 'all_in']

# ── 1. the switch cases ──────────────────────────────────────────────
cases = 0
for cid in DELETED:
    pat = re.compile(r"[ \t]*case '%s':[^\n]*\r?\n" % re.escape(cid))
    ms = list(pat.finditer(s))
    if len(ms) > 1:
        sys.exit('case x%d for %s (nothing written)' % (len(ms), cid))
    if ms:
        s = s[:ms[0].start()] + s[ms[0].end():]
        cases += 1
if cases != 20:
    sys.exit('removed %d cases, expected 20 (nothing written)' % cases)
edits.append('1 twenty switch cases')

# ── 2. NPC_RESCUES / NPC_ARMS rows ───────────────────────────────────
def table_bounds(src, decl, endmark):
    """The table's LAST ROW ends where the array's own `];` begins, which is
    not the same place as the next top-level declaration.

    The first version of this used the following declaration as the end
    marker, and deleting the LAST row of a table then swallowed the `];`
    along with it - both NPC_RESCUES and NPC_ARMS lost their terminator and
    the parse gate caught it immediately (`Unexpected token 'var'`). P863b
    repaired the two live tables; this is the same bug fixed at the source so
    a re-run from P862 produces correct output. `endmark` is kept only as the
    outer bound for the search."""
    i = src.find(decl)
    if i < 0:
        sys.exit('TABLE NOT FOUND: %s (nothing written)' % decl)
    outer = src.find(endmark, i)
    if outer < 0:
        sys.exit('TABLE OUTER BOUND NOT FOUND: %s (nothing written)' % decl)
    j = src.rfind('\n];', i, outer)
    if j < 0:
        sys.exit('TABLE TERMINATOR `];` NOT FOUND: %s (nothing written)' % decl)
    return i, j + 1


def drop_row(decl, endmark, cid, label):
    """Rows here carry function bodies, so the row is taken from its `{id:'x'`
    to the start of the NEXT `{id:` (or the table's end) - brace matching would
    have to lex the function bodies and their apostrophes."""
    global s
    lo, hi = table_bounds(s, decl, endmark)
    key = "{id:'%s'" % cid
    i = s.find(key, lo, hi)
    if i < 0:
        sys.exit('ROW NOT FOUND: %s in %s (nothing written)' % (cid, decl))
    nxt = s.find("{id:'", i + 1)
    end = nxt if (0 < nxt < hi) else hi
    k = i
    while k > 0 and s[k-1] in ' \t':
        k -= 1
    s = s[:k] + s[end:]
    edits.append(label)


# every rescue but Grog's: his is the one boss card P862 did not move, so his
# is the one rescue whose CARDS row still exists.
for cid in ['old_bones', 'ambrose_grace', 'wild_die', 'brutus_fist',
            'finnicks_palm', 'coin_flip', 'the_nudge']:
    drop_row('var NPC_RESCUES=[', 'var NPC_ARMS=[', cid, '2 rescue ' + cid)
# every arm but the loan: `loan` IS Corvus's Note now, so its row is live.
for cid in ['the_tab', 'corvus_ledger', 'twinning_charm', 'all_in', 'aldrics_vow']:
    drop_row('var NPC_ARMS=[', 'function ', cid, '3 arm ' + cid)

# ── 4. the literal id lists ──────────────────────────────────────────
sub("""var _GLINT_NEEDS_SELECTION=['frozen_die','coin_flip','the_nudge','twinning_charm','double_down_die','alchemist_touch','wild_die'];""",
    """/* P863: six of these seven cards are gone. frozen_die is Brutus's Grip now
   and is the only survivor that needs a selection before it can fire. */
var _GLINT_NEEDS_SELECTION=['frozen_die'];""",
    '4a glint list')

sub("""  const lingers=['mabels_stitch','aldrics_vow','whispers_hex','corvus_ledger','second_wind','all_in','broken_lantern'];""",
    """  /* P863: the ids, not the display names. second_wind IS Mabel's Stitch now
     and the_pyre is Ambrose's Pyre - both arm something that resolves later in
     the turn, which is what earns a persistent label. The five deleted ids
     that used to sit here are gone with their rows. */
  const lingers=['second_wind','loan','the_pyre'];""",
    '4b linger list')

# ── 5. the tripwire's grandfather list loses the two P862 retired ────
sub("""  the_tab:'CARDS active + the Amber family card. The CARDS row goes in section 2.',
  finnicks_palm:'CARDS active + his relic DIE. Two spoils tiles, one name, one icon - the brief section 6 case. The CARDS row goes in section 2.',""",
    """  /* P863: the_tab and finnicks_palm stood here until P862 deleted their CARDS
     rows, which is precisely what P860's entries said would happen. Removed
     rather than left to rot - a grandfather entry for a collision that no
     longer exists is a licence nobody is using, and the check reports stale
     entries as a console note so this one announced itself. */""",
    '5 grandfather trimmed')

# ── 6. the save strip asks the catalog ───────────────────────────────
sub("""    if(Array.isArray(S.run.cards))S.run.cards=S.run.cards.map(function(cid){return cid&&_removedCards.indexOf(cid)===-1?cid:null;});""",
    """    /* P863: ASK THE CATALOG, do not maintain a list of what left it. The
       comment above already promises this behaviour - "drop any equipped cards
       that no longer exist in the catalog (e.g. removed in an update)" - and
       the list had drifted from it: it named 4 of the 20 cards section 2
       deleted, so a run holding any of the other 16 kept a phantom id that
       buildCBar still COUNTS when it lays out the fan (a 3-card spread drawing
       2 cards, with a gap where the phantom would be) and that _pcSlotHtml
       paints as a filled, draggable, nameless slot, because .empty is gated on
       !cid rather than on whether the id resolves.
       try/catch, NOT typeof: CARDS is a const, and `typeof` on a const inside
       its temporal dead zone THROWS rather than returning 'undefined', so a
       typeof guard would be the very bug it was added to prevent. If the
       tables are not up yet the id is KEPT - losing a real card to a load-order
       accident is far worse than carrying a phantom for one boot. */
    var _cardGone=function(cid){
      if(!cid)return true;
      if(_removedCards.indexOf(cid)>=0)return true;
      try{return !(CARDS_MAP[cid]||NPC_CARDS_MAP[cid]);}catch(e){return false;}
    };
    if(Array.isArray(S.run.cards))S.run.cards=S.run.cards.map(function(cid){return _cardGone(cid)?null:cid;});""",
    '6a cards strip')

sub("""    S.run.pouch=S.run.pouch.map(function(cid){return cid&&_removedCards.indexOf(cid)===-1?cid:null;});""",
    """    /* P863: the pouch gets the same resolution test as the deck. It had NO
       removal migration beyond this list, and a phantom here is draggable into
       a deck slot - so a dead id could be shuffled around a run forever. */
    S.run.pouch=S.run.pouch.map(function(cid){return _cardGone(cid)?null:cid;});""",
    '6b pouch strip')

# ── post-asserts ─────────────────────────────────────────────────────
for cid in DELETED:
    if ("case '%s'" % cid) in s:
        sys.exit('CASE SURVIVES: %s (nothing written)' % cid)
if s.count("{id:'grogs_flask'") != 2:
    sys.exit("grogs_flask should be in CARDS and NPC_RESCUES (x2), found %d "
             "(nothing written)" % s.count("{id:'grogs_flask'"))
if s.count("{id:'loan'") != 2:
    sys.exit("loan should be in CARDS and NPC_ARMS (x2), found %d (nothing written)"
             % s.count("{id:'loan'"))
for needed in ['_cardGone', "_GLINT_NEEDS_SELECTION=['frozen_die']"]:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
# scoped to the grandfather object, because `finnicks_palm:` is ALSO a
# legitimate _RELIC_FAM key (the relic die keeps its name - the brief says so
# explicitly) and `the_tab:` appears in prose. A file-wide test for either
# string asserts against the wrong thing.
_gi = s.find('var _ID_GRANDFATHER={')
_ge = s.find('};', _gi)
if _gi < 0 or _ge < 0:
    sys.exit('GRANDFATHER BLOCK NOT FOUND (nothing written)')
_gblock = s[_gi:_ge]
for gone in ('the_tab:', 'finnicks_palm:'):
    if gone in _gblock:
        sys.exit('GRANDFATHER ENTRY SURVIVES: %s (nothing written)' % gone)
for kept in ('the_collector:', 'high_roller:', 'second_wind:', 'pickpocket:'):
    if kept not in _gblock:
        sys.exit('GRANDFATHER ENTRY LOST: %s (nothing written)' % kept)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % len(edits))
for e in edits:
    print('  ', e)
