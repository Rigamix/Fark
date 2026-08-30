# -*- coding: utf-8 -*-
u"""P871 (LIVE BREAKAGE, mine): NPC_BUST_SAVES comes back. P863 deleted the
whole table and P863b only put back the bracket the parse error pointed at.

WHAT DENIS HIT: "npcs freeze when it's their turn sometimes, stopping keeping
dice. Which just makes it impossible to continue." Reproduced in one run - the
rival's turn throws `ReferenceError: NPC_BUST_SAVES is not defined`, phase
stays 'opp' forever, and the match cannot continue. "Sometimes" because the
throw is on the rival's BUST path: it fires only when they actually bust.

HOW I BROKE IT. P863's row deleter took each row from its own `{id:` to the
next one, and for a table's LAST row it fell back to the table's outer bound -
which I had set to the following top-level declaration rather than the array's
terminator. NPC_RESCUES' last row therefore ran all the way to the next `var`
and swallowed everything between: the terminator AND the entire
NPC_BUST_SAVES table, 130 lines, sitting quietly in the gap.

HOW I MISSED IT, WHICH IS THE PART WORTH KEEPING. The parse gate caught the
damage instantly and said "Unexpected token 'var'". I read that as "the array
lost its closing bracket", added the bracket, watched the gate go green, and
stopped. The gate was telling me the file no longer PARSED; I heard it saying
the file was missing a bracket. A syntax error localises where parsing failed,
not what was removed - and once the bracket was back, a file missing an entire
well-formed declaration parses perfectly. Nothing downstream could catch it
either: the probe suite covers the boss-card flow, the cap, the badge and the
save migration, and not one of them makes a rival bust.

THE CHECK THAT WOULD HAVE CAUGHT IT, and it is cheap: diff every top-level
declaration against the previous commit. Run now it names NPC_BUST_SAVES in
one line, with a count of live references pointing into the hole. That belongs
in the chain beside the parse gate for any patch that DELETES code, rather
than in a person's memory - so tools/zv_decl_diff.js is added with this patch.

RESTORED WITH ONE ROW DROPPED. The `stitch` entry keyed on mabels_stitch,
which P862 deleted from the catalog, so it can never fire and keeping it would
be dead code that reads live. Its effect survives as the boss card
second_wind, whose row sits directly below it - and that row's two hardcoded
"SECOND WIND" strings now read the card's display NAME, because the card is
called MABEL'S STITCH now and announcing a name the player cannot find is the
same class of bug one layer down.

ALSO FIXED HERE: S.npcWonCards had no migration. P863 taught the loader to
strip card ids that no longer resolve from S.run.cards and S.run.pouch, and I
missed the third persisted field holding card ids - the ones the RIVAL won off
the player, which generateOppCards pushes straight into their hand. A
returning save can otherwise deal the rival a card the catalog no longer has.
"""
import io, os, sys, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []

# The table is lifted from the last commit that still had it rather than
# retyped: a 130-line hand transcription is its own bug surface, and git is
# the authority on what was there.
SRC_COMMIT = '7b62754'


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


if 'NPC_BUST_SAVES=[' in s:
    sys.exit('NPC_BUST_SAVES IS ALREADY PRESENT - this patch has run (nothing written)')

# ── lift the table out of the pre-damage commit ──────────────────────
try:
    old = subprocess.run(['git', 'show', SRC_COMMIT + ':fark_proto.html'],
                         cwd=ROOT, capture_output=True).stdout.decode('utf-8')
except Exception as e:
    sys.exit('could not read %s from git: %s (nothing written)' % (SRC_COMMIT, e))
i = old.find('var NPC_BUST_SAVES=[')
j = old.find('var NPC_ARMS=[', i)
if i < 0 or j < 0:
    sys.exit('the table is not in %s either (nothing written)' % SRC_COMMIT)
table = old[i:j]
k = table.find('/* P769: THE ARM TABLE')      # that comment belongs to NPC_ARMS
if k > 0:
    table = table[:k]
table = table.rstrip()

# drop the `stitch` row - its card id no longer exists
a = table.find("  {name:'stitch',try:function(ctx){")
b = table.find("  {name:'secondWind',try:function(ctx){")
if not (0 < a < b):
    sys.exit('could not bound the stitch row (nothing written)')
table = table[:a] + table[b:]
if "'mabels_stitch'" in table:
    sys.exit('stitch references survived the row drop (nothing written)')

# the announce text follows the CARD, which is Mabel's Stitch now
OLD_MSG = ("    return {kind:'bank',pts:(r&&r.total)||0,cid:'second_wind',\n"
           "      msg:G.rung.name+' \u2014 SECOND WIND! ROLLING 3 DICE',\n"
           "      label:G.rung.name+' SECOND WIND!'};")
NEW_MSG = ("    /* P871: the NAME comes from the card row. second_wind displays as\n"
           "       MABEL'S STITCH since the boss-card pass, so two hardcoded strings\n"
           "       here would announce a card the player cannot find anywhere. */\n"
           "    var _swN=((typeof getCard==='function'&&getCard('second_wind'))||{}).name||'SECOND WIND';\n"
           "    return {kind:'bank',pts:(r&&r.total)||0,cid:'second_wind',\n"
           "      msg:G.rung.name+' \u2014 '+_swN+'! ROLLING 3 DICE',\n"
           "      label:G.rung.name+' '+_swN+'!'};")
if table.count(OLD_MSG) != 1:
    ms = re.findall(re.escape(OLD_MSG).replace('\\\n', '\n').replace('\n', '\\r?\n'), table)
    if len(ms) != 1:
        sys.exit('secondWind message anchor x%d (nothing written)' % len(ms))
    table = re.sub(re.escape(OLD_MSG).replace('\\\n', '\n').replace('\n', '\\r?\n'),
                   NEW_MSG.replace('\n', '\r\n'), table)
else:
    table = table.replace(OLD_MSG, NEW_MSG)

BANNER = (u"];\n"
          u"/* P871: RESTORED. P863 deleted this entire table as collateral when it\n"
          u"   removed NPC_RESCUES' last row, and the parse error that followed named a\n"
          u"   missing bracket - so only the bracket came back. Its absence threw on\n"
          u"   every rival bust, which is why the freeze was intermittent rather than\n"
          u"   constant, and why no probe caught it: none of them makes a rival bust. */\n")

sub(u"""];
var NPC_ARMS=[""", BANNER + table + u"\nvar NPC_ARMS=[", '1 NPC_BUST_SAVES restored')

# ── the third persisted card field gets the same strip as the other two ──
sub(u"""    S.run.pouch=S.run.pouch.map(function(cid){return _cardGone(cid)?null:cid;});""",
    u"""    S.run.pouch=S.run.pouch.map(function(cid){return _cardGone(cid)?null:cid;});
    /* P871: THE THIRD FIELD. S.npcWonCards holds cards the RIVAL won off the
       player, and generateOppCards pushes them straight into their hand - so a
       returning save could deal an opponent a card the catalog no longer has.
       P863 stripped the player's two fields and missed this one, which is the
       same "what else reads this" question one table over. */
    if(S.npcWonCards&&typeof S.npcWonCards==='object'){
      Object.keys(S.npcWonCards).forEach(function(k){
        if(Array.isArray(S.npcWonCards[k]))
          S.npcWonCards[k]=S.npcWonCards[k].filter(function(cid){return !_cardGone(cid);});
      });
    }""",
    '2 npcWonCards migrated')

# ── post-asserts ─────────────────────────────────────────────────────
if s.count('var NPC_BUST_SAVES=[') != 1:
    sys.exit('the table is not declared exactly once (nothing written)')
# SCOPED to the restored table. A file-wide test for 'mabels_stitch' fails on
# code this patch did not touch and should not: the id legitimately survives in
# a CSS rule, in the CARD_BG colour map, and in the bust block P865 marked dead.
# The claim is about the TABLE, so the assert must be about the table.
_tblStart = s.find('var NPC_BUST_SAVES=[')
_tblEnd = s.find('var NPC_ARMS=[', _tblStart)
if "'mabels_stitch'" in s[_tblStart:_tblEnd]:
    sys.exit('THE DEAD STITCH ROW CAME BACK WITH IT (nothing written)')
if s.count("{name:'secondWind'") != 1:
    sys.exit('the secondWind save is missing (nothing written)')
if 'S.npcWonCards[k].filter' not in s:
    sys.exit('npcWonCards strip missing (nothing written)')
_r = s.find('var NPC_RESCUES=['); _b = s.find('var NPC_BUST_SAVES=['); _a = s.find('var NPC_ARMS=[')
if not (0 < _r < _b < _a):
    sys.exit('the restored table is in the wrong place (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
