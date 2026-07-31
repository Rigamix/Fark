/* WHERE DOES A BUST ACTUALLY START?
 * "They sit too low" is a statement about the visible head, not about the
 * image box - and those are only the same thing if the PNGs have no
 * transparent headroom. Under object-fit:cover with object-position 50% 0%
 * the image's TOP EDGE is pinned to the box top, so every pixel of empty
 * space above a character's head pushes that character down by exactly that
 * much. This measures the alpha bounding box of every bust so the answer is
 * a number rather than a nudge. */
const PT = 'Art/Assets/Frames/Patrons/Characters/optimized/';
const EXT = '_opt.webp';
const NAMES = (typeof PT_ART_POOL !== 'undefined') ? PT_ART_POOL.slice() : [];

function alphaBox(img){
  const W = img.naturalWidth, H = img.naturalHeight;
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const x = c.getContext('2d', {willReadFrequently:true});
  x.drawImage(img, 0, 0);
  const d = x.getImageData(0, 0, W, H).data;
  let top = -1, bot = -1, left = W, right = -1;
  const A = 24;                       /* ignore near-transparent fringe */
  for (let y = 0; y < H; y++){
    let rowHit = false;
    for (let px = 0; px < W; px++){
      if (d[(y*W + px)*4 + 3] > A){
        rowHit = true;
        if (px < left) left = px;
        if (px > right) right = px;
      }
    }
    if (rowHit){ if (top < 0) top = y; bot = y; }
  }
  return {W, H, top, bot, left, right,
          headroomPct: +(100*top/H).toFixed(2),
          footPct:     +(100*(H-1-bot)/H).toFixed(2),
          contentPct:  +(100*(bot-top+1)/H).toFixed(2)};
}

const out = {}, rows = [];
for (const n of NAMES){
  try{
    const img = new Image();
    img.decoding = 'sync';
    await new Promise((res, rej) => { img.onload = res; img.onerror = () => rej(new Error('404')); img.src = PT + n + EXT; });
    const b = alphaBox(img);
    rows.push({name:n, ...b});
  }catch(e){ rows.push({name:n, err:String(e.message||e)}); }
}
const ok = rows.filter(r => !r.err);
out.count = ok.length;
out.missing = rows.filter(r => r.err).map(r => r.name);

/* the number that matters: how much empty space sits above each head */
const hr = ok.map(r => r.headroomPct).sort((a,b)=>a-b);
out.headroom = {
  min: hr[0], max: hr[hr.length-1],
  median: hr[Math.floor(hr.length/2)],
  mean: +(hr.reduce((a,b)=>a+b,0)/hr.length).toFixed(2)
};
/* is it uniform? if the spread is wide, no single CSS number fixes all of them */
out.spread = +(hr[hr.length-1] - hr[0]).toFixed(2);
out.worst = ok.slice().sort((a,b)=>b.headroomPct-a.headroomPct).slice(0,6)
              .map(r => r.name + ' ' + r.headroomPct + '%');
out.tightest = ok.slice().sort((a,b)=>a.headroomPct-b.headroomPct).slice(0,6)
              .map(r => r.name + ' ' + r.headroomPct + '%');
/* aspect matters too - cover binds on whichever side runs out first */
out.aspects = ok.map(r => r.name + ' ' + r.W + 'x' + r.H + ' ar' + (r.W/r.H).toFixed(2));
out.all = ok.map(r => ({n:r.name, hr:r.headroomPct, foot:r.footPct, body:r.contentPct}));
return out;
