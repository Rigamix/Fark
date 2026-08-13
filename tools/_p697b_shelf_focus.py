# -*- coding: utf-8 -*-
"""P697b: the win screen wears the SHELF treatment, not the table's.

Denis, on seeing P697: "the focus state on cards should look like it does in
shelf screen or patron peek panel. You copied the one from the match screen
but as I said that state should ONLY be for the match screen. Other focus
states should all match the same style between dice, cards, etc."

So: revert the two P697 extensions to the match focus (it goes back to being
match-only, exactly as before), and give the win screen the fifth near-copy
of the shop/shelf focus - flown element + scrim + #xxFocusPanel - by the
P609 ruling (surfaces differ in root and scrim; the CSS is the shared part,
so #foFocusPanel simply joins the grouped selectors). The offer card's panel
carries a CLAIM plaque (the shop's BUY button, relabelled); the deck row and
everything else stays inspect-only with the shared close.
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
        sys.exit('ANCHOR x%d (need 1) for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── revert P697.1: the match focus mounts only in #screen-match again ──
sub(u"  /* P697: a card inside the WON overlay mounts its tip THERE - #end-ov is\n"
    u"     a stacking context above the tip's 9001, so a tip left in\n"
    u"     #screen-match would paint underneath the overlay it serves. The rect\n"
    u"     math below is container-relative either way; both boxes are the\n"
    u"     whole screen. */\n"
    u"  var ms=(el.closest&&el.closest('#end-ov'))||document.getElementById('screen-match')||document.body;\n"
    u"  /* P681: while a tip is open the status strips fade, so it never overlaps\n"
    u"     the score or the 'X IS ROLLING' line */\n"
    u"  try{document.getElementById('screen-match').classList.add('tip-open');}catch(e){}",
    u"  var ms=document.getElementById('screen-match')||document.body;\n"
    u"  /* P681: while a tip is open the status strips fade, so it never overlaps\n"
    u"     the score or the 'X IS ROLLING' line */\n"
    u"  try{ms.classList.add('tip-open');}catch(e){}",
    'P697b revert: focus mounts in #screen-match only')

# ── revert P697.2: the tip carries no button ──
sub(u"    +'<div class=\"cft-body\">'+_cftWords(_noOrphan(o.body||''),240)+'</div>'\n"
    u"    /* P697: the one button the focus ever carries - the win screen's\n"
    u"       CLAIM. At the table nobody passes btn and the focus stays a pure\n"
    u"       reading surface. */\n"
    u"    +(o.btn?'<div class=\"cft-btn\">'+o.btn+'</div>':'');\n"
    u"  ms.appendChild(tip);\n"
    u"  if(o.btn){var _bt=tip.querySelector('.cft-btn');if(_bt)_bt.onclick=function(ev){\n"
    u"    try{ev.stopPropagation();}catch(e){}\n"
    u"    var cb=o.cb;_cardFocusClose();if(cb)try{cb();}catch(e){}\n"
    u"  };}",
    u"    +'<div class=\"cft-body\">'+_cftWords(_noOrphan(o.body||''),240)+'</div>';\n"
    u"  ms.appendChild(tip);",
    'P697b revert: tip is read-only again')

# ── the wrappers become the fifth near-copy of the shelf focus ──
sub(u"/* P697: the win screen reads cards the same way the table does. The offer\n"
    u"   card's focus carries CLAIM; the drag-to-slot gesture stays the other\n"
    u"   door, untouched. The deck row reads without a button. */\n"
    u"function _foOfferTap(i){\n"
    u"  var o=_famOffer&&_famOffer[i];if(!o)return;\n"
    u"  var d=famDef(o.id);if(!d)return;\n"
    u"  var col=(FAMILIES[d.fam]||{}).color||'#f0c860';\n"
    u"  _cardFocusToggle(document.querySelectorAll('#end-ov .fo-offer .fcv')[i],{\n"
    u"    title:d.name.toUpperCase(),\n"
    u"    sub:FAMILIES[d.fam].name+' \\u00b7 '+(d.kind==='active'?'ACTIVE':'PASSIVE')\n"
    u"       +(d.consumable||d.id==='for_keeps'?' \\u00b7 BURNS ON USE':'')\n"
    u"       +(o.upgrade?' \\u00b7 UPGRADE':''),\n"
    u"    body:d.text[o.tier-1],col:col,below:true,\n"
    u"    btn:'CLAIM',cb:function(){famDraftPick(i);}});\n"
    u"}\n"
    u"function _foDeckTap(ci){\n"
    u"  _getS();var c=S.run&&S.run.fcards&&S.run.fcards[ci];if(!c)return;\n"
    u"  var d=famDef(c.id);if(!d)return;\n"
    u"  var col=(FAMILIES[d.fam]||{}).color||'#f0c860';\n"
    u"  _cardFocusToggle(document.querySelector('#end-ov .fo-slot[data-ci=\"'+ci+'\"] .fcv'),{\n"
    u"    title:d.name.toUpperCase(),\n"
    u"    sub:FAMILIES[d.fam].name+' \\u00b7 '+(d.kind==='active'?'ACTIVE':'PASSIVE'),\n"
    u"    body:d.text[c.tier-1],col:col});\n"
    u"}",
    u"/* P697b: THE WIN SCREEN WEARS THE SHELF TREATMENT (Denis: the match grow\n"
    u"   is match-only; dice, cards, shop and character panel all share the\n"
    u"   shop/shelf focus). Fifth near-copy of _loCardFocus by the P609 ruling -\n"
    u"   surfaces differ in root and scrim, the CSS is the shared part. The\n"
    u"   offer panel carries CLAIM (the shop's BUY plaque, relabelled); the\n"
    u"   drag-to-slot gesture stays the other door, untouched. */\n"
    u"function _foCardFocus(el,d,tier,opts){\n"
    u"  var ov=document.getElementById('end-ov');\n"
    u"  if(!ov||ov.classList.contains('fo-focus'))return;\n"
    u"  var col=(FAMILIES[d.fam]||{}).color||'#ffd98a';\n"
    u"  /* the scrim lives INSIDE .res-card: its stacking context is where the\n"
    u"     cards paint, so z50 sits under the zoomed card's 60 - the same\n"
    u"     geometry trick as #loFocusScrim, giant insets covering the screen */\n"
    u"  var host=ov.querySelector('.res-card')||ov;\n"
    u"  var scrim=document.getElementById('foFocusScrim');\n"
    u"  if(!scrim||!scrim.isConnected){scrim=document.createElement('div');scrim.id='foFocusScrim';host.appendChild(scrim);}\n"
    u"  scrim.onclick=_foUnfocus;\n"
    u"  var pan=document.getElementById('foFocusPanel');\n"
    u"  if(!pan){pan=document.createElement('div');pan.id='foFocusPanel';ov.appendChild(pan);}\n"
    u"  pan.innerHTML='<div class=\"fname\" style=\"color:'+col+';--fnoc:'+_fkDarker(col)+'\">'+_fkSheen(d.name)+'</div>'\n"
    u"    +'<div class=\"ffaces\"><span style=\"color:'+col+'\">'+FAMILIES[d.fam].name+'</span>'\n"
    u"      +'<span style=\"color:#cfc0a8\"> \\u00b7 '+(d.kind==='active'?'ACTIVE':'PASSIVE')\n"
    u"      +((d.consumable||d.id==='for_keeps')?' \\u00b7 BURNS ON USE':'')\n"
    u"      +((opts&&opts.upgrade)?' \\u00b7 UPGRADE':'')+'</span></div>'\n"
    u"    +'<div class=\"fdesc\">'+_accG(d.text[tier-1])+'</div>'\n"
    u"    +((opts&&opts.claim!=null)?'<div id=\"foClaimBtn\" onclick=\"_foClaim()\">'\n"
    u"      +'<img class=\"plq\" src=\"Art/Assets/Buttons/optimized/Button_new_02_opt.webp\" alt=\"\"><span>CLAIM</span></div>':'')\n"
    u"    +'<div id=\"foFBack\" onclick=\"_foUnfocus()\"><img src=\"Art/Assets/Icons/optimized/close_opt.webp\" alt=\"close\"></div>';\n"
    u"  window._foFocIdx=(opts&&opts.claim!=null)?opts.claim:null;\n"
    u"  var gr=ov.getBoundingClientRect(),nr=el.getBoundingClientRect();\n"
    u"  /* K and the landing height are _loCardFocus's numbers - one look */\n"
    u"  var K=2.05,wr=(Math.random()<0.5?-1:1)*(0.6+Math.random()*1.0);\n"
    u"  var ncx=nr.left+nr.width/2,ncy=nr.top+nr.height/2;\n"
    u"  var dx=(gr.left+gr.width/2)-ncx,dy=(gr.top+gr.height*0.365)-ncy;\n"
    u"  el.style.transition='transform .55s cubic-bezier(.3,1.35,.35,1)';\n"
    u"  el.style.transform='translate('+dx.toFixed(1)+'px, '+dy.toFixed(1)+'px) rotate('+wr.toFixed(1)+'deg) scale('+K+')';\n"
    u"  el.classList.add('zoom');\n"
    u"  ov.classList.add('fo-focus');\n"
    u"  window._foFocSp=el;\n"
    u"}\n"
    u"function _foUnfocus(){\n"
    u"  var ov=document.getElementById('end-ov');\n"
    u"  if(!ov||!ov.classList.contains('fo-focus'))return;\n"
    u"  ov.classList.remove('fo-focus');\n"
    u"  var sp=window._foFocSp;window._foFocSp=null;window._foFocIdx=null;\n"
    u"  if(sp){\n"
    u"    /* .fo-slot's resting transform is CSS-only, same as .loCard - clearing\n"
    u"       the inline one restores it (the P609 note, still true here) */\n"
    u"    sp.style.transition='transform .45s cubic-bezier(.3,1.2,.4,1)';\n"
    u"    sp.style.transform='';\n"
    u"    setTimeout(function(){sp.classList.remove('zoom');sp.style.transition='';},470);\n"
    u"  }\n"
    u"}\n"
    u"function _foClaim(){\n"
    u"  var i=window._foFocIdx;\n"
    u"  _foUnfocus();\n"
    u"  if(i!=null)famDraftPick(i);\n"
    u"}\n"
    u"function _foOfferTap(i){\n"
    u"  var o=_famOffer&&_famOffer[i];if(!o)return;\n"
    u"  var d=famDef(o.id);if(!d)return;\n"
    u"  var el=document.querySelectorAll('#end-ov .fo-offer .fo-card')[i];\n"
    u"  if(el)_foCardFocus(el,d,o.tier,{claim:i,upgrade:!!o.upgrade});\n"
    u"}\n"
    u"function _foDeckTap(ci){\n"
    u"  _getS();var c=S.run&&S.run.fcards&&S.run.fcards[ci];if(!c)return;\n"
    u"  var d=famDef(c.id);if(!d)return;\n"
    u"  var el=document.querySelector('#end-ov .fo-slot[data-ci=\"'+ci+'\"]');\n"
    u"  if(el)_foCardFocus(el,d,c.tier,null);\n"
    u"}",
    'P697b shelf-treatment near-copy')

# ── overlay entry closes the RIGHT focus now ──
sub(u"  try{_cardFocusClose();}catch(e){}/* P697: enter focus-clean */",
    u"  try{_cardFocusClose();}catch(e){}try{_foUnfocus();}catch(e){}/* P697b: enter focus-clean */",
    'P697b overlay entry closes both')

# ── the drag never starts under an open focus ──
sub(u"  offer.addEventListener('pointerdown',function(ev){\n"
    u"    var card=ev.target.closest&&ev.target.closest('.fo-card');if(!card)return;",
    u"  offer.addEventListener('pointerdown',function(ev){\n"
    u"    /* P697b: no drag out from under an open focus */\n"
    u"    try{if(document.getElementById('end-ov').classList.contains('fo-focus'))return;}catch(e){}\n"
    u"    var card=ev.target.closest&&ev.target.closest('.fo-card');if(!card)return;",
    'P697b drag guard under focus')

# ── the CSS: tip rules give way to the shelf plumbing ──
sub(u"/* P697: the focus serves the WON overlay too. Its tip mounts in #end-ov,\n"
    u"   where the #end-ov>* reset (position:relative;z-index:1) would win the\n"
    u"   cascade tie on specificity-equal #cardFocusTip - the id-qualified rule\n"
    u"   puts absolute back. cqw still resolves against #screen-match, the\n"
    u"   nearest size container, same as at the table. */\n"
    u"#end-ov>#cardFocusTip{position:absolute;z-index:9001}\n"
    u"/* the CLAIM plaque: P671b's gold, ink darker than trim; the tip itself\n"
    u"   is pointer-events:none, so the button re-arms its own */\n"
    u"#cardFocusTip .cft-btn{display:inline-block;pointer-events:auto;\n"
    u"  cursor:pointer;margin-top:2.2cqw;padding:1.6cqw 7cqw;\n"
    u"  font-family:'JMH Beda',serif;font-size:3.6cqw;letter-spacing:.1em;\n"
    u"  color:#241505;background:#c9a24a;border:2px solid #7a5a1c;\n"
    u"  border-radius:1.6cqw;box-shadow:0 2px 6px rgba(0,0,0,.5)}\n"
    u"#cardFocusTip .cft-btn:active{transform:translateY(1px)}",
    u"/* P697b: THE WIN SCREEN'S SHELF FOCUS. The panel joins the grouped\n"
    u"   #xxFocusPanel selectors (one look, five surfaces); this block is only\n"
    u"   the per-surface plumbing: the scrim (inside .res-card, whose stacking\n"
    u"   context is where the cards paint - z50 under the zoomed 60, giant\n"
    u"   insets covering the screen, the #loFocusScrim trick), the zoom lifts,\n"
    u"   and the chrome that sits ABOVE .res-card in #end-ov's own stack\n"
    u"   (win-board z3, skip z6, end-btns, resDlg) fading out for the read. */\n"
    u"#foFocusScrim{position:absolute;left:-60cqw;right:-60cqw;top:-100cqh;bottom:-100cqh;z-index:50;\n"
    u"  opacity:0;pointer-events:none;transition:opacity .35s;background:rgba(8,5,2,.78);\n"
    u"  -webkit-backdrop-filter:blur(6px) brightness(.55);backdrop-filter:blur(6px) brightness(.55)}\n"
    u"#end-ov.fo-focus #foFocusScrim{opacity:1;pointer-events:auto}\n"
    u"/* the #end-ov>* reset would win the cascade tie against the grouped\n"
    u"   panel rule - two ids put absolute back */\n"
    u"#end-ov>#foFocusPanel{position:absolute;z-index:55}\n"
    u"#end-ov .fo-card,#end-ov .fo-slot{transition:transform .18s ease,opacity .3s ease}\n"
    u"#end-ov .fo-card.zoom,#end-ov .fo-slot.zoom{z-index:60}\n"
    u"#end-ov.fo-focus .fo-card:not(.zoom),#end-ov.fo-focus .fo-slot:not(.zoom){opacity:0;pointer-events:none}\n"
    u"#end-ov.fo-focus>.fo-skip,#end-ov.fo-focus #end-btns,#end-ov.fo-focus .win-board,\n"
    u"#end-ov.fo-focus #resDlg,#end-ov.fo-focus .fo-title{opacity:0 !important;pointer-events:none !important;transition:opacity .3s}\n"
    u"#end-ov.fo-focus #foFocusPanel{opacity:1;pointer-events:auto;transform:none;transition-delay:.18s}\n"
    u"/* CLAIM: the shop's BUY plaque, relabelled */\n"
    u"#foClaimBtn{position:relative;width:64%;max-width:300px;aspect-ratio:934/235;margin:2.6cqh auto 0;cursor:pointer;\n"
    u"  display:flex;align-items:center;justify-content:center;transition:transform .1s}\n"
    u"#foClaimBtn:active{transform:scale(.96)}\n"
    u"#foClaimBtn img.plq{position:absolute;inset:0;width:100%;height:100%;object-fit:fill;pointer-events:none}\n"
    u"#foClaimBtn span{position:relative;z-index:1;font-family:'JMH Beda',serif;font-size:2.9cqh;letter-spacing:.06em;color:#402d14;\n"
    u"  text-shadow:0 -1px 0 rgba(120,85,45,.35),0 1px 0 rgba(255,246,220,.6)}",
    'P697b CSS plumbing')

# ── the panel joins every grouped rule ──
sub(u"#stFocusPanel,#loFocusPanel,#ptFocusPanel{position:absolute;left:6%;right:6%;top:53%;z-index:55;text-align:center;color:#fff;",
    u"#stFocusPanel,#loFocusPanel,#ptFocusPanel,#foFocusPanel{position:absolute;left:6%;right:6%;top:53%;z-index:55;text-align:center;color:#fff;",
    'grouped: panel base')
sub(u"#stFocusPanel .fname,#loFocusPanel .fname,#ptFocusPanel .fname{\n"
    u"  position:absolute;left:0;right:0;top:-41cqh;font-size:6.4cqh !important}",
    u"#stFocusPanel .fname,#loFocusPanel .fname,#ptFocusPanel .fname,#foFocusPanel .fname{\n"
    u"  position:absolute;left:0;right:0;top:-41cqh;font-size:6.4cqh !important}",
    'grouped: fname band')
sub(u"#stFocusPanel .fname,#loFocusPanel .fname,#ptFocusPanel .fname{font-family:'JMH Beda',serif;font-size:3.8cqh;color:#f6ecd4;letter-spacing:.09em;",
    u"#stFocusPanel .fname,#loFocusPanel .fname,#ptFocusPanel .fname,#foFocusPanel .fname{font-family:'JMH Beda',serif;font-size:3.8cqh;color:#f6ecd4;letter-spacing:.09em;",
    'grouped: fname font')
sub(u"#stFocusPanel .ffaces,#loFocusPanel .ffaces,#ptFocusPanel .ffaces{font-size:3cqh;color:#ffd98a;letter-spacing:.12em;margin-top:1cqh;",
    u"#stFocusPanel .ffaces,#loFocusPanel .ffaces,#ptFocusPanel .ffaces,#foFocusPanel .ffaces{font-size:3cqh;color:#ffd98a;letter-spacing:.12em;margin-top:1cqh;",
    'grouped: ffaces')
sub(u"#stFocusPanel .fdesc,#loFocusPanel .fdesc,#ptFocusPanel .fdesc{\n"
    u"  font-family:'Macondo',serif;font-weight:700}",
    u"#stFocusPanel .fdesc,#loFocusPanel .fdesc,#ptFocusPanel .fdesc,#foFocusPanel .fdesc{\n"
    u"  font-family:'Macondo',serif;font-weight:700}",
    'grouped: fdesc font')
sub(u"#stFocusPanel .fdesc,#loFocusPanel .fdesc,#ptFocusPanel .fdesc{font-size:2.4cqh;line-height:1.45;color:#f2e9d8;margin:3.2cqh auto 0;max-width:88%;",
    u"#stFocusPanel .fdesc,#loFocusPanel .fdesc,#ptFocusPanel .fdesc,#foFocusPanel .fdesc{font-size:2.4cqh;line-height:1.45;color:#f2e9d8;margin:3.2cqh auto 0;max-width:88%;",
    'grouped: fdesc size')
sub(u"#stFocusPanel .num,#loFocusPanel .num,#ptFocusPanel .num{color:#ffd98a;font-size:1.08em}",
    u"#stFocusPanel .num,#loFocusPanel .num,#ptFocusPanel .num,#foFocusPanel .num{color:#ffd98a;font-size:1.08em}",
    'grouped: num')
sub(u"#stFocusPanel .kw,#loFocusPanel .kw,#ptFocusPanel .kw,#nrFocusPanel .kw{color:#ffd98a}",
    u"#stFocusPanel .kw,#loFocusPanel .kw,#ptFocusPanel .kw,#nrFocusPanel .kw,#foFocusPanel .kw{color:#ffd98a}",
    'grouped: kw')
sub(u"#stBackBtn,#loFBack,#ptFBack{position:relative;width:15.2%;margin:3cqh auto 3.4cqh;cursor:pointer;transition:transform .1s}",
    u"#stBackBtn,#loFBack,#ptFBack,#foFBack{position:relative;width:15.2%;margin:3cqh auto 3.4cqh;cursor:pointer;transition:transform .1s}",
    'grouped: back btn')
sub(u"#stBackBtn:active,#loFBack:active,#ptFBack:active{transform:scale(.9)}",
    u"#stBackBtn:active,#loFBack:active,#ptFBack:active,#foFBack:active{transform:scale(.9)}",
    'grouped: back btn active')
sub(u"#stBackBtn img,#loFBack img,#ptFBack img{width:100%;display:block;pointer-events:none}",
    u"#stBackBtn img,#loFBack img,#ptFBack img,#foFBack img{width:100%;display:block;pointer-events:none}",
    'grouped: back btn img')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
