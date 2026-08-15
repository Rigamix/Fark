# -*- coding: utf-8 -*-
"""Lab v5: the user-grade UI. Three tabs - STAGE (boot, light studio with
per-light sliders, audio toggle, manual target play), CARD STUDIO (visual
gallery; picking a card narrows the UI to that card's workspace with a
drag-and-drop step sequencer), ADVANCED (the old dense dev controls,
unchanged ids so every engine function keeps working). Plus: game music/
ambiance muted by default, enchant/material application to a clicked die,
and the one-preset look buttons replaced by real sliders."""
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


# ── A. CSS for the new UI ──
sub(u"""  #catalogue textarea{width:100%;height:64px;background:#1a130a;color:#d8c9a0;
    border:1px solid #5a4626;font-family:inherit;font-size:12px;padding:5px}
</style>""",
    u"""  #catalogue textarea{width:100%;height:64px;background:#1a130a;color:#d8c9a0;
    border:1px solid #5a4626;font-family:inherit;font-size:12px;padding:5px}
  /* ── v5: the user-grade shell ── */
  #tabs{display:flex;gap:6px;margin:10px 0 14px;border-bottom:2px solid #3a2c18;padding-bottom:0}
  #tabs button{border-radius:6px 6px 0 0;border-bottom:none;font-size:13px;padding:8px 16px;margin:0}
  #tabs button.on{background:#3a2c18;color:#ffd98a;border-color:#8a6a36}
  .tab{display:none}
  .tab.on{display:block}
  .card-sec{background:#1a130a;border:1px solid #3a2c18;border-radius:8px;
    padding:12px 14px;margin:0 0 14px}
  .card-sec h3{margin:0 0 8px;font-size:12px;color:#c8a45c;letter-spacing:.08em;
    text-transform:uppercase;font-weight:normal}
  #gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(86px,1fr));gap:10px}
  .gcard{cursor:pointer;text-align:center;border:1px solid transparent;border-radius:6px;padding:6px 2px}
  .gcard:hover{border-color:#8a6a36;background:#241a0e}
  .gcard img{width:64px;border-radius:5px;display:block;margin:0 auto 4px}
  .gcard .swatch{width:44px;height:44px;border-radius:8px;margin:4px auto 6px;
    border:2px solid #5a4626}
  .gcard .gname{font-size:10px;color:#d8c9a0;line-height:1.2}
  .gcard .gnote{font-size:9px;color:#7ac06a}
  #ws{display:none}
  #ws.on{display:block}
  #wsHead{display:flex;gap:14px;align-items:flex-start;margin-bottom:10px}
  #wsHead img{width:96px;border-radius:6px}
  #wsHead .swatch{width:72px;height:72px;border-radius:10px;border:3px solid #5a4626}
  #wsName{font-size:16px;color:#ffd98a;margin:0 0 4px}
  #wsRules{font-size:11px;color:#9a8a68;line-height:1.5;max-width:420px}
  .pills{display:flex;gap:6px;margin:10px 0;flex-wrap:wrap}
  .pill{padding:5px 12px;border-radius:999px;border:1px solid #5a4626;cursor:pointer;
    font-size:11px;color:#b8a67e;background:#241a0e}
  .pill.on{background:#4a3418;color:#ffd98a;border-color:#ffd98a}
  #seq{display:flex;gap:12px;align-items:flex-start}
  #seqPal{flex:none;width:150px}
  #seqPal .pgrp{font-size:10px;color:#c8a45c;text-transform:uppercase;letter-spacing:.07em;
    margin:8px 0 4px}
  .chip{display:block;padding:6px 9px;margin:3px 0;border-radius:5px;font-size:11px;
    background:#241a0e;border:1px solid #5a4626;cursor:grab;user-select:none}
  .chip:hover{border-color:#8a6a36}
  .chip.v{border-left:3px solid #d89a20}
  .chip.s{border-left:3px solid #7a9ac0}
  .chip.m{border-left:3px solid #7ac06a}
  #seqLane{flex:1;min-height:140px;background:#12100a;border:2px dashed #3a2c18;
    border-radius:8px;padding:10px;display:flex;flex-wrap:wrap;gap:4px;align-items:flex-start;
    align-content:flex-start}
  #seqLane.over{border-color:#8a6a36}
  .step{background:#241a0e;border:1px solid #5a4626;border-radius:6px;padding:6px 9px;
    font-size:11px;cursor:pointer;position:relative;min-width:76px}
  .step.on{border-color:#ffd98a}
  .step .st-fx{color:#e8d9b8}
  .step .st-sub{color:#8a7a5a;font-size:9px}
  .step .st-del{position:absolute;top:1px;right:4px;color:#c05a3a;font-size:10px}
  .arrow{color:#5a4626;align-self:center;font-size:14px}
  .gapchip{align-self:center;font-size:9px;color:#8a7a5a}
  .gapchip input{width:40px;font-size:9px;padding:1px 2px}
  #stepEd{margin-top:10px;padding:8px 10px;background:#241a0e;border:1px solid #5a4626;
    border-radius:6px;display:none}
  #stepEd.on{display:block}
  #lightRow label{display:inline-block;min-width:210px;margin:3px 10px 3px 0}
</style>""",
    'v5 CSS')

# ── B. the panel restructures into tabs (all old ids preserved) ──
sub(u"""<div id="panel">
  <h1>FARK VFX LAB</h1>
  <div class="sub">The frame runs the REAL game — FX call the game's own functions.
    Author a recipe (keyframes + FX events on a target), SAVE it under a card + moment,
    EXPORT the JSON — that JSON is the implementation spec Claude wires into the
    pipeline, respecting the established gates. Designs: docs/CARD_VFX.md</div>

  <div class="grp">Setup</div>
  <div class="row">
    <button onclick="setup()">Boot into a match</button>
    <button onclick="roll()">Roll</button>
    <button onclick="reloadFrame()">Reload frame</button>
  </div>
  <div class="row">
    <select id="cardPick"></select>
    <select id="tierPick"><option value="1">tier I</option><option value="2">II</option><option value="3">III</option></select>
    <button onclick="addCard()">add to hand</button>
    <button onclick="clearHand()">clear hand</button>
  </div>

  <div class="grp">Target <span style="text-transform:none;color:#9a8a68">(pick, then the sliders move IT — live)</span></div>
  <div class="row" id="targetRow"><i style="color:#9a8a68">boot first</i></div>
  <div class="row">
    <label>dx <input type="range" id="pDx" min="-220" max="220" value="0" oninput="applyProps()"></label>
    <label>dy <input type="range" id="pDy" min="-320" max="320" value="0" oninput="applyProps()"></label>
    <label>scale <input type="range" id="pSc" min="0" max="300" value="100" oninput="applyProps()"></label>
  </div>
  <div class="row">
    <label>opacity <input type="range" id="pOp" min="0" max="100" value="100" oninput="applyProps()"></label>
    <label>rotate <input type="range" id="pRt" min="-180" max="180" value="0" oninput="applyProps()"></label>
    <button onclick="resetProps()">reset target</button>
  </div>
  <div class="row" style="border:1px dashed #3a2c18;border-radius:4px;padding:4px 8px">
    <b style="color:#c8a45c;font-size:11px;margin-right:6px">SHELL STUDIO</b>
    <label>corner% <input type="range" id="pCr" min="0" max="30" value="12"></label>
    <label>opacity <input type="range" id="shOp" min="10" max="90" value="42"></label>
    <label>specular <input type="range" id="shSpec" min="0" max="120" value="45"></label>
    <label>rims <select id="shRims"><option>1</option><option selected>2</option><option>3</option></select></label>
    <label>bubbles <input type="range" id="shBub" min="0" max="8" value="4"></label>
    <label>ghost blur% <input type="range" id="shGhost" min="0" max="60" value="25"></label>
  </div>

  <div class="grp">FX palette <span style="text-transform:none;color:#9a8a68">(fires on the target with the params below)</span></div>""",
    u"""<div id="panel">
  <h1>FARK VFX LAB</h1>
  <div id="tabs">
    <button id="tabB0" class="on" onclick="showTab(0)">Stage</button>
    <button id="tabB1" onclick="showTab(1)">Card studio</button>
    <button id="tabB2" onclick="showTab(2)">Advanced</button>
  </div>

  <!-- ═══ TAB 0 : STAGE ═══ -->
  <div class="tab on" id="tab0">
  <div class="card-sec">
    <h3>Setup</h3>
    <div class="row">
      <button onclick="setup()">Boot into a match</button>
      <button onclick="roll()">Roll</button>
      <button id="audBtn" class="on" onclick="toggleAudio()">game audio: OFF</button>
      <button onclick="reloadFrame()">Reload frame</button>
    </div>
    <div class="row">
      <select id="cardPick"></select>
      <select id="tierPick"><option value="1">tier I</option><option value="2">II</option><option value="3">III</option></select>
      <button onclick="addCard()">add to hand</button>
      <button onclick="clearHand()">clear hand</button>
    </div>
  </div>

  <div class="card-sec">
    <h3>Light studio <span style="text-transform:none;color:#9a8a68">(every light gets its own slider after boot)</span></h3>
    <div id="lightRow"><i style="color:#9a8a68">boot first — the sliders build from the live scene</i></div>
  </div>

  <div class="card-sec">
    <h3>Die dresser <span style="text-transform:none;color:#9a8a68">(pick a die target below, then give it a material or a brand)</span></h3>
    <div class="row">
      <select id="dressMat"></select>
      <button onclick="applyMat()">give material</button>
      <select id="dressEnch"></select>
      <select id="dressFace"><option>5</option><option>1</option></select>
      <button onclick="applyEnch()">give brand</button>
      <button onclick="clearEnch()">clear brand</button>
    </div>
  </div>

  <div class="card-sec">
    <h3>Target &amp; hand controls</h3>
    <div class="row" id="targetRow"><i style="color:#9a8a68">boot first</i></div>
    <div class="row">
      <label>dx <input type="range" id="pDx" min="-220" max="220" value="0" oninput="applyProps()"></label>
      <label>dy <input type="range" id="pDy" min="-320" max="320" value="0" oninput="applyProps()"></label>
      <label>scale <input type="range" id="pSc" min="0" max="300" value="100" oninput="applyProps()"></label>
    </div>
    <div class="row">
      <label>opacity <input type="range" id="pOp" min="0" max="100" value="100" oninput="applyProps()"></label>
      <label>rotate <input type="range" id="pRt" min="-180" max="180" value="0" oninput="applyProps()"></label>
      <button onclick="resetProps()">reset target</button>
    </div>
    <div class="row">
      <b style="color:#c8a45c;font-size:11px;margin-right:6px">SHELL STUDIO</b>
      <label>corner% <input type="range" id="pCr" min="0" max="30" value="12"></label>
      <label>opacity <input type="range" id="shOp" min="10" max="90" value="42"></label>
      <label>specular <input type="range" id="shSpec" min="0" max="120" value="45"></label>
      <label>rims <select id="shRims"><option>1</option><option selected>2</option><option>3</option></select></label>
      <label>bubbles <input type="range" id="shBub" min="0" max="8" value="4"></label>
      <label>ghost blur% <input type="range" id="shGhost" min="0" max="60" value="25"></label>
    </div>
  </div>
  </div>

  <!-- ═══ TAB 1 : CARD STUDIO ═══ -->
  <div class="tab" id="tab1">
    <div class="card-sec" id="galSec">
      <h3>Pick what you're designing <span style="text-transform:none;color:#9a8a68">(cards · dice · enchants — green dot = you noted it)</span></h3>
      <div id="gallery"><i style="color:#9a8a68">boot first</i></div>
    </div>
    <div id="ws">
      <button onclick="closeStudio()" style="margin-bottom:8px">← all cards</button>
      <div class="card-sec">
        <div id="wsHead"></div>
        <div class="pills" id="wsPills"></div>
        <div class="row">
          <button onclick="studioPlay()">▶ test on the table</button>
          <button onclick="studioSave()">save this moment</button>
          <span id="wsState" style="font-size:11px;color:#8a7a5a"></span>
        </div>
      </div>
      <div class="card-sec">
        <h3>The sequence <span style="text-transform:none;color:#9a8a68">(drag from the left · click a step to tune it · ✕ removes)</span></h3>
        <div id="seq">
          <div id="seqPal"></div>
          <div style="flex:1">
            <div id="seqLane" ondragover="laneOver(event)" ondragleave="laneLeave(event)" ondrop="laneDrop(event)"></div>
            <div id="stepEd"></div>
          </div>
        </div>
      </div>
      <div class="card-sec">
        <h3>Your spec notes <span style="text-transform:none;color:#9a8a68">(the authoritative channel — Claude implements from this)</span></h3>
        <textarea id="wsNotes" style="width:100%;height:70px;background:#12100a;color:#d8c9a0;border:1px solid #5a4626;font-family:inherit;font-size:12px;padding:6px" onchange="studioNoteSave()"></textarea>
      </div>
    </div>
  </div>

  <!-- ═══ TAB 2 : ADVANCED (the dev view - untouched machinery) ═══ -->
  <div class="tab" id="tab2">
  <div class="grp">FX palette <span style="text-transform:none;color:#9a8a68">(fires on the target with the params below)</span></div>""",
    'panel tabs restructure (head)')

# close tab2 + move export/catalogue/presets inside it; log stays outside
sub(u"""  <div class="grp">Presets (curated compositions)</div>
  <div class="row">
    <button onclick="r_amberSet()">amber sets</button>
    <button onclick="r_amberPark()">amber parks</button>
    <button onclick="r_amberReturn()">amber returns</button>
    <button onclick="r_redCandle()">red candle</button>
    <button onclick="r_shield()">bust shield</button>
    <button onclick="r_dimmerRoom()">darker room</button>
    <button onclick="r_softerKey()">softer key</button>
    <button onclick="r_resetLook()">reset look</button>
  </div>

  <div id="log"></div>
</div>""",
    u"""  <div class="grp">Presets (curated compositions)</div>
  <div class="row">
    <button onclick="r_amberSet()">amber sets</button>
    <button onclick="r_amberPark()">amber parks</button>
    <button onclick="r_amberReturn()">amber returns</button>
    <button onclick="r_redCandle()">red candle</button>
    <button onclick="r_shield()">bust shield</button>
  </div>
  </div>

  <div id="log"></div>
</div>""",
    'panel tabs restructure (tail)')

# ── C. setup() also builds lights, mutes audio, fills studio ──
sub(u"  log(ok?'match ready':'boot FAILED');\n  if(ok){fillCards();buildTargets();}",
    u"  log(ok?'match ready':'boot FAILED');\n"
    u"  if(ok){fillCards();buildTargets();buildLights();muteGame(_gameMuted);fillDresser();buildGallery();}",
    'setup wires the new panels')

# ── D. the new JS ──
NEW_JS = u"""
/* ═══ v5: tabs ═══ */
function showTab(i){
  for(var t=0;t<3;t++){
    document.getElementById('tab'+t).classList.toggle('on',t===i);
    document.getElementById('tabB'+t).classList.toggle('on',t===i);
  }
}

/* ═══ v5: game audio OFF by default (music + ambiance mp3s; the lab's
   own synth bank is untouched) ═══ */
var _gameMuted=true;
function muteGame(onOff){
  _gameMuted=onOff;
  try{gw();W.document.querySelectorAll('audio').forEach(function(a){
    a.muted=onOff;if(onOff)try{a.pause();}catch(e){}});}catch(e){}
  var b=document.getElementById('audBtn');
  if(b){b.textContent='game audio: '+(onOff?'OFF':'ON');b.classList.toggle('on',onOff);}
}
function toggleAudio(){muteGame(!_gameMuted);}
/* new <audio> elements appear later (music layers) - re-assert quietly */
setInterval(function(){if(_gameMuted)try{gw();W.document.querySelectorAll('audio').forEach(function(a){
  if(!a.muted){a.muted=true;try{a.pause();}catch(e){}}});}catch(e){}},1500);

/* ═══ v5: LIGHT STUDIO - every light in the live scene gets a slider,
   plus env brightness (art only, dice untouched), dice side-shadow
   strength, and an added bounce fill from below. ═══ */
var _lights=[],_bounce=null;
function buildLights(){
  var dx=E('window.D3X');
  var host=document.getElementById('lightRow');
  if(!dx||!dx.scene){host.innerHTML='<i>no 3D scene</i>';return;}
  _lights=[];
  dx.scene.traverse(function(o){if(o.isLight&&o!==_bounce)_lights.push(o);});
  var h='';
  _lights.forEach(function(l,i){
    l.userData._lab0=l.userData._lab0===undefined?l.intensity:l.userData._lab0;
    var nm=l.type.replace('Light','').toLowerCase();
    h+='<label>'+nm+' light <input type="range" min="0" max="220" value="'+Math.round(l.intensity/(l.userData._lab0||1)*100)+'" oninput="lightSet('+i+',this.value)"> <span id="lv'+i+'">'+Math.round(l.intensity*100)/100+'</span></label>';
  });
  h+='<label>bounce fill <input type="range" min="0" max="120" value="0" oninput="bounceSet(this.value)"> <span id="lvB">off</span></label>';
  h+='<br><label>env art brightness <input type="range" min="40" max="110" value="100" oninput="envSet(this.value)"> <span id="lvE">100%</span></label>';
  h+='<label>dice side-shadow <input type="range" min="0" max="90" value="'+Math.round((E('D3X.SIDEDIM_MAX')||0.5)*100)+'" oninput="sideSet(this.value)"> <span id="lvS"></span></label>';
  h+='<button onclick="lightsReset()" style="margin-left:8px">reset lights</button>';
  host.innerHTML=h;
  log('light studio: '+_lights.length+' scene lights found');
}
function lightSet(i,v){var l=_lights[i];if(!l)return;
  l.intensity=(l.userData._lab0||1)*v/100;
  var sp=document.getElementById('lv'+i);if(sp)sp.textContent=Math.round(l.intensity*100)/100;}
function bounceSet(v){
  var dx=E('window.D3X');if(!dx||!dx.scene)return;
  var T=W.__labEval('THREE');
  if(!_bounce){_bounce=new T.DirectionalLight(0xffe8c8,0);
    _bounce.position.set(0,-1,0.6);dx.scene.add(_bounce);}
  _bounce.intensity=v/100*0.8;
  var sp=document.getElementById('lvB');if(sp)sp.textContent=v>0?(_bounce.intensity.toFixed(2)):'off';}
function envSet(v){
  /* the ART dims; dice (canvas) and rows stay untouched - this is what
     'darker room' should have been */
  gw();var ms=W.document.getElementById('screen-match');if(!ms)return;
  ms.querySelectorAll('img').forEach(function(im){
    if(im.closest('#playerDiceRow,#oppDiceRow,#keptRow,#famRowP,#famRowO'))return;
    im.style.filter=v>=100?'':'brightness('+(v/100)+')';
  });
  var sp=document.getElementById('lvE');if(sp)sp.textContent=v+'%';}
function sideSet(v){E('D3X.SIDEDIM_MAX='+(v/100));
  var sp=document.getElementById('lvS');if(sp)sp.textContent=(v/100).toFixed(2);}
function lightsReset(){
  _lights.forEach(function(l){if(l.userData._lab0!==undefined)l.intensity=l.userData._lab0;});
  if(_bounce)_bounce.intensity=0;
  envSet(100);buildLights();}

/* ═══ v5: DIE DRESSER - click a die target, give it a material/brand ═══ */
var _MATS=['lucky','bone','iron','flint','lead','amber','jade','jade2','jade3',
  'brass','silver','crystal','ruby','obsidian','starstone','vagabond'];
var _ENCHS=['tithe','ward','snare','trade','snuff','quicksilver'];
function fillDresser(){
  document.getElementById('dressMat').innerHTML=_MATS.map(function(m){
    return '<option>'+m+'</option>';}).join('');
  document.getElementById('dressEnch').innerHTML=_ENCHS.map(function(e2){
    return '<option>'+e2+'</option>';}).join('');
}
function _dressSlot(){
  if(!target||target.k!=='die'){log('pick a DIE target first');return -1;}
  return target.i;
}
function applyMat(){
  var i=_dressSlot();if(i<0)return;
  var m=document.getElementById('dressMat').value;
  E('S.run.dice['+i+']='+JSON.stringify(m));
  E('G&&G.matchDice&&(G.matchDice['+i+']='+JSON.stringify(m)+')');
  var dx=E('window.D3X');var ds=dx.dice.filter(function(d){return d.match&&d.chip;});
  if(ds[i]){ds[i].mat=m;try{ds[i].chip._trueMat=m;}catch(e){}}
  E('D3X._reskin&&D3X._reskin()');
  log('die '+i+' is now '+m);
}
function applyEnch(){
  var i=_dressSlot();if(i<0)return;
  var k=document.getElementById('dressEnch').value;
  var face=+document.getElementById('dressFace').value;
  var ench=(k==='quicksilver')?{t:k}:{t:k,face:face};
  E('S.run.dieEnch=S.run.dieEnch||[];S.run.dieEnch['+i+']='+JSON.stringify(ench));
  E('G&&(G._enchArr=G._enchArr||[null,null,null,null,null,null],G._enchArr['+i+']='+JSON.stringify(ench)+')');
  E('D3X._reskin&&D3X._reskin()');
  log('die '+i+' branded: '+k+(ench.face?(' on its '+face):''));
}
function clearEnch(){
  var i=_dressSlot();if(i<0)return;
  E('S.run.dieEnch&&(S.run.dieEnch['+i+']=null)');
  E('G&&G._enchArr&&(G._enchArr['+i+']=null)');
  E('D3X._reskin&&D3X._reskin()');
  log('die '+i+' brand cleared');
}

/* ═══ v5: CARD STUDIO - gallery, workspace, step sequencer ═══ */
var _MATCOLS={lucky:'#dddd66',bone:'#f3e7c8',iron:'#b8c0d0',flint:'#9e9e9e',
  lead:'#a0a8c0',amber:'#ffd870',jade:'#70d898',jade2:'#4fc47e',jade3:'#2fae66',
  brass:'#e8b860',silver:'#e0e8f0',crystal:'#a8e8ff',ruby:'#ff7888',
  obsidian:'#c8a0e8',starstone:'#b0b8ff',vagabond:'#ff7888'};
var _studioId=null,_studioMoment='cast';
function buildGallery(){
  var live=E('FAM_LIVE')||{};var ns=noteStore();
  var h='';
  Object.keys(live).forEach(function(id){
    var d=E('famDef('+JSON.stringify(id)+')');if(!d)return;
    h+='<div class="gcard" onclick="openStudio('+JSON.stringify(id)+')">'
      +'<img src="assets/cards/'+id+'.webp" onerror="this.style.display=&quot;none&quot;">'
      +'<div class="gname">'+d.name+'</div>'
      +'<div class="gnote">'+(ns[id]?'\\u25cf':'')+'</div></div>';
  });
  _MATS.forEach(function(m){
    h+='<div class="gcard" onclick="openStudio('+JSON.stringify('mat:'+m)+')">'
      +'<div class="swatch" style="background:'+(_MATCOLS[m]||'#888')+'"></div>'
      +'<div class="gname">'+m+' die</div>'
      +'<div class="gnote">'+(ns['mat:'+m]?'\\u25cf':'')+'</div></div>';
  });
  _ENCHS.forEach(function(e2){
    h+='<div class="gcard" onclick="openStudio('+JSON.stringify('ench:'+e2)+')">'
      +'<div class="swatch" style="background:#241a0e;display:flex;align-items:center;justify-content:center;color:#ffd98a;font-size:22px">\\u2726</div>'
      +'<div class="gname">'+e2+'</div>'
      +'<div class="gnote">'+(ns['ench:'+e2]?'\\u25cf':'')+'</div></div>';
  });
  document.getElementById('gallery').innerHTML=h;
}
function openStudio(id){
  _studioId=id;
  document.getElementById('galSec').style.display='none';
  document.getElementById('ws').classList.add('on');
  var head=document.getElementById('wsHead');
  var isCard=id.indexOf(':')<0;
  var name=id,rules='';
  if(isCard){var d=E('famDef('+JSON.stringify(id)+')');
    if(d){name=d.name;rules=(d.text||[]).map(function(t,i){
      return '<b>'+['I','II','III'][i]+'.</b> '+t;}).join('<br>');}
    head.innerHTML='<img src="assets/cards/'+id+'.webp" onerror="this.style.display=&quot;none&quot;">'
      +'<div><div id="wsName">'+name+'</div><div id="wsRules">'+rules+'</div></div>';
    /* the card comes to the table so ▶ test hits the real thing */
    var g=E('G');
    if(g&&!(g.pF||[]).some(function(x){return x.id===id;})){
      document.getElementById('cardPick').value=id;addCard();
    }
  }else{
    var kind=id.split(':')[0],key=id.split(':')[1];
    var meta=ID_META[id];
    head.innerHTML='<div class="swatch" style="background:'+(kind==='mat'?(_MATCOLS[key]||'#888'):'#241a0e')+'"></div>'
      +'<div><div id="wsName">'+key+' '+(kind==='mat'?'die':'brand')+'</div>'
      +'<div id="wsRules">'+(meta?meta.n:'')+'</div></div>';
  }
  var pills=['cast','resolve','park','return','opp-fire','passive-glint'];
  document.getElementById('wsPills').innerHTML=pills.map(function(p){
    return '<span class="pill'+(p===_studioMoment?' on':'')+'" onclick="pickMoment(&quot;'+p+'&quot;,this)">'+p+'</span>';}).join('');
  document.getElementById('wsNotes').value=noteStore()[id]||'';
  studioLoad();
}
function closeStudio(){
  _studioId=null;
  document.getElementById('galSec').style.display='';
  document.getElementById('ws').classList.remove('on');
  buildGallery();
}
function pickMoment(m,el){_studioMoment=m;
  document.querySelectorAll('#wsPills .pill').forEach(function(p){p.classList.remove('on');});
  if(el)el.classList.add('on');
  studioLoad();}
function studioLoad(){
  var r=(store()[_studioId]||{})[_studioMoment];
  if(r){rec={keys:r.keys||[],fx:r.fx||[]};
    document.getElementById('wsState').textContent='saved version loaded';}
  else{var pr=labPreset(_studioId);
    rec=pr?{keys:pr.keys,fx:pr.fx}:{keys:[],fx:[]};
    document.getElementById('wsState').textContent=pr?'base preset — tweak away':'empty';}
  renderTables();renderSeq();
}
function studioSave(){
  var all=store();all[_studioId]=all[_studioId]||{};
  all[_studioId][_studioMoment]={target:target,keys:rec.keys,fx:rec.fx,
    notes:document.getElementById('wsNotes').value,saved:new Date().toISOString()};
  localStorage.fkLabRecipes=JSON.stringify(all);
  document.getElementById('wsState').textContent='saved \\u2713';
  log('saved '+_studioId+' / '+_studioMoment);}
function studioNoteSave(){saveNote(_studioId,document.getElementById('wsNotes').value);}
function studioPlay(){
  if(!target){
    /* sensible default: cards target themselves if dealt, else die 0 */
    if(_studioId&&_studioId.indexOf(':')<0){
      var g=E('G'),ix=((g&&g.pF)||[]).findIndex(function(x){return x.id===_studioId;});
      target=ix>=0?{k:'card',i:ix}:{k:'die',i:0};
    }else target={k:'die',i:0};
  }
  playRecipe();
}

/* ── the step sequencer: rec.fx as draggable steps ── */
var _MOTIONS={
  pop:[K(0,{}),K(140,{sc:110},'back-out'),K(320,{sc:100},'ease-out')],
  shake:[K(0,{}),K(60,{dx:-7},'ease-in'),K(120,{dx:7}),K(180,{dx:-3}),K(240,{dx:0},'back-out')],
  spin:[K(0,{}),K(300,{rt:180,sc:106},'ease-out'),K(620,{rt:360,sc:100},'back-out')],
  rise:[K(0,{}),K(260,{dy:-38},'ease-out'),K(700,{dy:-38}),K(1000,{dy:0},'back-out')],
  sink:[K(0,{}),K(400,{dy:44,sc:82},'ease-out')],
  fade:[K(0,{}),K(350,{op:0},'ease-out')],
  snap:[K(0,{}),K(60,{sc:95,rt:-2},'ease-in'),K(120,{sc:93,rt:2}),K(200,{sc:93,rt:-1}),K(340,{sc:100,rt:0},'back-out')]
};
var _selStep=-1;
function buildSeqPal(){
  var pal=document.getElementById('seqPal');
  var mk=function(cls,name){return '<span class="chip '+cls+'" draggable="true" ondragstart="palDrag(event,&quot;'+name+'&quot;)">'+name+'</span>';};
  var h='<div class="pgrp">motion</div>';
  Object.keys(_MOTIONS).forEach(function(m){h+=mk('m','motion:'+m);});
  h+='<div class="pgrp">visual</div>';
  ['spray','glow','flash','beam','ghost','amberShell','clearShell','break','shield','candle'].forEach(function(f){h+=mk('v',f);});
  h+='<div class="pgrp">sound</div>';
  SND.families.forEach(function(f){h+=mk('s','sound:'+f);});
  h+='<div class="pgrp">text</div>'+mk('v','announce');
  pal.innerHTML=h;
}
function palDrag(ev,name){ev.dataTransfer.setData('text/plain',name);}
function laneOver(ev){ev.preventDefault();document.getElementById('seqLane').classList.add('over');}
function laneLeave(ev){document.getElementById('seqLane').classList.remove('over');}
function laneDrop(ev){
  ev.preventDefault();document.getElementById('seqLane').classList.remove('over');
  var name=ev.dataTransfer.getData('text/plain');if(!name)return;
  if(name.slice(0,7)==='motion:'){
    rec.keys=_MOTIONS[name.slice(7)].map(function(k){return Object.assign({},k);});
    renderTables();renderSeq();log('motion set: '+name.slice(7));return;
  }
  var p;
  if(name.slice(0,6)==='sound:'){p={snd:name.slice(6),pitch:1,layers:1};name='sound';}
  else p=Object.assign({},fxParams());
  var last=rec.fx.length?rec.fx[rec.fx.length-1].t:0;
  rec.fx.push({t:last+160,fx:name,p:p});
  renderTables();renderSeq();
}
function renderSeq(){
  var lane=document.getElementById('seqLane');
  var h='';
  if(rec.keys.length>1){
    var mn='motion';
    Object.keys(_MOTIONS).forEach(function(m){
      if(JSON.stringify(_MOTIONS[m].map(function(k){return [k.t,k.dx,k.dy,k.sc,k.op,k.rt];}))
        ===JSON.stringify(rec.keys.map(function(k){return [k.t,k.dx,k.dy,k.sc,k.op,k.rt];})))mn=m;});
    h+='<div class="step" onclick="showTab(2)"><span class="st-fx">\\u21bb '+mn+'</span>'
      +'<div class="st-sub">'+rec.keys.length+' keys \\u00b7 edit in Advanced</div>'
      +'<span class="st-del" onclick="event.stopPropagation();rec.keys=[];renderTables();renderSeq()">\\u2715</span></div>'
      +'<span class="arrow">+</span>';
  }
  var prev=0;
  rec.fx.forEach(function(f,i){
    if(i>0)h+='<span class="arrow">\\u2192</span>';
    h+='<span class="gapchip">+<input type="number" value="'+(f.t-prev)+'" onchange="stepGap('+i+',this.value)">ms</span>';
    var sub=f.fx==='sound'?(f.p.snd+' \\u00d7'+(f.p.layers||1))
      :(f.fx==='announce'?('\\u201c'+String(f.p.text||'').slice(0,14)+'\\u2026\\u201d')
      :((f.p.col||'')+' n'+(f.p.count||'')));
    h+='<div class="step'+(i===_selStep?' on':'')+'" onclick="stepPick('+i+')">'
      +'<span class="st-fx">'+f.fx+'</span><div class="st-sub">'+sub+'</div>'
      +'<span class="st-del" onclick="event.stopPropagation();rec.fx.splice('+i+',1);_selStep=-1;renderTables();renderSeq()">\\u2715</span></div>';
    prev=f.t;
  });
  lane.innerHTML=h||'<i style="color:#5a4626">drag effects here \\u2014 first this, then this\\u2026</i>';
  renderStepEd();
}
function stepGap(i,v){
  var delta=(+v)-(rec.fx[i].t-(i>0?rec.fx[i-1].t:0));
  for(var j=i;j<rec.fx.length;j++)rec.fx[j].t+=delta;
  renderTables();renderSeq();}
function stepPick(i){_selStep=i;renderSeq();}
function renderStepEd(){
  var ed=document.getElementById('stepEd');
  var f=rec.fx[_selStep];
  if(!f){ed.classList.remove('on');return;}
  ed.classList.add('on');
  var h='<b style="color:#ffd98a;font-size:12px">'+f.fx+'</b> ';
  if(f.fx==='sound'){
    h+='<label>family <select onchange="rec.fx['+_selStep+'].p.snd=this.value;renderSeq()">'
      +SND.families.map(function(x){return '<option'+(x===f.p.snd?' selected':'')+'>'+x+'</option>';}).join('')+'</select></label>'
      +'<label>pitch <input type="range" min="50" max="200" value="'+((f.p.pitch||1)*100)+'" oninput="rec.fx['+_selStep+'].p.pitch=this.value/100"></label>'
      +'<label>voices <select onchange="rec.fx['+_selStep+'].p.layers=+this.value">'
      +[1,2,3].map(function(x){return '<option'+(x===(f.p.layers||1)?' selected':'')+'>'+x+'</option>';}).join('')+'</select></label>'
      +'<button onclick="SND.play(rec.fx['+_selStep+'].p.snd,rec.fx['+_selStep+'].p)">\\u25b6 hear</button>';
  }else if(f.fx==='announce'){
    h+='<input type="text" value="'+String(f.p.text||'').replace(/"/g,'&quot;')+'" size="40" onchange="rec.fx['+_selStep+'].p.text=this.value;renderSeq()">'
      +'<select onchange="rec.fx['+_selStep+'].p.annCol=this.value">'
      +['gold','red','green'].map(function(x){return '<option'+(x===f.p.annCol?' selected':'')+'>'+x+'</option>';}).join('')+'</select>';
  }else{
    h+='<label>colour <input type="color" value="'+(f.p.col||'#ffd98a')+'" oninput="rec.fx['+_selStep+'].p.col=this.value;renderSeq()"></label>'
      +'<label>count <input type="number" value="'+(f.p.count||16)+'" onchange="rec.fx['+_selStep+'].p.count=+this.value;renderSeq()"></label>'
      +'<label>speed <input type="number" value="'+(f.p.speed||85)+'" onchange="rec.fx['+_selStep+'].p.speed=+this.value"></label>'
      +'<label>gravity <input type="number" value="'+(f.p.g===undefined?110:f.p.g)+'" onchange="rec.fx['+_selStep+'].p.g=+this.value"></label>'
      +'<label>size <input type="number" value="'+(f.p.size||7)+'" onchange="rec.fx['+_selStep+'].p.size=+this.value"></label>'
      +'<label>ms <input type="number" value="'+(f.p.ms||600)+'" onchange="rec.fx['+_selStep+'].p.ms=+this.value"></label>'
      +'<button onclick="fire(rec.fx['+_selStep+'].fx,rec.fx['+_selStep+'].p)">\\u25b6 fire once</button>';
  }
  ed.innerHTML=h;
}
buildSeqPal();
/* keep the sequencer in step with Advanced edits */
var _origRenderTables=renderTables;
renderTables=function(){_origRenderTables();try{renderSeq();}catch(e){}};
"""

sub(u"function r_resetLook(){gw();var ms=W.document.getElementById('screen-match');\n"
    u"  if(ms)ms.style.filter='';log('reset (reload frame for exact lights)');}\n"
    u"</script>",
    u"function r_resetLook(){gw();var ms=W.document.getElementById('screen-match');\n"
    u"  if(ms)ms.style.filter='';log('reset (reload frame for exact lights)');}\n"
    + NEW_JS +
    u"</script>",
    'v5 JS appended')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
