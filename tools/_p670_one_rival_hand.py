# -*- coding: utf-8 -*-
"""P670: the rival holds ONE hand - the NPC cards join the family row, and the
legacy .mcard bar retires.

Denis: "On boss match I still see a doubling up of cards... a small one and
behind it, two big ones with the weathering effect I had asked to completely
remove." Then: "Proceed" on option (a) - one row, both sources.

WHAT THE DOUBLING WAS, measured in a real boss match: not one set drawn twice.
G.oF = [short_fuse] drawn as .fcv by famRenderRow, AND G.oCards =
[grogs_bump, her_lucky_coin] drawn as weathered .mcard by buildCBar into
#oppCards. Two systems, two looks, one screen. G.oCards is LIVE - about ninety
read sites, the whole NPC mechanic layer - so the cards must stay visible;
only the second renderer goes.

THE MAP CAME FIRST (seven readers over the file), and it is why this patch has
the shape it has:

  - buildCBar('oppCards',...) is called EXACTLY once, at match init. There is
    no mid-match rebuild of that bar - mid-match it only ever gets class
    toggles - so removing one call empties it for good.
  - triggerCard finds its flash target with a selector inside #oppCards and
    silently no-ops when it misses. Repointed at the family row, flashing with
    P666's own fx-pulse - the vocabulary exists precisely so this kind of site
    does not grow a second flash system.
  - _updateNpcCardVisuals reads usedOnce; npcUseActive reads npcActiveUses.
    Two exhaustion truths, and famRenderRow rebuilding every turn makes the
    gap LIVE: a rebuild would un-grey an exhausted active card because the
    updater cannot see npcActiveUses. One helper (_npcCardSpent) now holds the
    union, and both the bake and the updater call it.
  - The Pyre burn splices G.oCards and never re-renders - today the burned
    card's .mcard sits on screen forever, orphaned. In the fold the row is
    rebuilt from G.oCards at every turn start, so the burned card leaves at
    the next rebuild. A defect this patch removes by construction.
  - The weathering is a MutationObserver on .card-outer forcing aging level 3
    on npc/npcOnly cards. famCardArt emits no .card-outer, so drawing these
    cards as .fcv removes the weathering with no second change.
  - 16 of the 57 opponent-capable card ids have no webp in assets/cards/
    (the boss signature cards among them). The mcard system showed CARD_BG
    colour + the card's icon for those; the .fcv fallback does the same, as a
    cover the art paints over when it exists.

WHY famCardArt GROWS A BRANCH rather than a second builder existing: P591's
rule, "one builder, one look". The branch renders a def-less id from
CARDS/getNpcCard with no tier pip (npc cards have no tiers) and the cover
described above. Family cards are byte-identical to before.

WHAT DOES NOT CHANGE: #oppCards stays in the DOM (its #armLiftStrut is the
player bar's concern anyway); buildCBar keeps its two live player-bar callers;
the mid-match loadout panel keeps miniCardHTML and its hidden_cards gate; the
patron peek keeps its own renderers. Whisper's hidden_cards still does not
hide the table row - it did not hide the mcard bar either, and this patch
changes the renderer, not that rule.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── A. famCardArt learns the def-less card ──────────────────────────────
sub(u"function famCardArt(id,tier,opts){\n"
    u"  opts=opts||{};\n"
    u"  var d=famDef(id);if(!d)return '';",
    u"function famCardArt(id,tier,opts){\n"
    u"  opts=opts||{};\n"
    u"  var d=famDef(id);\n"
    u"  /* P670: AN NPC CARD THROUGH THE SAME BUILDER. The rival's G.oCards ids\n"
    u"     have no famDef - they live in CARDS/getNpcCard - and used to be drawn\n"
    u"     by buildCBar as weathered .mcard, which is the doubled look Denis\n"
    u"     reported. One builder, one look (P591): no tier pip because npc cards\n"
    u"     have no tiers, and a CARD_BG-coloured cover with the card's icon\n"
    u"     underneath the art, because 16 of the 57 opponent-capable ids have no\n"
    u"     webp - the cover is exactly what the mcard system showed for those. */\n"
    u"  if(!d){\n"
    u"    var c=(typeof CARDS!=='undefined'&&CARDS.find(function(x){return x.id===id;}))\n"
    u"          ||(typeof getNpcCard==='function'&&getNpcCard(id));\n"
    u"    if(!c)return '';\n"
    u"    return '<div class=\"fcv'+(opts.cls?' '+opts.cls:'')+'\" data-cid=\"'+c.id+'\"'\n"
    u"      +(opts.onclick?' onclick=\"'+opts.onclick+'\"':'')\n"
    u"      +(opts.style?' style=\"'+opts.style+'\"':'')+'>'\n"
    u"      +'<div class=\"fcvIn\">'\n"
    u"      +'<div class=\"fcvCover\" style=\"background:'+((typeof CARD_BG!=='undefined'&&CARD_BG[c.id])||'#444')+'\">'+(c.icon||'')+'</div>'\n"
    u"      +'<img src=\"assets/cards/'+c.id+'.webp\" alt=\"\" draggable=\"false\" onerror=\"this.remove()\">'\n"
    u"      +(opts.badge?'<span class=\"fcvBadge\">'+opts.badge+'</span>':'')\n"
    u"      +'</div></div>';\n"
    u"  }",
    'P670 famCardArt npc branch')

# ── B. one exhaustion truth ─────────────────────────────────────────────
sub(u"function _updateNpcCardVisuals(){\n"
    u"  if(!G||!G.oCards)return;\n"
    u"  var bar=document.getElementById('oppCards');if(!bar)return;\n"
    u"  G.oCards.forEach(function(cid){\n"
    u"    var mc=bar.querySelector('.mcard[data-cid=\"'+cid+'\"]');if(!mc)return;\n"
    u"    var npc=getNpcCard(cid);if(!npc)return;\n"
    u"    var eff=npc.effect||{};\n"
    u"    var usedVal=G.npcCardState.usedOnce[cid];\n"
    u"    var isExhausted=false;\n"
    u"    if(eff.type==='start_bonus')isExhausted=true;\n"
    u"    else if(typeof usedVal==='boolean')isExhausted=usedVal;\n"
    u"    else if(typeof usedVal==='number')isExhausted=usedVal>=_useCap(eff);\n"
    u"    mc.classList.toggle('used',isExhausted);\n"
    u"  });\n"
    u"}",
    u"/* P670: ONE EXHAUSTION TRUTH. _updateNpcCardVisuals read usedOnce and\n"
    u"   npcUseActive read npcActiveUses - two fields, two verdicts, and the gap\n"
    u"   went live the moment the row started rebuilding every turn: a rebuild\n"
    u"   would un-grey an exhausted active card because the updater cannot see\n"
    u"   the field the exhaustion lives in. Both writers and famRenderRow's bake\n"
    u"   now ask this one question. */\n"
    u"function _npcCardSpent(cid){\n"
    u"  try{\n"
    u"    var npc=getNpcCard(cid)||(typeof CARDS!=='undefined'&&CARDS.find(function(x){return x.id===cid;}));\n"
    u"    if(!npc)return false;\n"
    u"    var eff=npc.effect||{};\n"
    u"    var st=(G&&G.npcCardState)||{};\n"
    u"    if(st.npcActiveUses&&typeof st.npcActiveUses[cid]==='number'&&st.npcActiveUses[cid]<=0)return true;\n"
    u"    var usedVal=st.usedOnce&&st.usedOnce[cid];\n"
    u"    if(eff.type==='start_bonus')return true;\n"
    u"    if(typeof usedVal==='boolean')return usedVal;\n"
    u"    if(typeof usedVal==='number')return usedVal>=_useCap(eff);\n"
    u"  }catch(e){}\n"
    u"  return false;\n"
    u"}\n"
    u"function _updateNpcCardVisuals(){\n"
    u"  if(!G||!G.oCards)return;\n"
    u"  var bar=document.getElementById('oppCards');\n"
    u"  var row=document.getElementById('famRowO');\n"
    u"  G.oCards.forEach(function(cid){\n"
    u"    var spent=_npcCardSpent(cid);\n"
    u"    if(bar){var mc=bar.querySelector('.mcard[data-cid=\"'+cid+'\"]');if(mc)mc.classList.toggle('used',spent);}\n"
    u"    if(row){var fc=row.querySelector('.fcv[data-cid=\"'+cid+'\"]');if(fc)fc.classList.toggle('spent',spent);}\n"
    u"  });\n"
    u"}",
    'P670 one exhaustion truth')

sub(u"  /* Visual: dim the card in the opp bar */\n"
    u"  var chip=document.querySelector('#oppCards .mcard[data-cid=\"'+cid+'\"]');\n"
    u"  if(chip&&G.npcCardState.npcActiveUses[cid]<=0)chip.classList.add('used');",
    u"  /* Visual: dim the card in the opp bar - and its .fcv twin in the family\n"
    u"     row, which is where the rival's hand lives since P670 */\n"
    u"  var chip=document.querySelector('#oppCards .mcard[data-cid=\"'+cid+'\"]');\n"
    u"  if(chip&&G.npcCardState.npcActiveUses[cid]<=0)chip.classList.add('used');\n"
    u"  var _fc=document.querySelector('#famRowO .fcv[data-cid=\"'+cid+'\"]');\n"
    u"  if(_fc&&G.npcCardState.npcActiveUses[cid]<=0)_fc.classList.add('spent');",
    'P670 npcUseActive twin')

# ── C. the row draws both sources ───────────────────────────────────────
sub(u"    ho+=famCardArt(inst.id,inst.tier,{cls:'oppcard'+(_tg?' armed':'')+(inst.broken?' broken':''),\n"
    u"                                      onclick:'famOppTap('+i+')'});\n"
    u"  });\n"
    u"  hostO.innerHTML=ho;",
    u"    ho+=famCardArt(inst.id,inst.tier,{cls:'oppcard'+(_tg?' armed':'')+(inst.broken?' broken':''),\n"
    u"                                      onclick:'famOppTap('+i+')'});\n"
    u"  });\n"
    u"  /* P670: AND THE NPC CARDS, same row, same builder. These were buildCBar's\n"
    u"     weathered .mcard bar - the doubling Denis reported. G.oCards is the\n"
    u"     live NPC mechanic layer (~90 read sites), so the cards stay visible;\n"
    u"     only the second renderer went. Spent is BAKED here because this row is\n"
    u"     rebuilt every turn and a bake that disagreed with the updater would\n"
    u"     flicker - both ask _npcCardSpent. A card the Pyre burns leaves at the\n"
    u"     next rebuild, which the old bar never did (it was built once and the\n"
    u"     burned card sat orphaned on screen for the rest of the match). */\n"
    u"  (G&&G.oCards||[]).forEach(function(cid){\n"
    u"    ho+=famCardArt(cid,1,{cls:'oppcard npccard'+(_npcCardSpent(cid)?' spent':''),\n"
    u"                          onclick:\"npcOppTap('\"+cid+\"')\"});\n"
    u"  });\n"
    u"  hostO.innerHTML=ho;",
    'P670 the row draws both')

# ── D. the tap: what their card does ────────────────────────────────────
sub(u"function famOppTap(i){",
    u"/* P670: the npc card's read-sheet - the same shape famCardSheet builds for a\n"
    u"   family card, from the CARDS/getNpcCard def instead. Informational only,\n"
    u"   like famOppTap: their card, no PLAY button. */\n"
    u"function npcOppTap(cid){\n"
    u"  var c=(typeof CARDS!=='undefined'&&CARDS.find(function(x){return x.id===cid;}))\n"
    u"        ||(typeof getNpcCard==='function'&&getNpcCard(cid));\n"
    u"  if(!c)return;\n"
    u"  var spent=_npcCardSpent(cid);\n"
    u"  var h='<div style=\"text-align:center;padding:6px 4px 14px\">'\n"
    u"    +famCardArt(cid,1,{style:'width:38%;max-width:170px;margin:0 auto;display:inline-block'})\n"
    u"    +'<div style=\"font-family:'+\"'JMH Beda'\"+',serif;font-size:19px;color:#2a1808;margin-top:8px\">'+c.name+'</div>'\n"
    u"    +'<div style=\"font-size:12px;color:#6a5238;margin-top:2px\">'+(spent?'SPENT — used up for this match':'their card — read the table')+'</div>'\n"
    u"    +'<div style=\"font-size:14px;line-height:1.5;color:#3a2812;margin:10px auto 4px;max-width:88%\">'+_accG(c.desc||_sentenceCase(c.eff||''))+'</div>'\n"
    u"    +'</div>';\n"
    u"  _gbSheetOpen(h);\n"
    u"}\n"
    u"function famOppTap(i){",
    'P670 npcOppTap')

# ── E. the legacy bar retires; the row renders at init ──────────────────
sub(u"  // Build card bars\n"
    u"  buildCBar('oppCards',G.oCards,true,rung.name);\n"
    u"  buildCBar('playerCards',G.pCards,false,'YOU');\n"
    u"  _updateNpcCardVisuals();_updatePlayerCardVisuals();_applyMetaBoostVisuals();",
    u"  // Build card bars\n"
    u"  /* P670: the rival's .mcard bar is GONE - buildCBar('oppCards',...) was the\n"
    u"     second renderer behind the doubled cards. G.oCards now renders into the\n"
    u"     family row below, in the family row's look. The player bar keeps its\n"
    u"     builder (two live mid-match callers, and it is empty in real runs). */\n"
    u"  buildCBar('playerCards',G.pCards,false,'YOU');\n"
    u"  /* P670: and the row renders NOW rather than at the first turnStart -\n"
    u"     before this, a resumed match sat ~200ms (a fresh one ~800ms) with the\n"
    u"     rival's hand missing or holding the previous match's markup. */\n"
    u"  try{if(typeof famRenderRow==='function')famRenderRow();}catch(e){}\n"
    u"  _updateNpcCardVisuals();_updatePlayerCardVisuals();_applyMetaBoostVisuals();",
    'P670 retire the bar, render at init')

# ── F. triggerCard finds the family row ─────────────────────────────────
sub(u"  const barId=isPlayer?'playerCards':'oppCards';\n"
    u"  const bar=document.getElementById(barId);\n"
    u"  let mc=bar?bar.querySelector('.mcard[data-cid=\"'+cardId+'\"]'):null;",
    u"  const barId=isPlayer?'playerCards':'oppCards';\n"
    u"  const bar=document.getElementById(barId);\n"
    u"  let mc=bar?bar.querySelector('.mcard[data-cid=\"'+cardId+'\"]'):null;\n"
    u"  /* P670: the rival's cards are .fcv in the family row now, and this\n"
    u"     function used to no-op silently when the selector missed - every NPC\n"
    u"     trigger flash would simply have vanished with the bar. The flash on a\n"
    u"     .fcv is P666's own fx-pulse, not a second system. */\n"
    u"  const row=document.getElementById(isPlayer?'famRowP':'famRowO');\n"
    u"  const fcv=(!mc&&row)?row.querySelector('.fcv[data-cid=\"'+cardId+'\"]'):null;",
    'P670 triggerCard finds the row')

sub(u"  if(mc){\n"
    u"    mc.classList.remove('card-trigger');void mc.offsetWidth;\n"
    u"    mc.classList.add('card-trigger');\n"
    u"    setTimeout(function(){mc.classList.remove('card-trigger');},750);\n"
    u"  }",
    u"  if(mc){\n"
    u"    mc.classList.remove('card-trigger');void mc.offsetWidth;\n"
    u"    mc.classList.add('card-trigger');\n"
    u"    setTimeout(function(){mc.classList.remove('card-trigger');},750);\n"
    u"  }else if(fcv){\n"
    u"    fcv.classList.remove('fx-pulse');void fcv.offsetWidth;\n"
    u"    fcv.classList.add('fx-pulse');\n"
    u"    setTimeout(function(){fcv.classList.remove('fx-pulse');},520);\n"
    u"  }",
    'P670 the fx-pulse flash')

sub(u"  const labelParent=bar;\n"
    u"  if(mc&&labelParent){\n"
    u"    const lbl=document.createElement('div');\n"
    u"    lbl.className='card-trig-label'+(isPlayer?'':' opponent')+(persist?' persist':'');\n"
    u"    lbl.dataset.cid=cardId;\n"
    u"    lbl.textContent=msg;\n"
    u"    const cr=mc.getBoundingClientRect(),br=labelParent.getBoundingClientRect();",
    u"  /* P670: the label anchors to whichever element the card actually is - the\n"
    u"     legacy .mcard in its bar, or the .fcv in the family row. */\n"
    u"  const anchor=mc||fcv;\n"
    u"  const labelParent=mc?bar:row;\n"
    u"  if(anchor&&labelParent){\n"
    u"    const lbl=document.createElement('div');\n"
    u"    lbl.className='card-trig-label'+(isPlayer?'':' opponent')+(persist?' persist':'');\n"
    u"    lbl.dataset.cid=cardId;\n"
    u"    lbl.textContent=msg;\n"
    u"    const cr=anchor.getBoundingClientRect(),br=labelParent.getBoundingClientRect();",
    'P670 the label anchors to either')

# ── G. the CSS ──────────────────────────────────────────────────────────
sub(u"#screen-match #famRowO .fcv:nth-child(3){rotate:0deg}",
    u"#screen-match #famRowO .fcv:nth-child(3){rotate:0deg}\n"
    u"/* P670: the row can hold five now (up to 3 family + 2 npc on a late boss\n"
    u"   night) - the fan pattern covered three and children past it sat dead\n"
    u"   straight. */\n"
    u"#screen-match #famRowO .fcv:nth-child(4){rotate:-4deg}\n"
    u"#screen-match #famRowO .fcv:nth-child(5){rotate:4deg}",
    'P670 fan to five')

sub(u".fcv .fcvIn{position:relative;width:100%;height:100%}",
    u".fcv .fcvIn{position:relative;width:100%;height:100%}\n"
    u"/* P670: the art-less card's face - CARD_BG colour plus the card's icon,\n"
    u"   which is exactly what the mcard system showed for the 16 opponent ids\n"
    u"   with no webp. The img sits above it (z-index 1 vs 0) and simply paints\n"
    u"   over the cover when the art exists; onerror removes the img and the\n"
    u"   cover IS the face. */\n"
    u".fcv .fcvCover{position:absolute;inset:0;display:flex;align-items:center;\n"
    u"  justify-content:center;font-size:5cqw;z-index:0;border-radius:6%}\n"
    u".fcv .fcvIn img{position:relative;z-index:1}",
    'P670 the cover face')

sub(u"#screen-match #famRowO .fcv.broken{",
    u"/* P670: spent npc card, same statement as the player row's spent family\n"
    u"   card. The drop-shadows are repeated because filter REPLACES - the P668\n"
    u"   lesson, one selector up. */\n"
    u"#screen-match #famRowO .fcv.spent{\n"
    u"  filter:saturate(.25) brightness(.55)\n"
    u"         drop-shadow(0 0.2cqw 0.3cqw rgba(10,6,2,.55))\n"
    u"         drop-shadow(0 0.9cqw 1.4cqw rgba(10,6,2,.5))}\n"
    u"#screen-match #famRowO .fcv.broken{",
    'P670 spent look on the rival row')

sub(u".card-bar.top .card-trig-label{animation:cardTrigFloatDown 2.8s ease-out forwards}",
    u".card-bar.top .card-trig-label{animation:cardTrigFloatDown 2.8s ease-out forwards}\n"
    u"/* P670: trigger labels land in the family row now that the rival's cards\n"
    u"   live there - same float-down the top bar used. */\n"
    u"#famRowO .card-trig-label{animation:cardTrigFloatDown 2.8s ease-out forwards}",
    'P670 label animation in the row')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
