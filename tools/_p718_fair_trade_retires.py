# -*- coding: utf-8 -*-
"""P718: Fair Trade retires; For Keeps pays its prize on the spot.

Denis's ruling (a), his words: once the For Keeps die is visible, "there's
genuinely nothing left in the reserve system worth keeping around."

- The card def and its FAM_LIVE entry go (the CFX plumbing stays dormant -
  it no-ops with no card to arm it, per the earlier audit). A migration
  filters fair_trade out of saved decks so a held copy vanishes cleanly.
- famFkTake stops feeding the invisible reserve: a taken die now asks
  WHICH SEAT IT TAKES - your six as chips on the same win-card surface,
  tap one and that die (and its brand: the {mat, ench} pair retires
  together, stated on screen) leaves the table; or leave the prize on
  theirs. The lucky-die path keeps its trophy bookkeeping (names, grudges)
  and is never seated - it was never a playable material.
- Boss relic spoils still land in the dead reserve - flagged in OPEN.md,
  not silently changed: relics may want to be trophies, not seats.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    global s, n
    c = s.count(old)
    if c != count and '\n' in old:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == count:
            old, c = old2, count
            new = new.replace('\n', '\r\n')
    if c != count:
        sys.exit('ANCHOR x%d (need %d) for %s' % (c, count, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── the card goes ──
sub(u" {id:'fair_trade',fam:'silver',kind:'active',name:'Fair Trade',charges:[1,1,2],\n"
    u"  text:['Before you roll, your weakest die makes way for the best die you have won off another table. For this turn only.',\n"
    u"        'Before you roll, your weakest die makes way for the best die you have won off another table. For this turn only.',\n"
    u"        'Before you roll, your weakest die makes way for the best die you have won off another table. For this turn only. Twice a match.']},\n",
    u" /* P718: fair_trade RETIRED (Denis's ruling a). Its whole premise was the\n"
    u"    invisible dice reserve; For Keeps seats its prize directly now, so\n"
    u"    there is nothing left for it to lend. CFX.fair_trade stays dormant. */\n",
    'fair_trade def retired')

sub(u"var FAM_LIVE={slow_cook:1,steady_hand:1,fair_trade:1,retort:1,reprisal:1,pickpocket:1,falling_star:1,",
    u"var FAM_LIVE={slow_cook:1,steady_hand:1,retort:1,reprisal:1,pickpocket:1,falling_star:1,/* P718: fair_trade out */",
    'fair_trade out of FAM_LIVE')

# ── saved decks shed it ──
sub(u"    if(S.run.night===undefined)S.run.night=null;",
    u"    if(S.run.night===undefined)S.run.night=null;\n"
    u"    /* P718: fair_trade retired - a held copy vanishes from the deck */\n"
    u"    if(Array.isArray(S.run.fcards))S.run.fcards=S.run.fcards.filter(function(c){return !c||c.id!=='fair_trade';});",
    'fair_trade migrates out of decks')

# ── For Keeps seats its prize ──
sub(u"function famFkTake(i){\n"
    u"  var pool=window._fkPool;if(!pool)return;\n"
    u"  var m=pool[i];if(!m)return;\n"
    u"  _getS();S.run.diceInv=S.run.diceInv||[];\n"
    u"  S.run.diceInv.push(m);\n"
    u"  _enchInit();\n"
    u"  var msg;\n"
    u"  if(m==='lucky'){\n"
    u"    S.run.luckyNames=S.run.luckyNames||[];S.run.luckyNames.push(window._fkLucky);\n"
    u"    S.run._grudges=S.run._grudges||{};\n"
    u"    if(window._fkPersona)S.run._grudges[window._fkPersona]=true;/* the archetype remembers */\n"
    u"    msg='✦ '+window._fkLucky+' IS YOURS — ITS OWNER WILL REMEMBER';\n"
    u"  }else msg=getDie(m).name+' IS YOURS';\n"
    u"  window._fkPool=null;save();\n"
    u"  var rc=document.querySelector('#end-ov .res-card');\n"
    u"  /* P689: the last debug-styled injection - monospace pink on the win card */\n"
    u"  if(rc)rc.innerHTML='<div style=\"font-family:'+\"'JMH Beda'\"+',serif;font-size:15px;color:#3a2812;padding:30px 12px;text-align:center;line-height:1.5\">'+msg+'</div>';\n"
    u"  _famEndReady();\n"
    u"}",
    u"function famFkTake(i){\n"
    u"  var pool=window._fkPool;if(!pool)return;\n"
    u"  var m=pool[i];if(!m)return;\n"
    u"  _getS();_enchInit();\n"
    u"  /* P718: THE PRIZE SEATS IMMEDIATELY. The invisible reserve retired with\n"
    u"     Fair Trade (Denis: only the six exist) - a real die now asks which\n"
    u"     seat it takes; the lucky die stays a trophy (names + grudges), it was\n"
    u"     never a playable material. */\n"
    u"  if(m==='lucky'){\n"
    u"    S.run.luckyNames=S.run.luckyNames||[];S.run.luckyNames.push(window._fkLucky);\n"
    u"    S.run._grudges=S.run._grudges||{};\n"
    u"    if(window._fkPersona)S.run._grudges[window._fkPersona]=true;/* the archetype remembers */\n"
    u"    window._fkPool=null;save();\n"
    u"    var rc=document.querySelector('#end-ov .res-card');\n"
    u"    if(rc)rc.innerHTML='<div style=\"font-family:'+\"'JMH Beda'\"+',serif;font-size:15px;color:#3a2812;padding:30px 12px;text-align:center;line-height:1.5\">'\n"
    u"      +'✦ '+window._fkLucky+' IS YOURS — ITS OWNER WILL REMEMBER</div>';\n"
    u"    _famEndReady();\n"
    u"    return;\n"
    u"  }\n"
    u"  window._fkTaken={mat:m};\n"
    u"  window._fkPool=null;save();\n"
    u"  _fkSeatOffer();\n"
    u"}\n"
    u"/* P718: the seat choice, on the same win-card surface the pick used -\n"
    u"   the win-screen trade decision's shape, no sheet, no new state. */\n"
    u"function _fkSeatOffer(){\n"
    u"  var t=window._fkTaken;if(!t)return;\n"
    u"  var rc=document.querySelector('#end-ov .res-card');if(!rc)return;\n"
    u"  var h='<div style=\"font-family:'+\"'JMH Beda'\"+',serif;color:#3a2812;padding:14px 10px;text-align:center\">'\n"
    u"    +'<div style=\"font-size:15px;letter-spacing:.06em;margin-bottom:4px\">'+getDie(t.mat).name.toUpperCase()+' IS YOURS</div>'\n"
    u"    +'<div style=\"font-size:11px;color:#6a5238;margin-bottom:10px\">tap the die it replaces — that one leaves the table</div>'\n"
    u"    +'<div style=\"display:flex;gap:10px;justify-content:center;flex-wrap:wrap\">';\n"
    u"  (S.run.dice||[]).forEach(function(mm,si){\n"
    u"    h+='<div onclick=\"_fkSeatDo('+si+')\" style=\"cursor:pointer;text-align:center\">'\n"
    u"      +'<span class=\"seat-die dtype-'+mm+'\" style=\"width:32px;height:32px;display:block;margin:0 auto\"></span>'\n"
    u"      +'<div style=\"font-size:9px;color:#6a5238;margin-top:3px\">'+getDie(mm).name+'</div></div>';\n"
    u"  });\n"
    u"  h+='</div>'\n"
    u"    +'<div style=\"font-size:11px;color:#8a6a3c;margin-top:12px;cursor:pointer;text-decoration:underline\" onclick=\"_fkSeatSkip()\">leave it on their table</div>'\n"
    u"    +'</div>';\n"
    u"  rc.innerHTML=h;rc.classList.add('show');\n"
    u"}\n"
    u"function _fkSeatDo(si){\n"
    u"  var t=window._fkTaken;if(!t)return;\n"
    u"  _getS();_enchInit();\n"
    u"  if(!S.run.dice||si<0||si>=S.run.dice.length)return;\n"
    u"  var out=S.run.dice[si],outE=S.run.dieEnch[si]||null;\n"
    u"  /* the pair travels together: the outgoing die takes its brand with it,\n"
    u"     the incoming die arrives unbranded - both stated on screen */\n"
    u"  S.run.dice[si]=t.mat;S.run.dieEnch[si]=null;\n"
    u"  window._fkTaken=null;save();\n"
    u"  var rc=document.querySelector('#end-ov .res-card');\n"
    u"  if(rc)rc.innerHTML='<div style=\"font-family:'+\"'JMH Beda'\"+',serif;font-size:15px;color:#3a2812;padding:30px 12px;text-align:center;line-height:1.5\">'\n"
    u"    +getDie(t.mat).name.toUpperCase()+' TAKES THE SEAT — '+getDie(out).name.toUpperCase()+' RETIRES'\n"
    u"    +(outE?'<div style=\"font-size:11px;color:#8a4a18;margin-top:6px\">its brand goes with it</div>':'')+'</div>';\n"
    u"  _famEndReady();\n"
    u"}\n"
    u"function _fkSeatSkip(){\n"
    u"  window._fkTaken=null;save();\n"
    u"  var rc=document.querySelector('#end-ov .res-card');\n"
    u"  if(rc)rc.innerHTML='<div style=\"font-family:'+\"'JMH Beda'\"+',serif;font-size:15px;color:#3a2812;padding:30px 12px;text-align:center\">LEFT ON THEIR TABLE</div>';\n"
    u"  _famEndReady();\n"
    u"}",
    'famFkTake seats the prize')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
