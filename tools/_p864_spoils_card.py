# -*- coding: utf-8 -*-
u"""P864 (BOSS REWARD BRIEF section 4): the spoils screen offers HIS CARD
where it offered his die. Badge / card / purse, take one, still final.

Denis: "No one will pick a relic as a reward if it's just visual." That
follows his own P834 ruling - relics became trophies, rank 0 against real
dice, never seated - so the relic tile was a keepsake competing against two
mechanical rewards and losing every time.

THE SHELF IS KEPT BY GRANTING, NOT BY OFFERING. The brief says "keep the
trophy shelf itself if it costs nothing; just stop offering the relic as a
pick", and dropping the tile alone would not do that - it would leave the
shelf permanently empty, because the spoils pick was the ONLY live route into
S.trophies (the other push sits in the dead night-8 branch below). A shelf
that can never gain an entry is not a kept shelf. So the boss's die is now
awarded automatically on every boss win. That is the P834 ruling followed
through: a trophy is not a reward, so it should not have to beat one - it
should just be yours for winning.

AMBROSE HAS A ROUTE AFTER ALL, and the first reading of this file said he did
not. The night-8 branch above reads `G.rung.key==='ambrose'` and Ambrose's
rung key is 'bishop' (RUNGS[7], and the file's own idiom for him is
key==='bishop' at the FEATS check). The branch has never fired: he falls
through to this one, _bossKey resolves him by NAME, and his three tiles render
correctly. So the brief's eighth card is winnable. Two consequences worth
stating rather than acting on:
  - the +150 renown and the ambrose_weight trophy in that branch have NEVER
    paid. That is a live reward that does not exist, and fixing the key would
    also DELETE Ambrose's spoils screen, which section 2 needs. It is left
    exactly as it is and marked dead in place; the ruling is Denis's.
  - the automatic trophy grant below means ambrose_weight now reaches the
    shelf by the ordinary route, which is the half of that branch's intent
    that can be honoured without a ruling.

The tile is inline-styled like its two neighbours and the grid is untouched at
1fr 1fr 1fr, so the layout question is "does the same 3-column grid still fit",
not "does a new layout fit".
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


# ── 1. the card is resolved, the trophy is granted, _spoils carries both ──
sub(u"""    var _spTell=G.rung&&G.rung.tell;
    var _spPurse=500+((S.run.tier||0))*60;
    window._spoils={relic:_spRelic,tell:_spTell?_spTell.id:null,purse:_spPurse,tellName:_spTell?_spTell.name:'',tellDesc:_spTell?_spTell.desc:''};""",
    u"""    var _spTell=G.rung&&G.rung.tell;
    var _spPurse=500+((S.run.tier||0))*60;
    /* P864: HIS CARD. Found by the npc: tag rather than by a second boss->card
       map - section 2 put exactly one type:'active' row on each boss, so the
       tag IS the map and a hand-written table beside it could only ever drift
       from it. */
    var _spCardObj=null;
    try{_spCardObj=CARDS.filter(function(c){return c.type==='active'&&c.npc===_spKey;})[0]||null;}catch(e){}
    /* P864: THE TROPHY IS GRANTED, NOT OFFERED. P834 made relics trophies -
       rank 0 against real dice, never seated - so the die was a keepsake
       competing with two mechanical rewards and losing every time (Denis: "no
       one will pick a relic as a reward if it's just visual"). Dropping the
       tile on its own would have left S.trophies with NO live writer at all,
       because this pick was its only one; the other push is in the night-8
       branch above, which has never fired. A shelf that cannot gain an entry
       is not a kept shelf, so winning the boss now puts his die on it. */
    try{
      if(_spRelic){S.trophies=S.trophies||[];
        if(S.trophies.indexOf(_spRelic)<0){S.trophies.push(_spRelic);save();}}
    }catch(e){}
    window._spoils={relic:_spRelic,tell:_spTell?_spTell.id:null,purse:_spPurse,
      tellName:_spTell?_spTell.name:'',tellDesc:_spTell?_spTell.desc:'',
      card:_spCardObj?_spCardObj.id:null,cardName:_spCardObj?_spCardObj.name:'',
      cardEff:_spCardObj?_spCardObj.eff:'',cardDesc:_spCardObj?_spCardObj.desc:'',
      cardIcon:_spCardObj?_spCardObj.icon:''};""",
    '1 card resolved + trophy granted')

# ── 2. the tile ──────────────────────────────────────────────────────
sub(u"""    var rd=_spRelic?getDie(_spRelic):null;
    sh+='<div onclick="_gbSpoilsConfirm(\\'relic\\')" style="cursor:pointer;aspect-ratio:2/3;display:flex;flex-direction:column;background:#191919;border:2px solid #dc5;padding:7px">'
      +'<div style="font-size:11px;font-weight:bold;color:#eee">'+(rd?rd.name:'RELIC')+'</div>'
      +'<div style="font-size:10px;color:#dc5;margin:2px 0">HIS DIE \u2014 A TROPHY FOR THE SHELF</div>'
      +'<div style="flex:1;font-size:10px;color:#bbb;line-height:1.45;margin-top:4px">'+(rd?rd.desc:'')+'</div></div>';""",
    u"""    /* P864: HIS CARD takes the relic's tile. Same inline styling and the same
       1fr 1fr 1fr grid as its neighbours, so this is the existing layout with
       a different first tile - not a new layout. The eff line sits where the
       relic's one-liner sat and the long text below it, so the three tiles
       still read as one row of the same shape. */
    sh+='<div onclick="_gbSpoilsConfirm(\\'card\\')" style="cursor:pointer;aspect-ratio:2/3;display:flex;flex-direction:column;background:#191919;border:2px solid #dc5;padding:7px">'
      +'<div style="font-size:11px;font-weight:bold;color:#eee">'+(_spCardObj?(_spCardObj.icon+' '+_spCardObj.name):'HIS CARD')+'</div>'
      +'<div style="font-size:10px;color:#dc5;margin:2px 0">'+(_spCardObj?_spCardObj.eff:'HIS CARD')+'</div>'
      +'<div style="flex:1;font-size:10px;color:#bbb;line-height:1.45;margin-top:4px">'+(_spCardObj?_spCardObj.desc:'')+'</div></div>';""",
    '2 the card tile')

# ── 3. the confirm ───────────────────────────────────────────────────
sub(u"""  var what=kind==='relic'?('his die \u2014 '+(sp.relic?getDie(sp.relic).name:''))
    :kind==='tell'?('his rule \u2014 '+(sp.tellName||''))
    :('his purse \u2014 '+sp.purse+'g');
  _gbModalOpen('<b>Take '+what+'?</b><div class="gbx-label">it is final \u2014 the other two go back behind the bar</div>'""",
    u"""  var what=kind==='card'?('his card \u2014 '+(sp.cardName||''))
    :kind==='tell'?('his rule \u2014 '+(sp.tellName||''))
    :('his purse \u2014 '+sp.purse+'g');
  /* P864: the boss slot equips immediately on win (see _rewardSelectCard), so
     taking a second boss card REPLACES the first. "It is final" was already
     true of the choice; this says what the choice costs. */
  var _held='';
  try{
    if(kind==='card'&&S&&S.run&&S.run.cards&&S.run.cards[0]&&S.run.cards[0]!==sp.card){
      var _hc=getCard(S.run.cards[0]);
      if(_hc)_held='<div class="gbx-label">it takes the boss slot \u2014 '+_hc.name+' goes back behind the bar</div>';
    }
  }catch(e){}
  _gbModalOpen('<b>Take '+what+'?</b><div class="gbx-label">it is final \u2014 the other two go back behind the bar</div>'+_held""",
    '3 the confirm')

# ── 4. the grant ─────────────────────────────────────────────────────
sub(u"""  if(kind==='relic'&&sp.relic){
    /* P834 (Denis, ruling b): relics are TROPHIES, not dice - they rank
       0 against real dice, so seating one was strictly worse than any
       die the player owns; the value is the shelf story. Same shelf the
       Ambrose night-8 win already uses (the RUN WON screen renders \U0001f3c6
       per entry). */
    S.trophies=S.trophies||[];
    if(S.trophies.indexOf(sp.relic)<0)S.trophies.push(sp.relic);
    msg='THE TROPHY GOES ON YOUR SHELF: '+getDie(sp.relic).name;
  }""",
    u"""  if(kind==='card'&&sp.card){
    /* P864: the boss slot, idx 0, which _rewardSelectCard already describes as
       "always available - signatures equip immediately on win". No usedCards
       seeding here: a match seeds every held active from its ROW at start
       (usedCards[cid]=cd.maxUses||1), so a card granted between matches picks
       up its charges on the next one for free.
       The relic no longer arrives here - it is granted automatically at the
       win, so the shelf keeps filling without the die having to beat two
       mechanical rewards to get there (P834's ruling, followed through). */
    S.run.cards=S.run.cards||[null,null,null,null];
    S.run.cards[0]=sp.card;
    msg='HIS CARD IS YOURS: '+(sp.cardName||sp.card);
  }""",
    '4 the grant')

# ── 5. the dead night-8 branch, marked in place ──────────────────────
sub(u"""  /* Night 8 (Ambrose): renown payout, his die is a trophy \u2014 no spoils */
  if(win&&isBoss&&G.rung&&G.rung.key==='ambrose'){""",
    u"""  /* Night 8 (Ambrose): renown payout, his die is a trophy \u2014 no spoils */
  /* P864: THIS BRANCH HAS NEVER FIRED AND IS LEFT THAT WAY DELIBERATELY.
     Ambrose's rung key is 'bishop' (RUNGS[7]; the file's own idiom for him is
     key==='bishop', see the FEATS check), so `key==='ambrose'` never matches
     and he falls through to the ordinary boss-spoils branch below - where
     _bossKey resolves him BY NAME and his tiles render correctly. That is why
     the brief's eighth card is winnable at all.
     Two things follow, and neither is fixed here. The +150 renown and the
     trophy push below have never paid, so that is a reward the game does not
     have. And correcting the key would DELETE Ambrose's spoils screen, which
     section 2 needs, so this is a design ruling and not a typo fix. The
     trophy half is already honoured: P864 grants every boss's die at the win,
     ambrose_weight included. Denis's call on the renown. */
  if(win&&isBoss&&G.rung&&G.rung.key==='ambrose'){""",
    '5 dead branch marked')

# ── post-asserts ─────────────────────────────────────────────────────
if "_gbSpoilsConfirm('relic')" in s or '_gbSpoilsConfirm(\\\'relic\\\')' in s:
    sys.exit('RELIC TILE SURVIVES (nothing written)')
if s.count("kind==='card'") != 3:
    # three, not two: the confirm tests it twice (the summary line and the
    # replaces-your-boss-slot note) and famSpoilsPick once.
    sys.exit("kind==='card' appears %d times, expected 3 (confirm x2 + pick) "
             "(nothing written)" % s.count("kind==='card'"))
for needed in ['_spCardObj', 'S.run.cards[0]=sp.card', 'cardEff:', 'HIS CARD IS YOURS']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
if 'grid-template-columns:1fr 1fr 1fr' not in s:
    sys.exit('THE 3-COLUMN GRID WAS DISTURBED (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
