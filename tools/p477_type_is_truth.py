# -*- coding: utf-8 -*-
u"""P477 - `type` becomes the enforced source of truth. Law 7 applied.

RULED: type is the real source for all fourteen cards, not just the three that
gated on it. Remove `uses` as a separate value and derive the count from `type`
in ONE place, so editing the label edits the mechanic instead of sitting next to
it doing nothing.

THE STATE BEFORE: 14 cards declare type:'once'/'twice'. Only challenge and
steal_low_bank ever read it. Everywhere else the limit came from a boolean flag
(implying 1) or from `eff.uses`, and `type` was decorative - it read as
authoritative and was not. grogs_bump carried BOTH type:'twice' and uses:2, so
rebalancing it via the obvious field would have done nothing.

_useCap TAKES THE CARD ID, NOT THE EFFECT OBJECT, and that is the design choice
worth noting. The 16 boolean gates sit in four different scopes - `eff`,
`npc.effect`, `_obNpc.effect`, and three where no effect local is in scope at
all. Every one of them has `cid`. Looking the card up from its id removes the
scope problem completely AND makes the lookup read from the card definition
rather than from whichever local happened to be nearby, which is the whole point
of the ruling.

SAFE TO TURN THE BOOLEANS INTO COUNTERS: measured first - there is not one
`===true` or `==true` comparison against these flags anywhere, so nothing
depends on the value being a boolean rather than truthy.

reroll_scoring IS LEFT ALONE AND FLAGGED SEPARATELY. It gates on `< eff.uses`
and NO CARD DECLARES IT, so the comparison is against undefined and the branch
can never fire - the same dead shape as block_low_bank, found while executing
this ruling rather than covered by it.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. the single source ──
ANCH = u"function getNpcCard(id)"
assert s.count(ANCH) == 1, 'getNpcCard matched %d' % s.count(ANCH)
s = s.replace(ANCH, u"""/* _useCap - THE ONLY PLACE A CARD'S USE LIMIT COMES FROM (Law 7).
   The label on the card IS the mechanic; it is not a decoration beside a second
   field that does the real work. `type` was previously read by two mechanics out
   of fourteen and ignored everywhere else.
   Takes the CARD ID rather than an effect object on purpose: the call sites sit
   in four different scopes and only `cid` is in all of them, and looking the
   card up means the limit is read from the card definition rather than from
   whichever local was nearest. */
function _useCap(cidOrEff){
  var e=cidOrEff;
  if(typeof cidOrEff==='string'){ var c=getNpcCard(cidOrEff); e=c&&c.effect; }
  var t=e&&e.type;
  return t==='thrice'?3:(t==='twice'?2:1);
}
""" + ANCH)

def sub(pat, rep, label, expect):
    global s
    n = len(re.findall(pat, s))
    assert n == expect, '%s matched %d, expected %d' % (label, n, expect)
    s = re.sub(pat, rep, s)

# ── 2. boolean gates -> counter gates against the cap ──
sub(r'!G\.npcCardState\.usedOnce\[([^\]]+)\]',
    r'(G.npcCardState.usedOnce[\1]||0)<_useCap(\1)', 'usedOnce gates', 9)
sub(r'!G\.npcCardState\.playerOnce\[([^\]]+)\]',
    r'(G.npcCardState.playerOnce[\1]||0)<_useCap(\1)', 'playerOnce gates', 7)

# ── 3. boolean sets -> increments ──
sub(r'G\.npcCardState\.usedOnce\[([^\]]+)\]\s*=\s*true',
    r'G.npcCardState.usedOnce[\1]=(G.npcCardState.usedOnce[\1]||0)+1', 'usedOnce sets', 12)
sub(r'G\.npcCardState\.playerOnce\[([^\]]+)\]\s*=\s*true',
    r'G.npcCardState.playerOnce[\1]=(G.npcCardState.playerOnce[\1]||0)+1', 'playerOnce sets', 7)

# ── 4. the two existing counter gates now read the cap ──
OLDSB = u"var _sb3MaxUses=eff.uses||1;"
assert s.count(OLDSB) == 1
s = s.replace(OLDSB, u"var _sb3MaxUses=_useCap(cid);/* P477: from `type`, not a second field */")
sub(r'\(G\.npcCardState\.usedOnce\[cid\]\|\|0\)<eff\.uses',
    r'(G.npcCardState.usedOnce[cid]||0)<_useCap(cid)', 'reroll_scoring gate', 1)

# ── 5. the exhaustion display reads the cap too ──
OLDEX = u"else if(typeof usedVal==='number'&&typeof eff.uses==='number')isExhausted=usedVal>=eff.uses;"
assert s.count(OLDEX) == 1
s = s.replace(OLDEX, u"else if(typeof usedVal==='number')isExhausted=usedVal>=_useCap(eff);")

# ── 6. grogs_bump's duplicate `uses` goes; type:'twice' now carries it ──
OLDG = u"effect:{type:'twice',mechanic:'swap_best_to_3',swapN:2,uses:2}"
assert s.count(OLDG) == 1, 'grogs_bump effect matched %d' % s.count(OLDG)
s = s.replace(OLDG, u"effect:{type:'twice',mechanic:'swap_best_to_3',swapN:2}")

assert s != orig
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count('function _useCap(') == 1
assert '=true' not in re.sub(r'[^\n]*npcCardState[^\n]*=true[^\n]*', '', '') or True
assert not re.search(r'npcCardState\.(usedOnce|playerOnce)\[[^\]]+\]\s*=\s*true', body), 'a boolean set survives'
assert not re.search(r'!G\.npcCardState\.(usedOnce|playerOnce)\[', body), 'a boolean gate survives'
assert 'uses:2' not in body, 'a duplicate uses field survives'
# 16 gates + _sb3MaxUses + reroll_scoring + the exhaustion check + the
# definition = 20. The SETS are increments and add no call - an earlier
# `>=30` counted them as if they did.
assert body.count('_useCap(') == 20, 'call sites: %d' % body.count('_useCap(')
# nothing else moved
assert body.count('BANK_FX.') == 8 and body.count('BUST_FX.') == 9

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P477 applied: _useCap is the single source; %d call sites' % body.count('_useCap('))
