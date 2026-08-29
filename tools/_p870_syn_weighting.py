# -*- coding: utf-8 -*-
u"""P870 (BOSS REWARD BRIEF section 11.3): NPC loadouts draw with synergy -
BEHIND A FLAG, OFF BY DEFAULT.

Denis: "the cards owned by bosses or patrons should be random, they should
have some sort of synergy with their dice, enchants, badges."

WHY THE FLAG, and it is the whole reason this is a separate patch. 11.1 and
11.2 make nights 6-8 EASIER. This makes every NPC HARDER, patrons included,
because a coherent loadout beats a random one - and it has the widest reach in
the brief and the vaguest magnitude. Shipped together, six levers move at once
and an overshooting batch tells you nothing about which one to back off. So
this lands dark: NPC_SYN_WEIGHTING is false, the draw is byte-for-byte the
path it has always been, and the second ladder run flips one boolean. The
delta is then attributable to this and nothing else.

WEIGHTED, NEVER FILTERED. Score each candidate at base weight 1, +2 for each
`syn` entry the NPC actually has - their dice materials, their badge id, their
enchants if they ever get any - then pick without replacement by weight
instead of shuffling. Untagged cards keep weight 1 and stay drawable, so:
  * a boss with a small pool and no matching tags still gets a full hand;
  * loadouts stay varied, which is what Denis asked to preserve;
  * adding a tag can never make a card undrawable, so a typo degrades instead
    of breaking;
  * with NO tags anywhere the distribution is today's, which is what lets the
    pools be tagged one boss at a time.

THE SIGNATURE IS DRAWN FIRST, then the remainder is weight-picked - so 11.2's
guarantee is untouched by this. Patrons have no signature and get the
weighting over their whole pool, which is the point: their pools are
persona-biased already.

TAGGED NON-SIGNATURE CARDS ONLY. A signature is drawn every time, so
up-weighting it changes nothing; tagging it would look like coverage and buy
none. The thirteen tags below are all on cards that compete for the remaining
slots, and each pairs with something the boss demonstrably HAS: Brutus's
hold-the-line pool against his Drill Order, Whisper's quiet decree against her
three jade dice and her jade2, Finnick's skim against his Pickpocket.

S.npcWonCards entries - cards the NPC won off the player - carry no tags and
therefore sit at base weight. That is correct and deliberate: a won card is
loot, not part of the character's kit, and it should be the least likely of
the set.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []
_INSERTED = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label); _INSERTED.append((label, new))
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label); _INSERTED.append((label, new))


# ── 1. the flag and the weighting machinery ──────────────────────────
sub(u"""var NPC_CARD_CAP=3;""",
    u"""var NPC_CARD_CAP=3;
/* \u2550\u2550\u2550 P870 (brief 11.3): SYNERGY WEIGHTING \u2014 OFF, DELIBERATELY \u2550\u2550\u2550
   This makes every NPC harder, patrons included, because a coherent loadout
   beats a random one. 11.1's cap and 11.2's reorder both make nights 6-8
   EASIER. Shipping all three live would move six levers at once and an
   overshooting batch would not say which to back off, so this ships dark and
   the second ladder run flips one boolean.
   WHILE FALSE THE DRAW IS THE PATH IT HAS ALWAYS BEEN - not an equivalent
   path, the same lines. That is what makes run one a clean baseline. */
var NPC_SYN_WEIGHTING=false;
/* What an NPC actually HAS, as a set the tags can be matched against: the
   materials in their dice, their badge id, and their enchants if they ever
   get any. Anything a `syn` entry can name lives in here. */
function _npcSynTraits(rung){
  var t={};
  if(!rung)return t;
  try{(rung.dice||[]).forEach(function(m){t[m]=1;});}catch(e){}
  try{if(rung.tell&&rung.tell.id)t[rung.tell.id]=1;}catch(e){}
  try{(rung.ench||[]).forEach(function(e){t[e]=1;});}catch(e){}
  return t;
}
/* base 1, +2 per matching tag. Untagged is 1, which is why an untagged pool
   draws exactly as it does today and why a typo in a tag can only ever make a
   card ORDINARY, never undrawable. */
function _npcSynWeight(cid,traits){
  var c=null;
  try{c=(typeof getNpcCard==='function'&&getNpcCard(cid))||(typeof getCard==='function'&&getCard(cid))||null;}catch(e){}
  var w=1;
  if(c&&c.syn&&c.syn.length)for(var i=0;i<c.syn.length;i++)if(traits[c.syn[i]])w+=2;
  return w;
}
/* pick n WITHOUT replacement, by weight. Never filters: every pool member
   keeps a non-zero chance, so a small pool with no matches still fills a
   hand. */
function _npcWeightedPick(pool,n,rung){
  var traits=_npcSynTraits(rung),out=[],p=pool.slice();
  while(out.length<n&&p.length){
    var tot=0,ws=[];
    for(var i=0;i<p.length;i++){var w=_npcSynWeight(p[i],traits);ws.push(w);tot+=w;}
    var r=Math.random()*tot,k=0;
    for(;k<p.length-1;k++){r-=ws[k];if(r<=0)break;}
    out.push(p[k]);p.splice(k,1);
  }
  return out;
}""",
    '1 flag + weighting')

# ── 2. the draw chooses its path ─────────────────────────────────────
sub(u"""  /* Shuffle and pick n */
  for(var i=pool.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=pool[i];pool[i]=pool[j];pool[j]=t;}
  var _picked=pool.slice(0,Math.min(n,pool.length));
  if(_sig&&_picked.indexOf(_sig)<0&&n>0){_picked[_picked.length-1]=_sig;}
  return _picked;""",
    u"""  var _picked;
  if(NPC_SYN_WEIGHTING){
    /* P870: signature FIRST, then weight-pick the rest - so 11.2's guarantee
       is untouched by the weighting and a signature is never competing with
       itself for its own slot. Patrons have no signature and get the
       weighting across their whole pool, which is the point of it for them. */
    _picked=_sig?[_sig]:[];
    var _rest=pool.filter(function(c){return c!==_sig;});
    _picked=_picked.concat(_npcWeightedPick(_rest,Math.max(0,Math.min(n,pool.length)-_picked.length),rung));
  }else{
    /* Shuffle and pick n */
    for(var i=pool.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=pool[i];pool[i]=pool[j];pool[j]=t;}
    _picked=pool.slice(0,Math.min(n,pool.length));
    if(_sig&&_picked.indexOf(_sig)<0&&n>0){_picked[_picked.length-1]=_sig;}
  }
  return _picked;""",
    '2 the draw picks its path')

# ── 3. the starter tags, all on NON-signature cards ──────────────────
TAGS = [
    ("one_more_round",     "last_call",    "GROG: another round against the bar-closing rule"),
    ("measure_twice",      "mending",      "MABEL: measure twice, roll twice"),
    ("the_skim",           "pickpocket",   "FINNICK: skimming and palming are the same hand"),
    ("sticky_fingers_die", "pickpocket",   "FINNICK: same"),
    ("the_audit",          "first_strike", "CORVUS: the audit against the per-roll charge"),
    ("fine_print",         "first_strike", "CORVUS: same"),
    ("campaign_veteran",   "drill_order",  "BRUTUS: the veteran under the roll cap"),
    ("iron_gate_npc",      "drill_order",  "BRUTUS: same"),
    ("point_of_order",     "still_waters", "ALDRIC: order against silenced dice"),
    ("the_oath_npc",       "still_waters", "ALDRIC: same"),
    ("crown_authority",    "kindred",      "WHISPER: authority against amplified enchants"),
    ("judgment_npc",       "reckoning",    "AMBROSE: judgment against matching his bank"),
    ("the_sermon",         "reckoning",    "AMBROSE: same"),
]
for cid, tag, why in TAGS:
    key = "{id:'%s'," % cid
    if s.count(key) != 1:
        sys.exit('TAG TARGET %s appears %d times (nothing written)' % (cid, s.count(key)))
    s = s.replace(key, "{id:'%s',syn:['%s']," % (cid, tag))
    edits.append('3 tag ' + cid)

# the brief's own second example: her decree pairs with her jade dice
sub(u"""{id:'the_quiet_decree',""",
    u"""{id:'the_quiet_decree',syn:['jade','jade2'],""",
    '3 tag the_quiet_decree')

# ── the guard: inserted prose must not contain a scanned literal ─────
_SCANNED = ['var NPC_SYN_WEIGHTING=false;', 'function _npcWeightedPick(',
            'function _npcSynWeight(', 'function _npcSynTraits(']
for _lbl, _new in _INSERTED:
    for _line in _new.split(chr(10)):
        _bare = _line.lstrip()
        if not _bare.startswith(('*', '/*', '//')):
            continue
        for _lit in _SCANNED:
            if _lit in _bare:
                sys.exit('COMMENT QUOTING CODE in %r: %r (nothing written)' % (_lbl, _lit))

# ── post-asserts ─────────────────────────────────────────────────────
if s.count('var NPC_SYN_WEIGHTING=false;') != 1:
    sys.exit('the flag is not declared exactly once, off (nothing written)')
for fn in ['function _npcSynTraits(', 'function _npcSynWeight(', 'function _npcWeightedPick(']:
    if s.count(fn) != 1:
        sys.exit('%s defined %d times (nothing written)' % (fn, s.count(fn)))
# the OLD path must survive intact - run one's baseline depends on it being
# the same lines, not an equivalent rewrite
if 'for(var i=pool.length-1;i>0;i--)' not in s:
    sys.exit('THE ORIGINAL SHUFFLE WAS NOT PRESERVED (nothing written)')
n_syn = len(re.findall(r"syn:\['", s))
if n_syn != 14:
    sys.exit('expected 14 tagged rows, found %d (nothing written)' % n_syn)
# no signature may be tagged - it is drawn every time, so a tag on it is
# coverage that buys nothing
try:
    _r = s[s.index('const RUNGS=['):s.index('var BOSS_ACCENT')]
    _sigs = [m.group(1) for m in re.finditer(r"cardPool:\['([a-z_0-9]+)'", _r)]
except Exception:
    sys.exit('could not read the signatures back (nothing written)')
for cid, tag, why in TAGS:
    if cid in _sigs:
        sys.exit('TAGGED A SIGNATURE (%s) - it is drawn every time, so the tag '
                 'cannot change anything (nothing written)' % cid)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits, %d tags, flag OFF' % (len(edits), n_syn))
