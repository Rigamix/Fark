# -*- coding: utf-8 -*-
"""CORRECTION: which boss cards are actually inert?

I published "the boss holds cards and none of them work". That is WRONG, and
wrong in the direction that makes a finding look bigger than it is.

_npcFamCard(id) reads G.oF - the opponent's own family cards - and there are
TEN of them wired, not the four I reported: stargazer, slow_cook, sleight,
retort, preserve, pickpocket, ill_omen, honeytrap, encore, double_or_nothing.
Those DO have opponent behaviour. It lives in a hand-written NPC path rather
than in CFX, which is exactly the split P5 is meant to close - but "not on the
bus" is not "does nothing", and I conflated them.

Where the four came from: an earlier pass (cfx_bespoke) surfaced the
_npcFamCard sites that appeared among nine unexplained hits. That was a SUBSET
produced by a different question, and I carried its count into a claim about
the whole population without re-deriving it. Same shape as reading `missing[:6]`
as the data.

SO THE REAL QUESTION IS NARROWER: of the cards a boss can actually be DEALT,
which have neither a CFX hook that fires for the opponent nor an _npcFamCard
implementation? Those are the genuinely inert ones.

_famInitOpp deals only from the boss's OWN family, so the answer also depends
on which families bosses have - a card in nobody's family cannot be dealt at
all and its inertness costs nothing.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

def block(txt, start):
    b = txt.index('{', start)
    d, j = 0, b
    while j < len(txt):
        if txt[j] == '{':
            d += 1
        elif txt[j] == '}':
            d -= 1
            if d == 0:
                return txt[b:j + 1]
        j += 1
    return ''

# who the bosses are, and which family each brings
bf = re.search(r'\bBOSS_FAM\s*=\s*\{', s)
boss_fams = {}
if bf:
    for k, v in re.findall(r"([a-z_]+)\s*:\s*'([a-z]+)'", block(s, bf.end() - 1)):
        boss_fams[k] = v

# the live family cards, by family
fam_of, live = {}, set()
for m in re.finditer(r"\{id:'([a-z0-9_]+)',fam:'([a-z]+)'", s):
    fam_of[m.group(1)] = m.group(2)
lm = re.search(r'\bFAM_LIVE\s*=\s*\{', s)
if lm:
    live |= set(re.findall(r"([a-z0-9_]+)\s*:\s*1", block(s, lm.end() - 1)))
for arr in re.findall(r"\[([^\]]*)\]\.forEach\(function\(id\)\{FAM_LIVE\[id\]=1", s):
    live |= set(re.findall(r"'([a-z0-9_]+)'", arr))
live |= set(re.findall(r"FAM_LIVE\.([a-z0-9_]+)\s*=\s*1", s))

npc = set(re.findall(r"_npcFamCard\('([a-z0-9_]+)'\)", s))

# which cfx hooks fire for an opponent
HOOKS = ('roll', 'bank', 'bankBonus', 'turnStart', 'bust', 'commit',
         'deadRoll', 'rivalTurn')
opp_ok = {}
for m in re.finditer(r'\bCFX\.([A-Za-z_][\w]*)\s*=\s*\{', s):
    cid, body = m.group(1), block(s, m.end() - 1)
    for hm in re.finditer(r'\b(' + '|'.join(HOOKS) + r')\s*:\s*function\s*\(', body):
        hb = block(body, hm.end())
        if '_fxMine' not in hb:
            opp_ok.setdefault(cid, []).append(hm.group(1))

fams = sorted(set(boss_fams.values())) if boss_fams else sorted(set(fam_of.values()))
print('boss families: %s\n' % ', '.join(fams))
print('%-18s %-10s %-6s %-9s %s' % ('card', 'family', 'live', 'npc impl', 'opp-firing hooks'))
print('-' * 76)
inert = []
for cid, fam in sorted(fam_of.items(), key=lambda kv: (kv[1], kv[0])):
    if fam not in fams:
        continue
    if cid not in live:
        continue
    hooks = opp_ok.get(cid, [])
    has_npc = cid in npc
    print('%-18s %-10s %-6s %-9s %s'
          % (cid, fam, 'yes', 'yes' if has_npc else 'NO',
             ','.join(hooks) if hooks else '-'))
    if not has_npc and not hooks:
        inert.append((cid, fam))

print('\n' + '=' * 76)
print('GENUINELY INERT FOR A BOSS (%d): dealt by _famInitOpp, no NPC path, no'
      % len(inert))
print('opponent-firing hook.')
for cid, fam in inert:
    print('   %-18s %s' % (cid, fam))
print('\nNOT the "none of them work" I published. Ten cards have an NPC')
print('implementation; the gap is the ones above, and it is the ones above')
print('that P5 has to decide about.')
