/* Does a re-dress keep the pips, and are the pips black on a TINTED die?
   The second is the requirement "pips do not tint", and it holds only because
   the pips are pure black and _dress tints by MULTIPLY. Worth measuring rather
   than trusting: a dark-grey pip would look fine here and tint on jade. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(60);}return false;};
_getS(); S.run=S.run||{}; S.run.tier=2; S.run.gold=500;
S.run.dice=['bone','jade','amber','obsidian','starstone','iron'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
try{famLoadoutShow();}catch(e){}
if(!(await until(()=>window.D3X&&D3X.ready&&(D3X.dice||[]).length>0,20000)))return{error:'no dice'};
await sleep(1800);
function sample(t){
  const im=t&&t.image; if(!im)return null;
  const c=document.createElement('canvas');c.width=im.width;c.height=im.height;
  c.getContext('2d').drawImage(im,0,0);
  const g=c.getContext('2d');
  // centre of cell 0 (value 1) - that is the single pip
  const cw=im.width/3, ch=im.height/2;
  const d=g.getImageData(Math.round(cw*0.5),Math.round(ch*0.5),1,1).data;
  return [d[0],d[1],d[2]];
}
const before=D3X.dice.map(d=>{let px=null;d.obj.traverse(o=>{if(o.isMesh&&!px)px=sample(o.material.map);});return px;});
/* force the path that used to strip them */
D3X.dice.forEach(d=>{try{D3X._rebrand&&D3X._rebrand(d);}catch(e){}});
await sleep(900);
const after=D3X.dice.map(d=>{let px=null;d.obj.traverse(o=>{if(o.isMesh&&!px)px=sample(o.material.map);});return px;});
const tint=D3X.dice.map(d=>{let c=null;d.obj.traverse(o=>{if(o.isMesh&&!c)c='#'+o.material.color.getHexString();});return {mat:d.mat,c:c};});
const black=v=>v&&v[0]<40&&v[1]<40&&v[2]<40;
return {mats:D3X.dice.map(d=>d.mat), tints:tint,
  pipBefore:before, pipAfter:after,
  allBlackBefore:before.every(black), allBlackAfter:after.every(black),
  verdict: !before.every(v=>v) ? 'INCONCLUSIVE - could not sample the texture'
    : !before.every(black) ? 'FAIL - pips are not black at source: '+JSON.stringify(before)
    : !after.every(black) ? 'FAIL - a re-dress stripped or lightened the pips: '+JSON.stringify(after)
    : 'PASS - pips pure black on all six materials and they survive a re-dress'};
