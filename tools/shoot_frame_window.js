/* The window is where the frame's BACK layer paints its coloured field. Scan
 * frame_bg for its opaque box, and cross-check against the FG's top border. */
const load=src=>new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=rej;i.src=src;});
const box=async(src,thr)=>{
  const im=await load(src),w=im.naturalWidth,h=im.naturalHeight;
  const cv=document.createElement('canvas');cv.width=w;cv.height=h;
  const cx=cv.getContext('2d');cx.drawImage(im,0,0);
  const d=cx.getImageData(0,0,w,h).data;
  let t=-1,b=-1,l=-1,r=-1;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
    if(d[((y*w+x)<<2)+3]>thr){ if(t<0)t=y; b=y; if(l<0||x<l)l=x; if(x>r)r=x; }
  }
  return {size:[w,h],pct:{top:+(100*t/h).toFixed(1),bottom:+(100*b/h).toFixed(1),
    left:+(100*l/w).toFixed(1),right:+(100*r/w).toFixed(1)}};
};
const bg=await box('Art/Assets/Frames/Patrons/frame_bg_red.png',200);
/* the FG's opaque top border: how far down does the frame cover? scan its
   centre column for the first transparent pixel after an opaque run */
const im=await load('Art/Assets/Frames/Patrons/frame_fg_red.png');
const w=im.naturalWidth,h=im.naturalHeight;
const cv=document.createElement('canvas');cv.width=w;cv.height=h;
const cx=cv.getContext('2d');cx.drawImage(im,0,0);
const d=cx.getImageData(0,0,w,h).data;
const mid=Math.floor(w/2);
let firstOpaque=-1,windowTop=-1;
for(let y=0;y<h;y++){
  const a=d[((y*w+mid)<<2)+3];
  if(firstOpaque<0&&a>200)firstOpaque=y;
  if(firstOpaque>=0&&windowTop<0&&a<24)windowTop=y;
}
let windowBot=-1;
for(let y=h-1;y>0;y--){
  const a=d[((y*w+mid)<<2)+3];
  if(a>200){ /* keep scanning up through the bottom border */ } else { windowBot=y; break; }
}
return {frame_bg:bg,
  fg_topBorderEndsAt:+(100*windowTop/h).toFixed(1),
  fg_bottomClearTo:+(100*windowBot/h).toFixed(1)};
