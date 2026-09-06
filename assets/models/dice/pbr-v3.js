/* Fark: the painted surface itself controls polish, wear and shallow relief.
 * No procedural stone grid, decorative frame, or second blanket of gloss. */
(function(host){
 'use strict';
 var VERSION='fark-painted-pbr-v3',W=768,H=512,C=256,loaded={},cache={},masked={},cssCache={},geometry=null,environment=null,envTarget=null,owner=null;
 var time={value:1.75},lastMs=null,media=null,pack=host.FK_DICE_PAINT_PACK||{};
 var profiles={
   silver:{rough:[.34,.72],metal:1,env:.34,coat:0,normal:.65,contrast:1.55,gain:1.05,lift:8},
   obsidian:{rough:[.29,.64],metal:0,env:.24,coat:.035,normal:.50,contrast:1.55,gain:.82,lift:0},
   amber:{rough:[.32,.58],metal:0,env:.20,coat:.08,normal:.15,contrast:1.12,gain:1,lift:0},
   jade:{rough:[.38,.63],metal:0,env:.19,coat:.035,normal:.26,contrast:1.15,gain:1,lift:0},
   jade2:{rough:[.34,.59],metal:0,env:.21,coat:.05,normal:.26,contrast:1.15,gain:1,lift:0},
   starstone:{rough:[.43,.69],metal:0,env:.19,coat:0,normal:.30,contrast:1.2,gain:1,lift:0},
   vagabond:{rough:[.45,.72],metal:0,env:.17,coat:.025,normal:.28,contrast:1.15,gain:1,lift:0}
 };
 function has(mat){return Object.prototype.hasOwnProperty.call(profiles,mat);}
 function family(mat){return mat==='jade2'?'jade':mat;}
 function ink(mat){return pack[family(mat)]?pack[family(mat)].ink:'#14100c';}
 function source(mat){return loaded[family(mat)]||null;}
 function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
 function smooth(a,b,v){var t=clamp((v-a)/(b-a),0,1);return t*t*(3-2*t);}
 function canvas(w,h){var c=document.createElement('canvas');c.width=w;c.height=h;return c;}
 var ready=Promise.all(Object.keys(pack).filter(has).map(function(mat){return new Promise(function(resolve){var image=new Image();image.onload=function(){loaded[mat]=image;resolve();};image.onerror=function(){resolve();};image.src=pack[mat].albedo;});}));
 function map(T,c,base,linear){var t=new T.CanvasTexture(c);t.flipY=base.flipY;t.wrapS=base.wrapS;t.wrapT=base.wrapT;t.encoding=linear?T.LinearEncoding:base.encoding;t.anisotropy=base.anisotropy||1;t.userData={};return t;}
 function soften(input,radius){
   var temp=new Float32Array(C*C),out=new Float32Array(C*C),size=radius*2+1;
   for(var y=0;y<C;y++)for(var x=0;x<C;x++){var sum=0;for(var k=-radius;k<=radius;k++)sum+=input[y*C+clamp(x+k,0,C-1)];temp[y*C+x]=sum/size;}
   for(var yy=0;yy<C;yy++)for(var xx=0;xx<C;xx++){var total=0;for(var j=-radius;j<=radius;j++)total+=temp[clamp(yy+j,0,C-1)*C+xx];out[yy*C+xx]=total/size;}
   return out;
 }
 function paint(mat,faces,variants,P){
   var img=source(mat),profile=profiles[mat];if(!img||!profile)return null;
   var colour=canvas(W,H),normal=canvas(W,H),surface=canvas(W,H),cx=colour.getContext('2d'),nx=normal.getContext('2d'),sx=surface.getContext('2d');
   var ni=nx.createImageData(W,H),si=sx.createImageData(W,H),tile=canvas(C,C),tx=tile.getContext('2d',{willReadFrequently:true}),stats=[];
   for(var face=0;face<6;face++){
     var variant=((variants&&variants[face])||0)%6,ox=(face%3)*C,oy=Math.floor(face/3)*C;
     // Sample the unpipped interior. Every map uses these exact pixels, this
     // face variant and these UVs; the old painted frame never reaches the die.
     tx.drawImage(img,(variant%3)*C+32,Math.floor(variant/3)*C+32,192,192,0,0,C,C);
     var pixels=tx.getImageData(0,0,C,C),lum=new Float32Array(C*C),hist=new Uint32Array(256),mean=0;
     for(var i=0;i<C*C;i++){var at=i*4,l=pixels.data[at]*.2126+pixels.data[at+1]*.7152+pixels.data[at+2]*.0722;lum[i]=l;hist[Math.round(l)]++;mean+=l;}
     mean/=C*C;var count=0,lo=0,hi=255;
     for(var level=0;level<256;level++){count+=hist[level];if(count<C*C*.08)lo=level;if(count<C*C*.92)hi=level;}
     var span=Math.max(8,hi-lo),soft=soften(lum,2),broad=soften(soft,4);stats.push({variant:variant,lo:lo,hi:hi,mean:mean});
     for(var y=0;y<C;y++)for(var x=0;x<C;x++){
       var index=y*C+x,p=index*4,out=((oy+y)*W+ox+x)*4,n=clamp((soft[index]-lo)/span,0,1),polish=smooth(.07,.93,n);
       var rough=profile.rough[1]+(profile.rough[0]-profile.rough[1])*polish;
       // A filtered derivative of the same painted grain makes slight wear,
       // not a new pattern of cut triangles or deep engraved mineral veins.
       var edge=smooth(0,18,Math.min(x,y,C-1-x,C-1-y));
       var dx=(broad[y*C+clamp(x+2,0,C-1)]-broad[y*C+clamp(x-2,0,C-1)])/span*profile.normal*edge;
       var dy=(broad[clamp(y+2,0,C-1)*C+x]-broad[clamp(y-2,0,C-1)*C+x])/span*profile.normal*edge;
       var length=Math.sqrt(dx*dx+dy*dy+1);
       for(var c=0;c<3;c++){var value=(pixels.data[p+c]-mean)*profile.contrast+mean*profile.gain+profile.lift;if(mat==='jade2')value*=[180/255,213/255,183/255][c];pixels.data[p+c]=clamp(value,0,255);}
       ni.data[out]=(-dx/length*.5+.5)*255;ni.data[out+1]=(-dy/length*.5+.5)*255;ni.data[out+2]=(1/length*.5+.5)*255;ni.data[out+3]=255;
       // R isolates brighter painted inclusions / rubbed patches for the
       // very small clearcoat or Starstone shimmer. G roughness, B metalness.
       si.data[out]=smooth(.68,.99,n)*255;si.data[out+1]=rough*255;si.data[out+2]=profile.metal*255;si.data[out+3]=255;
     }
     tx.putImageData(pixels,0,0);cx.drawImage(tile,ox,oy);
   }
   nx.putImageData(ni,0,0);sx.putImageData(si,0,0);
   var values={};(faces||[1,2,3,4,5,6]).forEach(function(v){values[v]=true;});
   for(var value=1;value<=6;value++){
     var dc=(value-1)%3,dr=Math.floor((value-1)/3);cx.fillStyle=ink(mat);
     if(!values[value]){
       cx.save();cx.font='bold '+Math.round(C*.62)+'px Georgia,serif';cx.textAlign='center';var mt=cx.measureText('?');cx.fillText('?',(dc+.5)*C,(dr+.5)*C+(mt.actualBoundingBoxAscent||C*.42)/2);cx.restore();
       nx.fillStyle='#8080ff';nx.fillRect(dc*C,dr*C,C,C);sx.fillStyle='#00c000';sx.fillRect(dc*C,dr*C,C,C);
     }else (P.LAY[value]||[]).forEach(function(p){
       var px=(dc+P.GRID[p[0]])*C,py=(dr+P.GRID[p[1]])*C;P.draw(cx,px,py,P.R*C);
       nx.fillStyle='#8080ff';sx.fillStyle='#00c000';P.draw(nx,px,py,P.R*C+.5);P.draw(sx,px,py,P.R*C+.5);
     });
   }
   return {colour:colour,normal:normal,surface:surface,source:{family:family(mat),crop:[32,32,192,192],variants:stats}};
 }
 function build(T,base,mat,faces,variants,P){
   if(!has(mat)||!base)return null;var key=[base.uuid,mat,(faces||[]).join(','),(variants||[]).join(',')].join('|');if(cache[key])return cache[key];
   var p=paint(mat,faces,variants,P);if(!p)return null;var tex=map(T,p.colour,base,false);tex.userData.fkArtRevision=VERSION;tex.userData.fkVariants=(variants||[]).slice();
   tex.userData.fkPbr={version:VERSION,normalMap:map(T,p.normal,base,true),surfaceMap:map(T,p.surface,base,true),source:p.source};return cache[key]=tex;
 }
 function init(renderer){
   if(owner===renderer&&environment)return environment;var T=host.THREE,room=new T.Scene();room.background=new T.Color().setRGB(.018,.020,.024);var items=[];
   function panel(w,h,x,y,z,r,g,b){var m=new T.MeshBasicMaterial({color:new T.Color().setRGB(r,g,b),side:T.DoubleSide}),p=new T.Mesh(new T.PlaneGeometry(w,h),m);p.position.set(x,y,z);p.lookAt(0,0,0);room.add(p);items.push(p);}
   panel(5,11,-7,3,5,3.6,3.8,4);panel(11,4,2,8,3,2.6,2.6,2.5);panel(2,9,8,1,-3,1.2,1.05,.8);panel(9,5,0,-7,3,.06,.045,.035);panel(5,8,0,1,-9,.65,.7,.8);panel(2.4,9,6,-6,2,3.1,3.2,3.3);panel(3.8,9,4,7,-3,2.7,2.8,3);
   var pmrem=new T.PMREMGenerator(renderer),target=pmrem.fromScene(room,.12,.1,40);pmrem.dispose();items.forEach(function(p){p.geometry.dispose();p.material.dispose();});
   if(envTarget)envTarget.dispose();envTarget=target;environment=target.texture;owner=renderer;return environment;
 }
 function getGeometry(T){if(geometry)return geometry;var d=host.FK_DICE_BEVEL;if(!d)return null;var g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(d.position,3));g.setAttribute('normal',new T.Float32BufferAttribute(d.normal,3));g.setAttribute('uv',new T.Float32BufferAttribute(d.uv,2));g.setIndex(d.index);g.computeTangents();g.computeBoundingBox();g.computeBoundingSphere();return geometry=g;}
 function maps(T,tex,excluded){
   var data=tex&&tex.userData&&tex.userData.fkPbr;if(!data)return null;var faces=(excluded||[]).filter(function(v,i,a){return v>=1&&v<=6&&a.indexOf(v)===i;}).sort();if(!faces.length)return data;
   var key=tex.uuid+'|'+faces.join(',');if(masked[key])return masked[key];var n=canvas(W,H),s=canvas(W,H),nx=n.getContext('2d'),sx=s.getContext('2d');nx.drawImage(data.normalMap.image,0,0);sx.drawImage(data.surfaceMap.image,0,0);
   faces.forEach(function(v){var x=((v-1)%3)*C,y=Math.floor((v-1)/3)*C;nx.fillStyle='#8080ff';nx.fillRect(x,y,C,C);sx.fillStyle='#00c000';sx.fillRect(x,y,C,C);});
   return masked[key]={version:VERSION,normalMap:map(T,n,tex,true),surfaceMap:map(T,s,tex,true),source:data.source};
 }
 function shimmer(m,mat,surface){
   var u=m.userData.fkMineralLight;if(u){u.enabled.value=mat==='starstone'?1:0;u.map.value=surface;return;}
   if(mat!=='starstone')return;u=m.userData.fkMineralLight={time:time,map:{value:surface},enabled:{value:1}};
   var previous=m.onBeforeCompile,key=m.customProgramCacheKey?m.customProgramCacheKey():'';
   m.onBeforeCompile=function(shader,renderer){if(previous)previous.call(this,shader,renderer);shader.uniforms.fkMineralTime=u.time;shader.uniforms.fkMineralMap=u.map;shader.uniforms.fkMineralEnabled=u.enabled;
     shader.fragmentShader='uniform float fkMineralTime; uniform sampler2D fkMineralMap; uniform float fkMineralEnabled;\n'+shader.fragmentShader.replace('gl_FragColor = vec4( outgoingLight, diffuseColor.a );',[
       '#ifdef USE_UV','float fkMineral = texture2D(fkMineralMap, vUv).r;',
       'float fkBreath = 0.5 + 0.5 * sin(fkMineralTime * 0.55 + fkMineral * 4.7);',
       'outgoingLight += vec3(0.18, 0.34, 0.70) * fkMineral * fkMineral * (0.004 + 0.016 * fkBreath * fkBreath) * fkMineralEnabled;',
       '#endif','gl_FragColor = vec4( outgoingLight, diffuseColor.a );'
     ].join('\n'));};m.customProgramCacheKey=function(){return key+'|fark-painted-mineral-light-v3';};
 }
 function dress(m,mat,base,excluded){
   var d=maps(host.THREE,base,excluded),p=profiles[mat];if(!p||!d||!m.isMeshStandardMaterial)return false;
   m.normalMap=d.normalMap;m.roughnessMap=d.surfaceMap;m.metalnessMap=d.surfaceMap;m.envMap=environment;m.roughness=1;m.metalness=1;m.normalScale.set(1,1);m.envMapIntensity=p.env;
   m.clearcoat=p.coat;m.clearcoatMap=p.coat?d.surfaceMap:null;m.clearcoatRoughness=.9;m.clearcoatRoughnessMap=p.coat?d.surfaceMap:null;m.clearcoatNormalMap=p.coat?d.normalMap:null;
   shimmer(m,mat,d.surfaceMap);m.userData.fkPbrVersion=VERSION;m.userData.fkPbrMaterial=mat;m.needsUpdate=true;return true;
 }
 function material(T,mat,tex){var m=new T.MeshPhysicalMaterial({map:tex,color:0xffffff,roughness:.65});m.userData.baseMap=tex;m.userData.pipTinted=true;dress(m,mat,tex,[]);return m;}
 function cssFaces(mat,faces,P){if(!has(mat))return null;var key=mat+'|'+(faces||[]).join(',');if(cssCache[key])return cssCache[key];var p=paint(mat,faces,[0,1,2,3,4,5],P);if(!p)return null;var out=[];for(var i=0;i<6;i++){var c=canvas(C,C);c.getContext('2d').drawImage(p.colour,(i%3)*C,Math.floor(i/3)*C,C,C,0,0,C,C);out.push(c.toDataURL());}return cssCache[key]=out;}
 function update(now,reduced){
   if(reduced===undefined){var body=host.document&&host.document.body;reduced=!!(body&&body.classList.contains('reduced-motion'));if(!media&&host.matchMedia)media=host.matchMedia('(prefers-reduced-motion: reduce)');reduced=reduced||!!(media&&media.matches);}
   if(typeof now!=='number'||!isFinite(now))return time.value;if(lastMs===null)lastMs=now;var elapsed=clamp(now-lastMs,0,80);lastMs=now;if(!reduced)time.value+=elapsed*.001;return time.value;
 }
 host.FK_DICE_PBR={version:VERSION,has:has,available:function(mat){return !!source(mat);},source:source,ready:ready,profiles:profiles,ink:ink,init:init,geometry:getGeometry,build:build,material:material,dress:dress,maps:maps,cssFaces:cssFaces,update:update};
})(window);
