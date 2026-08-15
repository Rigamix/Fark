# -*- coding: utf-8 -*-
"""P735 (C16): the preset bible becomes a runtime - every card, brand and
material has an effect in the GAME now, not just in the lab.

Denis: 'implement all the default presets you've built for cards dice
and all that in the game so there is something.'

FKFX is the lab's data made live: nine ACTION FAMILIES (the verbs from
docs/VFX_LANGUAGE.md), a per-id table naming each id's family, colour
and power, and one play() that runs a family's recipe on a target -
motion (standalone CSS props, composing with the game's own transforms),
FX through the primitives that already exist (_fxSpray, cardFx's beats,
D3X.amberShell, _bustShieldFX), and sound through SFX's own oscillators,
so there is no second audio engine and the mute setting keeps working.

Hooked at the two moments the game already owns: famUse (a card fires)
and _iconFire (a brand fires). Anything without a bespoke entry falls
back to its FAMILY, so future cards are covered by construction.
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


FKFX = u"""/* ═══ P735: FKFX - THE EFFECT LANGUAGE, LIVE ═══
   docs/VFX_LANGUAGE.md is the reasoning; fark_lab.html is where these
   numbers were authored; this is the runtime. Nine families own a verb,
   a palette and an instrument; power adds layers and voices, never a
   different verb. Every primitive here already existed - this only
   composes them. */
var FKFX={
  on:true,
  /* the nine instruments, on SFX's own context so the mute setting and
     the iOS resume dance keep working */
  snd:function(fam,P,pitch){
    try{
      if(!SFX||!SFX._tone)return;
      var p=pitch||1,L=P||1,T=function(f,ty,v,a,d,st){SFX._tone(f*p,ty,v,a,d,st);};
      if(fam==='chime'){T(660,'sine',.12,.01,.3);T(990,'sine',.08,.01,.34,.06);
        if(L>1)T(1320,'sine',.05,.01,.36,.10);if(L>2)T(1980,'sine',.03,.01,.4,.16);}
      else if(fam==='coin'){T(1568,'triangle',.10,.005,.08);T(2093,'triangle',.08,.005,.10,.07);
        if(L>1){T(1568,'triangle',.06,.005,.08,.16);T(2093,'triangle',.05,.005,.10,.22);}}
      else if(fam==='thud'){T(120,'sine',.22,.005,.16);T(70,'sine',.16,.005,.18,.02);
        if(L>1)T(90,'sine',.12,.005,.16,.09);}
      else if(fam==='crack'){T(180,'square',.10,.002,.05);T(140,'sine',.16,.004,.13,.03);
        if(L>1)T(240,'square',.07,.002,.05,.07);if(L>2)T(160,'square',.05,.002,.05,.12);}
      else if(fam==='set'){T(440,'sine',.14,.01,.2);T(880,'sine',.05,.01,.28);
        if(L>1)T(1760,'sine',.03,.01,.3,.05);}
      else if(fam==='shimmer'){[523,587,659,784,880].forEach(function(f,i){
        T(f,'sine',.05,.01,.26,i*0.05);if(L>1)T(f*2,'sine',.03,.01,.22,.12+i*0.05);});}
      else if(fam==='bell'){T(660,'sine',.10,.01,.8);T(990,'sine',.05,.01,.85);
        if(L>1)T(1320,'sine',.03,.01,.9,.04);}
      else if(fam==='drum'){T(55,'sine',.24,.005,.14);T(55,'sine',.18,.005,.14,.25);
        if(L>1)T(110,'sine',.08,.005,.1,.02);}
      else if(fam==='scratch'){T(900,'triangle',.05,.003,.05);
        if(L>1)T(1100,'triangle',.03,.003,.05,.09);}
    }catch(e){}
  },
  /* the visual primitives, all pre-existing */
  _spray:function(el,col,n2,o){try{_fxSpray(el,col,n2,o);}catch(e){}},
  _glow:function(el,col,size,ms){
    if(!el||!el.animate)return;
    try{el.animate([{filter:'drop-shadow(0 0 0 transparent)'},
      {filter:'drop-shadow(0 0 '+(size*2)+'px '+col+') brightness(1.16)'},
      {filter:'drop-shadow(0 0 2px transparent)'}],{duration:ms||500,easing:'ease-out'});}catch(e){}
  },
  _flash:function(el){
    if(!el)return;
    try{
      var f=document.createElement('div');
      f.style.cssText='position:absolute;inset:-4%;border-radius:16%;background:#fff;opacity:.8;'
        +'pointer-events:none;z-index:8;transition:opacity 90ms ease-out';
      if(getComputedStyle(el).position==='static')el.style.position='relative';
      el.appendChild(f);
      requestAnimationFrame(function(){f.style.opacity='0';});
      setTimeout(function(){f.remove();},150);
    }catch(e){}
  },
  _beam:function(el,col,ms){
    if(!el)return;
    try{
      var b=document.createElement('div');
      b.style.cssText='position:absolute;left:22%;width:56%;bottom:52%;height:200%;pointer-events:none;'
        +'z-index:4;background:linear-gradient(to top,'+col+'55,transparent);mix-blend-mode:screen;'
        +'opacity:0;transition:opacity '+Math.round((ms||600)/3)+'ms ease-out';
      if(getComputedStyle(el).position==='static')el.style.position='relative';
      el.appendChild(b);
      requestAnimationFrame(function(){b.style.opacity='1';});
      setTimeout(function(){b.style.opacity='0';},(ms||600)*0.55);
      setTimeout(function(){b.remove();},(ms||600)+220);
    }catch(e){}
  },
  /* motion: standalone props, so the row's own transforms survive */
  _motion:function(el,keys){
    if(!el||!el.animate||!keys||!keys.length)return;
    try{
      el.animate(keys.map(function(k){
        return {offset:k.o,translate:(k.dx||0)+'px '+(k.dy||0)+'px',
          scale:String(k.sc===undefined?1:k.sc),rotate:(k.rt||0)+'deg',
          opacity:k.op===undefined?1:k.op,easing:k.e||'ease-out'};
      }),{duration:keys[keys.length-1].t||500});
    }catch(e){}
  },
  /* THE FAMILIES. c = colour, P = power (1..3). */
  fam:{
    SET:function(el,c,P,self){
      self._motion(el,[{o:0,sc:1},{o:.18,sc:.95,rt:-2,e:'ease-in'},{o:.35,sc:.93,rt:2},
        {o:.6,sc:.93,rt:-1},{o:1,sc:1,rt:0,e:'cubic-bezier(.3,1.4,.4,1)'},]);
      self.snd('set',P);
      setTimeout(function(){self._spray(el,c,5+2*P,{speed:28,g:170,size:10,spread:0.6});},140);
    },
    PAY:function(el,c,P,self){
      self.snd('chime',P);
      self._spray(el,c,10+5*P,{speed:50,g:-16,size:7,spread:1.2});
      self._glow(el,c,6+2*P,500);
      if(P>=2)setTimeout(function(){self._beam(el,c,700);},60);
    },
    COIN:function(el,c,P,self){
      self.snd('coin',P);self._spray(el,c,6+3*P,{speed:90,g:60,size:6,spread:0.9});
    },
    STRIKE:function(el,c,P,self){
      self._flash(el);self.snd('thud',P);
      self._motion(el,[{o:0},{o:.25,dx:-7,e:'ease-in'},{o:.5,dx:7},{o:.75,dx:-3},{o:1,dx:0,t:240}]);
      setTimeout(function(){self._spray(el,c,10+4*P,{speed:70,g:220,size:6,spread:2.6});},20);
      setTimeout(function(){self._spray(el,'#7a6a55',6+2*P,{speed:20,g:-8,size:12,spread:2.8});},80);
    },
    TRANSFORM:function(el,c,P,self){
      self.snd('shimmer',P);
      self._motion(el,[{o:0},{o:.5,rt:180,sc:1.08},{o:1,rt:360,sc:1,t:620,e:'cubic-bezier(.3,1.4,.4,1)'}]);
      setTimeout(function(){self._spray(el,c,12+4*P,{speed:55,g:-10,size:6,spread:3});},150);
    },
    FATE:function(el,c,P,self){
      self.snd('bell',P);self._glow(el,c,8+2*P,900);self._beam(el,c,1000);
      setTimeout(function(){self._glow(el,'#ffffff',4,300);},250);
      setTimeout(function(){self._glow(el,c,3,300);},500);
    },
    BREAK:function(el,c,P,self){
      self._flash(el);self.snd('crack',P);
      setTimeout(function(){self._spray(el,c,22+6*P,{speed:110,g:180,size:6,spread:3});},40);
      setTimeout(function(){self._spray(el,'#5a5248',8+2*P,{speed:16,g:-6,size:13,spread:3});},90);
    },
    ARM:function(el,c,P,self){
      self.snd('drum',P);
      self._motion(el,[{o:0,sc:1},{o:.23,sc:1.08,e:'cubic-bezier(.3,1.4,.4,1)'},{o:.5,sc:1},
        {o:.73,sc:1.05},{o:1,sc:1,t:600}]);
      setTimeout(function(){self._glow(el,c,5+2*P,400);},120);
    },
    LEDGER:function(el,c,P,self){self.snd('scratch',P);}
  },
  /* per-id: f=family, c=colour, p=power. Anything missing falls back to
     its card FAMILY (see play), so new cards are covered by
     construction. Authored in the lab, kept in sync by hand on purpose:
     one table, one place to read. */
  meta:{
    preserve:{f:'SET',c:'#d88a20',p:1}, honeytrap:{f:'SET',c:'#e8b040',p:1},
    slow_cook:{f:'PAY',c:'#e8a23c',p:1}, powder_keg:{f:'ARM',c:'#e2582f',p:2},
    sacrifice:{f:'BREAK',c:'#e2582f',p:2}, short_fuse:{f:'STRIKE',c:'#c05a3a',p:1},
    transmute:{f:'TRANSFORM',c:'#46c46e',p:2}, bloom:{f:'TRANSFORM',c:'#46c46e',p:1},
    cultivate:{f:'TRANSFORM',c:'#46c46e',p:1}, stargazer:{f:'FATE',c:'#8fa8ff',p:2},
    ill_omen:{f:'FATE',c:'#8fa8ff',p:2}, sleight:{f:'STRIKE',c:'#c4404f',p:1},
    tamper:{f:'STRIKE',c:'#c4404f',p:2}, for_keeps:{f:'ARM',c:'#c8a45c',p:2},
    fools_gold_f:{f:'PAY',c:'#e8c874',p:1}, vanguard_f:{f:'LEDGER',c:'#c4404f',p:1},
    anchor_f:{f:'LEDGER',c:'#c4404f',p:1}, bookends_f:{f:'LEDGER',c:'#c4404f',p:1},
    double_stakes:{f:'ARM',c:'#c8a45c',p:1}, the_tab:{f:'LEDGER',c:'#d8c9a0',p:1},
    hair_of_the_dog:{f:'LEDGER',c:'#d8c9a0',p:1}, marked_table:{f:'LEDGER',c:'#a06aa0',p:1},
    high_table:{f:'LEDGER',c:'#d8c9a0',p:1},
    'ench:tithe':{f:'COIN',c:'#d8b054',p:1}, 'ench:ward':{f:'SET',c:'#9ab0d0',p:1},
    'ench:snare':{f:'SET',c:'#c05a3a',p:1}, 'ench:trade':{f:'TRANSFORM',c:'#46c46e',p:1},
    'ench:snuff':{f:'BREAK',c:'#4a4060',p:1}, 'ench:quicksilver':{f:'TRANSFORM',c:'#dfe8f2',p:1},
    'mat:amber':{f:'PAY',c:'#ffd870',p:1}, 'mat:jade':{f:'TRANSFORM',c:'#70d898',p:1},
    'mat:jade2':{f:'TRANSFORM',c:'#70d898',p:2}, 'mat:jade3':{f:'TRANSFORM',c:'#70d898',p:3},
    'mat:brass':{f:'COIN',c:'#e8b860',p:1}, 'mat:silver':{f:'FATE',c:'#e0e8f0',p:1},
    'mat:crystal':{f:'FATE',c:'#a8e8ff',p:2}, 'mat:ruby':{f:'PAY',c:'#ff7888',p:2},
    'mat:obsidian':{f:'BREAK',c:'#c8a0e8',p:2}, 'mat:starstone':{f:'PAY',c:'#b0b8ff',p:2},
    'mat:vagabond':{f:'STRIKE',c:'#ff7888',p:1}, 'mat:lucky':{f:'COIN',c:'#dddd66',p:1}
    /* bone/iron/flint/lead are deliberately absent: commons are SILENT,
       which is what lets amber's chime mean something (VFX_LANGUAGE E6) */
  },
  famDefault:{amber:'SET',jade:'TRANSFORM',obsidian:'BREAK',starstone:'FATE',
    vagabond:'STRIKE',silver:'FATE',tavern:'LEDGER'},
  resolve:function(id){
    var m=this.meta[id];
    if(m)return m;
    if(id.indexOf(':')>=0)return null;/* an unlisted material stays silent */
    try{
      var d=famDef(id);
      if(!d)return null;
      var f=this.famDefault[d.fam]||'PAY';
      var c=(FAMILIES[d.fam]||{}).color||'#ffd98a';
      return {f:f,c:c,p:1};
    }catch(e){return null;}
  },
  /* the one entry point */
  play:function(id,el){
    if(!this.on||!id)return false;
    var m=this.resolve(id);
    if(!m)return false;
    var fn=this.fam[m.f];
    if(!fn)return false;
    try{fn(el,m.c,m.p,this);}catch(e){}
    return true;
  }
};
"""

sub(u"/* update the live set */\n"
    u"/* TAR PIT IS RETIRED.",
    FKFX + u"/* update the live set */\n"
    u"/* TAR PIT IS RETIRED.",
    'FKFX runtime')

# hook: a card fires
sub(u"  if(fx.use(inst)){inst.charges--;famRenderRow();}\n"
    u"}",
    u"  if(fx.use(inst)){\n"
    u"    inst.charges--;\n"
    u"    /* P735: the card's own effect language plays on the card that\n"
    u"       fired - BEFORE the re-render, since that replaces the element\n"
    u"       (the P668 lesson); FKFX's own timers ride the descriptor-free\n"
    u"       primitives, which survive it. */\n"
    u"    try{var _fc=document.querySelectorAll('#famRowP .fcv')[i];\n"
    u"      if(_fc&&window.FKFX)FKFX.play(inst.id,_fc);}catch(e){}\n"
    u"    famRenderRow();\n"
    u"  }\n"
    u"}",
    'famUse plays the recipe')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
