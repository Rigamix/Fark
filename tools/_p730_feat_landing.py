# -*- coding: utf-8 -*-
"""P730 (A4): a newly earned feat LANDS on the shelf board.

Denis won teetotaller and entering the shelf said nothing - the loud
overlay was retired (it interrupted the loadout screen three times in a
row) and its replacement pins silently, so the moment vanished entirely.
The moment moves to where the player already is: _featCeremony marks the
feat FRESH beside the pin, and the next shelf entry plays the landing -
the hotDice fanfare once for the batch, then each fresh pin drops in
scaled-down-from-large under a gold glow with a particle spray at the
thump. S.featsFresh rides the save, so a feat earned just before closing
the app still gets its landing next session.
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


# 1) the ceremony marks the debt
sub(u"    _getS();S.featsPinned=S.featsPinned||{};\n"
    u"    (list||[]).forEach(function(f){if(f&&f.id)S.featsPinned[f.id]=1;});\n"
    u"    save();",
    u"    _getS();S.featsPinned=S.featsPinned||{};\n"
    u"    (list||[]).forEach(function(f){if(f&&f.id){S.featsPinned[f.id]=1;\n"
    u"      /* P730: the shelf owes this one its landing moment */\n"
    u"      (S.featsFresh=S.featsFresh||{})[f.id]=1;}});\n"
    u"    save();",
    'ceremony marks fresh')

# 2) the shelf pays it
sub(u"  if(_pend.length){\n"
    u"    var _fs=_pend.map(function(id){return FEATS.find(function(x){return x.id===id;});}).filter(Boolean);\n"
    u"    if(_fs.length)_featCeremony(_fs);\n"
    u"  }",
    u"  if(_pend.length){\n"
    u"    var _fs=_pend.map(function(id){return FEATS.find(function(x){return x.id===id;});}).filter(Boolean);\n"
    u"    if(_fs.length)_featCeremony(_fs);\n"
    u"  }\n"
    u"  /* P730: THE LANDING. Feats award silently mid-match (the loud overlay\n"
    u"     interrupted, P338/P667) - so the MOMENT lives here, where the board\n"
    u"     is: each fresh pin drops in large-to-place under a gold glow with a\n"
    u"     spray at the thump, one fanfare for the batch (Denis: audio + pin\n"
    u"     animation with glow and particles). Fresh rides the save, so a feat\n"
    u"     earned just before quitting still lands next session. */\n"
    u"  try{\n"
    u"    var _frsh=Object.keys(S.featsFresh||{}).filter(function(id){return FEAT_ART[id];});\n"
    u"    if(_frsh.length){\n"
    u"      try{SFX.hotDice&&SFX.hotDice();}catch(e){}\n"
    u"      _frsh.forEach(function(id,ix){\n"
    u"        var el=ov.querySelector('.loFeat[data-png=\"'+FEAT_ART[id]+'\"]');\n"
    u"        if(!el)return;\n"
    u"        el.classList.remove('unpinned');\n"
    u"        setTimeout(function(){\n"
    u"          el.classList.add('pin-land');\n"
    u"          setTimeout(function(){try{_fxSpray(el,'#ffd98a',18,{speed:85,g:130,size:7,spread:2.2});}catch(e){}},420);\n"
    u"          setTimeout(function(){el.classList.remove('pin-land');},1700);\n"
    u"        },350+ix*450);\n"
    u"      });\n"
    u"      S.featsFresh={};try{save();}catch(e){}\n"
    u"    }\n"
    u"  }catch(e){}",
    'shelf plays the landing')

# 3) the look of the landing
sub(u".loFeat:active{transform:var(--jt,translate(-50%,-50%)) scale(1.12)}",
    u".loFeat:active{transform:var(--jt,translate(-50%,-50%)) scale(1.12)}\n"
    u"/* P730: the fresh pin's landing - standalone scale composes with the\n"
    u"   --jt transform, so the drop keeps the pin's jitter angle. Glow via\n"
    u"   filter; the spray fires from JS at the thump. */\n"
    u".loFeat.pin-land{animation:loPinLand .85s cubic-bezier(.3,1.4,.4,1) both;z-index:16}\n"
    u"@keyframes loPinLand{\n"
    u"  0%{scale:3.2;opacity:0;filter:drop-shadow(0 0 0 rgba(255,217,138,0))}\n"
    u"  45%{opacity:1}\n"
    u"  62%{scale:.92;filter:drop-shadow(0 0 14px rgba(255,217,138,.95))}\n"
    u"  80%{scale:1.06}\n"
    u"  100%{scale:1;filter:drop-shadow(0 0 5px rgba(255,217,138,.45))}}",
    'pin-land keyframes')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
