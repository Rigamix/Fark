/* Does the "?" actually land on the faces a die cannot roll, and only those?
   Counting BLOBS of ink per atlas cell: value v should give exactly v blobs
   where the die has that face, and something that is not v (the glyph) where
   it does not. Sampling a pixel would not distinguish a "?" from a pip. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(60);}return false;};
_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','jade','obsidian'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
try{famLoadoutShow();}catch(e){}
if(!(await until(()=>window.D3X&&D3X.ready&&(D3X.dice||[]).length>0,20000)))return{error:'no dice'};
await sleep(1800);
function blobs(im,cell){
  const cw=im.width/3, ch=im.height/2;
  const cx=(cell%3)*cw, cy=Math.floor(cell/3)*ch;
  /* CROP TO THE CELL INTERIOR. The art has dark rounded-corner notches; at full
     cell size they form a connected dark border that MERGES every pip into one
     blob - which is why the dark-pip materials all read 1 while obsidian, whose
     pips are ivory, read a perfect 1..6. The detector was wrong, not the render. */
  const ins=0.14;
  const ox=cx+cw*ins, oy=cy+ch*ins, iw=Math.round(cw*(1-2*ins)), ih=Math.round(ch*(1-2*ins));
  const c=document.createElement('canvas');c.width=iw;c.height=ih;
  const g=c.getContext('2d'); g.drawImage(im,ox,oy,cw*(1-2*ins),ch*(1-2*ins),0,0,iw,ih);
  const d=g.getImageData(0,0,iw,ih).data;
  const W=iw,H=ih, seen=new Uint8Array(W*H);
  // "ink" = far from the local face colour; sample the corner as the face tone
  const fr=d[0],fg=d[1],fb=d[2];
  const isInk=(i)=>{const dr=d[i]-fr,dg=d[i+1]-fg,db=d[i+2]-fb;
    return (dr*dr+dg*dg+db*db)>7000;};
  let n=0;
  for(let y=0;y<H;y++)for(let x=0;x<W;x++){
    const p=y*W+x; if(seen[p])continue; if(!isInk(p*4))continue;
    let sz=0; const st=[p]; seen[p]=1;
    while(st.length){const q=st.pop();sz++;const qx=q%W,qy=(q/W)|0;
      for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]]){const nx=qx+dx,ny=qy+dy;
        if(nx<0||ny<0||nx>=W||ny>=H)continue;const r=ny*W+nx;
        if(!seen[r]&&isInk(r*4)){seen[r]=1;st.push(r);}}}
    if(sz>18)n++;
  }
  return n;
}
const out={};
D3X.dice.forEach(d=>{
  let im=null; d.obj.traverse(o=>{if(o.isMesh&&!im&&o.material.map)im=o.material.map.image;});
  if(!im)return;
  const dt=(typeof getDie==='function'&&getDie(d.mat))||{};
  const faces=dt.faces||[1,2,3,4,5,6];
  const rows=[];
  for(let v=1;v<=6;v++) rows.push({v:v, canRoll:faces.indexOf(v)>=0, blobs:blobs(im,v-1)});
  out[d.mat]={faces:faces, cells:rows};
});
const prob=[];
Object.keys(out).forEach(m=>out[m].cells.forEach(c=>{
  if(c.canRoll && c.blobs!==c.v) prob.push(m+' v'+c.v+' should show '+c.v+' pips, found '+c.blobs+' blobs');
  if(!c.canRoll && c.blobs===c.v) prob.push(m+' v'+c.v+' is unrollable but still drew '+c.v+' pips');
}));
return {out, problems:prob,
  verdict: prob.length ? 'FAIL - '+prob.join('; ')
    : 'PASS - every rollable value shows exactly that many pips, and every value the die cannot roll shows something else (the ?)'};
