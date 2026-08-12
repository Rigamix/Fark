# -*- coding: utf-8 -*-
"""P666: one feedback vocabulary for card effects, and the silent ones wired to it.

Denis: "do an audit of potential effects missing for card activations. Logical
conclusion is that a lot are missing visual feedback... At the very least the
frozen card should be greyed out and maybe jiggle a bit when it happens. Same
with ALL other cards. Do a complete pass... ensuring that you don't create
useless code per effect. A lot of things should be reusable."

THE AUDIT, MEASURED. Every CFX registration read, and every one checked for a
call that produces something VISIBLE - particles, a class change, a sprite, a
dice-layer touch - as opposed to text or sound:

    23 cards registered
    19 of them had no visual feedback at all beyond famLog

Only steady_hand, encore, double_or_nothing and sacrifice showed anything.

FOUR VERBS, NOT NINETEEN EFFECTS. Reading what the cards actually do, every one
of them is doing one of four things to something on screen:

    hit    something of theirs is disabled or broken   tamper, ill_omen
    gain   something of yours is improved or saved     preserve, cultivate...
    steal  value crosses from them to you              pickpocket, reprisal...
    churn  dice are rerolled or changed                powder_keg, transmute...

so cardFx(kind, target) is the whole surface, and a card's effect adds ONE line
at the moment it already calls famLog - which is the instant the effect lands,
and the only instant that was ever in the right place.

IT REUSES WHAT IS THERE. The particles are FX with P664's diamonds, in the
family's own colour through _cardAccent; the shake and pulse are two keyframes
next to the ones the game already animates cards with; the target resolver
finds a card by id in whichever row it is in, so no caller has to know whether
a card is the player's or the rival's.

THE BROKEN STATE IS PERSISTENT, and that is deliberate: Denis asked for the
frozen card to be "greyed out and maybe jiggle a bit". The jiggle is the moment;
the grey is the fact, and it has to survive famRenderRow rebuilding the row -
which it does, because famRenderRow already writes a `broken` class from
inst.broken and nothing was styling it since P633 removed the .mcBack rules.
Grey only - no cross, no torn outline - because that weathering is what Denis
asked to be rid of.
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


SYSTEM = r"""
/* ═══════ CARD EFFECT FEEDBACK ═══════
   FOUR VERBS FOR TWENTY-THREE CARDS. Audited before it was written: 19 of the
   23 CFX registrations produced nothing visible at all, only famLog text. What
   they DO, though, is one of four things to something on screen - so this is
   the whole vocabulary, and a card's effect adds one line at the point it
   already calls famLog, which is the instant the effect lands.

     hit    something of theirs is disabled or broken
     gain   something of yours is improved or saved
     steal  value crosses from them to you
     churn  dice are rerolled or changed

   Everything here is reused: the particles are FX with P664's diamond and star,
   coloured by _cardAccent so a jade card throws jade; the shake and pulse are
   two keyframes beside the ones already animating cards; and _fxEl finds a card
   by id in whichever row holds it, so no caller needs to know whose it is. */
function _fxEl(t){
  if(!t)return null;
  if(t.nodeType===1)return t;
  try{
    if(t.card)return document.querySelector('#famRowP .fcv[data-cid="'+t.card+'"]')
                     ||document.querySelector('#famRowO .fcv[data-cid="'+t.card+'"]');
    if(t.oppCard)return document.querySelector('#famRowO .fcv[data-cid="'+t.oppCard+'"]');
    if(t.myCard)return document.querySelector('#famRowP .fcv[data-cid="'+t.myCard+'"]');
    if(t.row==='dice')return document.getElementById('playerDiceRow');
    if(t.row==='oppDice')return document.getElementById('oppDiceRow');
    if(t.row==='score')return document.querySelector('#raceWrap')||document.getElementById('hud');
  }catch(e){}
  return null;
}
/* the shared emitter: a spray of the game's own diamonds off an element */
function _fxSpray(el,col,count,opts){
  if(!el||typeof FX==='undefined'||!FX.emit)return;
  var r=el.getBoundingClientRect();if(!(r.width>0))return;
  opts=opts||{};
  var cx=r.left+r.width/2, cy=r.top+r.height/2;
  for(var i=0;i<count;i++){
    var a=(opts.dir!==undefined?opts.dir:-Math.PI/2)+(Math.random()-0.5)*(opts.spread||1.6);
    var sp=(opts.speed||70)*(0.5+Math.random());
    FX.emit({x:cx+(Math.random()-0.5)*r.width*0.8,
             y:cy+(Math.random()-0.5)*r.height*0.6,
             vx:Math.cos(a)*sp, vy:Math.sin(a)*sp,
             g:opts.g===undefined?90:opts.g,
             life:0.45+Math.random()*0.6,
             size:(opts.size||7)*(0.7+Math.random()*0.7),
             rot:Math.random()*Math.PI, vr:(Math.random()-0.5)*6,
             shape:(Math.random()<0.2?'star':'diamond'), color:col});
  }
}
function cardFx(kind,target,opts){
  opts=opts||{};
  var el=_fxEl(target);
  if(!el)return;
  var col=opts.color||_cardAccent(el);
  try{el.style.setProperty('--fx-glow',col);}catch(e){}
  /* the class is removed first so a repeat of the same verb re-triggers the
     animation rather than being swallowed as "already applied" */
  function beat(cls,ms){
    el.classList.remove(cls);void el.offsetWidth;el.classList.add(cls);
    setTimeout(function(){el.classList.remove(cls);},ms);
  }
  try{
    if(kind==='hit'){
      beat('fx-shake',460);
      _fxSpray(el,opts.color||'#6b5a48',14,{speed:55,g:220,size:6,spread:2.4});
      try{SFX.err&&SFX.err();}catch(e){}
    }else if(kind==='gain'){
      beat('fx-pulse',520);
      _fxSpray(el,col,16,{speed:60,g:-10,size:8,spread:1.1});
    }else if(kind==='churn'){
      beat('fx-pulse',420);
      _fxSpray(el,col,20,{speed:110,g:140,size:7,spread:2.8});
    }else if(kind==='steal'){
      /* value crossing the table: motes leave the target toward `to` */
      var dst=_fxEl(opts.to)||document.getElementById('hud');
      var a=r2(el,dst);
      _fxSpray(el,col,18,{dir:a,spread:0.5,speed:170,g:0,size:8});
      beat('fx-pulse',420);
    }
  }catch(e){}
  function r2(from,to){
    if(!to)return -Math.PI/2;
    var f=from.getBoundingClientRect(),t=to.getBoundingClientRect();
    return Math.atan2((t.top+t.height/2)-(f.top+f.height/2),
                      (t.left+t.width/2)-(f.left+f.width/2));
  }
}
"""

sub(u"/* tap a card at the table: the painted sheet; PLAY when usable */\n"
    u"function famCardTap(i){",
    SYSTEM.lstrip('\n') + u"/* tap a card at the table: the painted sheet; PLAY when usable */\n"
    u"function famCardTap(i){",
    'P666 the vocabulary')

# ── the two keyframes and the broken state ───────────────────────────────
sub(u"/* the fire flash, on the family card too - one selector rather than a second\n"
    u"   set of keyframes */\n"
    u".fcv.card-fired{animation:cardFired .42s ease-out}",
    u"/* the fire flash, on the family card too - one selector rather than a second\n"
    u"   set of keyframes */\n"
    u".fcv.card-fired{animation:cardFired .42s ease-out}\n"
    u"/* P666: the two motions the whole feedback vocabulary is built from. Both\n"
    u"   ride `transform`, which .fcv leaves free - its fan angle is on the\n"
    u"   standalone `rotate` and `translate`, so neither is disturbed. */\n"
    u"@keyframes fxShake{\n"
    u"  0%,100%{transform:translateX(0) rotate(0deg)}\n"
    u"  15%{transform:translateX(-4px) rotate(-2.5deg)}\n"
    u"  32%{transform:translateX(4px) rotate(2.5deg)}\n"
    u"  50%{transform:translateX(-3px) rotate(-1.6deg)}\n"
    u"  68%{transform:translateX(3px) rotate(1.6deg)}\n"
    u"  85%{transform:translateX(-1px) rotate(-.6deg)}}\n"
    u"/* the glow is the SAME recipe the die sparkles use - drop-shadow in the\n"
    u"   particle's own colour - so a card lighting up and a die sparkling are one\n"
    u"   visual language. --fx-glow is written by cardFx from the family accent.\n"
    u"   The card's own 2px drop-shadow is repeated here because an animated\n"
    u"   `filter` REPLACES the computed one; omitting it drops the card's shadow\n"
    u"   for the half second of the pulse. */\n"
    u"@keyframes fxPulse{\n"
    u"  0%{transform:scale(1);filter:drop-shadow(2px 3px 0 rgba(15,9,4,.4))}\n"
    u"  35%{transform:scale(1.09);\n"
    u"      filter:drop-shadow(2px 3px 0 rgba(15,9,4,.4))\n"
    u"             drop-shadow(0 0 12px var(--fx-glow,#ffd98a)) brightness(1.35)}\n"
    u"  100%{transform:scale(1);filter:drop-shadow(2px 3px 0 rgba(15,9,4,.4))}}\n"
    u".fx-shake{animation:fxShake .46s ease-in-out}\n"
    u".fx-pulse{animation:fxPulse .5s ease-out}\n"
    u"/* P666: BROKEN IS A LASTING FACT, not a beat - the card is out for the night,\n"
    u"   so it stays grey through every famRenderRow. The row already writes this\n"
    u"   class from inst.broken; nothing had styled it since P633 removed the\n"
    u"   .mcBack rules. Grey ONLY - no cross, no torn outline - because that\n"
    u"   weathering is exactly what Denis asked to be rid of on boss cards. */\n"
    u".fcv.broken{filter:grayscale(.92) brightness(.5)}",
    'P666 the motions and the broken state')

# ── wire the silent effects, one line each at the moment they land ───────
sub(u"    try{famRenderRow();}catch(e){}\n"
    u"    return true;\n"
    u"  }\n"
    u"};\n"
    u"CFX.sleight={",
    u"    try{famRenderRow();}catch(e){}\n"
    u"    /* P666: the card Denis named - it shakes as it breaks, then stays grey.\n"
    u"       AFTER famRenderRow, not before: the row rebuilds its innerHTML, so a\n"
    u"       class put on the old element is thrown away with it. The rebuilt card\n"
    u"       already carries `broken` from inst.broken, so the grey is there when\n"
    u"       the shake starts and stays after it ends. */\n"
    u"    cardFx('hit',{oppCard:tgt.id});\n"
    u"    return true;\n"
    u"  }\n"
    u"};\n"
    u"CFX.sleight={",
    'P666 wire Tamper')

sub(u"    if(ev.pts<=0){var take=Math.min(_ioP[0],G.oPts);G.oPts-=take;G.pPts+=take;\n"
    u"      G._featOmenTrue=true;/* OMENS TRUE */\n"
    u"      famLog('THE OMEN LANDS — YOU TAKE '+take);}\n"
    u"    else{G.oPts+=_ioP[1];famLog('THE OMEN MISSES — THEY GAIN '+_ioP[1]);}",
    u"    if(ev.pts<=0){var take=Math.min(_ioP[0],G.oPts);G.oPts-=take;G.pPts+=take;\n"
    u"      G._featOmenTrue=true;/* OMENS TRUE */\n"
    u"      famLog('THE OMEN LANDS — YOU TAKE '+take);\n"
    u"      cardFx('steal',{row:'oppDice'},{to:{row:'score'}});}\n"
    u"    else{G.oPts+=_ioP[1];famLog('THE OMEN MISSES — THEY GAIN '+_ioP[1]);\n"
    u"      cardFx('hit',{row:'score'});}",
    'P666 wire Ill Omen')

sub(u"    if(lift>0){G.oPts-=lift;G.pPts+=lift;famLog('PICKPOCKET LIFTS '+lift);try{updHUD();}catch(e){}}}",
    u"    if(lift>0){G.oPts-=lift;G.pPts+=lift;famLog('PICKPOCKET LIFTS '+lift);\n"
    u"      cardFx('steal',{row:'oppDice'},{to:{row:'score'}});\n"
    u"      try{updHUD();}catch(e){}}}",
    'P666 wire Pickpocket')

sub(u"    G._famSleight=true;\n"
    u"    famLog('SLEIGHT READY — THEIR NEXT ROLL COMES BACK');",
    u"    G._famSleight=true;\n"
    u"    famLog('SLEIGHT READY — THEIR NEXT ROLL COMES BACK');\n"
    u"    cardFx('churn',{row:'oppDice'});",
    'P666 wire Sleight')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
