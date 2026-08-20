# -*- coding: utf-8 -*-
"""P822: the patron die-family bias finally SELECTS something.

The leveling brief re-surfaces the master spec: trait biases the die
family (aggro->obsidian, hoard->amber, combo->vagabond/starstone,
straights->jade, ones->silver, triples->amber/jade). Recon verified
the gap: PERSONAS.dieBias never contained the family materials AND no
tier dicePool offers obsidian/silver/vagabond - the in-file P-note at
~24244 already knew: "a bias naming a material absent from every pool
selects nothing".

Two feeds, existing machinery untouched (the 60% bias pull filtered
through the tier pool does the leaning):
 1. dieBias gains each trait's family material, listed FIRST.
 2. The tier pools admit the family materials from tier 3 (night 4)
    up - nights 1-3 stay mundane, matching the '0-1 early' ramp the
    cards already follow.

Rival-side safety, checked before shipping: silver's 1/5-weighted
rollTable rides rollFace (the NPC's own roller - works both sides);
obsidian's shatter check lives only in the player's roll path, so a
rival obsidian is a stat-stick (OPEN.md notes it); vagabond's drag
is a player gesture - inert for rivals.
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


# 1) the trait's family material heads each bias list
sub("""const PERSONAS={
  ones:     {tags:['ONES'],            dieBias:['iron','lead','brass','crystal'], behavior:'safe'},
  triples:  {tags:['TRIPLES','COMBO'], dieBias:['amber','flint','jade'],          behavior:'chase'},
  straights:{tags:['STRAIGHTS','COMBO'],dieBias:['jade','jade2','flint'],         behavior:'chase'},
  aggro:    {tags:['AGGRO','ONES'],    dieBias:['iron','lead'],                   behavior:'normal'},
  hoard:    {tags:['HOARD'],           dieBias:['amber','crystal','lead'],        behavior:'safe'},
  combo:    {tags:['COMBO','TRIPLES'], dieBias:['amber','flint'],                 behavior:'normal'}
};""",
    """/* P822: each trait's FAMILY material heads its bias list (master brief:
   aggro->obsidian, hoard->amber, combo->vagabond/starstone,
   straights->jade, ones->silver, triples->amber/jade). The bias only
   selects what the tier pool offers, so nights 1-3 stay mundane and
   the family dice arrive with the night ladder. */
const PERSONAS={
  ones:     {tags:['ONES'],            dieBias:['silver','iron','lead','brass','crystal'], behavior:'safe'},
  triples:  {tags:['TRIPLES','COMBO'], dieBias:['amber','jade','flint'],          behavior:'chase'},
  straights:{tags:['STRAIGHTS','COMBO'],dieBias:['jade','jade2','flint'],         behavior:'chase'},
  aggro:    {tags:['AGGRO','ONES'],    dieBias:['obsidian','iron','lead'],        behavior:'normal'},
  hoard:    {tags:['HOARD'],           dieBias:['amber','crystal','lead'],        behavior:'safe'},
  combo:    {tags:['COMBO','TRIPLES'], dieBias:['vagabond','starstone','amber','flint'], behavior:'normal'}
};""",
    'family materials head the bias lists')

# 2) the tier pools admit them from night 4
sub("""    patronStats:{targetMin:5800,targetMax:7200,aggMin:.68,aggMax:.78,dicePool:['iron','lead','amber'],minBank:300,diceStop:2},""",
    """    patronStats:{targetMin:5800,targetMax:7200,aggMin:.68,aggMax:.78,dicePool:['iron','lead','amber','silver','obsidian'],minBank:300,diceStop:2},/* P822: family dice enter the ladder */""",
    'tier 3 pool')

sub("""    patronStats:{targetMin:6100,targetMax:7500,aggMin:.72,aggMax:.82,dicePool:['lead','flint','amber'],minBank:350,diceStop:2},""",
    """    patronStats:{targetMin:6100,targetMax:7500,aggMin:.72,aggMax:.82,dicePool:['lead','flint','amber','silver','obsidian','vagabond'],minBank:350,diceStop:2},/* P822 */""",
    'tier 4 pool')

sub("""    patronStats:{targetMin:7200,targetMax:8800,aggMin:.8,aggMax:.9,dicePool:['amber','jade','jade','starstone'],minBank:600,diceStop:1},""",
    """    patronStats:{targetMin:7200,targetMax:8800,aggMin:.8,aggMax:.9,dicePool:['amber','jade','jade','starstone','obsidian','silver','vagabond'],minBank:600,diceStop:1},/* P822 */""",
    'tier 5 pool')

sub("""    patronStats:{targetMin:7700,targetMax:9300,aggMin:.84,aggMax:.94,dicePool:['amber','jade','jade','starstone'],minBank:700,diceStop:1},""",
    """    patronStats:{targetMin:7700,targetMax:9300,aggMin:.84,aggMax:.94,dicePool:['amber','jade','jade','starstone','obsidian','silver','vagabond'],minBank:700,diceStop:1},/* P822 */""",
    'tier 6 pool')

sub("""    patronStats:{targetMin:8700,targetMax:10300,aggMin:.88,aggMax:.95,dicePool:['amber','jade','jade2','starstone'],minBank:800,diceStop:1},""",
    """    patronStats:{targetMin:8700,targetMax:10300,aggMin:.88,aggMax:.95,dicePool:['amber','jade','jade2','starstone','obsidian','silver','vagabond'],minBank:800,diceStop:1},/* P822 */""",
    'tier 7 pool')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
