# -*- coding: utf-8 -*-
"""Lab v9: the look persists. Every look dial saves to localStorage on
change (debounced) and re-applies on attach - the settings Denis
approves ARE the default from then on; reset look forgets them."""
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


sub(u"function copyLook(){",
    u"""var _lookT=null,_lastShadow=0;
function saveLook(){
  /* the look persists per browser and re-applies on every boot - the
     settings Denis approves ARE the default from then on */
  clearTimeout(_lookT);
  _lookT=setTimeout(function(){
    var v=function(id){var e2=document.getElementById(id);return e2?+e2.value:null;};
    var lk={vgA:v('vgA'),vgR:v('vgR'),vgC:v('vgC'),
      sh:_lastShadow||0,sd:E('D3X.SIDEDIM_MAX'),
      maskAmt:v('dgAmt'),maskAxis:(document.getElementById('dgAxis')||{}).value,
      bounce:_bounce?+_bounce.intensity.toFixed(3):0,
      lights:_lights.map(function(l){return +(l.intensity/(l.userData._lab0||1)).toFixed(3);}),
      GLOW:E('JSON.parse(JSON.stringify(D3X.GLOW))')};
    try{localStorage.fkLabLook=JSON.stringify(lk);}catch(e){}
  },400);
}
function applyLook(){
  var lk=null;try{lk=JSON.parse(localStorage.fkLabLook||'null');}catch(e){}
  if(!lk)return;
  var set=function(id,val){var e2=document.getElementById(id);
    if(e2&&val!==null&&val!==undefined)e2.value=val;};
  set('vgA',lk.vgA);set('vgR',lk.vgR);set('vgC',lk.vgC);vigSet();
  if(lk.sh)shadowSet(lk.sh);
  if(lk.sd!==null&&lk.sd!==undefined){E('D3X.SIDEDIM_MAX='+lk.sd);
    var sp=document.getElementById('lvS');if(sp)sp.textContent=(+lk.sd).toFixed(2);}
  if(lk.maskAmt){set('dgAmt',lk.maskAmt);
    var ax=document.getElementById('dgAxis');if(ax&&lk.maskAxis)ax.value=lk.maskAxis;
    gradeDice(lk.maskAmt);}
  if(lk.bounce)bounceSet(Math.round(lk.bounce/0.8*100));
  (lk.lights||[]).forEach(function(ratio,i){if(_lights[i])lightSet(i,Math.round(ratio*100));});
  if(lk.GLOW){Object.keys(lk.GLOW).forEach(function(k){
      E('D3X.GLOW.'+k+'='+JSON.stringify(lk.GLOW[k]));});
    var map={strength:['gStr',100],soft:['gSoft',1],rim:['gRim',1],line:['gLine',1],
      sx:['gSx',100],sy:['gSy',100],dy:['gDy',1]};
    Object.keys(map).forEach(function(k){
      if(lk.GLOW[k]!==undefined)set(map[k][0],lk.GLOW[k]*map[k][1]);});
    E('D3X._drawGlow&&D3X._drawGlow()');}
  log('saved look applied - this browser remembers it');
}
function copyLook(){""",
    'saveLook + applyLook')

sub(u"  var sp=document.getElementById('lvE');if(sp)sp.textContent=a>0?Math.round(a*100)+'%':'off';}",
    u"  var sp=document.getElementById('lvE');if(sp)sp.textContent=a>0?Math.round(a*100)+'%':'off';saveLook();}",
    'vigSet saves')

sub(u"""function shadowSet(v){
  gw();var msd=W.document.getElementById('matchShadows');
  if(msd)msd.style.filter=v>0?'brightness('+(1-v/100)+')':'';
  var sp=document.getElementById('lvSh');if(sp)sp.textContent=v>0?('-'+v+'%'):'normal';}""",
    u"""function shadowSet(v){
  gw();var msd=W.document.getElementById('matchShadows');
  if(msd)msd.style.filter=v>0?'brightness('+(1-v/100)+')':'';
  _lastShadow=+v;
  var sp=document.getElementById('lvSh');if(sp)sp.textContent=v>0?('-'+v+'%'):'normal';saveLook();}""",
    'shadowSet saves')

sub(u"""function sideSet(v){E('D3X.SIDEDIM_MAX='+(v/100));
  var sp=document.getElementById('lvS');if(sp)sp.textContent=(v/100).toFixed(2);}""",
    u"""function sideSet(v){E('D3X.SIDEDIM_MAX='+(v/100));
  var sp=document.getElementById('lvS');if(sp)sp.textContent=(v/100).toFixed(2);saveLook();}""",
    'sideSet saves')

sub(u"""  var sp=document.getElementById('lvG');
  if(sp)sp.textContent=amt===0?'off':((amt>0?'+':'')+amt+' '+axis);
}""",
    u"""  var sp=document.getElementById('lvG');
  if(sp)sp.textContent=amt===0?'off':((amt>0?'+':'')+amt+' '+axis);
  saveLook();
}""",
    'gradeDice saves')

sub(u"""function glowDial(field,v){
  /* the REAL glow: D3X.GLOW's own dials + P731's sx/sy/dy */
  E('D3X.GLOW.'+field+'='+v);
  E('D3X._drawGlow&&D3X._drawGlow()');
}""",
    u"""function glowDial(field,v){
  /* the REAL glow: D3X.GLOW's own dials + P731's sx/sy/dy */
  E('D3X.GLOW.'+field+'='+v);
  E('D3X._drawGlow&&D3X._drawGlow()');
  saveLook();
}""",
    'glowDial saves')

sub(u"""function lightSet(i,v){var l=_lights[i];if(!l)return;
  l.intensity=(l.userData._lab0||1)*v/100;
  var sp=document.getElementById('lv'+i);if(sp)sp.textContent=Math.round(l.intensity*100)/100;}""",
    u"""function lightSet(i,v){var l=_lights[i];if(!l)return;
  l.intensity=(l.userData._lab0||1)*v/100;
  var sp=document.getElementById('lv'+i);if(sp)sp.textContent=Math.round(l.intensity*100)/100;saveLook();}""",
    'lightSet saves')

sub(u"""  _bounce.intensity=v/100*0.8;
  var sp=document.getElementById('lvB');if(sp)sp.textContent=v>0?(_bounce.intensity.toFixed(2)):'off';}""",
    u"""  _bounce.intensity=v/100*0.8;
  var sp=document.getElementById('lvB');if(sp)sp.textContent=v>0?(_bounce.intensity.toFixed(2)):'off';saveLook();}""",
    'bounceSet saves')

sub(u"""function attach(){
  fillCards();buildTargets();buildLights();muteGame(_gameMuted);
  fillDresser();buildGallery();
  log('ATTACHED - the lab is driving the live match');
}""",
    u"""function attach(){
  fillCards();buildTargets();buildLights();muteGame(_gameMuted);
  fillDresser();buildGallery();
  log('ATTACHED - the lab is driving the live match');
  setTimeout(applyLook,400);/* after the studio rows exist */
}""",
    'attach applies the saved look')

sub(u"""function lightsReset(){
  _lights.forEach(function(l){if(l.userData._lab0!==undefined)l.intensity=l.userData._lab0;});""",
    u"""function lightsReset(){
  try{delete localStorage.fkLabLook;}catch(e){}
  _lights.forEach(function(l){if(l.userData._lab0!==undefined)l.intensity=l.userData._lab0;});""",
    'reset forgets the saved look')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
