# -*- coding: utf-8 -*-
"""Lab v3a: the sound bank + rounded shell corners (C15c part 1)."""
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


sub(u"""    <label>opacity <input type="range" id="pOp" min="0" max="100" value="100" oninput="applyProps()"></label>
    <label>rotate <input type="range" id="pRt" min="-180" max="180" value="0" oninput="applyProps()"></label>
    <button onclick="resetProps()">reset target</button>""",
    u"""    <label>opacity <input type="range" id="pOp" min="0" max="100" value="100" oninput="applyProps()"></label>
    <label>rotate <input type="range" id="pRt" min="-180" max="180" value="0" oninput="applyProps()"></label>
    <label>shell corner% <input type="range" id="pCr" min="0" max="30" value="12"></label>
    <button onclick="resetProps()">reset target</button>""",
    'corner slider')

sub(u"""  <div class="grp">Keyframes <span style="text-transform:none;color:#9a8a68">(t in ms · ease is INTO that key · edit cells directly)</span></div>""",
    u"""  <div class="grp">Sound bank <span style="text-transform:none;color:#9a8a68">(synthesized — same family = same instrument; power adds voices)</span></div>
  <div class="row" id="sndRow"></div>
  <div class="row">
    <label>pitch <input type="range" id="sndPitch" min="50" max="200" value="100"></label>
    <label>voices <select id="sndLayers"><option>1</option><option>2</option><option>3</option></select></label>
    <button onclick="addSndKey()">add sound @ t</button>
  </div>

  <div class="grp">Keyframes <span style="text-transform:none;color:#9a8a68">(t in ms · ease is INTO that key · edit cells directly)</span></div>""",
    'sound bank UI')

sub(u"""    <button onclick="loadRecipe()">load</button>""",
    u"""    <button onclick="loadRecipe()">load / base preset</button>""",
    'load button label')

SND_JS = u"""/* ── THE SOUND BANK — nine families, one AudioContext, synthesized.
   Same action family = same instrument; power adds VOICES (octave
   layers), never a different sound. Porting = folding into the game's
   SFX object, same synthesis. See docs/VFX_LANGUAGE.md §8. ── */
var _AC=null,_MG=null;
function ac(){if(!_AC){_AC=new (window.AudioContext||window.webkitAudioContext)();
  _MG=_AC.createGain();_MG.gain.value=0.4;_MG.connect(_AC.destination);}return _AC;}
function _tone(f0,t0,dur,type,peak,f1){
  var o=ac().createOscillator(),g=ac().createGain();
  o.type=type||'sine';o.frequency.setValueAtTime(f0,t0);
  if(f1)o.frequency.exponentialRampToValueAtTime(Math.max(20,f1),t0+dur*0.8);
  g.gain.setValueAtTime(0,t0);g.gain.linearRampToValueAtTime(peak,t0+0.012);
  g.gain.exponentialRampToValueAtTime(0.0001,t0+dur);
  o.connect(g);g.connect(_MG);o.start(t0);o.stop(t0+dur+0.05);}
function _noise(t0,dur,ftype,freq,peak){
  var nz=ac().createBufferSource(),b=ac().createBuffer(1,Math.floor(ac().sampleRate*0.25),ac().sampleRate);
  var d=b.getChannelData(0);for(var i=0;i<d.length;i++)d[i]=Math.random()*2-1;
  nz.buffer=b;var f=ac().createBiquadFilter();f.type=ftype;f.frequency.value=freq;
  var g=ac().createGain();g.gain.setValueAtTime(0,t0);
  g.gain.linearRampToValueAtTime(peak,t0+0.008);
  g.gain.exponentialRampToValueAtTime(0.0001,t0+dur);
  nz.connect(f);f.connect(g);g.connect(_MG);nz.start(t0);nz.stop(t0+dur+0.05);}
var SND={
  families:['chime','coin','thud','crack','set','shimmer','bell','drum','scratch'],
  play:function(fam,o){
    o=o||{};var p=o.pitch||1,L=o.layers||1;
    var t=ac().currentTime+0.01;
    try{
    if(fam==='chime'){_tone(660*p,t,0.35,'sine',0.25);_tone(990*p,t+0.06,0.4,'sine',0.16);
      if(L>1)_tone(1320*p,t+0.1,0.45,'sine',0.1);if(L>2)_tone(1980*p,t+0.16,0.5,'sine',0.06);}
    else if(fam==='coin'){_tone(1568*p,t,0.09,'triangle',0.2);_tone(2093*p,t+0.07,0.12,'triangle',0.16);
      if(L>1){_tone(1568*p,t+0.16,0.09,'triangle',0.13);_tone(2093*p,t+0.22,0.12,'triangle',0.1);}}
    else if(fam==='thud'){_tone(120*p,t,0.18,'sine',0.5,55*p);_noise(t,0.08,'lowpass',300,0.2);
      if(L>1)_tone(90*p,t+0.09,0.16,'sine',0.3,45*p);}
    else if(fam==='crack'){_noise(t,0.06,'highpass',2500,0.4);_tone(140*p,t+0.03,0.14,'sine',0.3,60*p);
      if(L>1)_noise(t+0.06,0.05,'highpass',3200,0.25);if(L>2)_noise(t+0.11,0.05,'highpass',1800,0.2);}
    else if(fam==='set'){_tone(440*p,t,0.2,'sine',0.3,220*p);_tone(880*p,t,0.3,'sine',0.07);
      if(L>1)_tone(1760*p,t+0.05,0.3,'sine',0.05);}
    else if(fam==='shimmer'){[523,587,659,784,880].forEach(function(f,i){
        _tone(f*p,t+i*0.05,0.3,'sine',0.07);
        if(L>1)_tone(f*2*p,t+0.12+i*0.05,0.25,'sine',0.04);});}
    else if(fam==='bell'){_tone(660*p,t,0.9,'sine',0.2);_tone(990*p,t,0.9,'sine',0.09);
      if(L>1)_tone(1320*p,t+0.04,1.0,'sine',0.05);}
    else if(fam==='drum'){_tone(55*p,t,0.16,'sine',0.5,40*p);_tone(55*p,t+0.25,0.16,'sine',0.4,40*p);
      if(L>1)_tone(110*p,t+0.02,0.1,'sine',0.15);}
    else if(fam==='scratch'){_noise(t,0.07,'bandpass',900*p,0.18);
      if(L>1)_noise(t+0.09,0.05,'bandpass',1100*p,0.12);}
    }catch(e){log('snd: '+e);}
  }};
var _sndFam='chime';
(function(){var h='';SND.families.forEach(function(f){
  h+='<button id="snd_'+f+'" onclick="pickSnd(&quot;'+f+'&quot;)">'+f+'</button>';});
  document.getElementById('sndRow').innerHTML=h;})();
function pickSnd(f){_sndFam=f;
  document.querySelectorAll('#sndRow button').forEach(function(b){b.classList.remove('on');});
  var b=document.getElementById('snd_'+f);if(b)b.classList.add('on');
  SND.play(f,sndOpts());}
function sndOpts(){return {pitch:(+document.getElementById('sndPitch').value)/100,
  layers:+document.getElementById('sndLayers').value};}
function addSndKey(){
  var t=+document.getElementById('keyT').value;
  var o=sndOpts();o.snd=_sndFam;
  rec.fx.push({t:t,fx:'sound',p:o});
  rec.fx.sort(function(a,b){return a.t-b.t;});
  renderTables();log('sound '+_sndFam+' @ '+t+'ms');}

/* rounded-box geometry: clamp each vertex to an inner box, push out by r —
   gives the shell its rounded corners; the slider picks r as % of size */
function roundedBoxGeo(T,size,rPct,seg){
  var r=size*Math.max(0.001,rPct)/100;
  var g=new T.BoxGeometry(size,size,size,seg||4,seg||4,seg||4);
  var pos=g.attributes.position,h=size/2-r;
  for(var i=0;i<pos.count;i++){
    var x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i);
    var cx=Math.max(-h,Math.min(h,x)),cy=Math.max(-h,Math.min(h,y)),cz=Math.max(-h,Math.min(h,z));
    var dx=x-cx,dy=y-cy,dz=z-cz,l=Math.sqrt(dx*dx+dy*dy+dz*dz)||1;
    pos.setXYZ(i,cx+dx/l*r,cy+dy/l*r,cz+dz/l*r);
  }
  g.computeVertexNormals();return g;
}

/* ── FX palette ───────────────────────────────────────────────────── */"""

sub(u"/* ── FX palette ───────────────────────────────────────────────────── */",
    SND_JS, 'sound bank JS + rounded geo')

sub(u"""  var c=new T.Color(col);
  var sh=new T.Mesh(body.geometry,new T.MeshBasicMaterial({
    color:c,transparent:true,opacity:0.5,depthWrite:false}));
  sh.name='labShell';sh.userData.outline=true;/* every die pass skips it */
  sh.scale.setScalar(1.16);""",
    u"""  var c=new T.Color(col);
  body.geometry.computeBoundingBox();
  var bb=body.geometry.boundingBox,sz=(bb.max.x-bb.min.x)*1.16;
  var rPct=+((document.getElementById('pCr')||{}).value||12);
  var sh=new T.Mesh(roundedBoxGeo(T,sz,rPct,4),new T.MeshBasicMaterial({
    color:c,transparent:true,opacity:0.5,depthWrite:false}));
  sh.name='labShell';sh.userData.outline=true;/* every die pass skips it */""",
    'shell rounds its corners')

sub(u"""    else if(fx==='announce'){E('famLog('+JSON.stringify(p.text)+','+JSON.stringify(p.annCol)+')');}""",
    u"""    else if(fx==='sound'){SND.play(p.snd||_sndFam,{pitch:p.pitch||1,layers:p.layers||1});}
    else if(fx==='announce'){E('famLog('+JSON.stringify(p.text)+','+JSON.stringify(p.annCol)+')');}""",
    'fire() learns sound')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
