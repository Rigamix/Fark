# -*- coding: utf-8 -*-
"""Lab v3b: the preset bible - every card, die material and enchant gets a
base recipe built from the family templates (docs/VFX_LANGUAGE.md is the
prose; this is the data). Load falls back to the preset when nothing is
saved, so Denis never starts from scratch."""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_lab.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  ' + label)


PRESETS_JS = u"""/* ── THE PRESET BIBLE. docs/VFX_LANGUAGE.md is the prose and the
   reasoning; THIS is the executable data. Nine family templates build
   every base recipe; ID_META assigns family/colour/power/notes per id.
   Anything not listed takes its family default - coverage by
   construction, future cards included. ── */
function K(t,p,ease){return Object.assign({t:t,dx:0,dy:0,sc:100,op:100,rt:0,ease:ease||'ease-out'},p||{});}
function F(t,fx,p){return {t:t,fx:fx,p:Object.assign({col:'#ffd98a',count:16,speed:85,g:110,size:7,spread:2.2,ms:600,text:'',annCol:'gold'},p||{})};}
function SN(t,fam,P,pitch){return {t:t,fx:'sound',p:{snd:fam,pitch:pitch||1,layers:P||1}};}
var FAM_T={
  SET:function(c,P){return {keys:[K(0,{}),K(160,{sc:93},'ease-out'),K(340,{sc:100},'back-out')],
    fx:[SN(0,'set',P),F(60,'amberShell',{col:c}),F(90,'spray',{col:c,count:8+4*P,speed:65,g:110,size:6,spread:1.8})]};},
  PAY:function(c,P){return {keys:[],
    fx:[SN(0,'chime',P),F(0,'spray',{col:c,count:10+5*P,speed:60,g:-40,size:7,spread:1.2}),
        F(0,'glow',{col:c,size:6+2*P,ms:500})]};},
  COIN:function(c,P){return {keys:[],
    fx:[SN(0,'coin',P),F(0,'spray',{col:c,count:6+3*P,speed:90,g:60,size:6,spread:0.9})]};},
  STRIKE:function(c,P){return {keys:[K(0,{}),K(60,{dx:-7},'ease-in'),K(120,{dx:7}),K(180,{dx:-3}),K(240,{dx:0},'back-out')],
    fx:[SN(0,'thud',P),F(20,'spray',{col:c,count:10+4*P,speed:70,g:220,size:6,spread:2.6})]};},
  TRANSFORM:function(c,P){return {keys:[K(0,{}),K(300,{rt:180,sc:108},'ease-out'),K(620,{rt:360,sc:100},'back-out')],
    fx:[SN(0,'shimmer',P),F(150,'spray',{col:c,count:12+4*P,speed:55,g:-10,size:6,spread:3})]};},
  FATE:function(c,P){return {keys:[K(0,{}),K(450,{op:78},'ease-out'),K(900,{op:100},'ease-out')],
    fx:[SN(0,'bell',P),F(0,'glow',{col:c,size:8+2*P,ms:900})]};},
  BREAK:function(c,P){return {keys:[],
    fx:[SN(0,'crack',P),F(40,'break',{col:c,count:22+6*P,speed:110,g:180,size:6,ms:520})]};},
  ARM:function(c,P){return {keys:[K(0,{}),K(140,{sc:108},'back-out'),K(300,{sc:100}),K(440,{sc:105},'back-out'),K(600,{sc:100})],
    fx:[SN(0,'drum',P),F(120,'glow',{col:c,size:5+2*P,ms:400})]};},
  LEDGER:function(c,P){return {keys:[],
    fx:[SN(0,'scratch',P),F(0,'announce',{text:'THE LEDGER NOTES IT',annCol:'gold'})]};}
};
/* per-id: f=family c=colour p=power(voices/layers) n=the intent note.
   Families per fam-colour rules in VFX_LANGUAGE.md §4-5. */
var ID_META={
  /* cards */
  preserve:{f:'SET',c:'#d88a20',p:1,n:'Shell closes rounded; die parks DOWN ITS LANE at 0.8. Tier III: a tiny fly sits in the amber. Return: clearShell + PAY sparks.'},
  honeytrap:{f:'SET',c:'#e8b040',p:1,n:'Glaze the kept pair (shell 0.35). The pulled die gets an aimed golden thread when it joins. Fun: two flies buzz one lap on cast.'},
  slow_cook:{f:'PAY',c:'#e8a23c',p:1,n:'Pot-bubble: 1-2 slow rising blobs per payout tick. Quiet.'},
  powder_keg:{f:'ARM',c:'#e2582f',p:2,n:'Pulse each charging roll; fuse underline shortens. Payoff = BREAK L2 + candle flicker (the logged E1 exception - it IS an explosion).'},
  sacrifice:{f:'BREAK',c:'#e2582f',p:2,n:'SEQUENCE, never blend: darken (bust-wipe ramp) then crack, shards fly INTO the card, THEN the PAY chime.'},
  short_fuse:{f:'STRIKE',c:'#c05a3a',p:1,n:'Fuse underline burns per turn on the card; STRIKE thud when it fires.'},
  transmute:{f:'TRANSFORM',c:'#46c46e',p:2,n:'The re-dress hides inside the swirl peak (map-swap trick).'},
  bloom:{f:'TRANSFORM',c:'#46c46e',p:1,n:'A leaf: low-count jade spray, rising, when it pays.'},
  cultivate:{f:'TRANSFORM',c:'#46c46e',p:1,n:'Same leaf language as bloom, one voice.'},
  stargazer:{f:'FATE',c:'#8fa8ff',p:2,n:'Three lay-posed preview dice fade in staggered with faint constellation lines between them.'},
  ill_omen:{f:'FATE',c:'#8fa8ff',p:2,n:'Bell + violet glow when armed; the FIRE beat is a STRIKE on the RIVAL row (direction rule).'},
  sleight:{f:'STRIKE',c:'#c4404f',p:1,n:'Points AT the victim die/card.'},
  tamper:{f:'STRIKE',c:'#c4404f',p:2,n:'Rival card shakes + rust burst; keep the red ARMED rise.'},
  for_keeps:{f:'ARM',c:'#c8a45c',p:2,n:'Drum on seating; PAY when the wager pays.'},
  fools_gold_f:{f:'PAY',c:'#e8c874',p:1,n:'THE LIE: gold glint, then the die desaturates over 400ms. The joke is the fade.'},
  vanguard_f:{f:'LEDGER',c:'#c4404f',p:1,n:'Lane floor-glow shows WHICH lane on arm (E4); LEDGER when it pays.'},
  anchor_f:{f:'LEDGER',c:'#c4404f',p:1,n:'Same lane floor-glow language as vanguard.'},
  bookends_f:{f:'LEDGER',c:'#c4404f',p:1,n:'Floor-glow BOTH row ends.'},
  double_stakes:{f:'ARM',c:'#c8a45c',p:1,n:'Wager pulse on arm; nothing else - restraint (E5).'},
  the_tab:{f:'LEDGER',c:'#d8c9a0',p:1,n:'Chalk tally strokes build in the announce.'},
  hair_of_the_dog:{f:'LEDGER',c:'#d8c9a0',p:1,n:'Announce only; red when the hangover bites.'},
  marked_table:{f:'LEDGER',c:'#a06aa0',p:1,n:'Announce in curse-violet.'},
  high_table:{f:'LEDGER',c:'#d8c9a0',p:1,n:'Announce only.'},
  /* die materials - their SCORING/trait moment (mat: prefix) */
  'mat:bone':{f:'LEDGER',c:'#f3e7c8',p:1,n:'SILENT by design (E6): commons do not sparkle, so amber can.'},
  'mat:iron':{f:'LEDGER',c:'#b8c0d0',p:1,n:'Silent (E6).'},
  'mat:flint':{f:'LEDGER',c:'#9e9e9e',p:1,n:'Silent (E6).'},
  'mat:lead':{f:'LEDGER',c:'#a0a8c0',p:1,n:'Silent (E6).'},
  'mat:amber':{f:'PAY',c:'#ffd870',p:1,n:'Triple bonus: chime + amber glint on the THREE dice of the triple.'},
  'mat:jade':{f:'TRANSFORM',c:'#70d898',p:1,n:'Wild face counts: one shimmer on that die.'},
  'mat:jade2':{f:'TRANSFORM',c:'#70d898',p:2,n:'Jade + one voice.'},
  'mat:jade3':{f:'TRANSFORM',c:'#70d898',p:3,n:'Jade + two voices.'},
  'mat:brass':{f:'COIN',c:'#e8b860',p:1,n:'Coin blip on its gold trait.'},
  'mat:silver':{f:'FATE',c:'#e0e8f0',p:1,n:'Soft fate tick when its save matters.'},
  'mat:crystal':{f:'FATE',c:'#a8e8ff',p:2,n:'Glass ring.'},
  'mat:ruby':{f:'PAY',c:'#ff7888',p:2,n:'Aggressive gain - PAY in red.'},
  'mat:obsidian':{f:'BREAK',c:'#c8a0e8',p:2,n:'Its break-trigger: crack flash, +1000 chime after.'},
  'mat:starstone':{f:'PAY',c:'#b0b8ff',p:2,n:'Pays at BANK: sparks arc toward the score.'},
  'mat:vagabond':{f:'STRIKE',c:'#ff7888',p:1,n:'The steal beat, pointed at the victim.'},
  'mat:lucky':{f:'COIN',c:'#dddd66',p:1,n:'Coin + a tiny green clover particle.'},
  /* enchants - the brand fires (ench: prefix) */
  'ench:tithe':{f:'COIN',c:'#d8b054',p:1,n:'Coin sparks arc from the die to the gold counter.'},
  'ench:ward':{f:'SET',c:'#9ab0d0',p:1,n:'Defensive: silver-blue rounded shell FLASH (200ms, not a hold) + the existing bust shield when it saves.'},
  'ench:snare':{f:'SET',c:'#c05a3a',p:1,n:'Hostile set: the enclose verb in rust - a trap laid ON the rival (E3 direction).'},
  'ench:trade':{f:'TRANSFORM',c:'#46c46e',p:1,n:'Two dice swap-swirl toward each other.'},
  'ench:snuff':{f:'BREAK',c:'#4a4060',p:1,n:'A pinch of dark shards. No candle - it is small.'},
  'ench:quicksilver':{f:'TRANSFORM',c:'#dfe8f2',p:1,n:'Mercury: fast silver shimmer, low gravity, on the free reroll.'}
};
var FAM_DEFAULT={amber:'SET',jade:'TRANSFORM',obsidian:'BREAK',starstone:'FATE',
  vagabond:'STRIKE',silver:'FATE',tavern:'LEDGER'};
function labPreset(id){
  var m=ID_META[id];
  if(!m&&id.indexOf(':')<0){
    var d=E('famDef('+JSON.stringify(id)+')');
    var fam=(d&&FAM_DEFAULT[d.fam])||'PAY';
    var famc=E('(FAMILIES['+JSON.stringify(d&&d.fam)+']||{}).color')||'#ffd98a';
    m={f:fam,c:famc,p:1,n:'(family default - no bespoke preset yet)'};
  }
  if(!m)return null;
  var built=FAM_T[m.f](m.c,m.p);
  return {keys:built.keys,fx:built.fx,notes:'['+m.f+' · power '+m.p+'] '+m.n};
}
"""

sub(u"/* ── recipes: save / load / export ────────────────────────────────── */",
    PRESETS_JS + u"\n/* ── recipes: save / load / export ────────────────────────────────── */",
    'preset bible inserted')

sub(u"""function loadRecipe(){
  var id=document.getElementById('recCard').value,mo=document.getElementById('recMoment').value;
  var r=(store()[id]||{})[mo];
  if(!r)return log('nothing saved for '+id+' / '+mo);
  rec={keys:r.keys||[],fx:r.fx||[]};if(r.target)target=r.target;
  document.getElementById('recNotes').value=r.notes||'';
  renderTables();log('loaded '+id+' / '+mo);}""",
    u"""function loadRecipe(){
  var id=document.getElementById('recCard').value,mo=document.getElementById('recMoment').value;
  var r=(store()[id]||{})[mo];
  if(!r){
    /* nothing saved: the BASE PRESET loads so nobody starts from scratch */
    var pr=labPreset(id);
    if(!pr)return log('nothing saved and no preset for '+id);
    rec={keys:pr.keys,fx:pr.fx};
    document.getElementById('recNotes').value=pr.notes;
    renderTables();log('BASE PRESET loaded for '+id+' - modify away, then save');
    return;
  }
  rec={keys:r.keys||[],fx:r.fx||[]};if(r.target)target=r.target;
  document.getElementById('recNotes').value=r.notes||'';
  renderTables();log('loaded '+id+' / '+mo);}""",
    'load falls back to the preset')

sub(u"""  document.getElementById('cardPick').innerHTML=opts;
  document.getElementById('recCard').innerHTML=opts;
  log('card list filled from FAM_LIVE');
}""",
    u"""  document.getElementById('cardPick').innerHTML=opts;
  /* the recipe selector holds cards AND materials AND enchants */
  var mats=['lucky','bone','iron','flint','lead','amber','jade','jade2','jade3',
    'brass','silver','crystal','ruby','obsidian','starstone','vagabond'];
  var enchs=['tithe','ward','snare','trade','snuff','quicksilver'];
  document.getElementById('recCard').innerHTML=
    '<optgroup label="cards">'+opts+'</optgroup>'
    +'<optgroup label="die materials">'+mats.map(function(m){
      return '<option value="mat:'+m+'">'+m+'</option>';}).join('')+'</optgroup>'
    +'<optgroup label="enchants">'+enchs.map(function(e2){
      return '<option value="ench:'+e2+'">'+e2+'</option>';}).join('')+'</optgroup>';
  log('card list filled from FAM_LIVE');
}""",
    'recipe selector covers all three')

sub(u"""  document.getElementById('catalogue').innerHTML=h||'<i>FAM_LIVE empty?</i>';
  return true;
}""",
    u"""  /* dice materials and enchants join the catalogue with the same
     notes-per-id channel; their ids wear mat:/ench: prefixes */
  var _cat=function(idp,label,extra){
    var nsv=ns[idp]?'● noted':'';
    return '<details><summary data-cid='+JSON.stringify(idp)+'>'+label
      +'<span class="dot">'+nsv+'</span></summary>'
      +(extra?'<div class="rules">'+extra+'</div>':'')
      +'<textarea placeholder="what must HAPPEN, step by step. Claude implements from THIS." '
      +'onchange="saveNote('+JSON.stringify(idp)+',this.value)">'+(ns[idp]||'')+'</textarea>'
      +'</details>';};
  h+='<div class="grp">die materials</div>';
  ['lucky','bone','iron','flint','lead','amber','jade','jade2','jade3',
   'brass','silver','crystal','ruby','obsidian','starstone','vagabond'].forEach(function(m){
    var meta=ID_META['mat:'+m];
    h+=_cat('mat:'+m,m,meta?('base: '+meta.n):'');
  });
  h+='<div class="grp">enchants</div>';
  ['tithe','ward','snare','trade','snuff','quicksilver'].forEach(function(e2){
    var meta=ID_META['ench:'+e2];
    h+=_cat('ench:'+e2,e2,meta?('base: '+meta.n):'');
  });
  document.getElementById('catalogue').innerHTML=h||'<i>FAM_LIVE empty?</i>';
  return true;
}""",
    'catalogue covers materials + enchants')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
