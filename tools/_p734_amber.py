# -*- coding: utf-8 -*-
"""P734 (A1b): the amber lifecycle - set, park, return, crack.

Denis's spec: 'when I use preserve the die should be covered in an amber
layer with an audio effect, and then when I bank, the preserved die
moves down somewhere but in a straight line in its lane, not greyed out
(ambered though) but out of the way so NPC dice don't overlap with it.
When it's my turn again and I roll, that die should scale back up and go
back into position in its original lane, but only after the rolled dice
have settled so it's visible. Then the amber shield effect goes away.'

The shell is the lab's approved material, ported as D3X.amberShell(d,on):
rounded rims (Phong specular), a ghost pass of the die's own textured
mesh (refraction blur), drifting inclusion bubbles - one reusable
primitive, since Honeytrap, Ward and Snare all speak the same verb.

The lifecycle rides the EXISTING pieces: the cast shells the captured
die where it sits; the payout's minted die (P559/P691's own code) is
shelled and parked down its lane; the turn's first roll schedules the
return for after the tape settles - rise, scale pop, crack (spray +
SFX), shell off.
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


# 1) the shell primitive, beside the dim bake
sub(u"""  /* P725b: THE SETTLED DIM, ONE EXIT PATH.""",
    u"""  /* P734: THE AMBER SHELL - the trap's material, authored in the lab and
     ported whole. Rounded rims carry a specular hot-spot (glossy), a
     ghost pass of the die's own textured mesh reads as refraction blur,
     and inclusion bubbles drift inside. One primitive: Honeytrap's
     glaze, Ward's flash and Snare's rust trap are the same verb in
     other colours. userData.outline keeps every die pass (dim, tint,
     reskin) off it. */
  AMBER:{col:0xd88a20, corner:12, rims:2, op:0.42, spec:45, ghost:0.25, bub:4},
  _roundBox:function(size,rPct,seg){
    var r=size*Math.max(0.001,rPct)/100;
    var g=new THREE.BoxGeometry(size,size,size,seg||4,seg||4,seg||4);
    var pos=g.attributes.position,h=size/2-r;
    for(var i=0;i<pos.count;i++){
      var x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i);
      var cx=Math.max(-h,Math.min(h,x)),cy=Math.max(-h,Math.min(h,y)),cz=Math.max(-h,Math.min(h,z));
      var dx=x-cx,dy=y-cy,dz=z-cz,L=Math.sqrt(dx*dx+dy*dy+dz*dz)||1;
      pos.setXYZ(i,cx+dx/L*r,cy+dy/L*r,cz+dz/L*r);
    }
    g.computeVertexNormals();return g;
  },
  amberShell:function(d,on,colOverride){
    if(!d||!d.obj)return false;
    var have=d.obj.getObjectByName('fkAmber');
    if(!on){
      if(have){d.obj.remove(have);
        have.traverse(function(o){if(o.material&&o.material.dispose)o.material.dispose();});}
      d.obj.traverse(function(o){
        if(o.isMesh&&o.material&&o.userData._ambCol){
          o.material.color.copy(o.userData._ambCol);delete o.userData._ambCol;}
      });
      return true;
    }
    if(have)return true;
    var A=this.AMBER,body=null;
    d.obj.traverse(function(o){if(!body&&o.isMesh&&!o.userData.outline)body=o;});
    if(!body)return false;
    var c=new THREE.Color(colOverride===undefined?A.col:colOverride);
    body.geometry.computeBoundingBox();
    var bb=body.geometry.boundingBox,sz=(bb.max.x-bb.min.x);
    var grp=new THREE.Group();grp.name='fkAmber';grp.userData.outline=true;
    for(var i=0;i<A.rims;i++){
      var m2=new THREE.Mesh(this._roundBox(sz*(1.10+i*0.06),A.corner,4),
        new THREE.MeshPhongMaterial({color:c,transparent:true,
          opacity:A.op*(i===0?1:0.4),depthWrite:false,
          specular:new THREE.Color(0xfff6e0),shininess:A.spec}));
      m2.userData.outline=true;grp.add(m2);
    }
    if(A.ghost>0){
      var gh=new THREE.Mesh(body.geometry,new THREE.MeshBasicMaterial({
        map:body.material.map||null,color:c,transparent:true,
        opacity:A.ghost,depthWrite:false}));
      gh.scale.setScalar(1.035);gh.userData.outline=true;grp.add(gh);
    }
    grp.userData.bub=[];grp.userData.lim=sz*0.32;
    for(var b=0;b<A.bub;b++){
      var bm=new THREE.Mesh(new THREE.SphereGeometry(sz*(0.025+Math.random()*0.02),6,6),
        new THREE.MeshPhongMaterial({color:0xffe8c0,transparent:true,opacity:0.5,
          specular:0xffffff,shininess:60,depthWrite:false}));
      bm.userData.outline=true;
      bm.position.set((Math.random()-0.5)*sz*0.5,(Math.random()-0.5)*sz*0.5,(Math.random()-0.5)*sz*0.5);
      bm.userData.ph=Math.random()*6.28;bm.userData.sp=0.6+Math.random()*0.8;
      grp.add(bm);grp.userData.bub.push(bm);
    }
    d.obj.add(grp);
    d.obj.traverse(function(o){
      if(!o.isMesh||!o.material||o.userData.outline)return;
      if(!o.userData._ambCol)o.userData._ambCol=o.material.color.clone();
      var base=o.userData._ambCol;
      o.material.color.setRGB(base.r*0.45+c.r*0.55,base.g*0.45+c.g*0.55,base.b*0.45+c.b*0.55);
    });
    return true;
  },
  /* the bubbles drift - called from frame(), costs nothing when no die
     wears a shell */
  _amberDrift:function(){
    var t=performance.now()/1000;
    for(var i=0;i<this.dice.length;i++){
      var g=this.dice[i].obj&&this.dice[i].obj.getObjectByName
        &&this.dice[i].obj.getObjectByName('fkAmber');
      if(!g||!g.userData.bub)continue;
      var lim=g.userData.lim||0.3;
      for(var b=0;b<g.userData.bub.length;b++){
        var bm=g.userData.bub[b];
        bm.position.y+=lim*0.004*bm.userData.sp;
        bm.position.x+=Math.sin(t*2+bm.userData.ph)*lim*0.002;
        if(bm.position.y>lim)bm.position.y=-lim;
      }
    }
  },
  /* find the tracked die that owns a chip element */
  _dieOfChip:function(el){
    if(!el)return null;
    for(var i=0;i<this.dice.length;i++){
      var d=this.dice[i];
      if(d.chip===el||(d.chip&&el.contains&&el.contains(d.chip))
        ||(d.chip&&d.chip.contains&&d.chip.contains(el)))return d;
    }
    return null;
  },
  /* P725b: THE SETTLED DIM, ONE EXIT PATH.""",
    'amberShell primitive')

# 2) drift from the frame loop
sub(u"  _drawGlow:function(){",
    u"  _amberTick:function(){try{this._amberDrift();}catch(e){}},\n"
    u"  _drawGlow:function(){",
    'amberTick')

sub(u"    var row=document.getElementById('playerDiceRow');\n"
    u"    var n=row?row.getElementsByClassName('die').length:0;",
    u"    this._amberTick();/* P734: the inclusions drift */\n"
    u"    var row=document.getElementById('playerDiceRow');\n"
    u"    var n=row?row.getElementsByClassName('die').length:0;",
    'drift on tick')

# 3) the cast: shell the die where it sits + audio
sub(u"""    G._famPreserve={val:found,mat:foundMat,ench:foundEnch||null,lane:(typeof foundLane==='number')?foundLane:null,pts:found===1?100:50,crack:(inst.tier===3?100:0)};/* P559 + P691 (D6a): the SEAT is preserved too */
    famLog('PRESERVED — A '+found+' WAITS IN AMBER FOR NEXT TURN');""",
    u"""    G._famPreserve={val:found,mat:foundMat,ench:foundEnch||null,lane:(typeof foundLane==='number')?foundLane:null,pts:found===1?100:50,crack:(inst.tier===3?100:0)};/* P559 + P691 (D6a): the SEAT is preserved too */
    /* P734: THE TRAP CLOSES, where the die is standing. The kept die
       matching the captured value takes the shell now - the announce is
       the ledger, this is the table answering. */
    try{
      var _kr2=document.getElementById('keptRow');
      var _cands=_kr2?[].slice.call(_kr2.querySelectorAll('.die')):[];
      var _hit=null;
      _cands.forEach(function(el){if(!_hit&&el._trueVal===found)_hit=el;});
      if(_hit&&window.D3X&&D3X.amberShell){
        var _dd=D3X._dieOfChip(_hit);
        if(_dd){D3X.amberShell(_dd,true);
          try{_fxSpray(_hit,'#e8a23c',12,{speed:28,g:170,size:10,spread:0.6});}catch(e){}}
      }
      SFX.bank&&SFX.bank();
    }catch(e){}
    famLog('PRESERVED — A '+found+' WAITS IN AMBER FOR NEXT TURN');""",
    'cast shells the die')

# 4) the payout: shell + park the minted die, then schedule its return
sub(u"""        var _pd=mkDie(_fp.val,_fp.mat||'bone',null,true,_fp.ench||null);
        _pd.classList.add('in-tray');
        _kr.appendChild(typeof _wrapDie==='function'?_wrapDie(_pd):_pd);""",
    u"""        var _pd=mkDie(_fp.val,_fp.mat||'bone',null,true,_fp.ench||null);
        _pd.classList.add('in-tray');
        var _pw=(typeof _wrapDie==='function')?_wrapDie(_pd):_pd;
        _kr.appendChild(_pw);
        /* P734: IT WAITS IN AMBER, PARKED. Ambered rather than greyed
           (Denis), and pushed down its own lane so the rival's dice
           never land on top of it. The return is scheduled by the
           turn's first roll - see _amberReturnWhenSettled. */
        window._fkAmberChip=_pd;window._fkAmberWrap=_pw;
        try{
          _pw.style.transition='translate .5s cubic-bezier(.4,.9,.3,1),scale .5s';
          _pw.style.translate='0 9cqw';_pw.style.scale='0.82';
        }catch(e){}
        var _shellIt=function(tries){
          var dd=window.D3X&&D3X._dieOfChip&&D3X._dieOfChip(_pd);
          if(dd&&D3X.amberShell){D3X.amberShell(dd,true);return;}
          if((tries||0)<40)setTimeout(function(){_shellIt((tries||0)+1);},60);
        };
        _shellIt(0);""",
    'payout parks the ambered die')

# 5) the return, after the thrown dice settle
sub(u"""function _bustImpact(){""",
    u"""/* P734: THE AMBER CRACKS WHEN THE THROW IS DONE. Called on every roll;
   it only does something while a preserved die is parked. The wait is
   on the DICE, not a timer - Denis: 'only after the rolled dice have
   settled so it's visible'. */
function _amberReturnWhenSettled(){
  var chip=window._fkAmberChip,wrap=window._fkAmberWrap;
  if(!chip||!chip.isConnected){window._fkAmberChip=window._fkAmberWrap=null;return;}
  var t0=performance.now();
  var wait=function(){
    var settled=true;
    try{
      if(window.D3X&&D3X.dice.length){
        settled=!D3X.dice.some(function(d){return d.match&&d.roll;});
      }
    }catch(e){}
    if(!settled&&performance.now()-t0<9000){setTimeout(wait,80);return;}
    /* it comes home: rise, pop, crack */
    try{
      if(wrap){wrap.style.transition='translate .45s cubic-bezier(.3,1.35,.4,1),scale .45s cubic-bezier(.3,1.35,.4,1)';
        wrap.style.translate='0 0';wrap.style.scale='1';}
    }catch(e){}
    setTimeout(function(){
      try{
        var dd=window.D3X&&D3X._dieOfChip&&D3X._dieOfChip(chip);
        if(dd&&D3X.amberShell)D3X.amberShell(dd,false);
        _fxSpray(chip,'#ffd98a',16,{speed:95,g:90,size:7,spread:2.4});
        SFX.cardFire&&SFX.cardFire();
      }catch(e){}
      window._fkAmberChip=window._fkAmberWrap=null;
    },430);
  };
  wait();
}
function _bustImpact(){""",
    'the return function')

sub(u"""function _bustImpact(){
  const area=document.getElementById('diceArea');""",
    u"""function _bustImpact(){
  const area=document.getElementById('diceArea');""",
    'anchor stability check')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
