# -*- coding: utf-8 -*-
"""P728 (B batch): nine small fixes from the 2026-08-15 playthrough notes.

1. NPC dialogue box a bit higher (13cqw -> 10cqw below the HUD).
2. Bank-to-win button scale LATCHES on the press instead of snapping back
   (flag on G; dies with the match).
3. Win screen: the card SLOTS drop ~6px; the cards stay.
4. Match tooltips appear faster (word stagger 38->20ms, body 240->110ms).
5. Tooltip body reads in the dialogue font; title and uses keep theirs.
6. Open tooltip hides the floating score numbers (selTag/oppTag/totals) -
   the same fade the status strips already do.
7. The player's announce strip sits ABOVE the dice, in the same measured
   reserve the rival's line uses (it is empty during the player's turn).
8. Shelf: the dotted slots fade while a card focus is open (the .flat
   class _loCardFocus already sets).
9. Shelf: hearts + gold hidden. Store: an unaffordable enchant still opens
   its pick panel, wearing the dice focus's NOT-ENOUGH plaque instead of
   the die tray - window-shopping tells the player what to save for.
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


# 1 - dialogue box higher
sub(u"#screen-match .dlg-box{--dlg-y:13cqw;z-index:9500}",
    u"#screen-match .dlg-box{--dlg-y:10cqw;z-index:9500}/* P728: a bit higher (Denis) */",
    'dlg box higher')

# 2a - latch at the press
sub(u"function handleYield(){\n"
    u"  SFX.nav();",
    u"function handleYield(){\n"
    u"  SFX.nav();\n"
    u"  /* P728: the bank-to-win scale must not snap back on the press - latch\n"
    u"     it for the rest of this match (the flag dies with G). */\n"
    u"  try{var _bw=document.getElementById('btnBank');\n"
    u"    if(G&&_bw&&_bw.classList.contains('bank-to-win'))G._bankedToWin=true;}catch(e){}",
    'bank-to-win latch set')

# 2b - honor the latch
sub(u"    var _wins=!!(G&&b&&_bpts>0&&(G.pPts+_bpts)>=G.target);",
    u"    var _wins=!!(G&&b&&_bpts>0&&(G.pPts+_bpts)>=G.target);\n"
    u"    if(G&&G._bankedToWin)_wins=true;/* P728: latched at the winning press */",
    'bank-to-win latch honored')

# 3 - win slots down a few px
sub(u".fo-slot:first-child{transform:rotate(-8deg) translateY(8px)}",
    u".fo-slot:first-child{transform:rotate(-8deg) translateY(14px)}/* P728: slots only, cards stay */",
    'win slot first down')
sub(u".fo-slot:nth-child(2){transform:translateY(-2px);z-index:2}",
    u".fo-slot:nth-child(2){transform:translateY(4px);z-index:2}/* P728 */",
    'win slot middle down')
sub(u".fo-slot:last-child{transform:rotate(8deg) translateY(8px)}",
    u".fo-slot:last-child{transform:rotate(8deg) translateY(14px)}/* P728 */",
    'win slot last down')

# 4 - tooltip faster
sub(u"    return '<span class=\"w\" style=\"animation-delay:'+(t0+(i++)*38)+'ms\">'+w+'</span>';",
    u"    return '<span class=\"w\" style=\"animation-delay:'+(t0+(i++)*20)+'ms\">'+w+'</span>';/* P728: faster */",
    'word stagger faster')
sub(u"  tip.innerHTML='<div class=\"cft-name\" style=\"--cft-a:'+(o.col||'#f0c860')+'\">'+_cftWords(o.title,0)+'</div>'\n"
    u"    +(o.sub?'<div class=\"cft-sub\">'+_cftWords(o.sub,140)+'</div>':'')\n"
    u"    +'<div class=\"cft-body\">'+_cftWords(_noOrphan(o.body||''),240)+'</div>';",
    u"  tip.innerHTML='<div class=\"cft-name\" style=\"--cft-a:'+(o.col||'#f0c860')+'\">'+_cftWords(o.title,0)+'</div>'\n"
    u"    +(o.sub?'<div class=\"cft-sub\">'+_cftWords(o.sub,70)+'</div>':'')\n"
    u"    +'<div class=\"cft-body\">'+_cftWords(_noOrphan(o.body||''),110)+'</div>';/* P728: faster */",
    'tooltip sections faster')

# 5 - body in the dialogue font
sub(u"#cardFocusTip .cft-body{font-family:'JMH Beda',serif;font-size:3.5cqw;",
    u"#cardFocusTip .cft-body{font-family:var(--font-dlg);font-size:3.4cqw;/* P728: the dialogue font (Denis) */",
    'tooltip body font')

# 6 - tip hides the score numbers
sub(u"#screen-match.tip-open .status-strip{opacity:0;transition:opacity .18s ease}",
    u"#screen-match.tip-open .status-strip{opacity:0;transition:opacity .18s ease}\n"
    u"/* P728: and the floating score numbers - they overlapped the tip's text\n"
    u"   (Denis's HONEYTRAP screenshot) */\n"
    u"#screen-match.tip-open .selTag,#screen-match.tip-open #selTotal,\n"
    u"#screen-match.tip-open .oppTag,#screen-match.tip-open #oppTotal{\n"
    u"  opacity:0;transition:opacity .18s ease}",
    'tip hides score numbers')

# 7 - the player's announces above the dice
sub(u"  top.style.bottom=(zr.bottom-hiY+_STACK_GAP)+'px';\n"
    u"  top.style.top='';\n"
    u"  bot.style.top=(loY-zr.top+_STACK_GAP)+'px';\n"
    u"  bot.style.bottom='';",
    u"  top.style.bottom=(zr.bottom-hiY+_STACK_GAP)+'px';\n"
    u"  top.style.top='';\n"
    u"  /* P728: the player's line moves ABOVE the dice, into the same measured\n"
    u"     reserve the rival's line uses - that slot is empty on the player's\n"
    u"     turn (the strips swap visibility), and the card-effect announces\n"
    u"     were landing across the dice and the hand (Denis's screenshot).\n"
    u"     loY stays computed above: the tag band still reads it. */\n"
    u"  bot.style.bottom=(zr.bottom-hiY+_STACK_GAP)+'px';\n"
    u"  bot.style.top='';",
    'announces above the dice')

# 8 - shelf slots fade under a card focus
sub(u"#loCardPlane .loSlot{position:absolute;width:21.5%;aspect-ratio:911/1298;\n"
    u"  transform:translate(-50%,-50%);pointer-events:none;\n"
    u"  border:0.5cqw dashed rgba(214,176,96,.38);border-radius:6%;\n"
    u"  background:rgba(26,15,6,.26)}",
    u"#loCardPlane .loSlot{position:absolute;width:21.5%;aspect-ratio:911/1298;\n"
    u"  transform:translate(-50%,-50%);pointer-events:none;\n"
    u"  border:0.5cqw dashed rgba(214,176,96,.38);border-radius:6%;\n"
    u"  background:rgba(26,15,6,.26);transition:opacity .25s ease}\n"
    u"/* P728: the dotted slots read as clutter behind an open card focus -\n"
    u"   .flat is the class _loCardFocus already sets for exactly that state */\n"
    u"#loCardPlane.flat .loSlot{opacity:0}\n"
    u"/* P728: the shelf hides the run HUD - hearts and gold belong to the room\n"
    u"   (Denis). #loHud is built by famLoadoutShow only. */\n"
    u"#gbLoadout #loHud{display:none}",
    'shelf slots fade + loHud hidden')

# 9 - window-shopping the enchants
sub(u"  if((S.run.gold||0)<e.price){try{famLog('NOT ENOUGH GOLD');}catch(x){}return;}\n"
    u"  _stEnchK=k;",
    u"  /* P728: window-shopping allowed - the pick panel opens either way, so\n"
    u"     the player learns what to save for (Denis). The apply path stays\n"
    u"     gated: without the tray there is nothing to tap. */\n"
    u"  var _afford=(S.run.gold||0)>=e.price;\n"
    u"  _stEnchK=k;",
    'ench tap ungated')

sub(u"  var row=document.getElementById('stEnchPickTray');\n"
    u"  /* the same six painted bays the BUY tray drops into */\n"
    u"  var SLX=[13.3,27.8,42.3,56.8,71.3,85.8];",
    u"  var row=document.getElementById('stEnchPickTray');\n"
    u"  if(!_afford){\n"
    u"    /* P728: the dice focus's NOT-ENOUGH plaque instead of the die tray */\n"
    u"    if(_hint)_hint.textContent='';\n"
    u"    row.innerHTML='<div id=\"stBuyBtn\" class=\"off\" style=\"position:relative;margin:10px auto 0\">'\n"
    u"      +'<img class=\"plq\" src=\"Art/Assets/Buttons/optimized/Button_new_02_opt.webp\" alt=\"\"><span>'\n"
    u"      +'<img class=\"pcoin\" src=\"Art/Assets/Icons/optimized/coin_opt.webp\" alt=\"gold\">'+e.price+' — NOT ENOUGH</span></div>';\n"
    u"  }else{\n"
    u"  /* the same six painted bays the BUY tray drops into */\n"
    u"  var SLX=[13.3,27.8,42.3,56.8,71.3,85.8];",
    'ench plaque branch open')

sub(u"  row.innerHTML=h;\n"
    u"  if(typeof _d3ChipScan==='function')try{_d3ChipScan(row);}catch(x){}\n"
    u"  var host=document.getElementById('gbShop');\n"
    u"  if(host)host.classList.add('st-epick');/* lifts #d3xCanvas over the scrim */",
    u"  row.innerHTML=h;\n"
    u"  if(typeof _d3ChipScan==='function')try{_d3ChipScan(row);}catch(x){}\n"
    u"  }/* P728: end afford branch */\n"
    u"  var host=document.getElementById('gbShop');\n"
    u"  if(host)host.classList.add('st-epick');/* lifts #d3xCanvas over the scrim */",
    'ench plaque branch close')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
