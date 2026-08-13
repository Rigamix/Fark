# -*- coding: utf-8 -*-
"""P688: the Game Over screen gets Denis's painting - the greybox retires.

The legacy census called _gbBarred "the most visible legacy screen": grey
gbx tiles at EVERY run end, while Denis's GameOver art (the evening street,
the GAME OVER banner, four stat pennants) sat unrendered in Art/Assets/.

Same function, same flow, painted face:
  - the street full-bleed, the banner on the loss path (its GAME OVER is
    baked into the art); the win path - which the banner would contradict -
    keeps the street and headlines THE HOUSE IS YOURS in type
  - the four pennants carry the run's four numbers: NIGHT reached, GOLD in
    the purse, FEATS this run, CARDS held - dark ink on the flags, per the
    text-darker-than-accent rule
  - the buttons wear the same plaque the rest of the game's buttons wear
    (Button_new_02), not the grey kit

_gbShelf stays reachable from the win path unchanged - one screen per patch.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0

# ── the new body ────────────────────────────────────────────────────────
i = s.index('function _gbBarred(){')
j = s.index('\n}\n', i) + 3
NEW = u"""function _gbBarred(){
  /* P688: the painted run-end. Same function, same three buttons, same two
     states - the grey gbx tiles are gone and Denis's street, banner and
     stat pennants render instead. */
  _getS();_gbSheetInfra();
  var scr=document.getElementById('screen-gameover');if(!scr)return;
  var host=document.getElementById('gbBarred');
  if(!host){host=document.createElement('div');host.id='gbBarred';scr.appendChild(host);}
  var won=!!(S.run&&(S.run.tier||0)>=TIERS.length);
  var tier=TIERS[Math.min(S.run?S.run.tier||0:0,TIERS.length-1)];
  var GO='Art/Assets/GameOver/optimized/';
  var night=Math.min((S.run?(S.run.tier||0):0)+1,TIERS.length);
  var gold=(S.run&&S.run.gold)||0;
  var feats=(S.run&&S.run._featsThisRun)||0;
  var cards=((S.run&&S.run.fcards)||[]).length+((S.run&&S.run.finv)||[]).length;
  var stats=[[night,'NIGHT'],[gold,'GOLD'],[feats,'FEATS'],[cards,'CARDS']];
  var h='<img class="go-bg" src="'+GO+'GameOver_bg_opt.webp" alt="">'
    +'<div class="go-col">';
  if(won){
    h+='<div class="go-head">THE HOUSE IS YOURS</div>'
      +'<div class="go-sub">you own the night</div>';
  }else{
    h+='<img class="go-banner" src="'+GO+'GameOver_banner_opt.webp" alt="GAME OVER">'
      +'<div class="go-sub">'+(tier.boss?tier.boss.name:'the house')+" won't have you back</div>";
  }
  h+='<div class="go-stats">';
  stats.forEach(function(st,i2){
    h+='<div class="go-stat"><img src="'+GO+'GameOver_stat0'+(i2+1)+'_opt.webp" alt="">'
      +'<b>'+st[0].toLocaleString()+'</b><span>'+st[1]+'</span></div>';
  });
  h+='</div><div class="go-btns">';
  if(won)h+='<div class="go-btn" onclick="_gbShelf()"><img class="plq" src="Art/Assets/Buttons/optimized/Button_new_02_opt.webp" alt=""><span>TO THE SHELF</span></div>';
  h+='<div class="go-btn" onclick="startNewRun();showScreen(\\'gauntlet\\')"><img class="plq" src="Art/Assets/Buttons/optimized/Button_new_02_opt.webp" alt=""><span>ONE MORE RUN</span></div>'
    +'<div class="go-btn go-btn-min" onclick="SFX.nav();showScreen(\\'menu\\')"><span>title</span></div>'
    +'</div></div>';
  host.innerHTML=h;
}
"""
s = s[:i] + NEW + s[j:]
n += 1
print('  ok  P688 the painted body')


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── the CSS ─────────────────────────────────────────────────────────────
sub(u"#gbSheet.fam-sheet .gbx-btn.primary{background:#c9a24a;border-color:#7a5a1c;color:#241505}",
    u"#gbSheet.fam-sheet .gbx-btn.primary{background:#c9a24a;border-color:#7a5a1c;color:#241505}\n"
    u"/* ── P688: THE PAINTED GAME OVER. #gbBarred is its own container so the\n"
    u"   cqw units track the screen the way the match does. Ink on the pennants\n"
    u"   darker than their cloth, per the rule. ── */\n"
    u"#gbBarred{position:absolute;inset:0;container-type:size;overflow:hidden}\n"
    u"#gbBarred .go-bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}\n"
    u"#gbBarred .go-col{position:absolute;inset:0;display:flex;flex-direction:column;\n"
    u"  align-items:center;justify-content:flex-start;padding-top:14cqh}\n"
    u"#gbBarred .go-banner{width:88cqw;max-width:520px;\n"
    u"  filter:drop-shadow(0 1cqw 0 rgba(15,9,4,.45))}\n"
    u"#gbBarred .go-head{font-family:'JMH Beda',serif;font-size:8.6cqw;color:#f0c860;\n"
    u"  letter-spacing:.06em;text-shadow:0 2px 0 rgba(20,12,4,.85),0 0 14px rgba(20,12,4,.7)}\n"
    u"#gbBarred .go-sub{font-family:'JMH Beda',serif;font-size:4cqw;color:#e8d8b8;\n"
    u"  margin-top:1.6cqh;text-shadow:0 1px 0 rgba(20,12,4,.85),0 0 6px rgba(20,12,4,.7)}\n"
    u"#gbBarred .go-stats{display:flex;gap:3cqw;margin-top:5cqh}\n"
    u"#gbBarred .go-stat{position:relative;width:19cqw;aspect-ratio:180/202;\n"
    u"  filter:drop-shadow(0 0.7cqw 0 rgba(15,9,4,.4))}\n"
    u"#gbBarred .go-stat img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}\n"
    u"#gbBarred .go-stat b{position:absolute;left:0;right:0;top:34%;text-align:center;\n"
    u"  font-family:'JMH Beda',serif;font-size:5.4cqw;font-weight:normal;color:#241505}\n"
    u"#gbBarred .go-stat span{position:absolute;left:0;right:0;top:62%;text-align:center;\n"
    u"  font-family:'JMH Beda',serif;font-size:2.5cqw;letter-spacing:.12em;color:rgba(36,21,5,.75)}\n"
    u"#gbBarred .go-btns{position:absolute;left:0;right:0;bottom:5cqh;display:flex;\n"
    u"  flex-direction:column;align-items:center;gap:1.8cqh}\n"
    u"#gbBarred .go-btn{position:relative;width:64cqw;height:9.5cqh;display:flex;\n"
    u"  align-items:center;justify-content:center;cursor:pointer;transition:transform .1s}\n"
    u"#gbBarred .go-btn:active{transform:scale(.96)}\n"
    u"#gbBarred .go-btn img.plq{position:absolute;inset:0;width:100%;height:100%;\n"
    u"  object-fit:fill;pointer-events:none;filter:drop-shadow(0 0.65cqh 0 rgba(30,18,8,.55))}\n"
    u"#gbBarred .go-btn span{position:relative;z-index:1;font-family:'JMH Beda',serif;\n"
    u"  font-size:4.6cqw;letter-spacing:.08em;color:#f4ead2;\n"
    u"  text-shadow:0 1px 0 rgba(20,12,4,.8)}\n"
    u"#gbBarred .go-btn-min{width:auto;height:auto;padding:1cqh 4cqw}\n"
    u"#gbBarred .go-btn-min span{font-size:3.4cqw;color:#c9b490}",
    'P688 the CSS')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
